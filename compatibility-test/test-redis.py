import redis
import time

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
    print("\nTesting PSUBSCRIBE command for key notifications...")
    pubsub = r.pubsub()
    # Subscribe to both keyspace and keyevent notification patterns.
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

def test_keepalive(r, conn_id):
    print(f"\nTesting KEEPALIVE command on connection {conn_id}...")
    result = r.execute_command("KEEPALIVE")
    print(f"KEEPALIVE response from connection {conn_id}:")
    print(result)

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
    
    # Test PSUBSCRIBE on one connection
    test_psubscribe(r1)
    
    # Test KEEPALIVE on connection 3 (which is not in subscription mode)
    test_keepalive(r3, 3)
