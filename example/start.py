#!/usr/bin/env python3
"""
start.py

A simple script to start the memcached_lite server as a daemon by dynamically
importing the memcached_lite module from GitHub using httpimport.
"""

import httpimport

# GitHub raw URL for the memcached_lite package
github_raw_url = "https://raw.githubusercontent.com/TakashiSasaki/memcached_lite/refs/heads/master"

with httpimport.remote_repo(github_raw_url, ["memcached_lite"]):
    import memcached_lite

def main():
    """
    Starts the memcached_lite server.
    
    This function calls the `start()` function from the memcached_lite module,
    which launches the server in the background.
    """
    memcached_lite.start()

if __name__ == "__main__":
    main()
