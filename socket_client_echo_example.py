# Echo Client Program Example
import socket

HOST = '192.168.1.111'  # IP Address of Backend/HOST server.
PORT = 7766 # Ephemeral Port Number
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    txt_to_send = ""
    while True:
        txt_to_send = input("Enter Text to Send: ")
        s.sendall(bytes(txt_to_send, 'utf-8'))
        if txt_to_send == "quit":
            break
        data = s.recv(1024)
        print("Data Echoed Back: ", data)
print(f"Connection to ({HOST}, {PORT}) was lost.")
