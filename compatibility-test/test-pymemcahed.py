from pymemcache.client import base
import time

client = base.Client(('127.0.0.1', 11211))

# -----------------------------
# Basic SET and GET operations
# -----------------------------
print('Set "foo" to "bar" with expiry of 10 seconds')
result = client.set('foo', 'bar', expire=10)
print(f'Set result: {result}')

print('Get key "foo"')
value = client.get('foo')
print(f'Value of "foo": {value}')

# -----------------------------
# Test overwriting an existing key
# -----------------------------
print('Overwrite key "foo" with "new_value"')
result = client.set('foo', 'new_value', expire=10)
print(f'Set result: {result}')

print('Get key "foo" after overwrite')
value = client.get('foo')
print(f'Value of "foo": {value}')

# -----------------------------
# Retrieve a non-existent key
# -----------------------------
print('Get non-existent key "baz"')
missing_value = client.get('baz')
print(f'Value of "baz": {missing_value}')

# -----------------------------
# Set multiple keys and retrieve them
# -----------------------------
print('Set multiple keys: "key1", "key2", "key3"')
client.set('key1', 'value1')
client.set('key2', 'value2')
client.set('key3', 'value3')

print('Get multiple keys')
values = client.get_multi(['key1', 'key2', 'key3', 'key4'])  # "key4" does not exist
print(f'Values: {values}')

# -----------------------------
# Test key expiration
# -----------------------------
print('Set key "temp" with expiry of 3 seconds')
client.set('temp', 'expire_me', expire=3)
print('Get key "temp" immediately')
print(f'Value of "temp": {client.get("temp")}')
print('Waiting 4 seconds for expiration...')
time.sleep(4)
print('Get key "temp" after expiration')
print(f'Value of "temp": {client.get("temp")}')

# -----------------------------
# Test delete operation
# -----------------------------
print('Delete key "foo"')
delete_result = client.delete('foo')
print(f'Delete result: {delete_result}')

print('Get key "foo" after deletion')
value_after_delete = client.get('foo')
print(f'Value of "foo" after deletion: {value_after_delete}')

# -----------------------------
# Test flush_all command
# -----------------------------
print('Flush all keys')
client.flush_all()
print('Get key "key1" after flush_all')
print(f'Value of "key1": {client.get("key1")}')

# -----------------------------
# Test noreply mode for SET and DELETE
# -----------------------------
print('Set "silent" to "test_noreply" with noreply mode')
client.set('silent', 'test_noreply', noreply=True)

print('Get "silent" after noreply set')
print(f'Value of "silent": {client.get("silent")}')

print('Delete "silent" with noreply mode')
client.delete('silent', noreply=True)

print('Get "silent" after noreply delete')
print(f'Value of "silent": {client.get("silent")}')

# -----------------------------
# Get server stats
# -----------------------------
print('Get server stats')
stats = client.stats()
print(f'Server stats: {stats}')
