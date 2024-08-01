import socket
import threading
import argparse


class Servidor:
   def __init__(self, TCP_IP, TCP_Port):
       self.TCP_IP = TCP_IP
       self.TCP_Port = TCP_Port
       self.socket = None

   def managment_client(self,client_socket, client_address):
        print(f"Conexión aceptada de {client_address}")

   def start_server(self):
           self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

            # Desactivar IPV6_V6ONLY
           self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)

           # Obtener información de direcciones
           addr_info = socket.getaddrinfo(self.TCP_IP, self.TCP_Port, socket.AF_INET6, socket.IPPROTO_TCP)

           if not addr_info:
               raise ValueError("No se pudo obtener información de direcciones.")

           # Seleccionar la primera dirección
           addr = addr_info[0][-1]

           self.socket.bind(addr)
           self.socket.listen(5)

           print(f"Servidor iniciado en {addr}")

           while True:
               client_socket, client_address = self.socket.accept()

               client_thread = threading.Thread(target=self.managment_client, args=(client_socket, client_address))
               client_thread.start()





if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Servidor 4 en línea')
   parser.add_argument('-p', '--port', required=True, type=int, help='Puerto de escucha')
   args = parser.parse_args()

   port = args.port

   servidor = Servidor("::", port)  
   servidor.start_server()



