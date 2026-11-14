"""Kho tài khoản người dùng của server, lưu bền trong một file JSON.

Tách khỏi ``server/server.py`` để phần điều phối mạng (Session / Router / Relay) không phụ thuộc vào chi tiết
lưu trữ. Nếu sau này thay file JSON bằng SQLite, chỉ cần thay lớp này và giữ nguyên ``check_or_register``.

Định dạng file: ``{"<tên người dùng>": "<chuỗi pbkdf2$iterations$salt$hash>"}``.
"""
import json
import os
import threading

from common import crypto
from common.fsutil import atomic_write_json


class UserStore:
    """users.json: {username: pbkdf2 hash}. Unknown usernames are registered on first login.

    Kho người dùng đơn giản dạng file JSON. Được gọi từ thread pool (`run_in_executor`) nên mọi truy cập
    vào `self.users` đều qua `self.lock`.
    """

    def __init__(self, path):
        self.path, self.lock = path, threading.Lock()
        self.users = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self.users = json.load(fh)

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
                    return True, "registered"
        ok = crypto.verify_password(password, stored)
        return ok, "welcome back" if ok else "wrong password"
