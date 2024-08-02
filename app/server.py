from Four_In_Line import CuatroInLine
import socket
import threading
import argparse
import os
from queue import Queue



class MainFourInLine:
   def __init__(self):
       self.game = CuatroInLine()
       self.running = True


   def board(self, cola_partida):
       board_message = ""
       for x in range(1, 9):
           board_message += f"  ({x}) "
       board_message += "\n -----------------------------------------------\n"

       for x in range(8):
           board_message += '|'
           for y in range(8):
               board_message += f"  {self.game.board[x][y]}  |"
           board_message += "\n -----------------------------------------------\n"

       cola_partida.put(board_message)


   def run(self, colas_partida, eventos):
       while self.running:
               turno = int(self.game.turn)
                   
               for x in range(2):
                   if x == turno:
                       colas_partida[x].put("turno")
                   else:
                       colas_partida[x].put("no turno")
                   
               for x in range(2):
                   self.board(colas_partida[x])

               turno_message = f"Turno del jugador {turno} --> En qué columna quieres insertar la ficha: "
               colas_partida[turno].put(turno_message)

               for x in range(2):
                   eventos[x].set()

               

class Servidor:
   def __init__(self, TCP_IP, TCP_Port):
       self.TCP_IP = TCP_IP
       self.TCP_Port = TCP_Port
       self.socket = None


   def managment_client(self, client_socket, client_address, evento, cola_partida, evento_partida):
       print(f"Conexión aceptada de {client_address}")

       try:
           mensaje = "Bienvenido al 4 en línea\n"
           client_socket.sendall(mensaje.encode())
          
           while True:
               evento.wait()
               
               data = cola_partida.get()

               evento.clear()

               if data == "turno":
                   tablero = cola_partida.get()
                   client_socket.sendall(tablero.encode())
                   
                   mensaje = cola_partida.get()
                   client_socket.sendall(mensaje.encode())

                   respuesta = client_socket.recv(1024).decode().strip()
                   if respuesta.isdigit() and 1 <= int(respuesta) <= 8:  
                        cola_partida.put(respuesta)
                        evento_partida.set()
    
               elif data == "no turno":
                   tablero = cola_partida.get()
                   client_socket.sendall(tablero.encode())
                   

       except socket.error as e:
           print(f"Error de socket: {e}")
       finally:
           client_socket.close()
           print(f"Conexión cerrada con {client_address}")


   def start_server(self):
       self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

       try:
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

           contador = 0
           eventos = []
           colas_partida = []

           while True:
               client_socket, client_address = self.socket.accept()

               evento = threading.Event()
               cola_partida = Queue()

               client_thread = threading.Thread(target=self.managment_client, args=(client_socket, client_address, evento, cola_partida))
               client_thread.start()

               eventos.append(evento)
               colas_partida.append(cola_partida)
               contador += 1

               if contador % 2 == 0:
                   partida = MainFourInLine()
                   partida_thread = threading.Thread(target=partida.run, args=(colas_partida, eventos))
                   partida_thread.start()

                   eventos = []
                   colas_partida = []
                   cola_partida = Queue()

       except socket.error as e:
           print(f"Error al enlazar el socket: {e}")
       finally:
           if self.socket:
               self.socket.close()




if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Servidor 4 en línea')
   parser.add_argument('-p', '--port', required=True, type=int, help='Puerto de escucha')
   args = parser.parse_args()

   port = args.port

   servidor = Servidor("::", 1234)  
   servidor.start_server()



