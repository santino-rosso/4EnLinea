from auth import autenticar_jugador
from stats import mostrar_estadisticas, update_statistics
from interfaceFourInLine import MainFourInLine
import socket
import threading
import argparse
from queue import Queue
from multiprocessing import Process, Pipe
from log import generador_registros
import signal


class Servidor:
    def __init__(self, TCP_Port, parent_conn):
        self.TCP_Port = TCP_Port
        self.sockets = []
        self.jugadores_espera = Queue()
        self.jugadores_online = []
        self.parent_conn = parent_conn
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()



    def managment_games(self):
        while not self.shutdown_event.is_set():
            if self.jugadores_espera.qsize() >= 2:
                partida = MainFourInLine()
                evento_partida = threading.Event()
                colas_partida = []
                eventos = []
                nombres = []
                
                for x in range(2):
                    jugador = self.jugadores_espera.get()
                    colas_partida.append(jugador[0])
                    eventos.append(jugador[1])
                    nombres.append(jugador[2])  

                partida_thread = threading.Thread(target=partida.run, args=(colas_partida, eventos, evento_partida,nombres,self.lock,self.parent_conn))
                partida_thread.start()


    def managment_client(self, client_socket, client_address, evento, cola_partida, verificado, usuario_nombre):
        print(f"Conexión aceptada de {client_address}")
        try:
            mensaje = "Bienvenido al 4 en línea\n"
            client_socket.sendall(mensaje.encode())

            if verificado == False:
                usuario_nombre, self.jugadores_online = autenticar_jugador(client_socket, self.jugadores_online)
                with self.lock:
                    self.parent_conn.send(f"{usuario_nombre} se ha conectado.")
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
                    with self.lock:
                        self.parent_conn.send(f"{usuario_nombre} se ha desconectado.")
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
        datos = [cola_partida, evento, usuario_nombre]
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
        ipv4_thread = threading.Thread(target=self.create_and_run_socket, args=(socket.AF_INET,))
        ipv6_thread = threading.Thread(target=self.create_and_run_socket, args=(socket.AF_INET6,))
        administracion_partidas_thread = threading.Thread(target=self.managment_games)
        
        ipv4_thread.start()
        ipv6_thread.start()
        administracion_partidas_thread.start()

        ipv4_thread.join()
        ipv6_thread.join()
    
    def create_and_run_socket(self, family):
        try:
            addr_info = socket.getaddrinfo(None, self.TCP_Port, family, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
            for addr in addr_info:
                family, socktype, proto, canonname, sockaddr = addr
                try:
                    server_socket = socket.socket(family, socktype, proto)
                    self.sockets.append(server_socket)
                    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    if family == socket.AF_INET6:
                        ip_version = "IPv6"
                        server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                    else:    
                        ip_version = "IPv4"
                    server_socket.bind(sockaddr)
                    server_socket.listen(7)
        
                    ip, port = sockaddr[:2]
                    print(f"Servidor escuchando en {ip_version} {ip}:{port}")
                except socket.error as e:
                    print(f"Error al iniciar el socket {ip_version} en {ip}:{port}. {e}")
                    continue
                    
                server_socket.settimeout(1.0)
                while not self.shutdown_event.is_set():
                    try:
                        client_socket, client_address = server_socket.accept()
                        print(f"Conexión aceptada de {client_address}")

                        evento = threading.Event()
                        cola_partida = Queue()
                        verificado = False

                        client_thread = threading.Thread(target=self.managment_client, args=(client_socket, client_address, evento, cola_partida, verificado, None))
                        client_thread.start()
                    except socket.timeout:
                        continue
                server_socket.close()

        except socket.error as e:
            print(f"Error al iniciar el servidor: {e}")


    def signal_handler(self,sig, frame):
        print("Señal de terminación recibida. Cerrando el servidor...")
        self.shutdown_event.set()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Servidor 4 en línea')
    parser.add_argument('-P', '--port', type=int, help='Puerto de escucha', default=1231)
    args = parser.parse_args()
    
    port = args.port

    parent_conn, child_conn = Pipe()

    registro = Process(target=generador_registros, args=(child_conn,))
    registro.start()

    servidor = Servidor(port, parent_conn)

    signal.signal(signal.SIGINT, servidor.signal_handler)
    signal.signal(signal.SIGTERM, servidor.signal_handler)

    servidor.start_server()

    registro.join()





