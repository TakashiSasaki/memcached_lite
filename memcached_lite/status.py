import socket

def status():
    host = '127.0.0.1'
    port = 11211
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        s.sendall(b"stats\r\n")
        data = b""
        while b"END" not in data:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        print(data.decode())
    except Exception as e:
        print("Error retrieving status:", e)
    finally:
        s.close()
