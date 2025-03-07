import redis
import time

def test_ping(r):
    print("Testing PING command...")
    result = r.ping()
    print("PING response:", result)  # Expected: True (i.e., "+PONG\r\n")

def test_info(r):
    print("\nTesting INFO command...")
    # INFO command returns a multi-line string; we print it directly.
    result = r.execute_command("INFO")
    print("INFO response:")
    print(result)

def test_client_list(r):
    print("\nTesting CLIENT LIST command...")
    result = r.execute_command("CLIENT", "LIST")
    print("CLIENT LIST response:")
    print(result)

def test_psubscribe(r):
    print("\nTesting PSUBSCRIBE command for key notifications...")
    pubsub = r.pubsub()
    # Subscribe to both __keyspace@0__:* and __keyevent@0__:* patterns
    pubsub.psubscribe("__keyspace@0__:*", "__keyevent@0__:*")
    print("Subscribed to key notification patterns. Waiting for messages for 10 seconds...")
    
    start = time.time()
    while time.time() - start < 10:
        message = pubsub.get_message(timeout=1)
        if message:
            print("Received message:", message)
        else:
            print("No message received...")
        time.sleep(1)
    pubsub.close()
    print("PSUBSCRIBE test complete.")

if __name__ == '__main__':
    # Connect to the server running on port 11311
    r = redis.Redis(host='localhost', port=11311, decode_responses=True)
    
    test_ping(r)
    test_info(r)
    test_client_list(r)
    test_psubscribe(r)
