# __main__.py

import sys
from .run_daemon import start, stop

def main():
    # 引数があり、かつ "stop" と一致する場合は stop() を呼ぶ
    if len(sys.argv) > 1 and sys.argv[1].lower() == "stop":
        stop()
    else:
        # それ以外の場合は start() を呼ぶ
        start()

if __name__ == "__main__":
    main()
