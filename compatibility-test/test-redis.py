import redis
import time
import asyncio
import sys
sys.path.append("..")
from memcached_lite.redis_lite import RedisLiteServer  # Assumes RedisLiteServer can be imported

# Create a server instance (assumes the server is running in the same environment)
server_instance = RedisLiteServer()

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
    # Create a subscription client specifically for set events.
    r_sub = redis.Redis(host='localhost', port=11311, decode_responses=True)
    pubsub = r_sub.pubsub()
    # Subscribe to keyevent 'set' and keyspace for "testkey"
    pubsub.psubscribe("__keyevent@0__:set", f"__keyspace@0__:testkey")
    print("Subscribed for set notifications for key 'testkey'.")
    
    # Wait to ensure subscription is active.
    await asyncio.sleep(2)
    
    # Define some binary value for the test.
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

if __name__ == '__main__':
    # Open 3 separate connections
    r1 = redis.Redis(host='localhost', port=11311, decode_responses=True)
    r2 = redis.Redis(host='localhost', port=11311, decode_responses=True)
    r3 = redis.Redis(host='localhost', port=11311, decode_responses=True)
    
    # Test PING and INFO on each connection
    test_ping(r1, 1)
    test_info(r1, 1)
    
    test_ping(r2, 2)
    test_info(r2, 2)
    
    test_ping(r3, 3)
    test_info(r3, 3)
    
    # Wait a moment to ensure all connections are established
    time.sleep(2)
    
    # Test CLIENT LIST using one connection
    test_client_list(r1)
    
    # Test PSUBSCRIBE on one connection (subscribe to multiple patterns)
    test_psubscribe(r1)
    
    # Test notify_set using asyncio
    asyncio.run(test_notify_set())
    
    # Final delay to keep connections alive before closing
    print("Waiting 10 seconds before closing all connections...")
    time.sleep(10)
