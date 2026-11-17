"""Lịch sử hội thoại phía server: người dùng đăng xuất / tắt máy rồi vào lại vẫn còn các đoạn chat cũ.

Server là nguồn lưu trữ duy nhất (client chỉ giữ bản trong RAM của phiên hiện tại): mỗi tin nhắn đã định
tuyến được ghi vào `history.json` trong thư mục dữ liệu của server và được gửi lại ngay sau khi xác thực.

Ghi đĩa được gom lại (debounce 1 giây) nên một đợt chat nhanh không tạo ra hàng loạt lần ghi, và luôn ghi
nguyên tử (`atomic_write_json`) để mất điện giữa chừng không làm hỏng file.
"""
import json
import logging

from common.fsutil import atomic_write_json

log = logging.getLogger("collabnet.history")

MAX_RECORDS = 4000               # tổng số tin giữ lại trên đĩa (cũ nhất bị bỏ khi vượt)
MAX_REPLAY = 300                 # số tin tối đa gửi lại cho một người khi đăng nhập
MAX_REPLAY_BYTES = 512 * 1024    # chặn payload HISTORY quá lớn (một thông điệp JSON tối đa 1 MB)


class HistoryStore:
    """Kho lịch sử tin nhắn: nạp một lần khi server khởi động, thêm dần khi có tin mới, ghi đĩa có debounce."""

    def __init__(self, path, loop):
        self.path, self.loop = path, loop
        self.records: list[dict] = []
        self._save_handle = None
        self._load()

    def _load(self):
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return                        # chưa có file (lần chạy đầu) hoặc file hỏng: bắt đầu với lịch sử rỗng
        if isinstance(data, list):
            self.records = [r for r in data
                            if isinstance(r, dict) and r.get("id") and r.get("from") and r.get("to")]

    def add(self, rec: dict):
        """Ghi một tin đã định tuyến xong; việc ghi đĩa diễn ra sau (gom nhiều tin vào một lần ghi)."""
        self.records.append(rec)
        if len(self.records) > MAX_RECORDS:
            del self.records[:len(self.records) - MAX_RECORDS]
        if self._save_handle is None:
            self._save_handle = self.loop.call_later(1.0, self.save)

    def for_user(self, user: str, since: float = 0.0) -> list[dict]:
        """Tin chung, tin `user` đã gửi và tin gửi riêng cho `user` — cũ nhất trước, giới hạn số lượng/dung lượng.

        `since` là thời điểm tài khoản được tạo: tin CHUNG cũ hơn mốc đó không được trả lại, để tài khoản mới
        đăng ký không nhận được hội thoại chung đã diễn ra trước khi nó tồn tại. Tin riêng không cần lọc vì
        chúng chỉ có thể phát sinh sau khi tài khoản đã tồn tại.
        """
        picked, total = [], 0
        for rec in reversed(self.records):
            if rec.get("to") == "*":
                if since:
                    try:
                        if float(rec.get("ts") or 0) < since:
                            continue
                    except (TypeError, ValueError):
                        continue                          # mốc giờ hỏng: bỏ qua cho an toàn
            elif rec.get("from") != user and rec.get("to") != user:
                continue
            total += len(rec.get("text") or "") + 96
            if picked and (total > MAX_REPLAY_BYTES or len(picked) >= MAX_REPLAY):
                break
            picked.append(rec)
        picked.reverse()
        return picked

    def save(self):
        if self._save_handle is not None:
            self._save_handle.cancel()
            self._save_handle = None
        try:
            atomic_write_json(self.path, self.records)
        except OSError:
            log.exception("cannot write chat history to %s", self.path)

    def close(self):
        self.save()
