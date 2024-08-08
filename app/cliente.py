import socket
import threading


class Cliente:
    def __init__(self, TCP_IP, TCP_Port):
        self.TCP_IP = TCP_IP
        self.TCP_Port = TCP_Port
        self.socket = None
        self.running = True

    def conectar(self):
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.connect((self.TCP_IP, self.TCP_Port))
        print("Conectado al servidor")

    def receive_messages(self):
        while self.running:
            message = self.socket.recv(1024).decode()
            if message == "":
                self.running = False
                break
            print(message)

    def send_messages(self):
        while self.running:
            message = input("")
            self.socket.sendall(message.encode())

    def jugar(self):
        receive_msg_thread = threading.Thread(target=self.receive_messages, args=())
        send_msg_thread = threading.Thread(target=self.send_messages, args=())
                
        receive_msg_thread.start()
        send_msg_thread.start()
                
        receive_msg_thread.join() 
        send_msg_thread.join()

    def cerrar(self):
         if self.socket:
               self.socket.close()


if __name__ == "__main__":
    cliente = Cliente(TCP_IP="::1", TCP_Port=12345)
    cliente.conectar()
    cliente.jugar()
    cliente.cerrar()

