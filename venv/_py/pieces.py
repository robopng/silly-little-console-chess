# class Piece as parent classes for Pieces
from math import floor

class Piece:
    """Create a chess piece. Utilize board math to check and perform legal moves.

        # 8 [00] [01] [02] [03] [04] [05] [06] [07]
        # 7 [08] [09] [10] [11] [12] [13] [14] [15]
        # 6 [16] [17] [18] [19] [20] [21] [22] [23]
        # 5 [24] [25] [26] [27] [28] [29] [30] [31]
        # 4 [32] [33] [34] [35] [36] [37] [38] [39]
        # 3 [40] [41] [42] [43] [44] [45] [46] [47]
        # 2 [48] [49] [50] [51] [52] [53] [54] [55]
        # 1 [56] [57] [58] [59] [60] [61] [62] [63]
        #    a    b    c    d    e    f    g    h
    """

    def __init__(self, pos, color):
        self.pos = pos
        self.color = color[0].lower()  # 'black' and 'white' or 'b' and 'w' or such

    def get_legal_moves(self, board):
        """Return a list of all legal moves. """

        return []

    def move(self, board, newpos):
        """Update piece position if requested move is within set of legal moves. """

        legal_moves = self.get_legal_moves(board)

        if newpos in legal_moves:
            old = self.pos
            self.pos = newpos
            return (old, self.pos)

        return None


class Pawn(Piece):
    def __init__(self, pos, color, hasmoved=False, passant=False):
        self.name = 'Pawn'
        self.pos = pos
        self.value = 1
        self.passant = passant

        # used to prevent duplication of code later down the line. this is only necessary in pawns
        # white pawns always decrease index - positive; black pawns increase - negative
        if color.lower().startswith('w'):
            self.tag = 'P'
            self.forwardoffsets = (8, 16)  # first handles normal move, second handles first move double move
            self.passantoffsets = (7, 9)  # first handles right diagonal, second handles left diagonal
            self.hasmoved = True if self.pos not in range(48, 56) else False # any pawn not on home row must have moved
        else:
            self.tag = 'p'
            self.forwardoffsets = (-8, -16)
            self.passantoffsets = (-7, -9)
            self.hasmoved = True if self.pos not in range(8, 16) else False

        super().__init__(pos, color)

    # pawns are tricky because their moves are unique depending on color so this method is very large
    # to handle that
    def get_legal_moves(self, board):
        legal_moves = []

        # handles positions of pawn in event of their respective moves
        pos_doub = self.pos - self.forwardoffsets[1]
        pos_norm = self.pos - self.forwardoffsets[0]
        pos_leftpassant = self.pos - self.passantoffsets[1]
        pos_rightpassant = self.pos - self.passantoffsets[0]

        # first move double move - guaranteed will never hit edge of board so no need to check
        if not self.hasmoved and not isinstance(board[pos_doub], Piece) and not isinstance(board[pos_norm], Piece):
            legal_moves.append(pos_doub)

        # normal move - promotion handled by board
        if pos_norm >= 0 and not isinstance(board[pos_norm], Piece):
            legal_moves.append(pos_norm)

        # en passant
        if self.passant:
            if isinstance(board[self.pos+1], Piece):
                legal_moves.append(pos_rightpassant)
            if isinstance(board[self.pos-1], Piece):
                legal_moves.append(pos_leftpassant)

        return legal_moves

class Knight(Piece):
    def __init__(self, pos, color):
        self.name = 'Knight'
        self.value = 3
        self.tag = 'N' if color.startswith('w') else 'n'

        super().__init__(pos, color)

    def get_legal_moves(self, board):
        legal_moves = []

        # upper right, bottom right, upper left, bottom left in that order
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, 15, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, -17, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, 17, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, -15, board))

        return legal_moves

    @staticmethod
    def legal_moves_helper(color, pos, offset, board):
        legal_moves = []
        pos -= offset

        # utilize the knowledge that a jump across the "edge" of the board will always end up on the wrong row
        if pos >= 0 and pos <= 63 and (abs(floor((pos+offset)/8) - floor(pos/8)) == 2):
            if not isinstance(board[pos], Piece) or board[pos].color != color:
                legal_moves.append(pos)

        return legal_moves

class Bishop(Piece):
    def __init__(self, pos, color):
        self.name = 'Bishop'
        self.value = 3
        self.tag = 'B' if color.startswith('w') else 'b'

        super().__init__(pos, color)

    def get_legal_moves(self, board):
        legal_moves = []

        # upper right, bottom right, upper left, bottom left in that order
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, 7, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, -9, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, 9, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, -7, board))

        return legal_moves

    @staticmethod
    def legal_moves_helper(color, pos, offset, board):
        legal_moves = []
        pos -= offset

        # same as in Knight- over edge moves end up on wrong row
        while(pos <= 63 and pos >= 0 and (abs(floor((pos+offset)/8) - floor((pos)/8)) == 1)):
            if not isinstance(board[pos], Piece):
                legal_moves.append(pos)
                pos -= offset
                continue
            elif board[pos].color != color:
                legal_moves.append(pos)
            break

        return legal_moves

class Rook(Piece):
    def __init__(self, pos, color):
        self.name = 'Rook'
        self.value = 1
        self.tag = 'R' if color.startswith('w') else 'r'

        super().__init__(pos, color)

    def get_legal_moves(self, board):
        legal_moves = []

        # left, right, down, up in that order
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, 1, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, -1, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, 8, board))
        legal_moves.extend(self.legal_moves_helper(self.color, self.pos, -8, board))

        return legal_moves

    @staticmethod
    def legal_moves_helper(color, pos, offset, board):
        legal_moves = []
        pos -= offset
        # i don't like this solution but i like it more than two methods
        if abs(offset ) == 1: leftbound = (pos+offset) - ((pos+offset)%8) - 1  # leftbound from original position
        else: leftbound = pos - pos%8 - 1  # bound doesn't matter so set it from current position to avoid errors

        while pos >= 0 and pos <= 63 and pos > leftbound and pos < (leftbound + 9):
            if not isinstance(board[pos], Piece):
                legal_moves.append(pos)

                pos -= offset
                leftbound = pos - (pos % 8) - 1 if abs(offset) == 8 else leftbound  # update only for vertical movement

                continue
            elif board[pos].color != color:
                legal_moves.append(pos)
            break

        return legal_moves

class Queen(Piece):
    def __init__(self, pos, color):
        self.name = 'Queen'
        self.value = 1
        self.tag = 'Q' if color.startswith('w') else 'q'

        super().__init__(pos, color)

    def get_legal_moves(self, board):
        legal_moves = []

        # gee Queen, you get *eight* method calls?
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, 7, board))
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, -9, board))
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, 9, board))
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, -7, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, 1, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, -1, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, 8, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, -8, board))

        return legal_moves

    @staticmethod
    def legal_moves_helper_bishop(color, pos, offset, board):
        # this method copied directly from Bishop class
        legal_moves = []
        pos -= offset

        # same as in Knight- over edge moves end up on wrong row
        while pos <= 63 and pos >= 0 and (abs(floor((pos+offset)/8) - floor(pos/8)) == 1):
            if not isinstance(board[pos], Piece):
                legal_moves.append(pos)
                pos -= offset
                continue
            elif board[pos].color != color:
                legal_moves.append(pos)
            break

        return legal_moves

    @staticmethod
    def legal_moves_helper_rook(color, pos, offset, board):
        # this method copied directly from Rook class
        legal_moves = []
        pos -= offset
        # i don't like this solution but i like it more than two methods
        if abs(offset ) == 1: leftbound = (pos+offset) - ((pos+offset)%8) - 1  # leftbound from original position
        else: leftbound = pos - pos%8 - 1  # bound doesn't matter so set it from current position to avoid errors

        while pos >= 0 and pos <= 63 and pos >= leftbound and pos <= (leftbound + 7):
            if not isinstance(board[pos], Piece):
                legal_moves.append(pos)

                pos -= offset
                leftbound = pos - (pos % 8)  # update to not break vertical movement

                continue
            elif board[pos].color != color:
                legal_moves.append(pos)
            break

        return legal_moves

class King(Piece):
    def __init__(self, pos, color):
        self.name = 'King'
        self.value = 1
        self.tag = 'K' if color.startswith('w') else 'k'
        self.castleking = False  # standard is default false
        self.castlequeen = False  #

        super().__init__(pos, color)

    def update_castle_rights(self, rights):
        """Update a King's castling rights using a rights string from a FEN. """
        if rights == '-':
            self.castleking = False
            self.castlequeen = False
        if self.tag in rights:
            self.castleking = True
        if chr(ord(self.tag) + 6) in rights:  # convert to q or Q
            self.castlequeen = True

    def get_legal_moves(self, board):
        legal_moves = []

        # gee ~~Queen~~ King, you get *eight* method calls?
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, 7, board))
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, -9, board))
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, 9, board))
        legal_moves.extend(self.legal_moves_helper_bishop(self.color, self.pos, -7, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, 1, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, -1, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, 8, board))
        legal_moves.extend(self.legal_moves_helper_rook(self.color, self.pos, -8, board))

        # done this way for readability - can alternatively be done as any(filter(lambda)) for speed
        if self.castleking and not any(isinstance(board[self.pos+n], Piece) for n in range(1,3)):
            if isinstance(board[self.pos+3], Rook):
                legal_moves.append(self.pos+2)
        if self.castlequeen and not any(isinstance(board[self.pos-n], Piece) for n in range(1,4)):
            if isinstance(board[self.pos-4], Rook):
                legal_moves.append(self.pos-2)

        return legal_moves

    @staticmethod
    def legal_moves_helper_bishop(color, pos, offset, board):
        # copied directly from Bishop class and changed to have one square move limit
        legal_moves = []
        pos -= offset

        if pos <= 63 and pos >= 0 and (pos % 8) != 0 and (abs(floor((pos + offset) / 8) - floor(pos / 8)) == 1):
            if not isinstance(board[pos], Piece) or board[pos].color != color:
                legal_moves.append(pos)

        return legal_moves

    @staticmethod
    def legal_moves_helper_rook(color, pos, offset, board):
        # copied directly from Rook class and changed to have one square move limit
        legal_moves = []
        pos -= offset
        # i don't like this solution but i like it more than two methods
        if abs(offset ) == 1: leftbound = (pos+offset) - ((pos+offset)%8) - 1  # leftbound from original position
        else: leftbound = pos - pos%8 - 1  # bound doesn't matter so set it from current position to avoid errors

        if pos > leftbound and pos < (leftbound + 7):
            if pos <= 63 and pos >= 0 and (not isinstance(board[pos], Piece) or board[pos].color != color):
                legal_moves.append(pos)

        return legal_moves