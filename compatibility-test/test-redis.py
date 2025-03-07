# filename: test-redis.py

import redis
import time
import asyncio
import sys
sys.path.append("..")
from memcached_lite import RedisNotificationServer

# Create a server instance (assumes RedisLiteServer is running in the same environment)
server_instance = RedisNotificationServer()

def test_ping(r, conn_id):
    print(f"Testing PING command on connection {conn_id}...")
    result = r.ping()
    print(f"PING response from connection {conn_id}: {result}")

def test_info(r, conn_id):
    print(f"\nTesting INFO command on connection {conn_id}...")
    result = r.execute_command("INFO")
    print(f"INFO response from connection {conn_id}:")
    print(result)

def test_client_list(r):
    print("\nTesting CLIENT LIST command (should reflect number of connections)...")
    result = r.execute_command("CLIENT", "LIST")
    print("CLIENT LIST response:")
    print(result)

def test_psubscribe(r):
    print("\nTesting PSUBSCRIBE command for key notifications with multiple patterns...")
    pubsub = r.pubsub()
    patterns = [
        "__keyspace@0__:*",
        "__keyspace@0__:user:*",
        "__keyspace@0__:order:*",
        "__keyevent@0__:*",
        "__keyevent@0__:user:*",
        "__keyevent@0__:order:*",
        "__keyspace@0__:session:*",
        "__keyevent@0__:session:*"
    ]
    pubsub.psubscribe(*patterns)
    print("Subscribed to multiple key notification patterns. Waiting for messages for 10 seconds...")
    
    start = time.time()
    while time.time() - start < 10:
        message = pubsub.get_message(timeout=1)
        if message:
            print("Received message:", message)
        else:
            print("No message received...")
        time.sleep(1)
    print("Waiting 5 seconds before closing pubsub connection...")
    time.sleep(5)
    pubsub.close()
    print("PSUBSCRIBE test complete.")

async def test_notify_set():
    print("\nTesting notify_set for key 'testkey' with binary data...")
    r_sub = redis.Redis(host='localhost', port=11311, decode_responses=True)
    pubsub = r_sub.pubsub()
    # Subscribe to keyevent 'set' and keyspace notifications for "testkey"
    pubsub.psubscribe("__keyevent@0__:set", f"__keyspace@0__:testkey")
    print("Subscribed for set notifications for key 'testkey'.")
    
    await asyncio.sleep(2)
    
    binary_value = b'\x01\x02\x03'
    print("Calling notify_set('testkey', binary_value)...")
    await server_instance.notify_set("testkey", binary_value)
    
    start = time.time()
    while time.time() - start < 5:
        message = pubsub.get_message(timeout=1)
        if message:
            print("Received set notification:", message)
        await asyncio.sleep(1)
    pubsub.close()
    print("notify_set test complete.")

async def test_notify_expire():
    print("\nTesting notify_expire for key 'testkey' (EXPIRE event)...")
    r_sub = redis.Redis(host='localhost', port=11311, decode_responses=True)
    pubsub = r_sub.pubsub()
    # Subscribe to keyevent 'expire' and keyspace notifications for "testkey"
    pubsub.psubscribe("__keyevent@0__:expire", f"__keyspace@0__:testkey")
    print("Subscribed for expire notifications for key 'testkey'.")
    
    await asyncio.sleep(2)
    
    print("Calling notify_expire('testkey')...")
    await server_instance.notify_expire("testkey")
    
    start = time.time()
    while time.time() - start < 5:
        message = pubsub.get_message(timeout=1)
        if message:
            print("Received expire notification:", message)
        await asyncio.sleep(1)
    pubsub.close()
    print("notify_expire test complete.")

async def test_notify_expired():
    print("\nTesting notify_expired for key 'testkey' (EXPIRED event)...")
    r_sub = redis.Redis(host='localhost', port=11311, decode_responses=True)
    pubsub = r_sub.pubsub()
    # Subscribe to keyevent 'expired' and keyspace notifications for "testkey"
    pubsub.psubscribe("__keyevent@0__:expired", f"__keyspace@0__:testkey")
    print("Subscribed for expired notifications for key 'testkey'.")
    
    await asyncio.sleep(2)
    
    print("Calling notify_expired('testkey')...")
    await server_instance.notify_expired("testkey")
    
    start = time.time()
    while time.time() - start < 5:
        message = pubsub.get_message(timeout=1)
        if message:
            print("Received expired notification:", message)
        await asyncio.sleep(1)
    pubsub.close()
    print("notify_expired test complete.")

if __name__ == '__main__':
    # Open 3 separate connections
    r1 = redis.Redis(host='localhost', port=11311, decode_responses=True)
    r2 = redis.Redis(host='localhost', port=11311, decode_responses=True)
    r3 = redis.Redis(host='localhost', port=11311, decode_responses=True)
    
    test_ping(r1, 1)
    test_info(r1, 1)
    
    test_ping(r2, 2)
    test_info(r2, 2)
    
    test_ping(r3, 3)
    test_info(r3, 3)
    
    time.sleep(2)
    
    test_client_list(r1)
    
    test_psubscribe(r1)
    
    asyncio.run(test_notify_set())
    asyncio.run(test_notify_expire())
    asyncio.run(test_notify_expired())
    
    print("Waiting 10 seconds before closing all connections...")
    time.sleep(10)
