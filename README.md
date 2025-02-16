# 4 en Línea Multijugador

## Descripción
Este proyecto implementa un juego multijugador de 4 en línea. Los jugadores pueden conectarse al servidor, competir entre ellos y acceder a sus estadísticas de juego, vinculadas a sus perfiles personales.

## Arquitectura
El sistema está compuesto por tres componentes principales:

1. **Cliente**: Se encarga de la interacción del jugador con el servidor.
2. **Servidor**: Maneja las conexiones, partidas y almacenamiento de datos.
3. **Base de Datos**: Almacena los datos del juego y estadísticas de los jugadores.

### Tecnologías utilizadas
- **Cliente**:
  - Sockets
  - Argparse
- **Servidor**:
  - Threading
  - SQLAlchemy
  - IPv4 e IPv6
  - Queue
  - Sockets
  - Argparse
  - Multiprocesamiento
- **Base de Datos**:
  - SQLite

## Funcionalidades

### Cliente
- **Conexión con el Servidor**: Establece una conexión de socket con el servidor para enviar y recibir datos en tiempo real.

### Servidor
- **Gestión de Conexiones**: Acepta conexiones de múltiples clientes y maneja partidas simultáneas con hilos.
- **Visualización de Estadísticas**: Muestra estadísticas de los jugadores y partidas.
- **Interfaz de Usuario**: Proporciona una interfaz para la interacción con el juego.
- **Autenticación y Autorización**: Valida credenciales de los jugadores.
- **Manejo de Partidas**: Controla la lógica del juego y sincroniza el estado en tiempo real.
- **Consultas SQL**: Realiza operaciones en la base de datos para recuperar y actualizar información.
- **Manejo de Errores**: Captura excepciones como jugadas inválidas o errores de conexión.
- **Soporte para IPv4 e IPv6**: Permite conexiones de clientes en ambas versiones del protocolo.
- **Registro de Eventos**: Mantiene un registro de eventos importantes como conexiones y partidas finalizadas.
- **Timeout de Clientes**: Desconecta a clientes inactivos automáticamente.

### Base de Datos
- **Almacenamiento de Datos**: Guarda perfiles de jugadores, estadísticas y datos del juego.

## Instalación y Uso

### Requisitos
- Python
- SQLAlchemy
- SQLite

### Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/4-en-linea-multijugador.git
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución

#### Servidor
Para iniciar el servidor:
```bash
python servidor.py --host 0.0.0.0 --port 8080
```

#### Cliente
Para conectar un cliente al servidor:
```bash
python cliente.py --host 127.0.0.1 --port 8080
```
