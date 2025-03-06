#!/usr/bin/env python3
# filenae: run_daemon.py
import sys
import os
import subprocess
import signal
import socket

def start():
    """
    Start memcached_lite.py as a detached process.
    """
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memcached_lite.py")
    
    if os.name == 'nt':
        DETACHED_PROCESS = 0x00000008
        proc = subprocess.Popen(
            [python_executable, script_path],
            creationflags=DETACHED_PROCESS,
            close_fds=True
        )
    else:
        proc = subprocess.Popen(
            [python_executable, script_path],
            preexec_fn=os.setsid,
            close_fds=True
        )
    print(f"memcached_lite started with PID {proc.pid}")

def get_pid_from_stats(host='127.0.0.1', port=11211):
    """
    Connect to the memcached_lite server and retrieve the PID from its stats output.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.sendall(b"stats\r\n")
        data = b""
        # Read data until we see the "END" line.
        while b"END" not in data:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        lines = data.decode().splitlines()
        pid = None
        for line in lines:
            # Expect a line like: "STAT pid <pid>"
            if line.startswith("STAT pid"):
                parts = line.split()
                if len(parts) >= 3 and parts[2].isdigit():
                    pid = int(parts[2])
                    break
        return pid
    finally:
        s.close()

def stop():
    """
    Stop the memcached_lite server by retrieving its PID from stats and terminating the process.
    """
    pid = get_pid_from_stats()
    if pid is None:
        print("Could not retrieve PID from stats. Is memcached_lite running?")
        return

    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/PID", str(pid), "/F"])
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"memcached_lite stopped. (PID: {pid})")
    except ProcessLookupError:
        print("Process not found. Maybe it's already stopped.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == "stop":
        stop()
    else:
        start()
