import threading, socket, pickle, time, uuid, os, logging
from os import path
from datetime import datetime
from gui_helper import *
from model import *
from utils import *
import mimetypes
import base64
import random
import string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

class Server:
    def __init__(self):
        self.gui_helper = GUIHelper()
        self.window = self.gui_helper.window_build(self._close_callback)
        self.clients = []
        self.logins = []
        self.the_file = []
        self.encryption_key = os.urandom(32)
        self._build()

    def encrypt_data(self, data):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CTR(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted_data

    def decrypt_data(self, data):
        iv = data[:16]
        encrypted_data = data[16:]
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CTR(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return decrypted_data

    def _build(self):
        self._build_message_area()
        self._build_connecteds_area()

    def _build_message_area(self):
        self.f_messages = self.gui_helper.message_area_build(self.window, 'Server logs', height=28)

    def _build_connecteds_area(self):
        self.f_connecteds = self.gui_helper.connecteds_area_build(self.window, 'Connected', height=27)

    def _show_message_on_screen(self, message):
        self.gui_helper.update_message_area(self.f_messages, message)

    def _update_users_on_screen(self):
        self.f_connecteds.delete(0, END)
        for i, user in enumerate(self.logins):
            self.f_connecteds.insert(i, user)

    def broadcast(self, current_client, message):
        if isinstance(message, str):
            log_message = Message()
            log_message.command = 'LOG'
            log_message.message = message
            message = log_message
        recipient = self.get_recipient(message)
        if recipient:
            if current_client != recipient:
                send_serialized(recipient, message)
            if message.command != 'REQUEST_PATH':
                send_serialized(current_client, message)
        else:
            for client in self.clients:
                if message.command == 'REQUEST_PATH':
                    if client != current_client:
                        send_serialized(client, message)
                else:
                    send_serialized(client, message)

    def broadcast_users_update(self, client):
        time.sleep(0.1)
        message = Message()
        message.command = 'UPDATE_USERS'
        message.message = '@@@'.join(self.logins)
        self.broadcast(client, message)
        message.command = None

    def get_recipient(self, message):
        if message.recipient and message.recipient != 'None':
            index = self.logins.index(message.recipient)
            recipient = self.clients[index]
            if recipient:
                return recipient
        return None

    def logout(self, client):
        try:
            index = self.clients.index(client)
            login = self.logins[index]
            self.server_log(client, 'Logout')
            self.clients.remove(client)
            self.logins.remove(login)
            self.broadcast_users_update(client)
            self._update_users_on_screen()
        finally:
            client.close()

    def make_client_login(self, client, data, message):
        if data.user in self.logins:
            self.feedback_login_status(client, 'LOGIN_INVALID')
        else:
            self.logins.append(data.user)
            self.clients.append(client)
            self.feedback_login_status(client, 'LOGIN_VALID')
            self.broadcast_users_update(client)
            self._update_users_on_screen()
            self.server_log(client, 'Login')

    def feedback_login_status(self, client, command):
        message = Message()
        message.command = command
        send_serialized(client, message)
        message.command = None

    def get_login_by_client(self, client):
        index = self.clients.index(client)
        return self.logins[index]

    def xor_encrypt(self, data, key):
        encrypted_data = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
        encoded_data = base64.b64encode(encrypted_data.encode()).decode()
        return encoded_data

    def xor_decrypt(self, data, key):
        decoded_data = base64.b64decode(data.encode()).decode()
        decrypted_data = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(decoded_data))
        return decrypted_data

    def generate_key(self, length=16):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    def server_receive_save_file(self, client, message, threadId):
        received_file_name = message.message
        saved_file_name = f'{threadId}_{received_file_name}'

        if not path.isdir('server_files'):
            os.mkdir('server_files')

        with open(f'server_files{os.path.sep}{saved_file_name}', 'wb') as arq:
            while True:
                chunk = client.recv(1024)
                if chunk:
                    arq.write(chunk)   
                else:
                    break

        file_message = Message()
        file_message.command = 'FILE'
        file_message.message = saved_file_name
        file_message.user = self.get_login_by_client(client)
 
        with open(f'server_files{os.path.sep}{saved_file_name}', 'rb') as file:
            while True:
                chunk = file.read(1024)
                if chunk:
                    encrypted_data = self.encrypt_data(chunk)
                    for c in self.clients:
                        c.send(encrypted_data)   
                    time.sleep(0.1)
                else:
                    break

     
        self.broadcast(client, file_message)

        self.server_log(client, f'File: {received_file_name}')




    def server_send_file_to_client(self, client):
        client.send(self.the_file[1].encode())
        time.sleep(0.1)
        with open(f'server_files{os.path.sep}{self.the_file[0]}', 'rb') as arq:
            while chunk := arq.read(1024):
                encrypted_data = self.encrypt_data(chunk)
                client.send(encrypted_data)
                time.sleep(0.1)
            client.send(b'done')
            time.sleep(0.1)

    def server_log(self, client, complement, recipient=None):
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        client_ip = client.getsockname()[0]
        client_login = self.get_login_by_client(client)
        if recipient is None:
            text_to_log = f'{now}; {client_ip}; {client_login}; {complement}'
        else:
            recipient_ip = recipient.getsockname()[0]
            recipient_login = self.get_login_by_client(recipient)
            text_to_log = f'{now}; {client_ip}; {client_login}; {recipient_ip}; {recipient_login}; {complement}'
        logging.basicConfig(filename='file.log', filemode='w', format='%(message)s')
        logging.warning(text_to_log)
        self._show_message_on_screen(text_to_log)
        self.broadcast(None, text_to_log)
        print(text_to_log)

    def handle(self, client, threadId):
        while True:
            message = Message()
            try:
                b_data = client.recv(1024)
                if b_data:
                    try:
                        data = get_serialized_message(client, b_data)
                        if data.command == 'LOGIN':
                            self.make_client_login(client, data, message)
                        elif data.command == 'LOGOUT':
                            message = Message()
                            message.command = 'LOGOUT_DONE'
                            send_serialized(client, message)
                            message.command = None
                            time.sleep(0.1)
                            self.logout(client)
                            break
                        elif data.command == 'SEND_PATH':
                            self.server_send_file_to_client(client)
                        else:
                            self.server_log(client, f'Message: {data.message}', self.get_recipient(data))
                            self.broadcast(client, data)
                    except:
                        try:
                            self.server_receive_save_file(client, b_data, threadId)
                        except Exception as e:
                            pass
                else:
                    self.logout(client)
                    break
            except Exception as e:
                self.logout(client)
                break

    def receive(self):
        while True:
            message = Message()
            client, address = self.server.accept()
            data = get_serialized_message(client)
            self.make_client_login(client, data, message)
            threadId = str(uuid.uuid4())
            threading.Thread(target=self.handle, args=(client, threadId)).start()

    def _close_callback(self):
        os._exit(0)
        self.window.destroy()

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 10000))
        self.server.listen()
        threading.Thread(target=self.receive).start()
        self.window.mainloop()

def get_serialized_message(client, b_data=None):
    if b_data is None:
        b_data = client.recv(1024)
    data = pickle.loads(b_data)
    return data

def send_serialized(client, message):
    data = pickle.dumps(message)
    client.send(data)

Server().run()
