import socket
import threading
import time
import os
import tkinter as tk
from tkinter import filedialog, Button, END, DISABLED, NORMAL
from gui_helper import *
from model import *
from utils import *
from PIL import Image, ImageTk
import webbrowser
import pickle
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

class Client:
    def __init__(self):
        self.gui_helper = GUIHelper()
        self.window = self.gui_helper.window_build(self._close_callback)
        self._build()
        self.message = Message()
        self.file_path = ''
        self.client = None
        self.users = []
        self.encryption_key = os.urandom(32)

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
        self._build_entry_area()
        self._build_you_area()
        self._build_actions_area()

    def _build_message_area(self):
        self.f_messages = self.gui_helper.message_area_build(self.window, 'Received messages:')

    def _build_connecteds_area(self):
        self.f_connecteds = self.gui_helper.connecteds_area_build(self.window, 'Send to:')

    def _build_entry_area(self):
        self.f_text = self.gui_helper.entry_area_build(self.window, 'Enter a message:')

    def _build_you_area(self):
        self.f_you_label = self.gui_helper.connected_area_build(self.window, 'Logged in as:')

    def _build_actions_area(self):
        actions = self.gui_helper.actions_area_build(self.window, self._send_message, self._send_file, self._desconnect, self._popup, self._open_emoji_popup)
        self.f_send, self.f_file, self.f_logout, self.f_connect, self.f_emoji = actions

    def _popup(self):
        self.popup = self.gui_helper.login_popup_build(self.window, 'Login', self._open_popup_callback, self._close_popup_callback)
        self.popup.mainloop()

    def _open_popup_callback(self, popup):
        self.f_login, self.f_do_login, self.f_label_fail = self.gui_helper.login_popup_elements_build(popup, 'Enter Your Name', self._do_login)
        self.f_connect['state'] = DISABLED
        self.f_connect['background'] = '#8d99ae'

    def _enable_actions(self):
        self.gui_helper.enable_actions(self)

    def _disable_actions(self):
        self.gui_helper.disabled_actions(self)

    def _do_login(self):
        if not self.f_login.get():
            self._show_validation_error('Required field.')
        else:
            self.message.user = self.f_login.get()
            self.message.command = 'LOGIN'
            if not self._connect_client():
                self._show_validation_error('Unavailable server.')
            else:
                self.f_you_label['text'] = self.message.user

    def _connect_client(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.client.connect_ex(('127.0.0.1', 10000)) == 0:
                send_serialized(self.client, self.message)
                threading.Thread(target=self._receive, daemon=True).start()
            else:
                return False
            return True
        except Exception as e:
            self._show_validation_error(f'Error connecting to server: {str(e)}')
            return False

    def _show_validation_error(self, message):
        self.f_label_fail['text'] = message
        self.f_label_fail.grid(row=2, column=0)

    def _show_message_on_screen(self, message):
        self.gui_helper.update_message_area(self.f_messages, message)

    def _update_users_on_screen(self, message):
        users = message.split('@@@')
        self.users = []
        self.f_connecteds.delete(0, END)
        self.f_connecteds.insert(0, 'Messages')
        for i, user in enumerate(users):
            if user != self.message.user:
                self.f_connecteds.insert(i + 1, user)
                self.users.append(user)
        self.f_connecteds.select_set(0)

    def _set_the_recipient(self):
        selected = self.f_connecteds.curselection()
        if selected and selected[0] != 0:
            self.message.recipient = self.users[selected[0] - 1]
        else:
            self.message.recipient = None

    def _send_message(self):
        text = self.f_text.get()
        if text:
            self._set_the_recipient()
            self.message.message = text
            self.message.command = 'MESSAGE'
            send_serialized(self.client, self.message)
            self.message.command = None
            self.f_text.delete(0, END)
            self.f_text.insert(0, '')

    def _send_file(self):
        self._set_the_recipient()
        file_path = filedialog.askopenfilename(initialdir=os.path.sep, title='Choose a file')
        if file_path and file_path != '':
            file_name = os.path.basename(file_path)
            recipient = 'None'
            if self.message.recipient:
                recipient = self.message.recipient
            self.client.send(file_name.encode())
            time.sleep(0.1)
            self.client.send(recipient.encode())
            time.sleep(0.1)
            with open(file_path, 'rb') as selected_file:
                while data := selected_file.read(1024):
                    encrypted_data = self.encrypt_data(data)
                    self.client.send(encrypted_data)
                    time.sleep(0.1)
            self.client.send(b'done')
            time.sleep(0.1)
            self._display_received_file(self.message.user, file_name, file_path)

    def _send_file_path(self):
        self.file_path = filedialog.askdirectory()
        if self.file_path and self.file_path != '':
            time.sleep(0.1)
            self.message.command = 'SEND_PATH'
            send_serialized(self.client, self.message)
            self.message.command = None

    def client_receive_save_file(self, data, file_name):
        save_as = f'client_files{os.path.sep}{file_name}'
        with open(save_as, 'wb') as arq:
            while True:
                chunk = self.client.recv(1024)
                if chunk:
                    if chunk == b'done':
                        break
                    decrypted_data = self.decrypt_data(chunk)
                    arq.write(decrypted_data)
                else:
                    break

        self._display_received_file('Sender', file_name, save_as)


    def _is_image_file(self, filename):
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        _, ext = os.path.splitext(filename)
        return ext.lower() in image_extensions

    def _is_video_file(self, filename):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        _, ext = os.path.splitext(filename)
        return ext.lower() in video_extensions

    def _receive(self):
        while True:
            try:
                b_data = self.client.recv(1024)
                if b_data:
                    try:
                        data = get_serialized_message(self.client, b_data)
                        if data.command == 'LOGIN_INVALID':
                            self._disable_actions()
                            self._show_validation_error('Please choose another login.')
                        elif data.command == 'LOGIN_VALID':
                            self.message.command = None
                            self._enable_actions()
                            self.popup.destroy()
                        elif data.command == 'UPDATE_USERS':
                            self.message.command = None
                            self._update_users_on_screen(data.message)
                        elif data.command == 'MESSAGE':
                            self._show_message_on_screen(f'{data.user}: {data.message}')
                        elif data.command == 'FILE':
                            file_name = data.message
                            self._show_message_on_screen(f'{data.user} sent a file: {file_name}')
                            file_data = self.client.recv(1024)
                            self.client_receive_save_file(file_data, file_name)
                        elif data.command == 'REQUEST_PATH':
                            self._send_file_path()
                        elif data.command == 'LOGOUT_DONE':
                            self._reset_gui()
                            self.client.close()
                            break
                    except Exception as e:
                        print(f"Error processing data: {e}")
                else:
                    self.client.close()
                    break
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.client.close()
                break

    def _display_received_file(self, user, filename, filepath):
        self.f_messages.configure(state='normal')
        if self._is_image_file(filename):
            img = Image.open(filepath)
            img = img.resize((200, 200), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.f_messages.insert(END, f'{user} sent an image:\n')
            self.f_messages.image_create(END, image=img)
            self.f_messages.image = img
            self.f_messages.insert(END, "\n")
        elif self._is_video_file(filename):
            self.f_messages.insert(END, f'{user} sent a video: {filename}\n')
            video_button = Button(self.f_messages, text='Play Video', command=lambda: self._play_video(filepath), background='#9732a8', font=('Arial', 12), fg='white', cursor='hand2')
            self.f_messages.window_create(END, window=video_button)
            self.f_messages.insert(END, "\n")
        else:
            self.f_messages.insert(END, f'{user} sent a file: ')
            file_link = Button(self.f_messages, text=filename, command=lambda: self._download_file(filepath), background='#9732a8', font=('Arial', 12), fg='white', cursor='hand2')
            self.f_messages.window_create(END, window=file_link)
            self.f_messages.insert(END, "\n")
        self.f_messages.configure(state='disabled')

    def _play_video(self, filepath):
        webbrowser.open(filepath)

    def _download_file(self, filepath):
        os.startfile(filepath)

    def _close_callback(self):
        self.window.destroy()
        if self.client:
            self.client.close()
        try:
            self.popup.destroy()
        except Exception as e:
            pass

    def _desconnect(self):
        self.message.command = 'LOGOUT'
        send_serialized(self.client, self.message)
        self.message.command = None

    def _close_popup_callback(self):
        self.popup.destroy()
        self.f_connect['state'] = NORMAL
        self.f_connect['background'] = '#64a6bd'

    def _reset_gui(self):
        self._disable_actions()
        self.f_you_label['text'] = ''
        self.f_connecteds.delete(0, END)
        self.f_messages.configure(state='normal')
        self.f_messages.delete('1.0', END)
        self.f_messages.configure(state='disabled')

    def run(self):
        self.window.mainloop()

    def _open_emoji_popup(self):
        self.gui_helper.open_emoji_popup(self.f_text)

Client().run()
