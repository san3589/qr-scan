import time
import tkinter
import os
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, Text, messagebox
from PIL import Image, ImageTk
import cv2
import pyzbar.pyzbar as pyzbar
import requests

camera_on = True

def get_camera_list():
    camera_list = []
    for i in range(0, 10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            name = cap.getBackendName()
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

    with open('cache.txt', 'r') as file:
        src = file.readlines()
    src = [sr.strip() for sr in src]
    if data['team'] not in src:
        response = requests.post(url="https://octopus-app-uckx7.ondigitalocean.app/api/event/activate_team",  json=data)
        if response.status_code == 200:
            logger(f"Данные команды {data['team']} успешно отправлены")
            with open('cache.txt', 'a') as file:
                file.write(f"{data['team']}\n")
        else:
            logger(f"Ошибка отправки данных команды {data['team']}")
    else:
        logger(f"Команда {data['team']} есть в кэше. Очистите кэш и повторите попытку")


def scan_qr_code(channel_id, camera_id):
    global camera_on

    if camera_on:
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            logger("Камера не включена")
            return

        while camera_on:
            ret, frame = cap.read()
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            photo = ImageTk.PhotoImage(image)
            camera_label.config(image=photo)
            camera_label.image = photo
            root.update()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decode_object = pyzbar.decode(gray)
            for obj in decode_object:
                data = obj.data.decode('utf-8')
                print(data)
                logger(f"QR код прочитан {data}")
                send_qr_data(data, channel_id)
                points = obj.polygon
                if len(points) > 4:
                    pt1 = (points[0].x, points[0].y)
                    pt2 = (points[1].x, points[1].y)
                    pt3 = (points[2].x, points[2].y)
                    pt4 = (points[3].x, points[3].y)
                    cv2.line(frame, pt1, pt2, (255, 0, 0), 3)
                    cv2.line(frame, pt2, pt3, (255, 0, 0), 3)
                    cv2.line(frame, pt3, pt4, (255, 0, 0), 3)
                    cv2.line(frame, pt4, pt1, (255, 0, 0), 3)
                    cv2.imshow('Камера', frame)

        # Закрываем камеру и окна
        cap.release()
        cv2.destroyAllWindows()
        root.destroy()


def toogle_camera():
    global camera_on, camera_var
    camera_on = not camera_on
    channel_name = channel_var.get()
    camera_index = camera_names.index(camera_var.get())
    camera_id = camera_list[camera_index][0]

    if channel_name:
        for channel in channels_info:
            if channel['name'] == channel_name:
                channel_id = channel['id']

                if camera_on:
                    camera_button.config(text="Отключить камеру")
                    scan_qr_code(channel_id, camera_id)
                else:
                    camera_button.config(text="Включить  камеру")
                    cv2.destroyAllWindows()
    else:
        messagebox.showwarning("Необходимо выбрать канал")



def logger(message):
    log_text.config(state='normal')
    log_text.insert(tkinter.END, f"{message}\n")
    log_text.config(state='disabled')


def clear_cache():
    if os.path.exists('cache.txt'):
        os.remove('cache.txt')
        logger('Кэш очищен')


root = Tk()
root.title('Скан QR Кодов')
camera_label = Label(root)
camera_label.pack()

channel_label = Label(root, text="ID канала")
channel_label.pack()

channel_var = StringVar(root)
channel_entry = Entry(root, textvariable=channel_var)
channel_entry.pack()

camera_var = StringVar(root)
camera_list = get_camera_list()
camera_names = [name for _, name in camera_list]

camera_var.set(camera_names[0])

camera_menu = tkinter.OptionMenu(root, camera_var, *camera_names)
camera_menu.pack()

camera_button = Button(root, text="Включить камеру", command=toogle_camera)
camera_button.pack()

log_text = Text(root, height=10, wrap=tkinter.WORD, state='disabled')
log_text.pack()

channels_info = get_channels_id()
channels_names = [channel['name'] for channel in channels_info]
channel_menu = OptionMenu(root, channel_var, *channels_names)
channel_menu.pack()

root.mainloop()
