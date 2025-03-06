# test-pymemcache.py
from pymemcache.client import base

client = base.Client(('127.0.0.1', 11211))

# キーをセット（expiryは10秒後）
print('Set "foo" to "bar" with expiry of 10 seconds')
result = client.set('foo', 'bar', expire=10)
print(f'Set result: {result}')

# キーを取得
print('Get key "foo"')
value = client.get('foo')
print(f'Value of "foo": {value}')

# 存在しないキーを取得
print('Get non-existent key "baz"')
missing_value = client.get('baz')
print(f'Value of "baz": {missing_value}')

# キーを削除
print('Delete key "foo"')
delete_result = client.delete('foo')
print(f'Delete result: {delete_result}')

# 削除後に再取得
print('Get key "foo" after deletion')
value_after_delete = client.get('foo')
print(f'Value of "foo" after deletion: {value_after_delete}')

# statsの取得
print('Get server stats')
stats = client.stats()
print(f'Server stats: {stats}')
