from logicFourInLine import FourInLine, FullColumn
import queue

class MainFourInLine:
    def __init__(self):
        self.game = FourInLine()
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


    def run(self, colas_partida, eventos, evento_partida, nombres, lock, parent_conn):
        with lock:
            parent_conn.send("Partida iniciada entre " + nombres[0] + " y " + nombres[1] + ".")
        for x in range(2):
            colas_partida[x].put(evento_partida)
            
        while self.running:
            turno = int(self.game.turn)
                    
            self.show_turn(colas_partida, turno)            
            
            for x in range(2):
                eventos[x].set()

            self.insert_token(colas_partida, eventos, turno, evento_partida)

            if self.game.winner():
                self.show_winner(colas_partida,eventos,turno)        

            if self.game.empate():
                self.show_empate(colas_partida,eventos,turno)
        
        with lock:
            parent_conn.send("Partida finalizada entre " + nombres[0] + " y " + nombres[1] + ".")

    def show_winner(self,colas_partida,eventos,turno):
        self.game.change_turn()

        for x in range(2):
            colas_partida[x].put("ganador/empate")

        for x in range(2):
            if x == int(self.game.turn):
                colas_partida[x].put("-------Ganaste-------\n")
            else:
                colas_partida[x].put("-------Perdiste-------\n")

        for x in range(2):
            self.board(colas_partida[x])
            if x != turno:
                eventos[x].set()

        self.running = False

    def show_empate(self,colas_partida,eventos,turno):
        for x in range(2):
            colas_partida[x].put("ganador/empate")

        for x in range(2):
            colas_partida[x].put("-------Empate-------\n")

        for x in range(2):
            self.board(colas_partida[x])

        self.running = False

    def show_turn(self, colas_partida, turno):
        for x in range(2):
            if x == turno:
                colas_partida[x].put("turno")
            else:
                colas_partida[x].put("no turno")
                    
        for x in range(2):
            self.board(colas_partida[x])

        turno_message = f"*Turno del jugador {turno} --> En qué columna quieres insertar la ficha: "
        colas_partida[turno].put(turno_message)

    def insert_token(self, colas_partida, eventos, turno, evento_partida):
        while True:
            evento_partida.wait(timeout=30)
                        
            try:    
                col = colas_partida[turno].get(timeout=0)
            except queue.Empty:
                self.show_winner_disconnection(colas_partida, eventos, turno)
                break

            col = int(col)-1
            evento_partida.clear()
            try:
                self.game.insert_token(col)
                colas_partida[turno].put("Ingresado")
                eventos[turno].set()
                break
            except FullColumn:
                colas_partida[turno].put("NoIngresado")
                error_FullColumn = "\n-------Columna llena-------\n*Ingrese una columna nuevamente\n"
                colas_partida[turno].put(error_FullColumn)
                eventos[turno].set()

    def show_winner_disconnection(self, colas_partida, eventos, turno):
        colas_partida[1 - turno].put("ganador/empate")
        colas_partida[1 - turno].put("-------Ganaste-------\n")
        self.board(colas_partida[1 - turno])
        eventos[1 - turno].set()
        self.running = False