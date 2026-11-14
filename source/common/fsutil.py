"""Tiện ích ghi file an toàn khi mất điện / crash giữa chừng.

Ghi vào file tạm cùng thư mục rồi ``os.replace`` (nguyên tử trên cả Windows lẫn POSIX), nhờ vậy file đích
luôn là bản cũ hoàn chỉnh hoặc bản mới hoàn chỉnh, không bao giờ là bản ghi dở.

Dùng cho: users.json (server), known_hosts.json (client) và khoá định danh Ed25519 của server.
"""
import json
import os
import tempfile


def atomic_write_text(path: str, text: str, mode: int | None = None) -> None:
    """Ghi `text` vào `path` một cách nguyên tử. `mode` (vd. 0o600) được áp dụng cho file tạm trước khi đổi tên."""
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)   # mkstemp tạo file với quyền 0o600
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def atomic_write_json(path: str, obj) -> None:
    """Ghi `obj` dưới dạng JSON, nguyên tử (xem `atomic_write_text`)."""
    atomic_write_text(path, json.dumps(obj))
