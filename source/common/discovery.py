"""LAN discovery over UDP broadcast: servers announce themselves, clients listen."""
import asyncio
import json
import socket

from .protocol import DISCOVERY_PORT


class Beacon:
    """Server side: broadcast {"svc":"collabnet","port":..,"name":..} every few seconds.

    Server phát gói UDP broadcast định kỳ để client trong cùng LAN tìm thấy mà không cần biết trước địa chỉ IP.
    Gửi thêm tới 127.0.0.1 để client chạy cùng máy cũng phát hiện được.
    """

    def __init__(self, loop, service_port: int, name: str, interval: float = 2.0):
        self.loop, self.interval = loop, interval
        self.msg = json.dumps({"svc": "collabnet", "port": service_port, "name": name}).encode()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setblocking(False)
        self._h = loop.call_soon(self._tick)

    def _tick(self):
        for dest in ("255.255.255.255", "127.0.0.1"):
            try:
                self.sock.sendto(self.msg, (dest, DISCOVERY_PORT))
            except OSError:
                pass                          # mạng chưa sẵn sàng / không có route broadcast: bỏ qua, lần sau thử lại
        self._h = self.loop.call_later(self.interval, self._tick)

    def close(self):
        self._h.cancel()
        self.sock.close()


async def discover(timeout: float = 2.5):
    """Client side: listen for beacons; returns [{"host","port","name"}].

    Dùng `loop.sock_recvfrom` thay cho `add_reader` để chạy được trên cả ProactorEventLoop (Windows mặc định,
    không hỗ trợ add_reader) lẫn SelectorEventLoop. Vòng lặp dừng khi hết `timeout` hoặc socket lỗi.
    """
    loop = asyncio.get_running_loop()
    # SO_REUSEADDR/SO_REUSEPORT cho phép nhiều client trên cùng máy cùng lắng nghe beacon trên một cổng.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
    try:
        sock.bind(("", DISCOVERY_PORT))
    except OSError:
        sock.close()
        return []
    sock.setblocking(False)
    found = {}
    deadline = loop.time() + timeout
    try:
        while (remaining := deadline - loop.time()) > 0:
            try:
                data, addr = await asyncio.wait_for(loop.sock_recvfrom(sock, 2048), remaining)
            except asyncio.TimeoutError:
                break                             # hết thời gian chờ: trả về những gì đã thấy
            except OSError:
                break                             # socket bị đóng / lỗi mạng: dừng sớm
            try:
                info = json.loads(data.decode())
                if info.get("svc") == "collabnet":
                    found[(addr[0], int(info["port"]))] = info.get("name", "")
            except (ValueError, KeyError, TypeError):
                continue                          # gói lạ trong LAN: bỏ qua, không làm hỏng lượt dò
    finally:
        sock.close()
    return [{"host": h, "port": p, "name": n} for (h, p), n in found.items()]
