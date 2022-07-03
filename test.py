from socket import *
import threading

sck = socket(AF_INET, SOCK_STREAM)
sck.bind(("127.0.0.1", 9000))
sck.listen(5)

def handle_client(c):
    print("Received connection from ", a)
    c.close();

    return

while True:
    c, a = sck.accept()
    t = threading.Thread(target=handle_client, args=(c, ))
    t.start()