import re
from board import Board

def play(FEN):
    board = Board(FEN)
    cmd = ["HELP", "FEN", "STR", "GET"]
    status = "ERROR"  # if it's not updated there is an error
    # playercolor, oppcolor = get_colors()  # for when engine is added
    gamecolor = 'White' if board.tomove.startswith('w') else 'Black'

    print(f'{gamecolor} to move.')

    # i think it looks nicer than True
    while 1:
        try:
            move = input(f"{gamecolor}'s move: ").strip().lower()
            if move.upper() in cmd:
                parse_command(move, board)
                continue
            if 'quit' in move: quit()

            status = board.read_move(move, gamecolor)
            gamecolor = opposite_color(gamecolor)
        except AssertionError as e:
            print(e)

    if not status == "ERROR":
        print(f'{status}!\nPlay again? y/n')
        if 'y' in input().lower():
            play(FEN)

def get_colors():
    print('White or Black? ')
    playercolor = input().lower()

    while not 'w' in playercolor or 'b' in playercolor:
        print('White or Black? ')
        playercolor = input()

    if 'w' in playercolor:
        return ('White', 'Black')
    elif 'b' in playercolor:
        return ('Black', 'White')

def opposite_color(color):
    return 'Black' if color.lower().startswith('w') else 'White'

def parse_command(cmd, board):
    commands = {
        "HELP": 'helpstring',
        "FEN": board.get_FEN(),
        "STR": board.gamestring,
        #"SET": input('Enter FEN: ')  # along these lines
        #"GET": board.all_moves_on_board,  # for testing
    }

    cmd = cmd.upper().strip()
    print(commands.get(cmd, None))

def prompt_FEN():
    FEN = """rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"""

    print('Begin from FEN? y/n')
    if input().startswith('y'):
        FEN = input('Enter FEN or type quit to use default: ').strip()
        valid = validate_FEN(FEN)

        while not valid == 'VALID':
            print(valid)
            FEN = input('Enter valid FEN or type n to use default: ')

            if 'quit' in FEN:
                FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                break

            valid = validate_FEN(FEN)

    if(len(FEN.split(' '))) == 1:
        FEN += ' w - - 0 1'

    return FEN

def validate_FEN(FEN):
    if not FEN.count('/') == 7: return 'Invalid Body Format'

    FEN = FEN.split(' ')
    main = FEN[0].split('/')
    # also implicitly fails length 0
    if list(filter(lambda z: not bool(re.match('\A[pnbrqkPNBRQK/1-9]+\Z', z)), FEN[0])): return 'Invalid Main Segment'
    total_squares = 0
    total_pieces = 0
    for c in FEN[0]:
        if c.isdigit():
            total_squares += int(c)
        elif not c == '/':
            total_pieces += 1
    print(total_squares + total_pieces)
    print(total_pieces)
    if not total_squares + total_pieces == 64: return 'Invalid Empty Square Count'

    if len(FEN) == 1:
        return 'VALID'

    if not len(FEN) == 6: return 'Invalid Segment Count'
    if len(FEN[1]) > 1 or not bool(re.match('^[WBwb]+', FEN[1])): return 'Invalid Tomove Segment'
    if not FEN[2] == '-':
        if len(FEN[2]) > 4 or not bool(re.match('^[KQkq]+$', FEN[2])): return 'Invalid Castling Segment'
    if not FEN[3] == '-':
        if not len(FEN[3]) == 2 or not FEN[3][0] in 'abcdefgh' or \
                not FEN[3][1] in '123456789': return 'Invalid En Passant Segment'
    if not FEN[4].isdigit() or int(FEN[4]) < 0: return 'Invalid Halfmove Segment'
    if not FEN[5].isdigit() or int(FEN[4]) < 0: return 'Invalid Fullmove Segment'
    # except:
    #     return 'Invalid FEN'

    return 'VALID'


print('Type start to begin.', end='\n\n')

while not 'start' in input().lower():
    if input() == quit: quit()
play(prompt_FEN())

# board = Board('r1bq1b1r/2p1k1pp/2Bp4/p3Pp2/4n1Q1/2N5/PPP2PPP/R1B1K2R w KQ - 1 11')
# tottime = 0
# cycles = 20000
# rounds = 100
# print(f'Running {cycles} cycles for {rounds} rounds')
# print(f'Input FEN: {board.get_FEN()}')
# for n in range(rounds):
#     t = time() * 1000
#     for m in range(cycles):
#         board.all_moves_on_board()
#     elap = time()*1000 - t
#     tottime += elap
#     print(f'Round {n+1} runtime: {elap} ms')
# print(f'Average runtime: {tottime/100} ms')