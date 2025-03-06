# __main__.py

import sys
from .run_daemon import start, stop
from .status import status

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "start":
            start()
        elif cmd == "stop":
            stop()
        elif cmd == "status":
            status()
        else:
            print(f"Unknown command: {sys.argv[1]}")
    else:
        # No argument given, default to status command
        status()

if __name__ == "__main__":
    main()
