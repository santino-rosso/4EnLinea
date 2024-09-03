from datetime import datetime

def generador_registros(child_conn):
    try:
        with open(f"logs.txt", "a") as file:
            while True:
                mensaje = child_conn.recv()
                hora = datetime.now().strftime("%H:%M:%S")
                fecha = datetime.now().strftime("%Y-%m-%d")
                file.write(f"[{fecha}] - [{hora}] - {mensaje}\n")
    except IOError as e:
        print(f"Error al escribir en el archivo: {e}.")
    except KeyboardInterrupt:
        print("Proceso de registros interrumpido.")
    finally:
        child_conn.close()
        print("Proceso de registros finalizado.")

