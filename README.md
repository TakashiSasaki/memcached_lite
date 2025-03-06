# memcached_lite

**memcached_lite** is a lightweight, pure-Python implementation of a Memcached-compatible server. It is built using asyncio for asynchronous operations and detailed logging, and it has been tested on Windows. This project is intended to provide a simple, in-memory key-value store with a subset of Memcached functionality.

## Features

- **Memcached-compatible commands:**
  - `set`, `get`, `delete`, `flush_all`, and `stats`
- **Enhanced statistics tracking:**
  - Returns detailed stats including:
    - `pid` (Process ID)
    - `time` (Current UNIX timestamp)
    - `uptime` (Server running time in seconds)
    - `curr_items` (Current number of items stored)
    - `total_items` (Total number of items stored since startup)
    - Command counters: `cmd_get`, `cmd_set`, `cmd_delete`
    - Cache hit/miss counters: `get_hits`, `get_misses`
    - `version` (Fixed version string)
    - `process_path` (Path to the Python executable)
- **Asynchronous operation** using Python’s asyncio.
- **Cross-platform compatibility:** Works on both Windows and Unix-like systems.
- **No PID file required:** The server uses its own stats output to retrieve the process ID when stopping, eliminating the need for a PID file.

## Installation

Since **memcached_lite** is implemented purely in Python, no build is required. You can simply clone or download the repository.

Optionally, if you wish to run the provided tests, install the following dependencies:

```bash
pip install python-memcached pymemcache
```

Alternatively, you can install these as optional dependencies:

```bash
pip install memcached_lite[test]
```

## Usage

### Running the Server

You can start the server as a daemon by using the command-line interface:

```bash
python -m memcached_lite start
```

This will start the server in the background.

### Stopping the Server

To stop the server, run:

```bash
python -m memcached_lite stop
```

The stop command retrieves the process ID via the server’s stats output and terminates the process.

### Checking the Server Status

To view the server’s statistics (including uptime, command counts, etc.), run:

```bash
python -m memcached_lite status
```

This command connects to the running server, sends the `stats` command, and displays the returned information.

### Using the Module in Your Code

You can also import the module and control the server programmatically:

```python
import memcached_lite

# Start the server (as a daemon)
memcached_lite.start()

# ... later, to check status:
memcached_lite.status()

# ... and to stop the server:
memcached_lite.stop()
```

## Project Structure

```
memcached_lite/
├── __init__.py         # Exposes start() and stop() functions for easy module import.
├── __main__.py         # CLI entry point for running commands: start, stop, status.
├── memcached_lite.py   # The main server implementation.
├── run_daemon.py       # Provides functions to launch the server as a detached process without using a PID file.
└── status.py           # Implements a utility to connect to the server and display stats.
```

## Repository and Author

- GitHub: [memcached_lite](https://github.com/TakashiSasaki/memcached_lite)
- Author: [Takashi Sasaki](https://x.com/TakashiSasaki)

## License

This project is licensed under the MIT License.
```

This version includes **all necessary updates**, such as:
- **GitHub repository link**: `[memcached_lite](https://github.com/TakashiSasaki/memcached_lite)`
- **Author's website (X.com profile)**: `[Takashi Sasaki](https://x.com/TakashiSasaki)`

Let me know if you need any final tweaks before committing! 🚀