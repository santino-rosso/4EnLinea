from datetime import datetime
import os

def generador_reportes (child_conn):
    try:
        with open(f"report_conexiones.txt", "a") as file:
            while True:
                mensaje = child_conn.recv()
                if mensaje == "FIN":
                    break
                nueva_fecha = datetime.now().strftime("%Y-%m-%d")
                if verificar_fecha(nueva_fecha) == False:
                    fecha_actual = nueva_fecha
                    file.write(f"\n\nFecha: {fecha_actual}\n")
                file.write(f"{mensaje}\n")
    except KeyboardInterrupt:
        print("Proceso de reporte interrumpido.")
    finally:
        child_conn.close()
        print("Proceso de reporte finalizado.")

def verificar_fecha (fecha_actual):
    if os.path.exists("report_conexiones.txt"):
        with open("report_conexiones.txt", "r") as file:
            contenido = file.read()
            if fecha_actual not in contenido:
                return False
            else:
                return True