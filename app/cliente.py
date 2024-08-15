import socket
import sys
import termios
import argparse
import selectors


class Cliente:
    def __init__(self, TCP_IP, TCP_Port):
        self.TCP_IP = TCP_IP
        self.TCP_Port = TCP_Port
        self.socket = None
        self.running = True

    def conectar(self):
        addr_info = socket.getaddrinfo(self.TCP_IP, self.TCP_Port, socket.AF_UNSPEC, socket.SOCK_STREAM)

        if not addr_info:
            raise ValueError("No se pudo obtener información de direcciones.")

        addr = addr_info[0][-1]

        self.socket = socket.socket(addr_info[0][0], socket.SOCK_STREAM)
        self.socket.connect(addr)

        print("Conectado al servidor")

    def receive_messages(self):
        while self.running:
            message = self.socket.recv(1024).decode()
            print(message)
            if message == "":
                self.running = False
                break
            elif "*" in message:
                self.clear_input_buffer()
                self.send_messages()

    def clear_input_buffer(self):
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

    def send_messages(self):
        selector = selectors.DefaultSelector()
        selector.register(sys.stdin, selectors.EVENT_READ)
        
        while True:
            events = selector.select(timeout=50)
            if events:
                for key, _ in events:
                    if key.fileobj is sys.stdin:
                        message = sys.stdin.readline().strip()
                        if message:
                            self.socket.sendall(message.encode())
                            return
                        else:
                            print("No se puede enviar mensajes vacíos")

            else:
                print("\nHas sido desconectado")
                self.running = False
                break

        selector.unregister(sys.stdin)
    
    def jugar(self):
        self.conectar()
        self.receive_messages()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cliente 4 en línea')
    parser.add_argument('-H','--host', type=str, help="Host a conectarse", default="localhost")
    parser.add_argument("-P","--port", type=int, help="Puerto a conectarse", default=1234)
    
    args = parser.parse_args()

    port = args.port
    host = args.host

    cliente = Cliente(host, port)
    cliente.jugar()

