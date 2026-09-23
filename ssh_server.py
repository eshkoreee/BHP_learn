#!/usr/bin/env python
import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__)) # сохраняет путь к папке что бы найти рядом лежащий SSH ключ
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, '.test_rsa.key')) # склеивает путь и сам файл SSH ключа читает его и превращает в реальный SSH ключ для клиента


class Server (paramiko.ServerInterface): # унаследуемся от ServerInterface
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED # если клиент хочет просто создать командную оболочку то пускает если нет запрещает 
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED # не отрубает подключение но не разрешает ничего кроме session

    def check_auth_password(self, username, password): # проверка логина и пароля
        if (username == 'roman') and (password == 'putin huilo'):
            return paramiko.AUTH_SUCCESSFUL # если неверно возващает None а Paramiko none воспринимает как ошибка аутентификации и закрывает SSH подключение


if __name__ == '__main__':
    server = '127.0.0.1'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # задаем что после отключения от порта не будем ждать таймер переподключения
        sock.bind((server, ssh_port)) # биндим айпи и порт
        sock.listen(100) # создаем очередь из 100 подключений
        print('[+] Listening for connection ...')
        client, addr = sock.accept() # принимаем подключения
    except Exception as e: # если ошибка пишем почему
        print('[-] Listen failed: ' + str(e))
        sys.exit(1) # аварийная остановка программы
    else:
        print(f'[+] Got a connection! from {addr}')

    bhSession = paramiko.Transport(client) # оборачивает сырой сокет в защищенное SSH соединение
    bhSession.add_server_key(HOSTKEY) # передает объект ключа SSH подключению клиента
    server = Server() # создаем экземпляр нашего класса
    bhSession.start_server(server=server) # запускает SSH сервер поверх нашего TCP подключения

    chan = bhSession.accept(20) # ждем ответа от клиента 20 секунд
    if chan is None: # если ничего то:
        print('*** No channel.')
        sys.exit(1) # аварийное отключение

    print('[+] Authenticated!')
    print(chan.recv(1024).decode()) # ClientConnected
    chan.send('Welcome to bh_ssh')
    try:
        while True:
            command = input("Enter command: ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()
