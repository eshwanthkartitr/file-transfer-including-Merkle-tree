import socket
import re
from pathlib import Path
import hashlib
import os
import time

default_down = str(Path.home()/"Downloads")

key = b'\x13\xe6\xa2F\x8a\xe9\xd6(\x88\xc0\x99t\x89\x18\xe9\xb6'


class MerkleTree:

    def myhash(self, data):
        return hashlib.sha256(data.encode()).hexdigest()

    def my_merkle_tree(self, data_blocks):
        if len(data_blocks) % 2 != 0:
            data_blocks.append(data_blocks[-1])

        # Hash each data block
        hashed_blocks = [self.myhash(data) for data in data_blocks]

        # Construct the Merkle Tree
        while len(hashed_blocks) > 1:
            new_hashes = [self.myhash(
                a + b) for a, b in zip(hashed_blocks[::2], hashed_blocks[1::2])]

            # If there's an odd number of blocks, append the last block
            if len(hashed_blocks) % 2 != 0:
                new_hashes.append(hashed_blocks[-1])

            hashed_blocks = new_hashes

        return hashed_blocks[0]


def merkle_solver(file_path):
    with open(file_path, 'r') as file:
        my_file = file.read().splitlines()

    obj = MerkleTree()
    out = obj.my_merkle_tree(my_file)
    print(out)

    new_line = f"{file_path} = {out}"

    existing_lines = set()
    try:
        with open("./client_storage/merk_val", 'r') as f:
            existing_lines = set(f.read().splitlines())
    except FileNotFoundError:
        pass

    path_exists = any(line.startswith(file_path) for line in existing_lines)

    if path_exists:
        updated_lines = [new_line if line.startswith(
            file_path) else line for line in existing_lines]
        updated_content = '\n'.join(updated_lines)
    else:
        updated_content = '\n'.join(existing_lines.union([new_line]))

    with open("./client_storage/merk_val.txt", 'w') as f:
        f.write(updated_content)
        f.close()


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
    return bytes(decrypted_data).decode()


def send_file(sock, filename):
    try:

        org_file = filename
        filename = "./client_storage/" + filename
        with open(filename, "rb") as fi:
            print(f"\nSTART {org_file} START1\n")
            print("sock = ", sock)

            while True:
                data = fi.read(1024)
                if not data:
                    break
                data = encrypt(data)
                print(data, "mom")
                sock.sendall(data)

            data = f"\nend_bro_now {filename}\n"
            sock.sendall(data.encode())
    except IOError:
        print(f'Error: Could not read file {filename}.')


def request_file(sock, fileName):
    time.sleep(1)
    data = sock.recv(1024).decode()
    print("Data - = ", data)
    org_file_name = re.search(r"START (\w+\.\w+) START1", data)
    filename_req = f"{default_down}/from_server_{org_file_name.group(1)}"
    print(filename_req)
    with open(filename_req, "w") as fo:
        while data:
            lines = data.split("\n")
            for line in lines:
                if line.strip():
                    if ("Sending data START" in line and "START1" in line):
                        line = re.sub(
                            r"Sending data START \w+\.txt START1", "", line)
                    if ("end_bro_now" in line):
                        match = re.search(r"(.*?)end_bro_now", line, re.DOTALL)
                        line = match.group(1)
                    fo.write(line)

            if "end_bro_now" in data:
                break
            data = sock.recv(1024).decode()
        fo.close()
    return filename_req


def check_and_delete(down_path, filename):
    # Read the file content
    with open(down_path, "r") as file:
        file_content = file.read().splitlines()
        print("file con t = ", file_content)

    obj = MerkleTree()
    new_hash = obj.my_merkle_tree(file_content)

    try:
        with open("./client_storage/merk_val.txt", "r") as merk_val_file:
            stored_lines = merk_val_file.read().splitlines()
    except FileNotFoundError:
        stored_lines = []

    stored_hash = None
    for line in stored_lines:
        if line.startswith(f"./client_storage/{filename} ="):
            stored_hash = line.split("=")[-1].strip()

    print("new hash = ", new_hash)
    print("stored hash = ", stored_hash)
    if stored_hash and stored_hash == new_hash:
        print("Hash values match. File is valid.")
    else:
        print("Hash values do not match. Deleting the file.")
        try:
            os.remove(down_path)
            print(f"File {down_path} deleted successfully.")
        except FileNotFoundError:
            print(f"File {down_path} not found.")


def main_pgm(fileName, num):
    host = '127.0.0.1'
    port = 8080

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    filename = fileName

    if num == 1:
        sock.sendall(f"Sending data \nSTART {filename} START1\n".encode())
        send_file(sock, filename)
        merkle_solver("./client_storage/"+filename)
    else:
        sock.sendall(f"Requesting file START {filename} START1".encode())
        print("Hello hi world")
        print("Works")
        filename_down = request_file(sock, filename)
        sock.close()
        filename = re.search(r'_([^_]+\.txt)', filename_down)
        print("hi", filename.group(1), filename_down)
        check_and_delete(filename_down, filename.group(1))


if __name__ == '__main__':
    print("Hello world")
    main_pgm("output_client_1_new.txt", 2)
