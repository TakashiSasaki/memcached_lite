# memcached_lite.py
# Memcached-compatible lightweight server (asyncio-based), fully protocol-compliant with detailed logging,
# improved stats, and refined noreply handling (using flexible detection)

import asyncio
import time
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

class MemcachedLite:
    def __init__(self):
        self.store = {}             # In-memory key-value store
        self.expirations = {}       # Expiration timestamps for keys
        self.start_time = time.time()

    def set(self, key, value, expiry=0):
        self.store[key] = value
        if expiry > 0:
            self.expirations[key] = time.time() + expiry
        else:
            self.expirations.pop(key, None)
        logging.debug(f"Set key: {key}, value: {value}, expiry: {expiry}")
        logging.debug(f"Current store: {self.store}")

    def get(self, key):
        expiry = self.expirations.get(key)
        if expiry and time.time() > expiry:
            self.delete(key)
            logging.debug(f"Key expired: {key}")
            return None
        value = self.store.get(key)
        logging.debug(f"Get key: {key}, returned value: {value}")
        return value

    def delete(self, key):
        existed = key in self.store
        self.store.pop(key, None)
        self.expirations.pop(key, None)
        logging.debug(f"Deleted key: {key}")
        logging.debug(f"Current store: {self.store}")
        return existed

    def flush(self):
        self.store.clear()
        self.expirations.clear()
        logging.debug("Flushed all keys")
        logging.debug(f"Current store: {self.store}")

    def stats(self):
        uptime = time.time() - self.start_time
        # Return simplified stats in standard format
        stats_data = {
            "uptime": f"{int(uptime)}",
            "curr_items": f"{len(self.store)}"
        }
        logging.debug(f"Stats requested: {stats_data}")
        return stats_data

class MemcachedServer:
    def __init__(self, host='127.0.0.1', port=11211):
        self.host = host
        self.port = port
        self.store = MemcachedLite()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info(f"Client connected: {addr}")
        try:
            while True:
                line = await reader.readline()
                if not line:
                    logging.info(f"Client disconnected (no data): {addr}")
                    break

                parts = line.decode().strip().split()
                logging.debug(f"Received line from {addr}: {parts}")
                if not parts:
                    writer.write(b'ERROR\r\n')
                    await writer.drain()
                    continue

                cmd = parts[0].lower()

                # set command: set <key> <flags> <expiry> <bytes> [noreply]
                if cmd == 'set' and len(parts) >= 5:
                    key = parts[1]
                    flags = parts[2]
                    expiry = int(parts[3])
                    bytes_length = int(parts[4])
                    # Detect noreply in any subsequent argument
                    noreply = any(part.lower() == 'noreply' for part in parts[5:])
                    try:
                        # Read exactly bytes_length + CRLF (i.e. +2 bytes)
                        data_block = await reader.readexactly(bytes_length + 2)
                        value = data_block[:-2].decode()
                        logging.debug(f"Set command - key: {key}, value: {value}, noreply: {noreply}")
                        self.store.set(key, value, expiry)
                        if not noreply:
                            writer.write(b'STORED\r\n')
                        else:
                            logging.debug("Noreply set: response suppressed")
                    except asyncio.IncompleteReadError:
                        writer.write(b'CLIENT_ERROR bad data chunk\r\n')

                # get command: get <key> [<key2> ...]
                elif cmd == 'get' and len(parts) >= 2:
                    for key in parts[1:]:
                        value = self.store.get(key)
                        if value is not None:
                            response = f"VALUE {key} 0 {len(value)}\r\n{value}\r\n"
                            writer.write(response.encode())
                    writer.write(b'END\r\n')

                # delete command: delete <key> [noreply]
                elif cmd == 'delete' and len(parts) >= 2:
                    key = parts[1]
                    noreply = any(part.lower() == 'noreply' for part in parts[2:])
                    existed = self.store.delete(key)
                    logging.debug(f"Delete command - key: {key}, existed: {existed}, noreply: {noreply}")
                    if not noreply:
                        if existed:
                            writer.write(b'DELETED\r\n')
                        else:
                            writer.write(b'NOT_FOUND\r\n')
                    else:
                        logging.debug("Noreply delete: response suppressed")

                # flush_all command: flush_all [noreply]
                elif cmd == 'flush_all':
                    noreply = any(part.lower() == 'noreply' for part in parts[1:])
                    self.store.flush()
                    logging.debug(f"Flush_all command, noreply: {noreply}")
                    if not noreply:
                        writer.write(b'OK\r\n')

                # stats command
                elif cmd == 'stats':
                    stats = self.store.stats()
                    for key, val in stats.items():
                        writer.write(f"STAT {key} {val}\r\n".encode())
                    writer.write(b'END\r\n')

                else:
                    writer.write(b'ERROR\r\n')

                await writer.drain()

        except (asyncio.IncompleteReadError, ConnectionResetError):
            logging.info(f"Client disconnected abruptly: {addr}")
        except Exception as e:
            logging.exception(f"Unexpected error with client {addr}: {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception as e:
                logging.exception(f"Error while closing writer for {addr}: {e}")
            logging.info(f"Connection closed: {addr}")

    async def start(self):
        self.store.start_time = time.time()
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logging.info(f"MemcachedLite running on {addr}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    server = MemcachedServer()
    asyncio.run(server.start())
