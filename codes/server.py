import base64
import socket
import threading
import re
import time

key = b'\x13\xe6\xa2F\x8a\xe9\xd6(\x88\xc0\x99t\x89\x18\xe9\xb6'


def encrypt(data, key=key):
    encrypted_data = bytearray()
    for i in range(len(data)):
        char = data[i]
        key_char = key[i % len(key)]
        encrypted_char = (char + key_char) % 256
        encrypted_data.append(encrypted_char)
    return bytes(encrypted_data)


def decrypt(data, key=key):
    decrypted_data = bytearray()
    for i in range(len(data)):
        char = data[i]
        key_char = key[i % len(key)]
        decrypted_char = (char - key_char) % 256
        decrypted_data.append(decrypted_char)
    try:
        return bytes(decrypted_data).decode()
    except:
        return bytes(decrypted_data)


def client_thread(conn, sock, client_id):
    fileno = 0
    fl = conn.recv(1024).decode()
    first_line = fl.split('\n')[0]
    print("fl = ", fl)
    h = 0
    if "Sending data" in first_line:
        print("Accepting data")
        org_file_name = re.search(r"START (\w+\.\w+) START1", fl)
        print(fl)
        org_file_name = org_file_name.group(1)
        data = fl
        print("data = ", data)
        filename = f'./servers_storage/output_client_{client_id}_{org_file_name}'
        with open(filename, "w") as fo:
            while data:
                print(f'Receiving data from client {client_id}')

                lines = data.decode().split("\n") if type(data) == bytes else data.split("\n")
                for line in lines:
                    if line:
                        fo.write(line)

                if h == 1:
                    print("works")
                    fo.write("\nend_bro_now"+m.decode())
                data = conn.recv(1024)
                print("data l = ", data)

                if b"end_bro_now" in data:
                    print("k = ", data)
                    data = data.split(b"\nend_bro_now")
                    m = data[1]
                    h = 1
                    data = decrypt(data[0])
                    print("data m = ", data)
                else:
                    data = decrypt(data)

            print(
                f'Received file from client {client_id} successfully! New filename is: {filename}')
            fileno += 1
            fo.close()
    if "Requesting file" in first_line:
        print("Sending file")
        data = fl
        print(data)
        if "START" in data:
            filename = re.search(r"START (\w+\.\w+) START1", data)
        print('bruv', filename.group(1))
        print("yes ")
        file_send(conn, filename.group(1))


def file_send(conn, filename):

    orig_filename = filename
    filename = "./servers_storage/"+orig_filename
    with open(filename, 'rb') as fi:
        while True:
            data = fi.read(1024)
            if not data:
                break
            data = data
            print(data, "lab")
            conn.sendall(data)
    conn.sendall(f"\nend_bro_now {orig_filename}\n".encode())
    print("ended")


def main_pgm(num):
    host = socket.gethostname()
    print(host)
    port = 8080
    totalclient = num

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(totalclient)
    print('Server is listening for clients...')

    client_threads = []

    while len(client_threads) < totalclient:
        # Accept a new connection
        conn, addr = sock.accept()

        print(f'Connected with client: {addr}')

        # Start a new thread for the new client
        thread = threading.Thread(
            target=client_thread, args=(conn, sock, len(client_threads) + 1))
        thread.start()
        client_threads.append(thread)

    # Wait for all threads to complete
    for thread in client_threads:
        thread.join()

    sock.close()


if _name_ == '_main_':
    print("Starting")
    main_pgm(1)
