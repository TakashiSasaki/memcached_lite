# filename: redis_notification.py

import asyncio
import fnmatch
import logging
from redis_lite import RedisLiteServer


class RedisNotificationServer(RedisLiteServer):
    async def notify_del(self, key: str):
        """
        Sends a deletion notification for the given key to all clients whose subscription
        patterns match either the keyevent channel or the keyspace channel for deletion.
        For keyevent notifications, the channel is '__keyevent@0__:del' and the data is the key.
        For keyspace notifications, the channel is '__keyspace@0__:{key}' and the data is 'del'.
        """
        event_channel = "__keyevent@0__:del"
        keyspace_channel = f"__keyspace@0__:{key}"
        
        event_msg = f"*3\r\n$7\r\nmessage\r\n${len(event_channel)}\r\n{event_channel}\r\n${len(key)}\r\n{key}\r\n"
        keyspace_msg = f"*3\r\n$7\r\nmessage\r\n${len(keyspace_channel)}\r\n{keyspace_channel}\r\n$3\r\nDEL\r\n"
        
        for cid, info in list(self.clients.items()):
            writer = info.get("writer")
            if writer and not writer.is_closing():
                for pattern in info["subscriptions"]:
                    if fnmatch.fnmatch(event_channel, pattern):
                        try:
                            writer.write(event_msg.encode())
                            await writer.drain()
                            logging.debug(f"Sent keyevent deletion notification for key '{key}' to client id {cid} (pattern: {pattern})")
                        except Exception as e:
                            logging.exception(f"Error sending keyevent deletion notification to client id {cid}: {e}")
                    if fnmatch.fnmatch(keyspace_channel, pattern):
                        try:
                            writer.write(keyspace_msg.encode())
                            await writer.drain()
                            logging.debug(f"Sent keyspace deletion notification for key '{key}' to client id {cid} (pattern: {pattern})")
                        except Exception as e:
                            logging.exception(f"Error sending keyspace deletion notification to client id {cid}: {e}")

    async def notify_set(self, key: str, value: bytes):
        """
        Sends a set notification for the given key and binary value to all clients whose subscription
        patterns match either the keyevent channel or the keyspace channel for 'set' events.
        
        For keyevent notifications, the channel is '__keyevent@0__:set'.
        The RESP message includes four elements: "message", the channel, the key, and the value.
        
        For keyspace notifications, the channel is '__keyspace@0__:{key}'.
        The RESP message includes four elements: "message", the channel, the event 'set', and the value.
        
        Since we assume the data is pure binary, we decode it using 'latin-1' for a one-to-one mapping.
        """
        event_channel = "__keyevent@0__:set"
        keyspace_channel = f"__keyspace@0__:{key}"
        
        value_str = value.decode('latin-1')
        
        event_msg = (
            f"*4\r\n"
            f"$7\r\nmessage\r\n"
            f"${len(event_channel)}\r\n{event_channel}\r\n"
            f"${len(key)}\r\n{key}\r\n"
            f"${len(value_str)}\r\n{value_str}\r\n"
        )
        keyspace_msg = (
            f"*4\r\n"
            f"$7\r\nmessage\r\n"
            f"${len(keyspace_channel)}\r\n{keyspace_channel}\r\n"
            f"$3\r\nset\r\n"
            f"${len(value_str)}\r\n{value_str}\r\n"
        )
        
        for cid, info in list(self.clients.items()):
            writer = info.get("writer")
            if writer and not writer.is_closing():
                for pattern in info["subscriptions"]:
                    if fnmatch.fnmatch(event_channel, pattern):
                        try:
                            writer.write(event_msg.encode())
                            await writer.drain()
                            logging.debug(f"Sent keyevent set notification for key '{key}' to client id {cid} (pattern: {pattern})")
                        except Exception as e:
                            logging.exception(f"Error sending keyevent set notification to client id {cid}: {e}")
                    if fnmatch.fnmatch(keyspace_channel, pattern):
                        try:
                            writer.write(keyspace_msg.encode())
                            await writer.drain()
                            logging.debug(f"Sent keyspace set notification for key '{key}' to client id {cid} (pattern: {pattern})")
                        except Exception as e:
                            logging.exception(f"Error sending keyspace set notification to client id {cid}: {e}")

    async def notify_expire(self, key: str):
        """
        Sends an expiration notification for the given key to all clients whose subscription
        patterns match either the keyevent channel or the keyspace channel for expiration.
        
        For keyevent notifications, the channel is '__keyevent@0__:expired' and the data is the key.
        For keyspace notifications, the channel is '__keyspace@0__:{key}' and the data is 'expired'.
        
        RESP message format:
          *3\r\n$7\r\nmessage\r\n$<len(channel)>\r\n<channel>\r\n$<len(data)>\r\n<data>\r\n
        """
        event_channel = "__keyevent@0__:expired"
        keyspace_channel = f"__keyspace@0__:{key}"
        
        event_msg = f"*3\r\n$7\r\nmessage\r\n${len(event_channel)}\r\n{event_channel}\r\n${len(key)}\r\n{key}\r\n"
        keyspace_msg = f"*3\r\n$7\r\nmessage\r\n${len(keyspace_channel)}\r\n{keyspace_channel}\r\n$7\r\nexpired\r\n"
        
        for cid, info in list(self.clients.items()):
            writer = info.get("writer")
            if writer and not writer.is_closing():
                for pattern in info["subscriptions"]:
                    if fnmatch.fnmatch(event_channel, pattern):
                        try:
                            writer.write(event_msg.encode())
                            await writer.drain()
                            logging.debug(f"Sent keyevent expired notification for key '{key}' to client id {cid} (pattern: {pattern})")
                        except Exception as e:
                            logging.exception(f"Error sending keyevent expired notification to client id {cid}: {e}")
                    if fnmatch.fnmatch(keyspace_channel, pattern):
                        try:
                            writer.write(keyspace_msg.encode())
                            await writer.drain()
                            logging.debug(f"Sent keyspace expired notification for key '{key}' to client id {cid} (pattern: {pattern})")
                        except Exception as e:
                            logging.exception(f"Error sending keyspace expired notification to client id {cid}: {e}")

if __name__ == '__main__':
    server = RedisNotificationServer()
    asyncio.run(server.start())
