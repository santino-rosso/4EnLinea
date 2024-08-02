class FullColumn(Exception):
    pass


class CuatroInLine:

    def __init__(self):
        self.board=[[" " for column in range(8)] for row in range(8)]
        self.turn = "0"

    def change_turn(self):
        if self.turn == "0":
            self.turn = "1"
        else:
            self.turn = "0"

    def insert_token(self,col):
        if self.board[0][col] != " ":
            raise FullColumn()
        self.row = self.calculate_row(col)
        self.board[self.row][col] = self.turn
        self.winner()
        self.empate()
        self.change_turn()

    def calculate_row(self,col):
        row = 7
        for i in range(8):
            if self.board[row - i][col] == " ":
                break
        return row - i

    def winner(self):
        for row in range(8):
            for col in range(8):
                if self.verify_horizontal(row,col) or self.verify_vertical(row,col) or self.verify_diagonal_up(row,col) or self.verify_diagonal_down(row,col):
                    return True
        return False

    def verify_horizontal(self,row,col):            
        token = self.board[row][col]
        if token == " ":
            return False
        for delta_col in range(4):
            if col + delta_col > 7:
                return False
            if self.board[row][col + delta_col] != token:
                return False
        return True

    def verify_vertical(self,row,col):
        token = self.board[row][col]
        if token == " ":
            return False
        for delta_row in range(4):
            if row + delta_row > 7:
                return False
            if self.board[row + delta_row][col] != token:
                return False
        return True

    def verify_diagonal_up(self,row,col):
        token = self.board[row][col]
        if token == " ":
            return False
        for delta in range(4):
            if row - delta < 0 or col + delta > 7:
                return False
            if self.board[row - delta][col + delta] != token:
                return False
        return True

    def verify_diagonal_down(self,row,col):
        token = self.board[row][col]
        if token == " ":
            return False
        for delta in range(4):
            if row + delta > 7 or col + delta > 7:
                return False
            if self.board[row + delta][col + delta] != token:
                return False
        return True

    def empate(self):
        if not self.winner():
            for x in range(8):
                if self.board[0][x] == " ":
                    return False
            return True
        return False