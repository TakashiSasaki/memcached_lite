# memcached_lite.py
# Memcached-compatible asyncio server (fixed protocol handling)

import asyncio
import time

class MemcachedLite:
    def __init__(self):
        self.store = {}
        self.expirations = {}
        self.start_time = time.time()

    def set(self, key, value, expiry=0):
        self.store[key] = value
        if expiry > 0:
            self.expirations[key] = time.time() + expiry
        else:
            self.expirations.pop(key, None)

    def get(self, key):
        expiry = self.expirations.get(key)
        if expiry and time.time() > expiry:
            self.delete(key)
            return None
        return self.store.get(key)

    def delete(self, key):
        self.store.pop(key, None)
        self.expirations.pop(key, None)

    def flush(self):
        self.store.clear()
        self.expirations.clear()

    def stats(self):
        return {
            "keys": len(self.store),
            "uptime": f"{time.time() - self.start_time:.2f}"
        }

class MemcachedServer:
    def __init__(self, host='127.0.0.1', port=11211):
        self.host = host
        self.port = port
        self.store = MemcachedLite()

    async def handle_client(self, reader, writer):
        while True:
            line = await reader.readline()
            if not line:
                break

            parts = line.decode().strip().split()
            if not parts:
                writer.write(b'ERROR\r\n')
                await writer.drain()
                continue

            cmd = parts[0].lower()

            if cmd == 'set' and len(parts) == 5:
                key, flags, expiry, bytes_length = parts[1], parts[2], int(parts[3]), int(parts[4])
                try:
                    data = await reader.readexactly(bytes_length + 2)
                    value = data[:-2].decode()
                    self.store.set(key, value, expiry)
                    writer.write(b'STORED\r\n')
                except asyncio.IncompleteReadError:
                    writer.write(b'CLIENT_ERROR bad data chunk\r\n')

            elif cmd == 'get' and len(parts) >= 2:
                response = ""
                for key in parts[1:]:
                    value = self.store.get(key)
                    if value is not None:
                        response += f"VALUE {key} 0 {len(value)}\r\n{value}\r\n"
                response += "END\r\n"
                writer.write(response.encode())

            elif cmd == 'delete' and len(parts) == 2:
                self.store.delete(parts[1])
                writer.write(b'DELETED\r\n')

            elif cmd == 'flush_all':
                self.store.flush()
                writer.write(b'OK\r\n')

            elif cmd == 'stats':
                stats = self.store.stats()
                response = ""
                for key, val in stats.items():
                    response += f'STAT {key} {val}\r\n'
                response += 'END\r\n'
                writer.write(response.encode())

            else:
                writer.write(b'ERROR\r\n')

            await writer.drain()

        writer.close()

    async def start(self):
        self.store.start_time = time.time()
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"MemcachedLite running on {addr}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    server = MemcachedServer()
    asyncio.run(server.start())
