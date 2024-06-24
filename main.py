import time
import tkinter
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, Text, messagebox
from PIL import Image, ImageTk
import cv2
import pyzbar.pyzbar as pyzbar
import requests

API_URL_CATEGORY_INFO = ""
API_URL_QR_CODE_INFO = ""
API_KEY = ""

camera_on = False


def get_categories_id():

    res = requests.get("https://octopus-app-uckx7.ondigitalocean.app/api/channels")
    if res.status_code == 200:
        channels = []
        for chanel in res.json()['data']['channels']:
            channels.append(chanel['id'])
        return channels
    else:
        logger("Получение данных c api неудачно")
        return None



def send_qr_data(qr_data, category_id):
    data = qr_data
    data["channel_id"] = category_id
    response = requests.post(url="https://octopus-app-uckx7.ondigitalocean.app/api/event/activate_team",  data=data)
    if response.status_code == 200:
        logger("Данные успешно отправлены")
    else:
        logger('Ошибка отправки данных')


def scan_qr_code(category_id):
    global camera_on

    if camera_on:
        cap = cv2.VideoCapture(0)
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
                logger("QR код прочитан")
                send_qr_data(data, category_id)
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
    global camera_on
    camera_on = not camera_on
    category_id = category_var.get()
    if category_id:
        if camera_on:
            camera_button.config(text="Отключить камеру")
            scan_qr_code(category_id)
        else:
            camera_button.config(text="Включить  камеру")
            cv2.destroyAllWindows()
    else:
        messagebox.showwarning("Необходимо выбрать категорию")


def logger(message):
    log_text.config(state='normal')
    log_text.insert(tkinter.END, f"{message}\n")
    log_text.config(state='disabled')


root = Tk()
root.title('Скан QR Кодов')
camera_label = Label(root)
camera_label.pack()

category_label = Label(root, text="ID категории")
category_label.pack()

category_var = StringVar(root)
category_entry = Entry(root, textvariable=category_var)
category_entry.pack()
camera_button = Button(root, text="Включить камеру", command=toogle_camera)
camera_button.pack()

log_text = Text(root, height=10, wrap=tkinter.WORD, state='disabled')
log_text.pack()

category_ids = get_categories_id()
category_menu = OptionMenu(root, category_var, *category_ids)
category_menu.pack()

root.mainloop()
