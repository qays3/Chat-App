import requests
from tkinter import *
from tkinter import Toplevel, Canvas, Frame, Scrollbar

class GUIHelper:
    def __init__(self):
        pass

    def window_build(self, close_callback):
        window = Tk()
        window.title('Space Spellcasters')
        window.geometry('870x700+0+0')
        window.configure(background='#2b2d42', pady=30)
        window.protocol('WM_DELETE_WINDOW', close_callback)
        window.grid_rowconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=0)
        window.grid_rowconfigure(2, weight=0)
        window.grid_columnconfigure(0, weight=3)
        window.grid_columnconfigure(1, weight=1)

      
        icon_image = PhotoImage(file="./logo/Chat-App.png")
        window.iconphoto(False, icon_image)

        return window

    def message_area_build(self, window, title, height=22):
        lb_messages = LabelFrame(window, text=title, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        text_area = Text(lb_messages, height=height, width=59, background='#edf2f4', font=('Arial', 14))
        text_area.configure(state='disabled')
        text_area.pack(fill=BOTH, expand=True)
        lb_messages.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        return text_area

    def connecteds_area_build(self, window, title, height=21):
        lb_connecteds = LabelFrame(window, text=title, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        f_connecteds = Listbox(lb_connecteds, height=height, width=15, background='#edf2f4', font=('Arial', 14))
        f_connecteds.pack(fill=BOTH, expand=True)
        lb_connecteds.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        return f_connecteds

    def entry_area_build(self, window, title):
        lb_text = LabelFrame(window, text=title, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        f_text = Entry(lb_text, background='#edf2f4', font=('Arial', 14))
        f_text.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        lb_text.grid(row=1, column=0, sticky='we', padx=10, pady=10)
        return f_text

    def connected_area_build(self, window, title):
        lb_you = LabelFrame(window, text=title, background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        f_you_label = Label(lb_you, text='', fg='white', background='#8d99ae', font=('Arial', 13, 'bold'), padx=10)
        f_you_label.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        lb_you.grid(row=1, column=1, sticky='we', padx=10, pady=10)
        return f_you_label

    def actions_area_build(self, window, send_action, file_action, logout_action, login_action, emoji_action):
        lb_actions = LabelFrame(window, text='', background='#8d99ae', font=('Arial', 12, 'bold'), fg='white')
        f_connect = Button(lb_actions, text='\U0001F4F1 Connect', width=10, command=login_action, font=('Arial', 12), cursor='hand2')
        f_connect.pack(side=RIGHT, fill=BOTH, expand=True)
        f_send = Button(lb_actions, text='\U0001F4E4 Send', width=10, command=send_action, font=('Arial', 12), cursor='hand2', state=DISABLED)
        f_send.pack(side=LEFT, fill=BOTH, expand=True)
        f_file = Button(lb_actions, text='\U0001F4C1 File', width=10, command=file_action, font=('Arial', 12), cursor='hand2', state=DISABLED)
        f_file.pack(side=LEFT, fill=BOTH, expand=True)
        f_emoji = Button(lb_actions, text='\U0001F600 Emoji', width=10, command=emoji_action, font=('Arial', 12), cursor='hand2', state=DISABLED)
        f_emoji.pack(side=LEFT, fill=BOTH, expand=True)
        f_logout = Button(lb_actions, text='\U0001F6AA Go Out', width=10, command=logout_action, font=('Arial', 12), cursor='hand2', state=DISABLED)
        f_logout.pack(side=RIGHT, fill=BOTH, expand=True)
        lb_actions.grid(row=2, column=0, columnspan=2, sticky='we', padx=10, pady=10)
        return [f_send, f_file, f_logout, f_connect, f_emoji]

    def login_popup_build(self, window, title, open_callback, close_callback):
        popup = Toplevel(window)
        popup.configure(background='#2b2d42', pady=30)
        popup.title(title)
        popup.protocol('WM_DELETE_WINDOW', close_callback)
        open_callback(popup)
        return popup

    def login_popup_elements_build(self, popup, title, do_login_action):
        f_label_login = Label(popup, text=title, fg='white', background='#2b2d42', font=('Arial', 12))
        f_label_login.grid(row=0, column=0, sticky='w')
        f_login = Entry(popup, width=30, background='#edf2f4', font=('Arial', 14))
        f_login.grid(row=1, column=0, sticky='we', padx=10, pady=10)
        f_do_login = Button(popup, text='enter', width=10, command=do_login_action, background='#9732a8', font=('Arial', 12), fg='white', cursor='hand2')
        f_do_login.grid(row=1, column=1, sticky='we', padx=10, pady=10)
        f_label_fail = Label(popup, text='', fg='#ef233c', background='#2b2d42', font=('Arial', 12))
        f_label_fail.grid(row=2, column=0, columnspan=2, sticky='we')
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=1)
        popup.grid_rowconfigure(2, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_columnconfigure(1, weight=1)
        return [f_login, f_do_login, f_label_fail]

    def enable_actions(self, context):
        context.f_send['state'] = NORMAL
        context.f_send['background'] = '#5BBA6F'
        context.f_file['state'] = NORMAL
        context.f_file['background'] = '#395697'
        context.f_emoji['state'] = NORMAL
        context.f_emoji['background'] = '#FFD700'
        context.f_connect['state'] = DISABLED
        context.f_connect['background'] = '#8d99ae'
        context.f_logout['state'] = NORMAL
        context.f_logout['background'] = '#ef233c'

    def disabled_actions(self, context):
        context.f_send['state'] = DISABLED
        context.f_send['background'] = '#8d99ae'
        context.f_file['state'] = DISABLED
        context.f_file['background'] = '#8d99ae'
        context.f_emoji['state'] = DISABLED
        context.f_emoji['background'] = '#8d99ae'
        context.f_connect['state'] = NORMAL
        context.f_connect['background'] = '#9732a8'
        context.f_logout['state'] = DISABLED
        context.f_logout['background'] = '#8d99ae'

    def update_message_area(self, text_area, message):
        text_area.configure(state='normal')
        text_area.insert('end', f"{message}\n")
        text_area.configure(state='disabled')
        text_area.see('end')

    def open_emoji_popup(self, entry):
        popup = Toplevel()
        popup.title("Select an Emoji")
        popup.geometry("600x400")

        canvas = Canvas(popup)
        scrollbar = Scrollbar(popup, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        try:
            response = requests.get("https://emoji-api.com/emojis?access_key=b59e93777698c5f1b0db689ee9502c2b134e08c0")
            response.raise_for_status()
            emojis = response.json()
        except requests.RequestException as e:
            print(f"Error fetching emojis: {e}")
            emojis = []

        row = 0
        col = 0
        for emoji in emojis:
            button = Button(scrollable_frame, text=emoji["character"], font=('Arial', 20), bg=self.get_random_color(),
                            command=lambda e=emoji["character"]: self.insert_emoji(entry, e))
            button.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col >= 10:   
                col = 0
                row += 1

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

    def insert_emoji(self, entry, emoji):
        entry.insert(END, emoji)

    def get_random_color(self):
        import random
        colors = ["#FFB6C1", "#FF69B4", "#FF6347", "#FFD700", "#ADFF2F", "#7FFF00", "#00FFFF", "#1E90FF", "#DA70D6"]
        return random.choice(colors)