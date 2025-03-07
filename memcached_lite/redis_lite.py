import asyncio
import time
import os
import sys
import logging

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

async def read_line(reader):
    """Read a line and strip CRLF."""
    line = await reader.readline()
    if not line:
        return None
    return line.decode().rstrip('\r\n')

async def parse_resp_command(reader):
    """
    Minimal RESP parser.
    If the command starts with '*' it parses a multi-bulk command.
    Otherwise, it falls back to splitting the line.
    """
    line = await read_line(reader)
    if line is None:
        return None
    if line.startswith("*"):
        try:
            num_args = int(line[1:])
        except ValueError:
            return None
        args = []
        for _ in range(num_args):
            bulk_header = await read_line(reader)
            if bulk_header is None or not bulk_header.startswith("$"):
                return None
            try:
                length = int(bulk_header[1:])
            except ValueError:
                return None
            arg = await reader.readexactly(length)
            # Read the trailing CRLF
            await reader.readexactly(2)
            args.append(arg.decode())
        return args
    else:
        # Fallback: inline command
        return line.split()

class RedisLiteServer:
    def __init__(self, host='127.0.0.1', port=11311):
        self.host = host
        self.port = port
        self.clients = {}           # Mapping: client_id -> { "id": client_id, "addr": addr, "subscriptions": [], "writer": writer }
        self.client_counter = 0     # Unique id counter for clients

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        # Assign a unique client id and store connection info.
        self.client_counter += 1
        client_id = self.client_counter
        self.clients[client_id] = {
            "id": client_id,
            "addr": addr,
            "subscriptions": [],
            "writer": writer
        }
        logging.info(f"Client connected: {addr}, assigned id: {client_id}")

        subscription_mode = False  # Flag indicating subscription mode
        try:
            while True:
                if subscription_mode:
                    # In subscription mode, simply wait for incoming data and ignore it.
                    data = await reader.read(1024)
                    if not data:
                        logging.info(f"Client {addr} (id: {client_id}) disconnected from subscription mode.")
                        break
                    logging.debug(f"(Subscription mode) Ignored data from {addr} (id: {client_id}): {data.decode().strip()}")
                    continue

                cmd_parts = await parse_resp_command(reader)
                if not cmd_parts:
                    logging.info(f"Client {addr} (id: {client_id}) disconnected (no command).")
                    break
                logging.debug(f"Parsed command from {addr} (id: {client_id}): {cmd_parts}")
                command = cmd_parts[0].upper()

                if command == "PING":
                    logging.debug(f"PING received from {addr} (id: {client_id})")
                    writer.write(b"+PONG\r\n")
                elif command == "INFO":
                    logging.debug(f"INFO command received from {addr} (id: {client_id})")
                    info_response = (
                        "# Server\r\n"
                        "redis_version:1.0\r\n"
                        f"process_id:{os.getpid()}\r\n"
                        f"uptime_in_seconds:{int(time.time())}\r\n"
                        "# Clients\r\n"
                        f"connected_clients:{len(self.clients)}\r\n"
                        "# Memory\r\n"
                        "used_memory:10240\r\n"
                        "used_memory_human:10K\r\n"
                        "maxmemory:0\r\n"
                    )
                    # Format as RESP Bulk String: $<length>\r\n<data>\r\n
                    resp = f"${len(info_response)}\r\n{info_response}\r\n"
                    writer.write(resp.encode())
                elif command == "CLIENT" and len(cmd_parts) >= 2 and cmd_parts[1].upper() == "LIST":
                    logging.debug(f"CLIENT LIST command received from {addr} (id: {client_id})")
                    # Build client list info for each connected client.
                    lines = []
                    for cid, info in self.clients.items():
                        client_addr = info["addr"]
                        subs = ",".join(info["subscriptions"]) if info["subscriptions"] else ""
                        line = (f"id={cid} addr={client_addr[0]}:{client_addr[1]} fd=5 name= age=0 idle=0 flags=N "
                                f"db=0 sub=0 psub={len(info['subscriptions'])} multi=-1 qbuf=0 qbuf-free=32768 obl=0 oll=0 omem=0 "
                                f"events=r cmd=client subscriptions=[{subs}]\r\n")
                        lines.append(line)
                    client_list = "".join(lines)
                    resp = f"${len(client_list)}\r\n{client_list}\r\n"
                    writer.write(resp.encode())
                elif command == "PSUBSCRIBE":
                    logging.debug(f"PSUBSCRIBE command received from {addr} (id: {client_id})")
                    if len(cmd_parts) < 2:
                        writer.write(b"-ERR wrong number of arguments for 'psubscribe' command\r\n")
                    else:
                        subscription_count = 0
                        for pattern in cmd_parts[1:]:
                            subscription_count += 1
                            # Record the subscription pattern in the client's registry.
                            self.clients[client_id]["subscriptions"].append(pattern)
                            # Send RESP-formatted subscription confirmation:
                            # *3\r\n$10\r\npsubscribe\r\n$<len(pattern)>\r\n<pattern>\r\n:<subscription_count>\r\n
                            response = f"*3\r\n$10\r\npsubscribe\r\n${len(pattern)}\r\n{pattern}\r\n:{subscription_count}\r\n"
                            writer.write(response.encode())
                            logging.info(f"Client {addr} (id: {client_id}) subscribed to pattern: {pattern} (total: {subscription_count})")
                        # Enter subscription mode: keep the connection open and ignore further commands.
                        subscription_mode = True
                else:
                    logging.debug(f"Unknown command from {addr} (id: {client_id}): {cmd_parts}")
                    writer.write(b"-ERR unknown command\r\n")
                await writer.drain()
        except Exception as e:
            logging.exception(f"Error handling client {addr} (id: {client_id}): {e}")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception as e:
                logging.exception(f"Error closing connection for {addr} (id: {client_id}): {e}")
            # Remove client from registry
            if client_id in self.clients:
                del self.clients[client_id]
                logging.info(f"Removed client id {client_id} from registry")
            logging.info(f"Connection closed: {addr} (id: {client_id})")

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logging.info(f"RedisLiteServer listening on {addr}")
        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    server = RedisLiteServer()
    asyncio.run(server.start())
