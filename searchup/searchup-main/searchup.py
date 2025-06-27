import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import webbrowser
import ctypes
import winreg
from tkinter import messagebox

current_engine = "naver"
current_alpha = 0.95
target_alpha = 1.0
alpha_step = 0.05

def 검색():
    keyword = entry.get()
    if not keyword:
        return
    if current_engine == "naver":
        url = f"https://search.naver.com/search.naver?query={keyword}"
    else:
        url = f"https://www.google.com/search?q={keyword}"
    webbrowser.open(url)

def 선택_네이버():
    global current_engine
    current_engine = "naver"
    naver_button.config(bg="#DFF6FF")
    google_button.config(bg="white")

def 선택_구글():
    global current_engine
    current_engine = "google"
    google_button.config(bg="#DFF6FF")
    naver_button.config(bg="white")

def 부드럽게_변경():
    global current_alpha
    if abs(current_alpha - target_alpha) < 0.01:
        root.attributes("-alpha", target_alpha)
        return
    if current_alpha < target_alpha:
        current_alpha += alpha_step
    else:
        current_alpha -= alpha_step
    root.attributes("-alpha", current_alpha)
    root.after(30, 부드럽게_변경)

def on_enter(event):
    global target_alpha
    target_alpha = 1.0
    부드럽게_변경()

def on_leave(event):
    global target_alpha
    target_alpha = 0.3  # 매우 낮은 투명도(거의 안 보임)
    부드럽게_변경()

def 시작_이동(event):
    root.x = event.x
    root.y = event.y

def 이동(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")

def round_image(img, size, radius):
    img = img.convert("RGBA")
    if img.size != (size, size):
        img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    img.putalpha(mask)
    return img

def 둥글게_창_모서리(hwnd, width, height, radius):
    region = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, width, height, radius, radius)
    ctypes.windll.user32.SetWindowRgn(hwnd, region, True)

def 시작프로그램_등록():
    try:
        python_path = os.path.abspath(__file__)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SearchWidget", 0, winreg.REG_SZ, f'python "{python_path}"')
        winreg.CloseKey(key)
    except Exception as e:
        print("시작프로그램 등록 실패:", e)

def 시작프로그램_확인():
    config_path = os.path.join(os.path.dirname(__file__), "start_check_done.txt")
    if not os.path.exists(config_path):
        응답 = messagebox.askyesno("시작 프로그램 등록", "이 프로그램을 윈도우 시작 시 자동 실행할까요?")
        if 응답:
            시작프로그램_등록()
        with open(config_path, "w") as f:
            f.write("done")

def create_rounded_bg(width, height, radius, color="#FFFFFF", transparent="#FF00FF"):
    scale = 4  # 고해상도 스케일
    w, h, r = width * scale, height * scale, radius * scale
    img = Image.new("RGBA", (w, h), transparent)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, w, h), radius=r, fill=color)
    img = img.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

# 설정
WINDOW_WIDTH = 340
WINDOW_HEIGHT = 48

root = tk.Tk()
root.overrideredirect(True)
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+100+100")
root.attributes("-topmost", True)
root.attributes("-alpha", current_alpha)
root.config(bg="#FF00FF")
root.wm_attributes("-transparentcolor", "#FF00FF")

root.bind("<Enter>", on_enter)
root.bind("<Leave>", on_leave)

# 라운드 배경
bg_img = create_rounded_bg(WINDOW_WIDTH, WINDOW_HEIGHT, 30, color="#FFFFFF", transparent="#FF00FF")
bg_label = tk.Label(root, image=bg_img, borderwidth=0)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

frame = tk.Frame(root, bg="white")
frame.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

frame.bind("<Button-1>", 시작_이동)
frame.bind("<B1-Motion>", 이동)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_SIZE = 32
RADIUS = 16

def load_image_safe(path):
    try:
        return Image.open(path)
    except FileNotFoundError:
        return Image.new("RGBA", (IMG_SIZE, IMG_SIZE), (200, 200, 200, 255))

naver_img_raw = round_image(load_image_safe(os.path.join(BASE_DIR, "naver.png")), IMG_SIZE, RADIUS)
google_img_raw = round_image(load_image_safe(os.path.join(BASE_DIR, "google.png")), IMG_SIZE, RADIUS)
search_img_raw = round_image(load_image_safe(os.path.join(BASE_DIR, "img.png")), IMG_SIZE, RADIUS)

naver_img = ImageTk.PhotoImage(naver_img_raw)
google_img = ImageTk.PhotoImage(google_img_raw)
search_img = ImageTk.PhotoImage(search_img_raw)

naver_button = tk.Button(frame, image=naver_img, command=선택_네이버, bg="white", activebackground="white", bd=0)
naver_button.place(x=8, y=8, width=32, height=32)

google_button = tk.Button(frame, image=google_img, command=선택_구글, bg="white", activebackground="white", bd=0)
google_button.place(x=48, y=8, width=32, height=32)

entry_width = WINDOW_WIDTH - 140
entry = tk.Entry(frame, width=18, font=("Arial", 14), relief="solid", bd=1)
entry.place(x=90, y=10, width=entry_width, height=28)
entry.bind("<Return>", lambda e: 검색())

search_button = tk.Button(frame, image=search_img, command=검색, bg="white", activebackground="white", bd=0)
search_button.place(x=WINDOW_WIDTH - 40, y=8, width=32, height=32)

선택_네이버()

root.update_idletasks()
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
둥글게_창_모서리(hwnd, WINDOW_WIDTH, WINDOW_HEIGHT, 30)

시작프로그램_확인()
root.mainloop()
