from Four_In_Line import CuatroInLine, FullColumn
from Data_Base import Session,Usuario,HashPassword
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


   def run(self, colas_partida, eventos, evento_partida):
       for x in range(2):
           colas_partida[x].put(evento_partida)
        
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

               while True:
                    evento_partida.wait()
                    col = int(colas_partida[turno].get())-1
                    evento_partida.clear()
                    try:
                        self.game.insert_token(col)
                        colas_partida[turno].put("Ingresado")
                        eventos[turno].set()
                        break
                    except FullColumn:
                        colas_partida[turno].put("NoIngresado")
                        error_FullColumn = f"\n-------Columna llena-------\nIngrese una columna nuevamente\n{os.linesep}"
                        colas_partida[turno].put(error_FullColumn)
                        eventos[turno].set()

               if self.game.winner():
                    self.game.change_turn()
                       
                    for x in range(2):
                        colas_partida[x].put("ganador/empate")

                    for x in range(2):
                        if x == int(self.game.turn):
                            colas_partida[x].put(f"-------Ganaste-------\n")
                        else:
                            colas_partida[x].put(f"-------Perdiste-------\n")
                       
                    for x in range(2):
                        self.board(colas_partida[x])
                        eventos[x].set()
                       
                    self.running = False

               if self.game.empate():
                    for x in range(2):
                        colas_partida[x].put("ganador/empate")
                    
                    for x in range(2):
                        colas_partida[x].put(f"-------Empate-------\n")
                            
                    for x in range(2):
                        self.board(colas_partida[x])
                        eventos[x].set()

                    self.running = False
            


class Servidor:
   def __init__(self, TCP_IP, TCP_Port):
       self.TCP_IP = TCP_IP
       self.TCP_Port = TCP_Port
       self.socket = None
       self.jugadores_espera = Queue()
       self.session = Session()


   def managment_partida(self):
       while True:
           if self.jugadores_espera.qsize() >= 2:
                partida = MainFourInLine()
                evento_partida = threading.Event()
                colas_partida = []
                eventos = []
                
                for x in range(2):
                    jugador = self.jugadores_espera.get()
                    colas_partida.append(jugador[0])
                    eventos.append(jugador[1])

                partida_thread = threading.Thread(target=partida.run, args=(colas_partida, eventos, evento_partida))
                partida_thread.start()
   
   def autenticar_jugador(self, client_socket):
        client_socket.sendall("1. Iniciar sesión\n2. Registrarse\nElija una opción: ".encode())
        opcion = client_socket.recv(1024).decode().strip()

        if opcion == "1":
            client_socket.sendall("Ingrese su usuario: ".encode())
            usuario_nombre = client_socket.recv(1024).decode().strip()
            client_socket.sendall("Ingrese su contraseña: ".encode())
            contrasena = client_socket.recv(1024).decode().strip()

            usuario = self.session.query(Usuario).filter_by(username=usuario_nombre).first()

            if usuario and HashPassword.verify_password(usuario.password_hash, contrasena):
                client_socket.sendall("Inicio de sesión exitoso!\n".encode())
                return usuario_nombre
            else:
                client_socket.sendall("Usuario o contraseña incorrectos.\n".encode())
                return self.autenticar_jugador(client_socket)

        elif opcion == "2":
            client_socket.sendall("Ingrese un nuevo usuario: ".encode())
            nuevo_usuario_nombre = client_socket.recv(1024).decode().strip()
            client_socket.sendall("Ingrese una nueva contraseña: ".encode())
            nueva_contrasena = client_socket.recv(1024).decode().strip()
            
            usuario_existente = self.session.query(Usuario).filter_by(username=nuevo_usuario_nombre).first()

            if usuario_existente:
                client_socket.sendall("El usuario ya existe. Intente nuevamente.\n".encode())
                return self.autenticar_jugador(client_socket)
            else:
                hash = HashPassword.hash_password(nueva_contrasena)
                nuevo_usuario = Usuario(username=nuevo_usuario_nombre, password_hash=hash)
                self.session.add(nuevo_usuario)
                self.session.commit()
                client_socket.sendall("Registro exitoso!\n".encode())
                return nuevo_usuario_nombre
        else:
            client_socket.sendall("Opción no válida. Intente nuevamente.\n".encode())
            return self.autenticar_jugador(client_socket)


   def managment_client(self, client_socket, client_address, evento, cola_partida, verificado, usuario_nombre):
       print(f"Conexión aceptada de {client_address}")
       try:
           if verificado == False:
                usuario_nombre = self.autenticar_jugador(client_socket)
                verificado = True
           
           datos = [cola_partida,evento]
           self.jugadores_espera.put(datos)

           mensaje = "Bienvenido al 4 en línea\n"
           client_socket.sendall(mensaje.encode())
          
           evento_partida = cola_partida.get()

           jugando = True
          
           while jugando:
               evento.wait()
               
               data = cola_partida.get()

               evento.clear()
               if data == "turno":
                   tablero = cola_partida.get()
                   client_socket.sendall(tablero.encode())
                   
                   mensaje = cola_partida.get()
                   client_socket.sendall(mensaje.encode())

                   while True:
                        respuesta = client_socket.recv(1024).decode().strip()
                        if respuesta.isdigit() and 1 <= int(respuesta) <= 8:  
                            cola_partida.put(respuesta)
                            evento_partida.set()
                            evento.wait()
                            if cola_partida.get() == "Ingresado":
                                break
                            else:
                                error = cola_partida.get()
                                client_socket.sendall(error.encode())
                            evento.clear()
                        else:
                            mensaje_error = "Entrada inválida. Por favor ingrese un número entre 1 y 8.\n"
                            client_socket.sendall(mensaje_error.encode())
    

               elif data == "no turno":
                   tablero = cola_partida.get()
                   client_socket.sendall(tablero.encode())
                   
                   
               elif data == "ganador/empate":
                   mensajeGanEmp = cola_partida.get()
                   usuario = self.session.query(Usuario).filter_by(username=usuario_nombre).first()
                   if usuario:
                        if mensajeGanEmp.strip() == "-------Ganaste-------":
                            usuario.partidas_ganadas += 1
                        elif mensajeGanEmp.strip() == "-------Perdiste-------":
                            usuario.partidas_perdidas += 1
                        elif mensajeGanEmp.strip() == "-------Empate-------":
                            usuario.partidas_empatadas += 1 
                   else:
                        print("Usuario no encontrado.")
                   client_socket.sendall(mensajeGanEmp.encode())
                   tablero = cola_partida.get()
                   client_socket.sendall(tablero.encode())
                   mensaje = "Queres voler a jugar?\n 1 --> Si\n 2 --> No"
                   client_socket.sendall(mensaje.encode())
                   while True:
                        respuesta = client_socket.recv(1024).decode().strip()
                        if respuesta.isdigit() and 1 == int(respuesta):  
                            self.managment_client(client_socket, client_address, evento, cola_partida, verificado, usuario_nombre)
                        elif respuesta.isdigit() and 2 == int(respuesta):
                            mensaje_despedida = "Chau.\n"
                            client_socket.sendall(mensaje_despedida.encode())
                            jugando = False
                            break
                        else:
                            mensaje_error = "Entrada inválida. Por favor ingrese un número entre 1 y 2.\n"
                            client_socket.sendall(mensaje_error.encode())


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

           administracion_partidas_thread = threading.Thread(target=self.managment_partida)
           administracion_partidas_thread.start()

           while True:
               client_socket, client_address = self.socket.accept()

               evento = threading.Event()
               cola_partida = Queue()
               verificado = False

               client_thread = threading.Thread(target=self.managment_client, args=(client_socket, client_address, evento, cola_partida, verificado,None))
               client_thread.start()

       except socket.error as e:
           print(f"Error al enlazar el socket: {e}")
       except ValueError as ve:
           print(f"Error: {ve}")
       finally:
           if self.socket:
               self.socket.close()
           try:
                self.session.commit()
                print("Datos actualizados y commit realizado.")
           except Exception as e:
                print(f"Error al hacer commit: {e}")
                self.session.rollback()
           self.session.close()





if __name__ == '__main__':
   parser = argparse.ArgumentParser(description='Servidor 4 en línea')
   parser.add_argument('-p', '--port', required=True, type=int, help='Puerto de escucha')
   args = parser.parse_args()

   port = args.port

   servidor = Servidor("::", port)  
   servidor.start_server()



