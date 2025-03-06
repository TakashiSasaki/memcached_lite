#!/usr/bin/env python3
"""
stop.py

A simple script to stop the running memcached_lite server by dynamically
importing the memcached_lite module from GitHub using httpimport.
The stop command retrieves the server's PID via its stats and terminates the process.
"""

import httpimport

# GitHub raw URL for the memcached_lite package
github_raw_url = "https://raw.githubusercontent.com/TakashiSasaki/memcached_lite/refs/heads/master"

with httpimport.remote_repo(github_raw_url, ["memcached_lite"]):
    import memcached_lite

def main():
    """
    Stops the memcached_lite server.
    
    This function calls the `stop()` function from the memcached_lite module,
    which retrieves the process ID from the server's stats and terminates the process.
    """
    memcached_lite.stop()

if __name__ == "__main__":
    main()
