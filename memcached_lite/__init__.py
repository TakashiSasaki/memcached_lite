# __init__.py

# run_daemon.py の start/stop をインポートし、
# memcached_lite モジュールから直接呼び出せるようにする。
from .run_daemon import start, stop
from .status import status
