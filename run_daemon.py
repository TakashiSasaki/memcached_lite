#!/usr/bin/env python3
import sys
import os
import subprocess

def run_daemon():
    # Get the path to the current Python interpreter and the memcached_lite.py script.
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memcached_lite.py")
    
    if os.name == 'nt':
        # Windows: use DETACHED_PROCESS flag to run the child process detached from the console.
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen([python_executable, script_path],
                         creationflags=DETACHED_PROCESS,
                         close_fds=True)
    else:
        # Unix/Linux: use preexec_fn=os.setsid to start the process in a new session.
        subprocess.Popen([python_executable, script_path],
                         preexec_fn=os.setsid,
                         close_fds=True)

if __name__ == '__main__':
    run_daemon()
