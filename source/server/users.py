"""Kho tài khoản người dùng của server, lưu bền trong một file JSON.

Tách khỏi ``server/server.py`` để phần điều phối mạng (Session / Server) không phụ thuộc vào chi tiết lưu trữ.
Nếu sau này thay file JSON bằng SQLite, chỉ cần thay lớp này và giữ nguyên ``check_or_register``.

Định dạng file: ``{"<tên người dùng>": "<chuỗi pbkdf2$iterations$salt$hash>"}``.
"""
import json
import logging
import os
import threading
import time

from common import crypto
from common.fsutil import atomic_write_json

log = logging.getLogger("collabnet.users")


class UserStore:
    """Kho users.json: {tên người dùng: hash PBKDF2}; tên chưa có sẽ được đăng ký ngay lần đăng nhập đầu.

    Được gọi từ thread pool (`run_in_executor`) nên mọi truy cập vào `self.users` đều qua `self.lock`.
    """

    def __init__(self, path, first_seen_path=None):
        self.path, self.lock = path, threading.Lock()
        # Thời điểm tài khoản được tạo (lần đăng nhập đầu). Giữ ở file riêng để users.json (chỉ có hash mật khẩu)
        # không phải đổi định dạng và người dùng cũ không bị ảnh hưởng.
        self.first_seen_path = first_seen_path or os.path.join(os.path.dirname(os.path.abspath(path)), "first_seen.json")
        self.users, self.first_seen = {}, {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self.users = json.load(fh)
        if os.path.exists(self.first_seen_path):
            try:
                with open(self.first_seen_path, encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    self.first_seen = {u: float(t) for u, t in data.items()
                                       if isinstance(t, (int, float)) and not isinstance(t, bool)}
            except (OSError, ValueError):
                log.warning("cannot read %s; treating all accounts as pre-existing", self.first_seen_path)

    def first_seen_of(self, user) -> float:
        """Thời điểm tài khoản được tạo; 0.0 nếu không rõ (tài khoản có từ trước khi lưu mốc này)."""
        with self.lock:
            return float(self.first_seen.get(user) or 0.0)

    def check_or_register(self, user, password):
        """Trả về (ok, thông điệp). Tên chưa tồn tại sẽ được đăng ký với mật khẩu này (tối thiểu 4 ký tự).

        PBKDF2 (hàng chục ms) luôn chạy NGOÀI lock: nếu giữ lock suốt lúc băm thì mọi lượt đăng nhập song song
        bị xếp hàng tuần tự. Lock chỉ bao quanh thao tác đọc/ghi dict và file.
        """
        with self.lock:
            stored = self.users.get(user)
        if stored is None:
            if len(password) < 4:
                return False, "password too short (min 4)"
            new_hash = crypto.hash_password(password)
            with self.lock:
                stored = self.users.setdefault(user, new_hash)   # luồng khác có thể vừa đăng ký cùng tên
                if stored is new_hash:                           # ta là người đăng ký thành công
                    try:
                        atomic_write_json(self.path, self.users)
                    except OSError:
                        del self.users[user]                     # không để bộ nhớ lệch với đĩa
                        raise
                    # Mốc tạo tài khoản = lần đăng nhập đầu; dùng để không trả lại tin chung cũ hơn mốc này.
                    self.first_seen[user] = time.time()
                    try:
                        atomic_write_json(self.first_seen_path, self.first_seen)
                    except OSError:                              # không đăng nhập được chỉ vì lỗi ghi mốc phụ
                        log.exception("cannot write %s", self.first_seen_path)
                    return True, "registered"
        ok = crypto.verify_password(password, stored)
        return ok, "welcome back" if ok else "wrong password"
