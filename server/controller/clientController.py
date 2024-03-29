from controller.errorController import log_error
from controller.configController import get_config
from controller.commandController import check_command
import random

config = get_config()
clients = []

class Client:
    def __init__(self, client_socket, addr, nick):
        self.client_socket = client_socket
        self.addr = addr
        self.nick = nick
        self.buffer_size = config['buffer_size']
        self.channel = config['default_channel']
        self.away = ""
        self.ignore = []

    def send(self, data):
        try:
            self.client_socket.send(data.encode('utf-8'))
        except Exception as e:
            log_error(e)

    def is_ignored(self, addr):
        return addr in self.ignore

    def recv(self, length):
        try:
            return self.client_socket.recv(length).decode('utf-8')
        except Exception as e:
            log_error(e)

    def dm(self, client, nick, msg):
        for c in clients:
            if c.nick == nick:
                if not c.is_ignored(client.addr):
                    c.send(f"{client.nick} >> {msg}")

    def leave(self):
        self.client_socket.close()
        clients.remove(self)
        self.say(f"{self.nick} has left #{self.channel}")

    def say(self, msg):
        broadcast(self, msg)

def handle_client(client_socket, addr):
    try:
        client = Client(client_socket, addr, nick=f"Guest{random.randint(1, 9999)}")
        clients.append(client)
        broadcast(client, f"{client.nick} has joined #{client.channel}")
        while True:
            try:
                msg = client.recv(client.buffer_size)
                if not msg:
                    client.leave()
                    break
                if not msg.strip() == "":
                    cmd = check_command(msg, client, clients)
                    if not cmd:
                        msg = f"<{client.nick}> {msg}"
                        client.say(msg)
                    elif cmd != True:
                        client.say(cmd)
            except Exception as e:
                log_error(e)
                client.leave()
                break
    except Exception as e:
        log_error(e)
    finally:
        if client in clients:
            client.leave()

def broadcast(client, msg):
    if len(clients) <= 0:
        return
    for c in clients:
        try:
            if c.channel == client.channel:
                if not c.is_ignored(client.addr):
                    c.send(msg)
        except Exception as e:
            log_error(e)
            c.leave()