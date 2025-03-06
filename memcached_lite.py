# memcached_lite.py
# Memcached-compatible lightweight server (asyncio-based) with enhanced statistics tracking,
# including process information, command counters, and uptime tracking.

import asyncio
import time
import os
import sys
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

class MemcachedLite:
    def __init__(self):
        self.store = {}             # In-memory key-value store
        self.expirations = {}       # Expiration timestamps for keys
        self.start_time = time.time()
        self.get_hits = 0           # Count of successful GET operations
        self.get_misses = 0         # Count of GET operations with no result
        self.cmd_get = 0            # Total number of GET commands executed
        self.cmd_set = 0            # Total number of SET commands executed
        self.cmd_delete = 0         # Total number of DELETE commands executed
        self.total_items = 0        # Total number of items stored since startup
        self.version = "memcached_lite 0.1"  # Fixed version string
        self.pid = os.getpid()      # Process ID
        self.process_path = sys.executable  # Path to the Python executable

    def set(self, key, value, expiry=0):
        self.store[key] = value
        if expiry > 0:
            self.expirations[key] = time.time() + expiry
        else:
            self.expirations.pop(key, None)
        self.cmd_set += 1
        self.total_items += 1
        logging.debug(f"Set key: {key}, value: {value}, expiry: {expiry}")
        logging.debug(f"Current store: {self.store}")

    def get(self, key):
        self.cmd_get += 1
        expiry = self.expirations.get(key)
        if expiry and time.time() > expiry:
            self.delete(key)
            logging.debug(f"Key expired: {key}")
            self.get_misses += 1
            return None
        value = self.store.get(key)
        if value is not None:
            self.get_hits += 1
        else:
            self.get_misses += 1
        logging.debug(f"Get key: {key}, returned value: {value}")
        return value

    def delete(self, key):
        self.cmd_delete += 1
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
        # Return enhanced stats
        stats_data = {
            "pid": f"{self.pid}",
            "time": f"{int(time.time())}",
            "uptime": f"{int(uptime)}",
            "curr_items": f"{len(self.store)}",
            "total_items": f"{self.total_items}",
            "get_hits": f"{self.get_hits}",
            "get_misses": f"{self.get_misses}",
            "cmd_get": f"{self.cmd_get}",
            "cmd_set": f"{self.cmd_set}",
            "cmd_delete": f"{self.cmd_delete}",
            "version": self.version,
            "process_path": self.process_path
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
