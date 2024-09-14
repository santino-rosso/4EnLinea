from datetime import datetime

def generador_registros(cola):
    try:
        with open(f"logs.txt", "a") as file:
            while True:
                try:    
                    mensaje = cola.get()
                    if mensaje == "terminar":
                        break
                    hora = datetime.now().strftime("%H:%M:%S")
                    fecha = datetime.now().strftime("%Y-%m-%d")
                    file.write(f"[{fecha}] - [{hora}] - {mensaje}\n")
                except KeyboardInterrupt:
                    continue
    except IOError as e:
        print(f"Error al escribir en el archivo: {e}.")
    finally:
        print("Proceso de registros finalizado.")

