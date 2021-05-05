class WebInterface:
    def __init__(self):
        self.inputlabel = ''
        self.btnlabel = 'Submit'
        self.errmsg = ''
        self.board = ''
        self.next_link = ''
        self.wname = 'White player'
        self.bname = 'Black player'
        self.winner = None
        self.info = None

class Cell:
    number = 0

    def __init__(self, text='', type=''):
        self.text = text
        if type != '':
            self.type = type
        else:
            self.type = 'black' if (Cell.number % 2 == 0) else 'white'
        Cell.number += 1

    def __repr__(self):
        return str(self.text) + str(self.type)


class MoveError(Exception):
    '''Custom error for invalid moves.'''
    pass

def vector(start, end):
    '''
    Return three values as a tuple:
    - x, the number of spaces moved horizontally,
    - y, the number of spaces moved vertically,
    - dist, the total number of spaces moved.
    
    positive integers indicate upward or rightward direction,
    negative integers indicate downward or leftward direction.
    dist is always positive.
    '''
    x = end[0] - start[0]
    y = end[1] - start[1]
    dist = abs(x) + abs(y)
    return x, y, dist

class BasePiece:
    def __init__(self, colour):
        if type(colour) != str:
            raise TypeError('colour argument must be str')
        elif colour.lower() not in {'white', 'black'}:
            raise ValueError('colour must be {white,black}')
        else:
            self.colour = colour
            self.moved = 0

    def __repr__(self):
        return f'BasePiece({repr(self.colour)})'

    def __str__(self):
        try:
            return f'{self.colour} {self.name}'
        except NameError:
            return f'{self.colour} piece'
    def symbol(self):
        return f'{self.sym1[self.colour]}'

    @staticmethod
    def vector(start, end):
        x = end[0] - start[0]
        y = end[1] - start[1]
        dist = abs(x) + abs(y)
        return x, y, dist


class King(BasePiece):
    name = 'king'
    sym1 = {'white': '♔', 'black': '♚'}

    def __repr__(self):
        return f'King({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        '''King can move 1 step horizontally or vertically.'''
        x, y, dist = self.vector(start, end)
        return dist == 1 or abs(x) == abs(y) == 1 


class Queen(BasePiece):
    name = 'queen'
    sym1 = {'white': '♕', 'black': '♛'}

    def __repr__(self):
        return f'Queen({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if (x != 0 and y != 0 and abs(x) == abs(y)) \
                or (x == 0 and y != 0) \
                or (y == 0 and x != 0):
            return True
        else:
            return False


class Bishop(BasePiece):
    name = 'bishop'
    sym1 = {'white': '♗', 'black': '♝'}

    def __repr__(self):
        return f'Bishop({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if x != 0 and y != 0 and abs(x) == abs(y):
            return True
        else:
            return False


class Knight(BasePiece):
    name = 'knight'
    sym1 = {'white': '♘', 'black': '♞'}

    def __repr__(self):
        return f'Knight({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple):
        x, y, dist = self.vector(start, end)
        if dist == 3 and 0 < abs(x) < 3 and 0 < abs(y) < 3:
            return True
        else:
            return False


class Rook(BasePiece):
    name = 'rook'
    sym1 = {'white': '♖', 'black': '♜'}

    def __repr__(self):
        return f'Rook({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple, **kwargs):
        x, y, dist = self.vector(start, end)
        if kwargs.get('castling', False):
            if self.colour == 'white':
                row = 0
            elif self.colour == 'black':
                row = 7
            if start[1] != end[1] != row:
                return False
            elif not((start[0] == 0 and end[0] == 3)
                     or (start[0] == 7 and end[0] == 5)):
                return False
            else:
                return True
        else:
            if (x == 0 and y != 0) or (y == 0 and x != 0):
                return True
            else:
                return False


class Pawn(BasePiece):
    name = 'pawn'
    sym1 = {'white': '♙', 'black': '♟︎'}

    def __repr__(self):
        return f'Pawn({repr(self.colour)})'

    def isvalid(self, start: tuple, end: tuple, **kwargs):
        x, y, dist = self.vector(start, end)
        capture = kwargs.get('capture', False)
        xmove = 1 if capture else 0
        if abs(x) == xmove == 1:
            if self.colour == 'black' and y == -1 \
                    or self.colour == 'white' and y == 1:
                return True
        elif x == xmove == 0:
            if self.colour == 'black':
                if start[1] != 6:
                    return (y == -1)
                else:
                    return (0 > y >= -2 and not capture)
            elif self.colour == 'white':
                if start[1] != 1:
                    return (y == 1)
                else:
                    return (0 < y <= 2 and not capture)
        return False


class Board:
    '''
    ATTRIBUTES

    turn <{'white', 'black'}>
        The current player's colour.

    winner <{'white', 'black', None}>
        The winner (if game has ended).
        If game has not ended, returns None

    checkmate <{'white', 'black', None}>
        Whether any player is checkmated.

    METHODS

    start()
        Start a game. White goes first.

    display()
        Print the game board.

    prompt(colour)
        Prompt the player for input.

    next_turn()
        Go on to the next player's turn.

    isvalid(start, end)
        Checks if the move (start -> end) is valid for this turn.

    update(start, end)
        Carries out the move (start -> end) and updates the board.
    '''

    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug', False)
        self._position = {}
        self.winner = None
        self.checkmate = None
        self.turn = 'white'

    def coords(self, colour=None):
        '''
        Return list of piece coordinates.
        Allows optional filtering by colour
        '''
        if colour == None:
            return list(self._position.keys())
        else:
            pieces_coords_list = list(self._position.keys())
            found_pieces_coord = []

            for coord in pieces_coords_list:
                piece = self.get_piece(coord)
                if piece.colour == colour:
                    found_pieces_coord.append(coord)
            return found_pieces_coord

    def pieces(self, colour=None):
        
        if colour == None:
            return list(self._position.values())
        else:
            pieces_list = []
            for coord in self.coords(colour=colour):
                piece = self.get_piece(coord)
                pieces_list.append(piece)
                return pieces_list

    def get_coords(self, colour, name):
        """
        Return a list of coords where piece colour and name match.
        Returns empty list if no such piece found.
        (Meant to be used in a for loop.)
        """
        found_piece_coord = []
        
        for coord in self.coords(colour):
            piece = self.get_piece(coord)
            if piece.name == name:
                found_piece_coord.append(coord)
        return found_piece_coord


    def add(self, coord: tuple, piece):
        self._position[coord] = piece

    def move(self, start, end):
        piece = self.get_piece(start)
        self.remove(start)
        self.add(end, piece)
        self.get_piece(end).notmoved = False

    def remove(self, pos):
        del self._position[pos]

    def castle(self, start, end):
        '''Carry out castling move (assuming move is validated)'''
        self.move(start, end)
        # Move the king
        row = start[1]
        if start[0] == 0:
            self.move((4, row), (2, row))
        elif start[0] == 7:
            self.move((4, row), (6, row))
        
    def nojumpcheck(self, start, end):
        """
        return False if there is a piece in between start and end
        """

        x, y, dist = vector(start, end)
        if abs(x) == 1 or abs(y) == 1:
            return True

        # moving vertical
        elif x == 0:
            pos_check = list(start)
            for i in range(abs(y) - 1):
                pos_check[1] += y/abs(y)
                if self.get_piece(tuple(pos_check)) != None:
                    return False
            return True

        # moving horizontal
        elif y == 0:
            pos_check = list(start)
            for i in range(abs(x) - 1):
                    return False
            return True

        # moving diagonal
        elif abs(x) == abs(y):
            pos_check = list(start)
            for i in range(abs(x) - 1):
                pos_check[1] += y/abs(y)
                pos_check[0] += x/abs(x)
                if self.get_piece(tuple(pos_check)) != None:
                    return False
            return True


    def get_piece(self, coord):
        '''
        Retrieves the piece at `coord`.
        `coord` is assumed to be a 2-ple of ints representing
        (col,row).

        Return:
        BasePiece instance
        or None if no piece found
        '''
        return self._position.get(coord, None)

    def alive(self, colour, name):
        for piece in self.pieces():
            if piece.colour == colour and piece.name == name:
                return True
        return False

    # def promotepawns(self, PieceClass=None):
    #     for coord in self.coords():
    #         row = coord[1]
    #         piece = self.get_piece(coord)
    #         for opprow, colour in zip([0, 7], ['black', 'white']):
    #             if row == opprow and piece.name == 'pawn' \
    #                     and piece.colour == colour:
    #                 if PieceClass is None:
    #                     PieceClass = self.promoteprompt()
    #                 promoted_piece = PieceClass(colour)
    #                 self.remove(coord)
    #                 self.add(coord, promoted_piece)


    def promotepawns(self, PieceClass=None):
        for coord in self.coords():
            row = coord[1]
            piece = self.get_piece(coord)
            for opprow, colour in zip([0, 7], ['black', 'white']):
                if row == opprow and piece.name == 'pawn' \
                        and piece.colour == colour:
                    print(PieceClass)
                    if PieceClass is None:
                        return True
                    else:
                        promoted_piece = PieceClass(colour)
                        self.info = f"Promoted pawn at {coord} to {promoted_piece.name}"
                        self.remove(coord)
                        self.add(coord, promoted_piece)

    def king_and_rook_unmoved(self, colour, rook_coord):
        row = rook_coord[1]
        king = self.get_piece((4, row))
        rook = self.get_piece(rook_coord)
        return king.notmoved and rook.notmoved

    def no_pieces_between_king_and_rook(self, colour, rook_coord):
        row = rook_coord[1]
        rook_col = rook_coord[0]
        if rook_col == 0:
            columns = (1, 2, 3)
        elif rook_col == 7:
            columns = (5, 6)
        else:
            raise MoveError('Invalid move: castling from {rook_coord}')
        for col in columns:
            if self.get_piece((col, row)) is not None:
                return False
        return True

    def movetype(self, start ,end):
        '''
        Determines the type of board move by:
        1. Checking if the player is moving a piece of their
           own colour
        2. Checking if the piece at `start` and the piece at
           `end` are the same colour
        3. Checking if the move is valid for that piece type

        Returns:
        'move' for normal moves
        'capture' for captures
        'castling' for rook castling
        'promotion' for pawn promotion
        None for invalid moves
        '''
        if self.debug:
            print(f'== movetype({start}, {end}) ==')
        if start is None or end is None:
            return None
        start_piece = self.get_piece(start)
        end_piece = self.get_piece(end)
        if self.debug:
            print(f'START_PIECE: {start_piece}')
            print(f'END_PIECE: {end_piece}')
        if start_piece is None \
                or start_piece.colour != self.turn:
            return None
        if end[1] in (0, 7) and start_piece.name == 'pawn':
            if start_piece.isvalid(start, end, capture=True) or start_piece.isvalid(start, end, capture=False):
                return 'promotion'
        if not self.nojumpcheck(start, end):
            return None
        if end_piece is not None:
            # handle special cases
            if start_piece.name == 'pawn' \
                    and end_piece.colour != start_piece.colour \
                    and start_piece.isvalid(start, end, capture=True):
                return 'capture'
            elif end_piece.colour != start_piece.colour and start_piece.isvalid(start, end) and start_piece.name != 'pawn':
                return 'capture'
            else:
                return None
        else:  # end piece is None
            if start_piece.name == 'rook' \
                    and start_piece.isvalid(start, end, castling=True) \
                    and self.king_and_rook_unmoved(self.turn, start) \
                    and self.no_pieces_between_king_and_rook(self.turn, start):
                return 'castling'
            elif start_piece.isvalid(start, end):
                return 'move'
            else:
                return None
        return True

    @classmethod
    def promoteprompt(cls):
        choice = input(f'Promote pawn to '
                       '(r=Rook, k=Knight, b=Bishop, '
                       'q=Queen): ').lower()
        if choice not in 'rkbq':
            return cls.promoteprompt()
        elif choice == 'r':
            return Rook
        elif choice == 'k':
            return Knight
        elif choice == 'b':
            return Bishop
        elif choice == 'q':
            return Queen

    def printmove(self, start, end, **kwargs):
        startstr = f'{start[0]}{start[1]}'
        endstr = f'{end[0]}{end[1]}'
        print(f'{self.get_piece(start)} {startstr} -> {endstr}', end='')
        if kwargs.get('capture', False):
            print(f' captures {self.get_piece(end)}')
        elif kwargs.get('castling', False):
            print(f' (castling)')
        elif kwargs.get(' promotion', False):
            print('promotion')
        else:
            print('')

    def get_kingthreat_coords(self, colour):
        """
        Checks for pieces with a valid move for attacking king of the specified colour.
        Returns a list of the coordinates of these pieces.
        """

        initial_turn = self.turn
        opponent_colour = 'white' if colour == 'black' else 'black'
        self.turn = opponent_colour
        attacking_pieces = []
        opponent_coords_list = self.coords(opponent_colour)
        own_king_coord = self.get_coords(colour, 'king')[0]
        
        for start_coord in opponent_coords_list:
            if self.movetype(start_coord, own_king_coord) != None:
                attacking_pieces.append(start_coord)
        self.turn = initial_turn
        return attacking_pieces

    def check(self, colour, start=None, end=None):
        """
        the colour argument tells which king to check if it is checked. Assuming that it is a validated move (except if the move would result in check)
        return boolean
        """
        initial_turn = self.turn
        self.turn = colour
        if start != None and end != None:
            temp_board = Board()
            temp_board.turn = self.turn
            # copy board
            for k,v in self._position.items():
                temp_board._position[k] = v

            try:
                temp_board.update(start, end)
            except MoveError:
                pass
            king_threat_pieces = temp_board.get_kingthreat_coords(colour)
        else:
            king_threat_pieces = self.get_kingthreat_coords(colour)

        self.turn = initial_turn

        if len(king_threat_pieces) == 0:
            return False
        else:
            return True

    def get_valid_move_coords(self, piece_coord):
        '''
        Returns a list of valid end coordinates for the piece at piece_coord.
        Returns an empty list if there are no valid moves.
        '''
        initial_turn = self.turn
        self.turn = self.get_piece(piece_coord).colour
        valid_coord_list = []
        for i in range(8):
            for j in range(8):
                if self.movetype(piece_coord, (i, j)) != None:
                    valid_coord_list.append((i, j))
        self.turn = initial_turn
        return valid_coord_list


    def checkmate_checking(self, colour):
        """
        self.checkmate(colour)

        Check if the colour is in checkmate 

        Steps:
        1. if there are two attacking pieces, King must move away,

        2. if only one attacking piece, see if king can move away or
        see if any other pieces are able to block/eat it

        3. see if it will now result in check, if it does not, it will not checkmate
        """
        # base check to make sure that at least when the king is eaten, it will end.
        king_list = []
        for piece in self.pieces():
            if piece.name == 'king':
                king_list.append(piece)
        if len(king_list) == 1:
            return True

        own_king_coord = self.get_coords(colour, 'king')[0]

        # Generating possible king moves
        possible_king_move = set(self.get_valid_move_coords(own_king_coord))

        initial_turn = self.turn
        self.turn = colour

        # See if king can move or capture
        for end_coord in possible_king_move:
            try:
                if not self.check(colour, own_king_coord, end_coord):
                        self.turn = initial_turn
                        return False
            except MoveError:
                continue

        attacking_pieces = self.get_kingthreat_coords(colour)
        own_pieces_list = self.coords(colour)
        if len(attacking_pieces) == 0:
            self.turn = initial_turn
            return False

        # if king is the only piece left, if king cannot move, checkmate
        # If attacking pieces is more than 2, and king cannot move away, checkmate
        if len(attacking_pieces) >= 2 or len(own_pieces_list) == 1:
            self.turn = initial_turn
            return True

        # For only one piece attacking.
        # Check if it can be eaten.
        for coord in own_pieces_list:
            if self.movetype(coord, attacking_pieces[0]) != None:
                if self.check(colour, coord, attacking_pieces[0]):
                    self.turn = initial_turn

                else:
                    self.turn = initial_turn
                    return False

        # Get all attacking piece valid_move square
        attacking_valid_move_set = set(
            self.get_valid_move_coords(attacking_pieces[0]))

        # See if any piece can block it.

        for coord in own_pieces_list:
            for move in attacking_valid_move_set:
                if self.movetype(
                        coord, move) != None and not self.check(colour, coord, move):
                    self.turn = initial_turn
                    return False
        self.turn = initial_turn
        return True

    def start(self):
        colour = 'black'
        self.add((0, 7), Rook(colour))
        self.add((1, 7), Knight(colour))
        self.add((2, 7), Bishop(colour))
        self.add((3, 7), Queen(colour))
        self.add((4, 7), King(colour))
        self.add((5, 7), Bishop(colour))
        self.add((6, 7), Knight(colour))
        self.add((7, 7), Rook(colour))
        for x in range(0, 8):
            self.add((x, 6), Pawn(colour))

        colour = 'white'
        self.add((0, 0), Rook(colour))
        self.add((1, 0), Knight(colour))
        self.add((2, 0), Bishop(colour))
        self.add((3, 0), Queen(colour))
        self.add((4, 0), King(colour))
        self.add((5, 0), Bishop(colour))
        self.add((6, 0), Knight(colour))
        self.add((7, 0), Rook(colour))
        for x in range(0, 8):
            self.add((x, 1), Pawn(colour))

        self.turn = 'white'

        for piece in self.pieces():
            piece.notmoved = True

    def display(self):
        '''
        Displays the contents of the board.
        Each piece is represented by two letters.
        First letter is the colour (W for white, B for black).
        Second letter is the name (Starting letter for each piece).
        '''
        Cell.number = 0
        if self.debug:
            print('== DEBUG MODE ON ==')
        # helper function to generate symbols for piece

        def sym(piece):
            colour_sym = piece.colour[0].upper()
            piece_sym = piece.name[0].upper()
            return f'{colour_sym}{piece_sym}'

        # Row 7 is at the top, so print in reverse order
        row_list = []
        temp = []
        temp.append(Cell(type='label corner'))
        for i in range(8):
            temp.append(Cell(i, 'label columnlabel'))
        row_list.append(temp)

        for row in range(7, -1, -1):
            temp = []
            temp.append(Cell(row, 'label rowlabel'))
            for col in range(8):
                coord = (col, row)  # tuple
                if coord in self.coords():
                    piece = self.get_piece(coord)
                    temp.append(Cell(piece.symbol()))
                else:
                    piece = None
                    temp.append(Cell())
            row_list.append(temp)
            if self.checkmate is not None:
                print(f'{self.checkmate} is checkmated!')
        return row_list

    def prompt(self, move, ui: WebInterface = WebInterface()):
        if self.debug:
            print('== PROMPT ==')

        def valid_format(inputstr):
            return len(inputstr) == 5 and inputstr[2] == ' ' \
                and inputstr[0:1].isdigit() \
                and inputstr[3:4].isdigit()

        def valid_num(inputstr):
            for char in (inputstr[0:1] + inputstr[3:4]):
                if char not in '01234567':
                    return False
            return True

        def split_and_convert(inputstr):
            '''Convert 5-char inputstr into start and end tuples.'''
            start, end = inputstr.split(' ')
            start = (int(start[0]), int(start[1]))
            end = (int(end[0]), int(end[1]))
            return (start, end)

        while True:
            inputstr = move
            if not valid_format(inputstr):
                ui.errmsg = ('Invalid move. Please enter your move in the '
                             'following format: __ __, _ represents a digit.')
                return 'error'
            elif not valid_num(inputstr):
                ui.errmsg = ('Invalid move. Move digits should be 0-7.')
                return 'error'
            else:
                start, end = split_and_convert(inputstr)
                if self.movetype(start, end) is None:
                    ui.errmsg = ('Invalid move. Please make a valid move.')
                    return 'error'
                else:
                    return start, end

    def pawns_to_promote(self, colour):
            '''Returns the first coord of any pawn to be promoted'''
            if colour == 'white':
                enemy_home = 7
            elif colour == 'black':
                enemy_home = 0
            else:
                raise ValueError("colour must be {'white', 'black'}")
            for coord in self.get_coords(colour, 'pawn'):
                col, row = coord
                if row == enemy_home:
                    # TODO: replace with raise PromptPromotionPiece
                    # with 'msg' argument and 'prompt' kwarg
                    return coord
            return None

    def promote_pawn(self, coord, char, **kwargs):
        piece_dict = {'r': Rook,
                     'k': Knight,
                     'b': Bishop,
                     'q': Queen,
                     }
        # Transfer old_piece move attributes to new_piece
        old_piece = self.get_piece(coord)
        new_piece = piece_dict[char.lower()](old_piece.colour)
        new_piece.moved = old_piece.moved
        self.add(coord, new_piece, push_to=kwargs.get('push_to'))

    def update(self, start ,end , promote_piece=None):
        '''
        Update board according to requested move.
        If an opponent piece is at end, capture it.
        '''

        if self.debug:
            print('== UPDATE ==')
        movetype = self.movetype(start, end)
        if movetype is None:
            raise MoveError(f'Invalid move ({self.printmove(start, end)})')
        elif movetype == 'castling':
            self.printmove(start, end, castling=True)
            self.castle(start, end)
        elif movetype == 'capture':
            self.printmove(start, end, capture=True)
            self.remove(end)
            self.move(start, end)
        elif movetype == 'move':
            self.printmove(start, end)
            self.move(start, end)
        elif movetype == 'promotion':
            self.printmove(start, end, promotion=True)
            self.move(start, end)
            # self.promotepawns(promote_piece)
            # assert False, 'NOT SURE IF WORKS!'
        else:
            raise MoveError('Unknown error, please report '
                            f'(movetype={repr(movetype)}).')
        # self.promotepawns()
        if not self.alive('white', 'king'):
            self.winner = 'black'
        elif not self.alive('black', 'king'):
            self.winner = 'white'

    def next_turn(self):
        if self.debug:
            print('== NEXT TURN ==')
        if self.turn == 'white':
            self.turn = 'black'
        elif self.turn == 'black':
            self.turn = 'white'

    def undo(self,move):
        end ,start = move
        piece = self.get_piece(start)
        self.remove(start)
        self.add(end,piece)
            
    def as_str(self):
        '''
        Returns the contents of the board
        as a linebreak-delimited string.
        '''
        output = []
        # Row 7 is at the top, so print in reverse order
        for row in range(7, -1, -1):
            line = []
            for col in range(8):
                coord = (col, row)  # tuple
                if coord in self.coords():
                    line.append(f'{self.get_piece(coord).symbol()}')
                else:
                    line.append(' ')
            output.append(line)
        return output
