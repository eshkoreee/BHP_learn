import base64
import win32api
import win32con
import win32gui
import win32ui

def get_dimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN) # получаем границы рабочего стола если мониторов несколько их тоже задевает
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (width, height, left, top)

def screenshot(name='screenshot'):
    hdesktop = win32gui.GetDesktopWindow() # получаем дескриптор рабочего стола охватывающее весь экран
    width, height, left, top = get_dimensions()

    desktop_dc = win32gui.GetWindowDC(hdesktop) # получаем сырой контекст устройсва позволяющее рисовать прямо на экране
    img_dc = win32ui.CreateDCFromHandle(desktop_dc) # оборачиваем сырой контекст в обертку win32ui для вызова его методов
    mem_dc = img_dc.CreateCompatibleDC() # получаем совместимый контекст устройства в памяти. она хранит разрешение экрана и глубину цвета

    screenshot = win32ui.CreateBitmap() # создаем битовую карту для получения в нее скриншота и последующего сохранения в файл. пока что у нее нет размеров и данных для сохранения
    screenshot.CreateCompatibleBitmap(img_dc, width, height) # создаем теперь на основе прошлой карты новую битовую карту нужного размера совместимую с экраном пока что это пустое место в памяти
    mem_dc.SelectObject(screenshot) # прикрепляем битовую карту к контексту устройства теперь если мы че то будем рисовать в mem_dc это все будет помещаться в screenshot
    mem_dc.BitBlt((0,0), (width, height), img_dc, (left, top), win32con.SRCCOPY) # тут происходит копирование: mem_dc куда копируем, (0,0) координаты в целевом контексте с которых начинается вставка(левый верхний угол)
    # разрешение (размер) копируемой области, img_dc это контекст экрана откуда копируем, (left, top) координаты в исходном контексте img_dc для поддержки нескольких экранов, win32con.SRCCOPY сама операция копирования. копирует как есть на самом деле
    screenshot.SaveBitmapFile(mem_dc, f'{name}.bmp') # сохраняем скриншот в файл.bmp. в screenshot хранится собственно сам скриншот, в mem_dc контекст памяти с которым связана битовая карта и в конечном итоге пишем название файла

    mem_dc.DeleteDC() # удаляем контекст устройства который мы сохраняли в памяти
    win32gui.DeleteObject(screenshot.GetHandle()) # удаляем объект битовой карты по его дескриптору. освобождает память которую занимал скриншот
    # все эти удаления нужны что бы уже не нужная структура не нагружала компьютер

def run():
    screenshot()
    with open('screenshot.bmp') as f:
        img = f.read()
    return img

if __name__ == '__main__':
    screenshot()
