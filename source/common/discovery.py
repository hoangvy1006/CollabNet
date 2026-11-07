"""LAN discovery over UDP broadcast: servers announce themselves, clients listen."""
import asyncio
import json
import socket

from .protocol import DISCOVERY_PORT


class Beacon:
    """Server side: broadcast {"svc":"collabnet","port":..,"name":..} every few seconds."""

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
                pass
        self._h = self.loop.call_later(self.interval, self._tick)

    def close(self):
        self._h.cancel()
        self.sock.close()


async def discover(timeout: float = 2.5):
    """Client side: listen for beacons; returns [{"host","port","name"}]."""
    loop = asyncio.get_running_loop()
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

    def readable():
        try:
            data, addr = sock.recvfrom(1024)
            info = json.loads(data.decode())
            if info.get("svc") == "collabnet":
                found[(addr[0], int(info["port"]))] = info.get("name", "")
        except (OSError, ValueError, KeyError):
            pass

    loop.add_reader(sock.fileno(), readable)
    try:
        await asyncio.sleep(timeout)
    finally:
        loop.remove_reader(sock.fileno())
        sock.close()
    return [{"host": h, "port": p, "name": n} for (h, p), n in found.items()]
