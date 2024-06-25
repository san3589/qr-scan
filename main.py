import time
import tkinter
import os
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, Text, messagebox, scrolledtext
from PIL import Image, ImageTk
import cv2
import pyzbar.pyzbar as pyzbar
from pygrabber.dshow_graph import FilterGraph
import requests

camera_on = True

def get_camera_list():
    camera_list = []
    devices = FilterGraph().get_input_devices()
    for i in range(0, 10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            name = devices[i]
            if not name:
                name = f"Камера {i}"
            camera_list.append((i, name))
            cap.release()
    return camera_list


def update_camera_menu():
    global camera_list, camera_var, camera_menu
    camera_list = get_camera_list()
    camera_names = [name for _, name in camera_list]
    camera_menu.destroy()
    camera_menu = tkinter.OptionMenu(root, camera_var, *camera_names)
    camera_menu.pack()


def get_channels_id():
    res = requests.get("https://octopus-app-uckx7.ondigitalocean.app/api/channels")
    if res.status_code == 200:
        channels = []
        for chanel in res.json()['data']['channels']:
            channels.append({'id': chanel['id'], 'name':chanel['name']})
        return channels
    else:
        logger("Получение данных c api неудачно")
        return None


def send_qr_data(qr_data, channel_id):

    data = {}
    data["channel_id"] = int(channel_id)
    data["team"] = qr_data
    try:
        with open('cache.txt', 'r') as file:
            src = file.readlines()
    except FileNotFoundError:
        src = []
    src = [sr.strip() for sr in src]
    if data['team'] not in src:
        response = requests.post(url="https://octopus-app-uckx7.ondigitalocean.app/api/event/activate_team",  json=data)
        if response.status_code == 200:
            logger(f"Данные команды {data['team']} успешно отправлены")
            with open('cache.txt', 'a') as file:
                file.write(f"{data['team']}\n")
                time.sleep(1)
        else:
            logger(f"Ошибка отправки данных команды {data['team']}")
    else:
        logger(f"Команда {data['team']} есть в кэше. Очистите кэш и повторите попытку")
        # time.sleep(1)


def scan_qr_code(channel_id, camera_id):
    global camera_on

    if camera_on:
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            logger("Камера не включена")
            return

        while camera_on:
            ret, frame = cap.read()
            camera_label.config(state='normal', width=400, height=400)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decode_object = pyzbar.decode(gray)
            for obj in decode_object:
                x, y, w, h = obj.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                data = obj.data.decode('utf-8')
                logger(f"QR код прочитан {data}")
                send_qr_data(data, channel_id)
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            photo = ImageTk.PhotoImage(image)
            camera_label.config(image=photo)
            camera_label.image = photo
            root.update()

        cap.release()
        camera_label.config(state='disabled')


def toggle_camera():
    global camera_on, camera_var

    channel_name = channel_var.get()
    camera_index = camera_names.index(camera_var.get())
    camera_id = camera_list[camera_index][0]

    if not camera_on:  # Если камера выключена, включаем ее
        camera_on = True
        camera_button.config(text="Отключить камеру")
        logger(f"Камера {camera_names[camera_index]} включена")
        if channel_name:
            for channel in channels_info:
                if channel['name'] == channel_name:
                    channel_id = channel['id']
                    scan_qr_code(channel_id, camera_id)
        else:
            messagebox.showwarning("Необходимо выбрать канал")
    else:  # Если камера включена, выключаем ее
        camera_on = False
        camera_button.config(text="Включить  камеру")
        logger(f"Камера {camera_names[camera_index]} отключена")




def logger(message):
    now = datetime.now()
    log_text.config(state='normal')
    log_text.insert(tkinter.END, f"{message}\n")
    with open('logger.txt', 'a', encoding='utf-8') as file:
        file.write(f"{now.isoformat()} {message}\n")
    log_text.config(state='disabled')


def clear_cache():
    if os.path.exists('cache.txt'):
        os.remove('cache.txt')
        logger('Кэш очищен')
    else:
        logger("Кэш пуст")


root = Tk()
root.title('QR Scanner')
camera_label = Label(root)
camera_label.grid(row=0, column=0, columnspan=3, sticky="nw")

#
clear_button = Button(root, text="Очистить кэш", command=clear_cache, width=15, height=2, font=("Arial", 12))
clear_button.grid(row=0, column=2, sticky="ne", padx=10, pady=10)


channel_label = Label(root, text="Название канала")
channel_label.grid(row=0, column=1, sticky="s")


channel_var = StringVar(root)
channel_entry = Entry(root, textvariable=channel_var)
channel_entry.grid(row=1, column=1, sticky="w")


channels_info = get_channels_id()
channels_names = [channel['name'] for channel in channels_info]
channel_menu = OptionMenu(root, channel_var, *channels_names)
channel_menu.grid(row=1, column=2, sticky="w")


camera_var = StringVar(root)
camera_list = get_camera_list()
camera_names = [name for _, name in camera_list]
camera_var.set(camera_names[0])
camera_menu = OptionMenu(root, camera_var, *camera_names)
camera_menu.grid(row=2, column=2, sticky="w")


camera_button = Button(root, text="Включить камеру", command=toggle_camera, width=15, height=2, padx=5, pady=5, font=('Arial', 12))
camera_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)


log_text = scrolledtext.ScrolledText(root, height=20, wrap=tkinter.WORD, state='disabled')
log_text.config(state='normal')
log_text.grid(row=3, column=0, columnspan=3, sticky="nsew")


root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)


root.mainloop()
