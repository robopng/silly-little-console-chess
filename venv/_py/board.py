# Board class controls board layout, where pieces are on board
from pieces import *
from math import copysign

class Board:
    """Create an 8x8 chessboard and control inputs and outputs.

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

    def __init__(self, FEN=None):
        self.board = self.checker([None for n in range(64)])
        self.gamestring = ''

        # all used for FEN strings and rule calculations
        self.halfmoves = 0
        self.fullmoves = 1
        self.passant = '-'
        self.castle = 'KQkq'
        self.tomove = 'w'

        if FEN:
            self.read_FEN(FEN)

    @property
    def all_moves_on_board(self):
        """Get every legal move on the board. """
        # this method for testing purposes only!
        # profile
        # 6    0.000    0.000    0.031    0.005 board.py:117(all_moves_on_board)
        # cprofile
        # 6    0.000    0.000    0.002    0.000 board.py:117(all_moves_on_board)
        # generally, calling this method 20,000 times takes around 0.5 to 0.6 seconds

        from time import time_ns, sleep

        moves = []
        for n in range(64):
            if isinstance(self.board[n], Piece):
                moves.append((self.board[n], self.board[n].pos, self.board[n].get_legal_moves(self.board)))
        return moves

    def read_move(self, move, color):
        """Read a user inputted move, in custom program format. """
        # in format "mov a1 a2": move piece at a1 square to a2
        move = move.split(' ')
        origin = self.get_pos(move[1])
        to = self.get_pos(move[2])

        assert isinstance(self.board[origin], Piece), 'Not a piece!'
        assert color.lower().startswith(self.board[origin].color), 'Wrong color piece!'
        assert self.board[origin].move(self.board, to), 'Illegal move!'

        status = self.register_move((origin, to))
        self.print_board(self.board)
        print(f'Moved {self.board[to].name} to {self.reverse_pos(to)}')
        return status

    def register_move(self, move):
        """Register a certain input move and process its consequences. """
        # deal with win/lose/draw conditions before anything else
        if self.halfmoves == 50: return "DRAW"
        # if either player has no legal moves: return "DRAW"
        # if enemy king has no moves and is in check: return "WIN"
        # if your king has no moves and is in check: return "LOSE"

        self.passant = '-'
        self.halfmoves = 0 if isinstance(self.board[move[1]], Piece) else self.halfmoves + 1
        if self.tomove == 'b':
            self.gamestring += f'Black: {self.board[move[0]].name} to {self.reverse_pos(move[1])}\n'
            self.tomove = 'w'
            self.fullmoves += 1
        else:
            self.gamestring += f'{self.fullmoves}:  White: {self.board[move[0]].name} to {self.reverse_pos(move[1])}, '
            self.tomove = 'b'

        self.board[move[1]], self.board[move[0]] = self.board[move[0]], 0

        offset = move[1] - move[0]
        if isinstance(self.board[move[1]], Pawn): self.register_move_pawn(move, offset)
        elif isinstance(self.board[move[1]], King): self.register_move_king(move, offset)

        return "CONTINUE"

    def register_move_pawn(self, move, offset):
        """Aid the register_move function concerning special Pawn move cases. """
        # no more double moves :^(
        self.board[move[1]].hasmoved = True
        self.halfmoves = 0
        # passant offset is always odd because it's a diagonal move
        if offset % 2 == 1:
            self.board[move[1]].passant = False

            # copied from update_passant
            captured = ((8 - int(self.passant[1])) * 8) + (ord(self.passant[0]) - 97)
            captured -= int(copysign(8, offset))  # going back up/down
            self.board[captured] = 0

            # just need to check and make sure, for that one edge case where two pawns can passant
            if isinstance(self.board[captured + 1], Pawn): self.board[captured + 1].passant = False
            if isinstance(self.board[captured - 1], Pawn): self.board[captured - 1].passant = False
        elif floor(move[1] / 8) == 0:
            # make this prompt the user later on
            self.board[move[1]] == Queen(move[1], self.board[move[1]].color)

    def register_move_king(self, move, offset):
        """Aid the register_move function concern special King move cases. """
        tag = self.board[move[1]].tag

        self.castle = self.castle.replace(tag, '')
        self.castle = self.castle.replace(chr(ord(tag) + 6), '')
        self.board[move[1]].update_castle_rights(self.castle)

        # kingside else queenside
        if offset == 2:
            rook_to, rook_at = move[1] - 1, move[1] + 1
        else:
            rook_to, rook_at = move[1] + 1, move[1] - 2
        self.board[rook_to], self.board[rook_at] = self.board[rook_at], 0

    def update_passant(self):
        """Update en passant conditions for any pawns near the target square."""
        if self.passant == '-': return

        target = self.get_pos(self.passant)

        # yuck!
        if target > 23:
            if isinstance(self.board[target-9], Pawn) and (target+1) % 8 != 0:
                self.board[target-9].passant = True
            if isinstance(self.board[target-7], Pawn) and target % 8 != 0:
                self.board[target-7].passant = True
        else:
            if isinstance(self.board[target+7], Pawn) and (target+1) % 8 != 0:
                self.board[target+7].passant = True
            if isinstance(self.board[target+9], Pawn) and target % 8 != 0:
                self.board[target+9].passant = True

    def read_FEN(self, FEN):
        """Take an input FEN string and convert the board to that position. """

        # laying pieces down
        index = 0
        for n in FEN:
            if n.isdigit():
                index += int(n)
                continue
            elif n.isalnum():
                color = 'b' if n.lower() == n else 'w'

                # done like this to avoid even more conditional logic
                lookup = {
                    "P": Pawn(index, color),
                    "N": Knight(index, color),
                    "B": Bishop(index, color),
                    "R": Rook(index, color),
                    "Q": Queen(index, color),
                    "K": King(index, color)
                }

                self.board[index] = lookup[n.upper()]
                index += 1
                continue
            elif n == '/':
                continue
            break

        args = FEN.split(' ')
        # first arg already handled
        self.tomove = args[1]
        self.castle = args[2]
        self.passant = args[3]
        self.halfmoves = int(args[4])
        self.fullmoves = int(args[5])

        self.update_passant()
        [self.board[n].update_castle_rights(self.castle) for n in range(64) if isinstance(self.board[n], King)]

        self.print_board(self.board)  # for startup purposes- see main.py

    def get_FEN(self):
        """Return a FEN string created from board at time of call. """

        FEN = ""
        passed_squares = 0
        for n in range(64):
            if isinstance(self.board[n], Piece):
                # dump int down for passed squares before adding piece tag i.e. n3b1p
                if passed_squares != 0:
                    FEN += str(passed_squares)
                    passed_squares = 0

                FEN += self.board[n].tag
            else:
                passed_squares += 1

            # not statement is too hard to read. leave it like this
            if (n+1) % 8 == 0:
                # dump int down for passed squares to prevent something like .../32/...
                if passed_squares != 0:
                    FEN += str(passed_squares)
                    passed_squares = 0

                FEN += "/"

        FEN = FEN[:-1]  # too lazy to fix this naturally- there is a trailing /
        FEN += " " + self.tomove + " "
        FEN += self.castle + " "
        FEN += self.passant + " "
        FEN += str(self.halfmoves) + " "
        FEN += str(self.fullmoves)
        return FEN

    @staticmethod
    def checker(board):
        """Checker the board. """
        for n in range(8):
            for m in range(8):
                if isinstance(board[(n*8) + m], Piece): continue
                board[(n*8) + m] = (n+m) % 2
        return board

    @staticmethod
    def print_board(board):
        """Print the board with Pieces as tags. """
        print('\n' * 100)

        board = Board.checker(board)  # just in case any captures have messed it up

        for n in range(8):
            printout = []
            for m in range(8):
                if isinstance(board[(n*8) + m], Piece):
                    printout.append(board[(n*8) + m].tag)
                else:
                    printout.append(str(board[(n*8) + m]))  # str to make it same width as tags
            print(f'{8-n} {printout}')

        print('    ', end = '')
        for n in range(8):
            print(f'{chr(n+97)}    ', end = '')
        print()

    @staticmethod
    def get_pos(str):
        """Get the absolute list position from a given chess coordinate. """
        return ((8 - int(str[1])) * 8) + (ord(str[0]) - 97)

    @staticmethod
    def reverse_pos(pos):
        """Get a chess coordinate from a given absolute position. """
        num = 8 - int(floor(pos/8))  # 1-8
        char = chr((pos - (8 * (8 - num))) + 97)  # a-h
        return f'{char}{num}'
    