from auth import autenticar_jugador
from stats import mostrar_estadisticas, update_statistics
from interfaceFourInLine import MainFourInLine
import socket
import threading
import argparse
from queue import Queue

class Servidor:
    def __init__(self, TCP_IP, TCP_Port):
        self.TCP_IP = TCP_IP
        self.TCP_Port = TCP_Port
        self.socket = None
        self.jugadores_espera = Queue()
        self.jugadores_online = []

    def managment_games(self):
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

    def managment_client(self, client_socket, client_address, evento, cola_partida, verificado, usuario_nombre):
        print(f"Conexión aceptada de {client_address}")
        try:
            mensaje = "Bienvenido al 4 en línea\n"
            client_socket.sendall(mensaje.encode())

            if verificado == False:
                usuario_nombre, self.jugadores_online = autenticar_jugador(client_socket, self.jugadores_online)
                verificado = True

            while True:
                menu = ("*1. Jugar\n*2. Ver estadísticas\n*3. Salir\nElija una opción: ")
                client_socket.sendall(menu.encode())
                opcion = client_socket.recv(1024).decode().strip()

                if opcion == "1":
                    self.handle_game_session(client_socket, evento, cola_partida, usuario_nombre)

                elif opcion == "2":
                    mostrar_estadisticas(client_socket, usuario_nombre)

                elif opcion == "3":
                    client_socket.sendall("Desconectando...\n".encode())
                    break

                else:
                    client_socket.sendall("Opción no válida. Intente nuevamente.\n".encode())

        except socket.error as e:
            print(f"Error de socket: {e}")
        finally:
            if usuario_nombre in self.jugadores_online:
                self.jugadores_online.remove(usuario_nombre)
            client_socket.close()
            print(f"Conexión cerrada con {client_address}")

    def handle_game_session(self, client_socket, evento, cola_partida, usuario_nombre): 
        datos = [cola_partida, evento]
        self.jugadores_espera.put(datos)
        mensaje = "Esperando otro jugador...\n"
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
                        mensaje_error = "*Entrada inválida. Por favor ingrese un número entre 1 y 8.\n"
                        client_socket.sendall(mensaje_error.encode())
                
            elif data == "no turno":
                tablero = cola_partida.get()
                client_socket.sendall(tablero.encode())
                            
            elif data == "ganador/empate":
                mensajeGanEmp = cola_partida.get()
                update_statistics(mensajeGanEmp, usuario_nombre)
                client_socket.sendall(mensajeGanEmp.encode())
                tablero = cola_partida.get()
                client_socket.sendall(tablero.encode())
                mensaje = "Redirigiendo al inicio...\n"
                client_socket.sendall(mensaje.encode())
                jugando = False

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

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

            administracion_partidas_thread = threading.Thread(target=self.managment_games)
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





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Servidor 4 en línea')
    parser.add_argument('-H', '--host', type=str, help="Host de escucha", default="::")
    parser.add_argument('-P', '--port', type=int, help='Puerto de escucha', default=1234)
    args = parser.parse_args()
    
    port = args.port
    host = args.host

    servidor = Servidor(host, port)  
    servidor.start_server()




