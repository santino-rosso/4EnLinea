from Data_Base import Session,Usuario

def mostrar_estadisticas(client_socket, usuario_nombre):
    session = Session()
    usuario = session.query(Usuario).filter_by(username=usuario_nombre).first()
    if usuario!=None:
        stats = (f"Estadísticas de {usuario_nombre}:\n"f"Partidas ganadas: {usuario.partidas_ganadas}\n"f"Partidas perdidas: {usuario.partidas_perdidas}\n"f"Partidas empatadas: {usuario.partidas_empatadas}\n")
        client_socket.sendall(stats.encode())
    else:
        client_socket.sendall("Usuario no encontrado.\n".encode())
    session.close()

def update_statistics(mensajeGanEmp, usuario_nombre):
    session = Session()
    usuario = session.query(Usuario).filter_by(username=usuario_nombre).first()
    if usuario:
        if mensajeGanEmp.strip() == "-------Ganaste-------":
            usuario.partidas_ganadas += 1
        elif mensajeGanEmp.strip() == "-------Perdiste-------":
            usuario.partidas_perdidas += 1
        elif mensajeGanEmp.strip() == "-------Empate-------":
            usuario.partidas_empatadas += 1 
        try:
            session.commit()
        except Exception as e:
            print(f"Error al hacer commit: {e}")
            session.rollback()
        finally:
            session.close()
    else:
        print("Usuario no encontrado.")