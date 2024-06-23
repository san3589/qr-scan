import time
import tkinter
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, Text
from PIL import Image, ImageTk
import cv2
import pyzbar.pyzbar as pyzbar
import requests

API_URL_CATEGORY_INFO = ""
API_URL_QR_CODE_INFO = ""
API_KEY = ""

camera_on = False



def get_categories_id():
    headers = {}
    # response = requests.get(url=API_URL_CATEGORY_INFO, headers=headers)
    # if response.status_code == 200:
    #     return response.json()
    # else:
    #     messagebox.showerror("Ошибка получений категорий. Попробуйте снова.")
    return [1, 2, 3]

def send_qr_data(qr_data, category_id):

    headers = {}
    data = qr_data
    params = {'category': category_id}
    response = requests.post(url=API_URL_QR_CODE_INFO, headers=headers, data=data, params=params)
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
        while camera_on:
            ret, frame = cap.read()
            if not ret:
                break

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
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                photo = ImageTk.PhotoImage(image)
                camera_label.config(image=photo)
                camera_label.image = photo
                root.update()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    camera_on = False
                    break
        cap.release()
        cv2.destroyAllWindows()

def start_scan():
    category_id = category_var.get()
    if category_id:
        scan_qr_code(category_id)
    else:
       logger("Необходимо выбрать категорию")
def toogle_camera():
    global camera_on
    camera_on = not camera_on
    if camera_on:
        camera_button.config(text="Отключить камеру")
        scan_qr_code(category_var.get())
    else:
        camera_button.config(text="Включить камеру камеру")
        cv2.destroyAllWindows()

def logger(message):
    log_text.config(state='normal')
    log_text.insert(tkinter.END, f"{message}\n")
    log_text.config(state='disabled')


root  = Tk()
root.title('Скан QR Кодов')
camera_label = Label(root)
camera_label.pack()

category_label = Label(root, text="ID категории")
category_label.pack()

category_var = StringVar(root)
category_entry = Entry(root, textvariable=category_var)
category_entry.pack()
start_button = Button(root, text="Начать сканирование", command=start_scan)
camera_button = Button(root, text="Включить камеру", command=toogle_camera)
camera_button.pack()

category_ids = get_categories_id()
category_menu = OptionMenu(root, category_var, *category_ids)
category_menu.pack()

log_text = Text(root, height=10, wrap=tkinter.WORD, state='disabled')
log_text.pack()


root.mainloop()