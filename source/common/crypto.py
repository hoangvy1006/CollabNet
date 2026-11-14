"""Cryptographic primitives used by CollabNet.

* X25519 ephemeral Diffie-Hellman  -> forward-secret shared secret
* Ed25519 server identity          -> authenticates the server (anti man-in-the-middle)
* HKDF-SHA256                      -> two directional AES-256 keys
* AES-256-GCM                      -> authenticated encryption of every packet
* PBKDF2-HMAC-SHA256               -> salted password hashes stored on the server

Only the well-known `cryptography` package is used; no home-made crypto.
"""
import hashlib
import hmac
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .fsutil import atomic_write_text

_RAW = dict(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
PBKDF2_ITERATIONS = 120_000


# ---------------------------------------------------------------- key agreement
def new_ephemeral():
    """Return (private_key_object, 32-byte public key)."""
    # Khoá tạm chỉ dùng cho MỘT phiên bắt tay (forward secrecy): bí mật chung X25519 không thể tái tạo nếu
    # thiếu khoá riêng tạm này, nên sau này lộ khoá dài hạn cũng không giải mã ngược được lưu lượng cũ.
    priv = X25519PrivateKey.generate()
    return priv, priv.public_key().public_bytes(**_RAW)


def transcript(client_pub: bytes, server_pub: bytes, client_cid: int, server_cid: int) -> bytes:
    """Data signed by the server so that the client knows the handshake is genuine."""
    # Chữ ký bao gồm cả hai khoá công khai tạm thời và hai connection id: gắn chặt chữ ký vào đúng phiên
    # bắt tay này nên không thể bị phát lại (replay) sang một phiên khác.
    return b"collabnet-v1-handshake" + client_pub + server_pub + client_cid.to_bytes(4, "big") + server_cid.to_bytes(4, "big")


def derive_keys(priv, peer_pub: bytes, client_pub: bytes, server_pub: bytes):
    """ECDH + HKDF. Returns (key_client_to_server, key_server_to_client)."""
    # HKDF tách bí mật chung X25519 thành hai khoá AES-256 độc lập, mỗi chiều truyền một khoá riêng.
    shared = priv.exchange(X25519PublicKey.from_public_bytes(peer_pub))
    okm = HKDF(algorithm=hashes.SHA256(), length=64, salt=client_pub + server_pub,
               info=b"collabnet-v1-keys").derive(shared)
    return okm[:32], okm[32:]


class PacketCipher:
    """AES-256-GCM. Nonce = 4 zero bytes || 8-byte packet number.

    Each direction has its own key and packet numbers are never reused
    (retransmissions get a *new* packet number), so a nonce is never repeated.
    The packet header is authenticated as additional data (AAD).
    """

    def __init__(self, key: bytes):
        self._aead = AESGCM(key)

    @staticmethod
    def _nonce(pn: int) -> bytes:
        # 96-bit nonce: 32 zero bits || 64-bit packet number. Retransmits use a
        # fresh packet number, so this nonce never repeats for a given key.
        if not 0 <= pn < (1 << 64):
            raise ValueError("packet number does not fit the AES-GCM nonce")
        return b"\x00\x00\x00\x00" + pn.to_bytes(8, "big")

    def seal(self, pn: int, aad: bytes, plaintext: bytes) -> bytes:
        return self._aead.encrypt(self._nonce(pn), plaintext, aad)

    def open(self, pn: int, aad: bytes, ciphertext: bytes) -> bytes:
        return self._aead.decrypt(self._nonce(pn), ciphertext, aad)  # raises InvalidTag


# ---------------------------------------------------------------- server identity
def load_or_create_identity(path: str) -> Ed25519PrivateKey:
    """Nạp khoá định danh Ed25519 của server; chưa có thì sinh mới và lưu với quyền 0600.

    Ghi nguyên tử (file tạm + rename): nếu server bị tắt đúng lúc đang ghi thì không để lại file khoá rỗng /
    ghi dở khiến lần khởi động sau không đọc được khoá (và client phải xoá pin cũ).
    """
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(fh.read().strip()))
    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw,
                            encryption_algorithm=serialization.NoEncryption())
    atomic_write_text(path, raw.hex(), mode=0o600)
    return key


def public_bytes(identity: Ed25519PrivateKey) -> bytes:
    # Khoá công khai dạng raw 32 byte: đây là giá trị client ghim (TOFU) và hiển thị thành fingerprint.
    return identity.public_key().public_bytes(**_RAW)


def sign(identity: Ed25519PrivateKey, data: bytes) -> bytes:
    # Chữ ký 64 byte trên transcript bắt tay; chỉ server (bên giữ khoá riêng) tạo được chữ ký này.
    return identity.sign(data)


def verify(pub: bytes, sig: bytes, data: bytes) -> bool:
    # Mọi lỗi (sai độ dài khoá, chữ ký không khớp...) đều coi là "không hợp lệ", không để lan ra ngoài.
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, data)
        return True
    except Exception:
        return False


def fingerprint(pub: bytes) -> str:
    # Dấu vân tay ngắn gọn (128 bit đầu của SHA-256) để người dùng so sánh bằng mắt / client ghim (TOFU).
    h = hashlib.sha256(pub).hexdigest()[:32]
    return ":".join(h[i:i + 4] for i in range(0, len(h), 4))


# ---------------------------------------------------------------- passwords
def hash_password(password: str, salt: bytes | None = None, iterations: int = PBKDF2_ITERATIONS) -> str:
    # Định dạng lưu: "pbkdf2$<iterations>$<salt hex>$<hash hex>". Tham số iterations được ghi kèm để sau này
    # tăng độ khó vẫn xác thực được các mật khẩu cũ (verify_password đọc đúng số vòng đã dùng).
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    # So sánh bằng compare_digest (thời gian không phụ thuộc nội dung) để tránh tấn công đo thời gian.
    try:
        _, it, salt, dk = stored.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(it))
        return hmac.compare_digest(calc, bytes.fromhex(dk))
    except Exception:
        return False
