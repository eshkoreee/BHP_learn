from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll
import random
import sys
import time
import win32api

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)
    ]

def get_last_input():
    struct_lastinputinfo = LASTINPUTINFO() # создаем структуру для winAPI
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO) # сохраняем размер структуры что так же требует winAPI
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo)) # заполняем 2 поле в структуре временем последнего ввода пользователя в миллисекундах
    run_time = windll.kernel32.GetTickCount() # получаем время работы систему в миллисекундах
    elapsed = run_time - struct_lastinputinfo.dwTime # получаем время которое простояла система без действия после последнего взаимодействия пользователя с компьютером в миллисекундах
    print(f"[*] It's been {elapsed} milliseconds since the last input event.") # выводим об этом в консоль
    return elapsed

# while True:
#     get_last_input()
#     time.sleep(1)

class Detector:
    def __init__(self):
        self.double_clicks = 0
        self.keystrokes = 0
        self.mouse_clicks = 0

    def get_key_press(self):
        for i in range(0, 0xff):  # проходим по всем виртуальным клавишам на клавиатуре 0-255 
            state = win32api.GetAsyncKeyState(i) # проверяем клавишу на наличие нажатия 
            if state & 0x0001: # проверка что клавиша была нажата именно в момент проверки
                if i == 0x1: # проверка что активна именно левая кнопка мыши
                    self.mouse_clicks += 1
                    return time.time() # возвращаем время в которое закончилась проверка работы ЛКМ
                elif i > 32 and i < 127: # проверка что активная клавиша является печатной
                    self.keystrokes += 1
        return None

    def detect(self):
        previous_timestamp = None
        first_double_click = None
        double_click_threshold = 0.35
        
        max_double_clicks = 10
        max_keystrokes = random.randint(10,25)
        max_mouse_clicks = random.randint(5,25)
        max_input_threshold = 30000

        last_input = get_last_input() # получаем время которое пользователь не трогал компьютер
        if last_input >= max_input_threshold: # если это больше 30 секунд то вырубаем все что есть
            sys.exit(0)
        
        detection_complete = False
        while not detection_complete:
            keypress_time = self.get_key_press() # получаем время первого срабатывания любого события клавиатуры или мыши
            if keypress_time is not None and previous_timestamp is not None: # проверка были ли какие то действия до этой итерации
                elapsed = keypress_time - previous_timestamp # получаем время которое прошло между прошлым нажатием и последним
                
                if elapsed <= double_click_threshold: # проверка было ли это двойное нажатие
                    self.mouse_clicks -= 2 # переносим данные из 1 переменной в другую
                    self.double_clicks += 1
                    if first_double_click is None:
                        first_double_click = time.time() # сохраняем время первого дабл клика
                    else:
                        if self.double_clicks >= max_double_clicks: # проверка привысили ли мы максимальный лимит кликов
                            if (keypress_time - first_double_click <= # проверка что если между последним кликом и первым дабл кликом прошло меньше минимального интервала 0.35 секунды на 1 дабл клик если нажатия были быстрее то отрубаемся
                                (max_double_clicks*double_click_threshold)):
                                sys.exit(0)
                if (self.keystrokes >= max_keystrokes and 
                    self.double_clicks >= max_double_clicks and 
                    self.mouse_clicks >= max_mouse_clicks): # если во время проверки нажатия привысили все лимиты то даем флагу detection_complete = True
                    detection_complete = True
                    
                previous_timestamp = keypress_time # если детекта не было то сохраняем время нажатия в отдельную переменную для последующего сравнения
            elif keypress_time is not None: # при первом слове нажатия сохраняем время его нажатия в отдельную переменную
                previous_timestamp = keypress_time

if __name__ == '__main__':
    d = Detector()
    d.detect()
    print('okay.')

