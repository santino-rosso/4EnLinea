from Data_Base import Session,Usuario
from passwordHash import HashPassword

def autenticar_jugador(client_socket, jugadores_online):
    client_socket.sendall("*1. Iniciar sesión\n*2. Registrarse\nElija una opción: ".encode())
    opcion = client_socket.recv(1024).decode().strip()
    session = Session()
    if opcion == "1":
        client_socket.sendall("*Ingrese su usuario: ".encode())
        usuario_nombre = client_socket.recv(1024).decode().strip()
        client_socket.sendall("*Ingrese su contraseña: ".encode())
        contrasena = client_socket.recv(1024).decode().strip()
        usuario = session.query(Usuario).filter_by(username=usuario_nombre).first()
        if usuario!=None and usuario.username in jugadores_online:
            client_socket.sendall("El usuario ya está en línea. Intente nuevamente.\n".encode())
            return autenticar_jugador(client_socket, jugadores_online)
        if usuario!=None and HashPassword.verify_password(usuario.password_hash, contrasena):
            client_socket.sendall("Inicio de sesión exitoso!\n".encode())
            jugadores_online.append(usuario_nombre)
            return usuario_nombre, jugadores_online
        else:
            client_socket.sendall("Usuario o contraseña incorrectos.\n".encode())
            return autenticar_jugador(client_socket, jugadores_online)

    elif opcion == "2":
        client_socket.sendall("*Ingrese un nuevo usuario: ".encode())
        nuevo_usuario_nombre = client_socket.recv(1024).decode().strip()
        client_socket.sendall("*Ingrese una nueva contraseña: ".encode())
        nueva_contrasena = client_socket.recv(1024).decode().strip()
            
        usuario_existente = session.query(Usuario).filter_by(username=nuevo_usuario_nombre).first()

        if usuario_existente!=None:
            client_socket.sendall("El usuario ya existe. Intente nuevamente.\n".encode())
            return autenticar_jugador(client_socket, jugadores_online)
        else:
            hash = HashPassword.hash_password(nueva_contrasena)
            nuevo_usuario = Usuario(username=nuevo_usuario_nombre, password_hash=hash)
            session.add(nuevo_usuario)
            try:
                session.commit()
                client_socket.sendall("Registro exitoso!\n".encode())
            except Exception as e:
                print(f"Error al hacer commit: {e}")
                session.rollback()
            finally:
                session.close()
            return autenticar_jugador(client_socket, jugadores_online)
    else:
        client_socket.sendall("Opción no válida. Intente nuevamente.\n".encode())
        return autenticar_jugador(client_socket, jugadores_online)