#!/usr/bin/env python3
import sys
import os
import subprocess
import signal

# memcached_liteサーバのPIDを記録するファイル
PID_FILE = os.path.join(os.path.dirname(__file__), 'memcached_lite.pid')

def start():
    """
    memcached_lite.py をバックグラウンドで起動し、PIDをファイルに書き込む
    """
    # すでにPIDファイルがある場合は、すでに起動している可能性がある
    if os.path.exists(PID_FILE):
        print("memcached_lite is already running or PID file exists.")
        return

    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memcached_lite.py")

    if os.name == 'nt':
        # Windows: DETACHED_PROCESS フラグでコンソールから切り離す
        DETACHED_PROCESS = 0x00000008
        proc = subprocess.Popen(
            [python_executable, script_path],
            creationflags=DETACHED_PROCESS,
            close_fds=True
        )
    else:
        # Unix/Linux: setsidで新しいセッションとして起動
        proc = subprocess.Popen(
            [python_executable, script_path],
            preexec_fn=os.setsid,
            close_fds=True
        )

    # 起動したプロセスのPIDをファイルに書き込み
    with open(PID_FILE, 'w') as f:
        f.write(str(proc.pid))

    print(f"memcached_lite started with PID {proc.pid}")

def stop():
    """
    PIDファイルからPIDを読み取り、プロセスを終了させる
    """
    if not os.path.exists(PID_FILE):
        print("memcached_lite is not running or PID file not found.")
        return

    with open(PID_FILE, 'r') as f:
        pid_str = f.read().strip()
    if not pid_str.isdigit():
        print("PID file is invalid.")
        return

    pid = int(pid_str)

    # プロセスを終了
    try:
        if os.name == 'nt':
            # Windowsの場合はtaskkillコマンドなどを使う
            subprocess.run(["taskkill", "/PID", str(pid), "/F"])
        else:
            # Unix系の場合はSIGTERMを送る
            os.kill(pid, signal.SIGTERM)
        print(f"memcached_lite stopped. (PID: {pid})")
    except ProcessLookupError:
        print("Process not found. Maybe it's already stopped.")

    # PIDファイルを削除
    os.remove(PID_FILE)
