import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk 
import threading
import brain
import mouth
import speech_recognition as sr
import time
import pygame
import os
import re # Thư viện xử lý văn bản

# --- CẤU HÌNH ---
AVATAR_DIR = "./avatar/" 
BG_COLOR = "#00ff00" # Màu xanh lá để lọc nền

class WaifuApp:
    def __init__(self, root):
        self.root = root
        
        # 1. Cấu hình cửa sổ
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG_COLOR)
        self.root.wm_attributes("-transparentcolor", BG_COLOR) 
        
        # Vị trí & Kích thước
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"350x550+{screen_width-400}+{screen_height-600}")

        # 2. Tải toàn bộ hình ảnh cảm xúc
        self.avatars = {}
        self.load_avatar_images()

        # 3. Giao diện Avatar
        self.current_state = "normal" # Trạng thái hiện tại
        self.label_avatar = tk.Label(root, image=self.avatars["normal"], bg=BG_COLOR, bd=0)
        self.label_avatar.pack(pady=0)

        # 4. Khung Chat
        self.chat_frame = tk.Frame(root, bg="#ffe4e1") 
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.chat_history = scrolledtext.ScrolledText(self.chat_frame, width=30, height=8, 
                                                      font=("Arial", 9), bg="#fff0f5", bd=0)
        self.chat_history.pack(padx=5, pady=5, fill="both", expand=True)
        self.chat_history.insert(tk.END, "Elysia: Hi Senpai~ ♪\n")
        self.chat_history.config(state=tk.DISABLED)

        # Ô Nhập liệu
        self.entry = tk.Entry(self.chat_frame, font=("Arial", 10), bg="white", bd=1)
        self.entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5, pady=5)
        self.entry.bind("<Return>", self.send_message)

        # Nút Mic
        self.btn_mic = tk.Button(self.chat_frame, text="🎤", command=self.manual_listen, bg="white", bd=0)
        self.btn_mic.pack(side=tk.RIGHT, padx=5)

        # Nút Thoát
        btn_close = tk.Button(root, text="X", command=self.close_app, bg="red", fg="white", font=("Arial", 8, "bold"))
        btn_close.place(x=320, y=5, width=20, height=20)

        # --- LOGIC ---
        self.is_talking = False
        self.idle_timer = time.time()
        
        # Kéo thả cửa sổ
        self.label_avatar.bind('<Button-1>', self.start_move)
        self.label_avatar.bind('<B1-Motion>', self.do_move)
        
        self.update_animation()

    def load_avatar_images(self):
        # Danh sách các trạng thái cần tải
        states = ["normal", "talking", "happy", "sad", "shock"]
        
        for state in states:
            path = os.path.join(AVATAR_DIR, f"{state}.png")
            try:
                # Resize ảnh về 250x250 cho vừa vặn
                img = Image.open(path).resize((250, 250))
                self.avatars[state] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"⚠️ Thiếu ảnh: {state}.png -> Dùng tạm ảnh normal")
                # Nếu thiếu ảnh nào thì dùng ảnh normal hoặc tạo ảnh trắng
                if "normal" in self.avatars:
                    self.avatars[state] = self.avatars["normal"]
                else:
                    self.avatars[state] = ImageTk.PhotoImage(Image.new('RGB', (250, 250), color='white'))

    # --- HÀM DI CHUYỂN ---
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.x
        y = self.root.winfo_y() + event.y - self.y
        self.root.geometry(f"+{x}+{y}")

    def close_app(self):
        self.root.destroy()
        os._exit(0)

    # --- ANIMATION & CẢM XÚC ---
    def set_emotion(self, text):
        # Quét văn bản xem có thẻ cảm xúc không
        if "[FACE:HAPPY]" in text: self.current_state = "happy"
        elif "[FACE:SAD]" in text: self.current_state = "sad"
        elif "[FACE:SHOCK]" in text: self.current_state = "shock"
        else: self.current_state = "normal"

    def update_animation(self):
        # Kiểm tra loa có đang nói không
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            self.is_talking = True
        else:
            self.is_talking = False

        current_time = time.time()
        
        if self.is_talking:
            # Khi nói: Nháy giữa ảnh Talking và ảnh Cảm Xúc hiện tại
            if int(current_time * 10) % 2 == 0: 
                self.label_avatar.config(image=self.avatars["talking"])
            else: 
                # Nháy về ảnh cảm xúc đang giữ (ví dụ đang vui thì nháy về happy)
                self.label_avatar.config(image=self.avatars[self.current_state])
            self.idle_timer = current_time 
        else:
            # Khi im lặng: Giữ nguyên ảnh cảm xúc
            # Sau 5 giây thì tự về mặt bình thường
            if current_time - self.idle_timer > 5:
                self.current_state = "normal"
            
            self.label_avatar.config(image=self.avatars[self.current_state])

        self.root.after(100, self.update_animation)

    # --- XỬ LÝ TIN NHẮN ---
    def log_chat(self, user, ai):
        self.chat_history.config(state=tk.NORMAL)
        if user: self.chat_history.insert(tk.END, f"Senpai: {user}\n")
        if ai: self.chat_history.insert(tk.END, f"Elysia: {ai}\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def process_input(self, text):
        if not text: return
        self.log_chat(text, None) 
        
        # Gửi lên não
        response = brain.ask_brain(text)
        
        # 1. Đặt cảm xúc cho Avatar
        self.set_emotion(response)

        # 2. Làm sạch văn bản để hiển thị và đọc
        clean_text = response.replace("[FACE:HAPPY]", "").replace("[FACE:SAD]", "").replace("[FACE:SHOCK]", "").replace("[FACE:NORMAL]", "")
        self.log_chat(None, clean_text)
        
        # 3. Nói
        threading.Thread(target=mouth.say, args=(clean_text,)).start()

    def send_message(self, event):
        text = self.entry.get()
        self.entry.delete(0, tk.END)
        self.process_input(text)

    def manual_listen(self):
        threading.Thread(target=self.listen_thread).start()

    def listen_thread(self):
        r = sr.Recognizer()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, "Đang nghe...")
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                text = r.recognize_google(audio, language="vi-VN")
                self.entry.delete(0, tk.END)
                self.process_input(text)
            except:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "...")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaifuApp(root)
    root.mainloop()