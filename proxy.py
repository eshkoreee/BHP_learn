import sys
import socket
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])


def hexdump(src, length=16, show=True):
    if isinstance(src, bytes): # проверка байты ли это
        src = src.decode() # декодирует в символы
    results = list()
    for i in range(0, len(src), length): # от нуля до размера буфера и шаг равен 16
        word = str(src[i:i+length]) # список элементов от i до i плюс 16
        printable = word.translate(HEX_FILTER) # фильтрует нечитаемые и вспомогательные символы на точки
        hexa = ' '.join([f'{ord(c):02X}' for c in word]) # превращает список символов в 16 ричную систему и склеивает результаты через пробел
        hexwidth = length*3 # на 1 символ уходит 2 символа плюс пробел поэтому length будет икс 3 от реального размера
        results.append(f'{i:04x}  {hexa:<{hexwidth}}  {printable}') # собирает данные и выравнивает по размеру hexwidth(48 символов)
    if show: # проверка хочешь ли ты прочитать блок сейчас или передать для дальнейшей манипуляции с ним
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    buffer = b""
    connection.settimeout(10) # задаем таймер 10 секунд
    try:
        while True: 
            data = connection.recv(4096)
            if not data: # каждый пакет с сервера мы добавляем в буфер
                break # если ничего не пришло возвращаем что есть

            buffer += data 
    except Exception as e:
        print('error ', e) # по истечению таймера выводит исключение
        pass # при исключении выходим с цикла и возвращаемся в proxy_handler

    return buffer


def request_handler(buffer):
    # perform packet modifications
    return buffer


def response_handler(buffer):
    # perform packet modifications
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    # создаем сокет для сервера и сразу к нему подключаемся. например к google.com
    if receive_first:
        remote_buffer = receive_from(remote_socket) # передаем сокет сервера в метод
        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer) # превращает байты в блок 16ричных символов

            # remote_buffer = response_handler(remote_buffer)
            # client_socket.send(remote_buffer) нужно для модификации трафика 
            # print("[==>] Sent to local.") если понадобится можно расскоментировать

    while True:
        local_buffer = receive_from(client_socket) # 10 сек ждем данные со стороны клиента, жертвы
        if len(local_buffer):
            print(f"[<==] Received {len(local_buffer)} bytes from local.")
            hexdump(local_buffer) # превращаем буфер в блок 16ричных символов и помещаем в results в методе

            local_buffer = request_handler(local_buffer) # если не модифицируем данные то ничего не происходит
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer): # то же самое что и на 68-70 строчках только от сервера
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer) # модификация трафика если надо
            client_socket.send(remote_buffer)
            print("[==>] Sent to local.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: # сверху передаем данные с консоли и создаем объект сокета
        server.bind((local_host, local_port))
    except Exception as e:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        print(e) # проверка на подлинность хоста и порта
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        print("> Received incoming connection from %s:%d" % (addr[0], addr[1]))
        # одобряем подключение и оповещаем об этом через print
        proxy_thread = threading.Thread(
            target=proxy_handler, # создаем поток для нашего клиента и передаем хост порт удаленного сервака
            args=(client_socket, remote_host,
                  remote_port, receive_first))
        proxy_thread.start() # запускаем поток


def main(): # начало программы 
    if len(sys.argv[1:]) != 5: # проверка что аргументов ровно 5 если нет выводит инструкцию
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0) # досрочно завершает программму 0 значит без ошибок
    
    local_host = sys.argv[1] #  размещает введенные данные по переменным
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first: # ввели ли мы True для ожидания ответа от сервера
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, # для обработки клиента
                remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()
