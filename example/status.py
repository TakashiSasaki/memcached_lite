#!/usr/bin/env python3
"""
status.py

A simple script to check the status of the running memcached_lite server by
connecting to it and displaying its statistics. The module is dynamically
imported from GitHub using httpimport.
"""

import httpimport

# GitHub raw URL for the memcached_lite package
github_raw_url = "https://raw.githubusercontent.com/TakashiSasaki/memcached_lite/refs/heads/master"

with httpimport.remote_repo(github_raw_url, ["memcached_lite"]):
    import memcached_lite

def main():
    """
    Displays the status of the memcached_lite server.
    
    This function calls the `status()` function from the memcached_lite module,
    which connects to the running server, sends the `stats` command, and prints
    the returned statistics.
    """
    memcached_lite.status()

if __name__ == "__main__":
    main()
