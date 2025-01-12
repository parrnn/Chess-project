import copy
import re
from abc import ABC, abstractmethod
import random
from colorama import Fore, Back, Style
from enum import Enum


import sys
f1=open("input.txt","rt")
sys.stdin=f1
f2=open("out.txt","wt")
sys.stdout=f2

class ChessSituation(Enum):
    NOTHING: int = 0
    MOVED: int = 1
    SELECTED: int = 2


class UserSituation(Enum):
    NOTHING: int = 0
    LOGGEDIN: int = 1
    PLAYING: int = 2


class User:
    users = []

    def __init__(self, username: str = "", password: str = "", wins: int = 0, draws: int = 0, losses: int = 0,
                 scores: int = 0, undos: int = 0):
        self.username = username
        self.password = password
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.scores = scores
        self.undos = undos

    @staticmethod
    def register(username: str, password: str):
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return None
        if not re.search("^[a-zA-Z0-9_]+$", password):
            print("password format is invalid")
            return None

        if username in User.users:
            print("a user exists with this username")
            return None

        User.users.append(User(username, password))
        print("register successful")

    @staticmethod
    def login(username: str, password: str):
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return None

        user = next((u for u in User.users if u.username == username), None)
        if not user:
            print("no user exists with this username")
            return None

        if not re.search("^[a-zA-Z0-9_]+$", password):
            print("password format is invalid")
            return None
        if user.password != password:
            print("incorrect password")
            return None
        print("login successful")
        chess.white_user = user  # Assuming chess is defined elsewhere
        return user

    @staticmethod
    def remove(username: str, password: str):
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return None

        user = next((u for u in User.users if u.username == username), None)
        if not user:
            print("no user exists with this username")
            return None

        if not re.search("^[a-zA-Z0-9_]+$", password):
            print("password format is invalid")
            return None
        if user.password != password:
            print("incorrect password")
            return None

        User.users = [u for u in User.users if u.username != username]
        print(f"removed {username} successfully")

    @staticmethod
    def show_scoreboard():
        sorted_users = sorted(User.users, key=lambda u: (-u.scores, -u.wins, -u.draws, u.losses, u.username))
        for user in sorted_users:
            print(f"{user.username} {user.scores} {user.wins} {user.draws} {user.losses}")

    def __str__(self):
        return f"{self.username}"

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.username or other == self.password
        elif isinstance(other, User):
            return other.username == self.username or other.password == self.password

    def log_out(self, username: str, password: str):
        pass


class Piece(ABC):
    def __init__(self, name: str = "", x: int = 0, y: int = 0, color: str = "", prev_x: int = 0, prev_y: int = 0,
                 dest_x: int = 0, dest_y: int = 0, if_undo: bool = False):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.prev_x = prev_x
        self.prev_y = prev_y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.if_undo = if_undo

    def __str__(self):
        return f"{self.name}{self.color}"

    def __eq__(self, other):
        if other is None:
            return False
        return self.y == other.y and self.x == other.x

    @abstractmethod
    def move(self, x, y, board):
        pass


class King(Piece):
    def __init__(self, color, x, y):
        super().__init__('K', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Check if move is within valid range for the King
        if ((s_c - d_c) ** 2) + ((s_r - d_r) ** 2) <= 0 or ((s_c - d_c) ** 2) + ((s_r - d_r) ** 2) > 2:
            result.valid = False
            result.message = "Invalid move for King."
            return result  # Return a MoveResult with valid=False and a message

        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:
                result.valid = False
                result.message = "cannot move to the spot"
                return result  # Return a MoveResult indicating an invalid capture attempt
            else:
                result.captured_piece = dest_piece
                result.message = "rival piece destroyed"
                board[d_r][d_c] = None
                board[d_r][d_c] = self
                board[s_r][s_c] = None
                result.valid = True
                result.new_position = (x, y)
                self.x, self.y = x, y
                return result

        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "moved"
        self.x, self.y = x, y
        return result


class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__('Q', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        if s_r == d_r or s_c == d_c:
            if s_r == d_r:
                step = 1 if d_c > s_c else -1
                for c in range(s_c + step, d_c, step):
                    if board[s_r][c] is not None:
                        result.valid = False
                        result.message = "cannot move to the spot"
                        return result
            elif s_c == d_c:
                step = 1 if d_r > s_r else -1
                for r in range(s_r + step, d_r, step):
                    if board[r][s_c] is not None:
                        result.valid = False
                        result.message = "cannot move to the spot"
                        return result
        elif abs(s_r - d_r) == abs(s_c - d_c):
            row_step = 1 if d_r > s_r else -1
            col_step = 1 if d_c > s_c else -1
            r, c = s_r + row_step, s_c + col_step
            while r != d_r and c != d_c:
                if board[r][c] is not None:
                    result.valid = False
                    result.message = "cannot move to the spot"
                    return result
                r += row_step
                c += col_step
        # else:
        #     result.valid = False
        #     result.message = "Invalid move for Queen. Queen can only move in straight lines or diagonally."
        #     return result
        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:
                result.valid = False
                result.message = "cannot move to the spot"
                return result
            else:
                result.captured_piece = dest_piece
                result.message = "rival piece destroyed"
                board[d_r][d_c] = None
                board[d_r][d_c] = self
                board[s_r][s_c] = None
                result.valid = True
                result.new_position = (x, y)
                self.x, self.y = x, y
                return result
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "moved"
        self.x, self.y = x, y
        return result


class Knight(Piece):
    def __init__(self, color, x, y):
        super().__init__('N', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Validate Knight's unique "L" shaped movement
        if ((d_c - s_c) ** 2) + ((d_r - s_r) ** 2) != 5:
            result.valid = False
            # result.message = "Invalid move for Knight. Knight moves in an L-shape."
            result.message = "cannot move to the spot"
            return result

        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:
                result.valid = False
                result.message = "cannot move to the spot"
                return result
            else:
                result.captured_piece = dest_piece
                result.message = "rival piece destroyed"
                board[d_r][d_c] = None
                board[d_r][d_c] = self
                board[s_r][s_c] = None
                result.valid = True
                result.new_position = (x, y)
                self.x, self.y = x, y
                return result
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "moved"
        self.x, self.y = x, y
        return result


class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__('B', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)
        if abs(s_r - d_r) != abs(s_c - d_c):
            result.valid = False
            # result.message = "Invalid move for Bishop. Bishop can only move diagonally."
            result.message = "cannot move to the spot"
            return result
        row_step = 1 if d_r > s_r else -1
        col_step = 1 if d_c > s_c else -1
        r, c = s_r + row_step, s_c + col_step
        while r != d_r and c != d_c:
            if board[r][c] is not None:
                result.valid = False
                result.message = "cannot move to the spot"
                return result
            r += row_step
            c += col_step
        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:
                result.valid = False
                result.message = "cannot move to the spot"
                return result
            else:
                result.captured_piece = dest_piece
                result.message = "rival piece destroyed"
                board[d_r][d_c] = None
                board[d_r][d_c] = self
                board[s_r][s_c] = None
                result.valid = True
                result.new_position = (x, y)
                self.x, self.y = x, y
                return result
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "moved"
        self.x, self.y = x, y
        return result


class Rook(Piece):
    def __init__(self, color, x, y):
        super().__init__('R', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        if s_r != d_r and s_c != d_c:
            result.valid = False
            # result.message = "Invalid move for Rook. Rook can only move in straight lines."
            result.message = "cannot move to the spot"
            return result
        if s_r == d_r:
            if any(board[s_r][min(s_c, d_c) + 1:max(s_c, d_c)]):
                result.valid = False
                result.message = "cannot move to the spot"
                return result
        if s_c == d_c:
            if any(board[i][s_c] for i in range(min(s_r, d_r) + 1, max(s_r, d_r))):
                result.valid = False
                result.message = "cannot move to the spot"
                return result
        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:
                result.valid = False
                result.message = "cannot move to the spot"
                return result
            else:
                result.captured_piece = dest_piece
                result.message = "rival piece destroyed"
                board[d_r][d_c] = None
                board[d_r][d_c] = self
                board[s_r][s_c] = None
                result.valid = True
                result.new_position = (x, y)
                self.x, self.y = x, y
                return result
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "moved"
        self.x, self.y = x, y
        return result


class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__('P', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)
        direction = -1 if self.color == "w" else 1
        starting_row = 6 if self.color == "w" else 1
        promotion_row = 0 if self.color == "w" else 7
        if s_c == d_c:  # Same column
            if d_r == s_r + direction:  # Move one square forward
                if board[d_r][d_c] is None:  # Square must be empty
                    board[d_r][d_c] = self
                    board[s_r][s_c] = None
                    self.x, self.y = x, y
                    result.valid = True
                    result.new_position = (x, y)
                    result.message = "moved"
                    return result
            elif s_r == starting_row and d_r == s_r + 2 * direction:
                if board[d_r][d_c] is None and board[s_r + direction][d_c] is None:
                    board[d_r][d_c] = self
                    board[s_r][s_c] = None
                    self.x, self.y = x, y
                    result.valid = True
                    result.new_position = (x, y)
                    result.message = "moved"
                    return result
        elif abs(d_c - s_c) == 1 and d_r == s_r + direction:
            dest_piece = board[d_r][d_c]
            if dest_piece is not None and dest_piece.color != self.color:
                board[d_r][d_c] = self
                board[s_r][s_c] = None
                self.x, self.y = x, y
                result.valid = True
                result.captured_piece = dest_piece
                result.new_position = (x, y)
                result.message = "rival piece destroyed"
                return result
        result.valid = False
        # result.message = "Invalid move for Pawn"
        result.message = "cannot move to the spot"
        return result

class CoordinatesHelper:
    @staticmethod
    def cartesian_to_index(x, y):
        c = x - 1
        r = 8 - y
        return r, c

    @staticmethod
    def index_to_cartesian(r, c):
        x = c + 1
        y = 8 - r
        return x, y


class MoveResult:
    def __init__(self, valid=False,hit=False, new_position=None, captured_piece=None, message=""):
        self.valid = valid
        self.hit=hit
        self.new_position = new_position
        self.captured_piece = captured_piece
        self.message = message

    def __str__(self):
        return (f"MoveResult(valid={self.valid}, "
                f"new_position={self.new_position}, "
                f"captured_piece={self.captured_piece}, "
                f"message='{self.message}')")


class Chess:
    def __init__(self, white_user: 'User' = None, black_user: 'User' = None, board: list = None,
                 limit: int = 0, moves: list = None, kills: list = None, turn: 'User' = None,
                 selected_piece : 'Piece' = None, moves_count: int = 0, undo_count: int = 0, undid: bool = False,
                 last_move: list = None, last_kill=None,move_res:'MoveResult'=None):
        self.white_user = white_user
        self.black_user = black_user
        self.board = board if board is not None else []
        self.limit = limit
        self.moves = moves if moves is not None else []
        self.kills = kills if kills is not None else []
        self.turn = turn
        self.selected_piece = selected_piece
        self.moves_count = moves_count
        self.undo_count = undo_count
        self.undid = undid
        self.Chess_situ: ChessSituation = ChessSituation.NOTHING
        self.User_situ: UserSituation = UserSituation.NOTHING
        self.last_move = last_move if last_move is not None else []
        self.last_kill = last_kill
        self.move_res=move_res

    def move(self, x: int, y: int) -> bool:
        if chess.User_situ == chess.User_situ.PLAYING and chess.Chess_situ!=ChessSituation.SELECTED:
            print("invalid command ( MOVE selected nist )")
        if chess.User_situ == chess.User_situ.NOTHING:
            print("invalid command (MOVE logged in nist )")
        if chess.User_situ == chess.User_situ.LOGGEDIN:
            print("invalid command (MOVE playing nist) ")
        if self.selected_piece==None:
            print("do not have any selected piece")
        if chess.Chess_situ == chess.Chess_situ.MOVED:
            print("already moved")
            return False
        if self.Chess_situ != ChessSituation.SELECTED:
            # print("do not have any selected piece")
            return False

        self.move_res = self.selected_piece.move(x, y, self.board)

        if self.move_res.captured_piece:
            self.last_kill = self.move_res.captured_piece
            self.kills.append((self.move_res.captured_piece, x, y))

        return self.process_move_result(self.move_res)

    def process_move_result(self, move_result: MoveResult) -> bool:
        if self.Chess_situ != ChessSituation.SELECTED:
            print("No piece selected. You must select a piece before moving.")
            return False

        if not move_result.valid:
            print(move_result.message)
            return False

        self.Chess_situ = ChessSituation.MOVED
        # self.moves_count+=1
        print(move_result.message)
        # if self.moves_count==self.limit:
        #     print("draw")
        #     self.white_user.scores+=1
        #     self.black_user.scores+=1
        #     self.end_game()
        return True
    def initialize(self):
        self.board = [[None for i in range(8)] for j in range(8)]
        self.board[0] = [Rook("b", 1, 8), Knight("b", 2, 8), Bishop("b", 3, 8), Queen("b", 4, 8), King("b", 5, 8),
                         Bishop("b", 6, 8), Knight("b", 7, 8), Rook("b", 8, 8)]
        self.board[7] = [Rook("w", 1, 1), Knight("w", 2, 1), Bishop("w", 3, 1), Queen("w", 4, 1), King("w", 5, 1),
                         Bishop("w", 6, 1), Knight("w", 7, 1), Rook("w", 8, 1)]
        self.board[1] = [Pawn("b", i, 7) for i in range(1, 9)]
        self.board[6] = [Pawn("w", i, 2) for i in range(1, 9)]

    def print(self):
        if chess.User_situ != UserSituation.PLAYING:
            print("invalid command ( SHOW BOARD age playing nbud anjam nshe")
        else:
            for row in self.board:
                print("|".join([
                    str(piece) if piece is not None else "  "
                    for piece in row
                ]) + "|")

    def random_board(self, count, selected_class):
        a = 0
        self.board = [[None for i in range(8)] for j in range(8)]
        arr = []
        while a < count:
            r = random.randint(0, 7)
            c = random.randint(0, 7)
            if self.board[r][c] is None:
                x, y = CoordinatesHelper.index_to_cartesian(r, c)
                piece_type = random.randint(0, 1)
                color = random.choice(['b', 'w'])
                if piece_type == 0:
                    piece = selected_class(color, x, y)
                    arr.append(piece)
                else:
                    piece = Pawn(color, x, y)
                self.board[r][c] = piece
                a += 1

        self.selected_piece = arr[-1]
        self.print()

    def select(self, x, y, board):
        if chess.User_situ == UserSituation.PLAYING:
            r, c = CoordinatesHelper.cartesian_to_index(x, y)
            if self.Chess_situ == ChessSituation.NOTHING :
                if board[r][c] is None:
                    print("no piece on this spot")
                    return False
                if self.turn != board[r][c].color:
                    print("you can only select one of your pieces")
                    return False
                self.selected_piece = board[r][c]
                self.Chess_situ = ChessSituation.SELECTED
                # print(f"{self.selected_piece} selected")
                print("selected")
                return True
            elif self.Chess_situ == ChessSituation.SELECTED :
                self.selected_piece = board[r][c]
                self.Chess_situ = ChessSituation.SELECTED
                # print(f"{self.selected_piece} selected")
                print("selected")
                return True
        print("invalid command(SELECT age playing nbud)")

    def new_game(self, username: str, limit):
        # Check if the user is logged in
        if self.User_situ != UserSituation.LOGGEDIN:
            print("invalid command NEW_GAME age logged in nbud")
            return False

        # Validate username format
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return False

        # Check if the username is the same as the white user
        # if username == self.white_user:
        #     print("you must choose another player to start a game.")
        #     return False

        # Check if the username exists in User.users
        if username not in User.users:
            print("no user exists with this username")
            return False

        # Validate and convert the limit to an integer
        limit = str(limit)
        if not limit.isdigit() and limit != "0":
            print("number should be positive to have a limit or 0 for no limit")
            return False
        limit = int(limit)

        # Ensure the limit is valid
        if limit < 0:
            print("number should be positive to have a limit or 0 for no limit")
            return False
        if username == self.white_user:
            print("you must choose another player to start a game")
            return False
        # Set up the game
        self.limit = limit
        self.User_situ = UserSituation.PLAYING
        self.black_user = User.users[User.users.index(username)]
        print(f"new game started successfully between {self.white_user} and {self.black_user} with limit {limit}")
        self.initialize()
        self.turn = "w"
        return True

    def end_game(self):
        if chess.User_situ == UserSituation.PLAYING:
            self.black_user.undos=0
            self.black_user = None
            self.kills = []
            self.moves = []
            self.moves_count = 0
            self.undo_count = 0
            self.last_move = []
            self.last_kill = None
            self.undid = False
            self.white_user.undos=0
            # self.last_move =None
            # self.moves_count = 0
            # self.undo_count = 0
            # self.last_kill = None
            self.User_situ = UserSituation.LOGGEDIN
            self.Chess_situ = ChessSituation.NOTHING


    def next_turn(self):
        if self.User_situ != UserSituation.PLAYING:
            print("invalid command (NEXT_TURN age playing nbud")
            return
        if self.Chess_situ != ChessSituation.MOVED:
            print("you must move then proceed to next turn")
            return

        if self.move_res and self.move_res.captured_piece:
            captured = self.move_res.captured_piece
            self.last_kill = captured
            self.kills.append(f"{captured} captured!")
            if str(captured) == "Kb":
                print(f"turn completed")
                self.white_user.scores += 3
                self.white_user.wins += 1
                self.black_user.losses += 1
                print(f"player {self.white_user} with color white won")
                self.end_game()
                return
            elif str(captured) == "Kw":
                print(f"turn completed")
                self.black_user.scores += 3
                self.black_user.wins += 1
                self.white_user.losses += 1
                print(f"player {self.black_user} with color black won")
                self.end_game()
                return

        self.selected_piece = None
        self.moves_count += 1
        if self.limit == 0:
            self.turn = 'b' if self.turn == 'w' else 'w'
            print(f"turn completed")
            self.Chess_situ = ChessSituation.NOTHING
            self.undid = False

        elif self.moves_count < self.limit:
            self.turn = 'b' if self.turn == 'w' else 'w'

            self.Chess_situ = ChessSituation.NOTHING
            self.undid = False
            print(f"turn completed")
        elif self.moves_count == self.limit:
            # Check for draw if the game exceeds the move limit
            print(f"turn completed")
            print("draw")
            self.white_user.draws += 1
            self.white_user.scores += 1
            self.black_user.draws += 1
            self.black_user.scores += 1
            self.end_game()
    def undo(self):
        current_player = self.white_user if self.turn == "w" else self.black_user
        if current_player.undos >= 2:
            print(f"you cannot undo anymore")
            return
        if self.Chess_situ != ChessSituation.MOVED:
            print("you must move before undo")
            return
        if self.undid:
            print("you have used your undo for this turn")
            return
        if self.User_situ != UserSituation.PLAYING:
            print("invalid command (UNDO age playing nbud)")
            return
        self.undid = True
        current_r, current_c = CoordinatesHelper.cartesian_to_index(self.selected_piece.x, self.selected_piece.y)
        prev_r, prev_c = CoordinatesHelper.cartesian_to_index(self.selected_piece.prev_x, self.selected_piece.prev_y)

        self.board[prev_r][prev_c] = self.selected_piece
        self.board[current_r][current_c] = None
        self.selected_piece.x, self.selected_piece.y = self.selected_piece.prev_x, self.selected_piece.prev_y

        if self.last_kill:
            last_kill_piece, last_kill_x, last_kill_y = self.kills.pop()  # Get the last kill details
            last_kill_r, last_kill_c = CoordinatesHelper.cartesian_to_index(last_kill_x, last_kill_y)
            self.board[last_kill_r][last_kill_c] = last_kill_piece
        if self.moves:
            self.moves.pop()
        self.Chess_situ = ChessSituation.SELECTED
        current_player.undos += 1
        print(f"undo completed")
        return True
    def show_turn(self):
        if self.User_situ != UserSituation.PLAYING:
            print("invalid command (SHOW_TURN age playing nbud)")
            return
        if self.turn == "w":
            print(f"it is player {self.white_user} turn with color white")
            return self.turn
        else:
            print(f"it is player {self.black_user} turn with color black")
            return self.turn

    def show_moves(self, aarg=False):
        if self.User_situ != UserSituation.PLAYING:
            print("invalid command (SHOW_MOVES age playing nbud")
            return
        if aarg:
            for move in self.moves:
                print(move)
                # print(move[1])
        else:
            for move in self.moves:
                if move[1] == self.turn:
                    print(move)
    def show_last_move(self):
        if self.User_situ != UserSituation.PLAYING:
            print("invalid command (SHOW LAST MOVE age playing nbud")
            return
        else:
            print(self.last_move[-1])

    def show_killed(self, aarg2=False):
        if self.User_situ != UserSituation.PLAYING:
            print("invalid command (SHOW_KILLED age playing nbud")
            return
        if not self.kills:
            return
        # Loop through kills list and validate each item's structure
        for item in self.kills:
            if len(item) == 3:  # Ensure the item has exactly 3 values
                captured_piece, x, y = item
                if aarg2:
                    print(f"{captured_piece} killed in spot {y},{x}")
                else:
                    # Only show opponent's captured pieces
                    if captured_piece.color == self.turn:
                        print(f"{captured_piece} killed in spot {y},{x}")

    def forfeit(self):
        if self.User_situ != UserSituation.PLAYING:
            print("invalid command (FORFEIT age playing nbud)")
            return
        if self.turn == "w":
            self.white_user.scores -= 1
            self.white_user.losses += 1
            self.black_user.scores += 2
            self.black_user.wins += 1
            print("you have forfeited")
            print(f"player {self.black_user} with color black won")
        elif self.turn == "b":
            self.black_user.scores -= 1
            self.black_user.losses += 1
            self.white_user.scores += 2
            self.white_user.wins += 1
            print("you have forfeited")
            print(f"player {self.white_user} with color white won")


# player1 = User("alireza", "12345", 10, 5, 5, 15)
# player2 = User("amir", "09876", 3, 1, 4, 2)
# player3 = User("zahra", "54321", 10, 6, 3, 8)
# player4 = User("ahmad", "67890", 10, 5, 5, 10)
# player5 = User("paria", "11111", 8, 4, 5, 12)
# player6 = User("nazi", "22222", 10, 5, 5, 15)
# player7 = User("amirali", "09876", 3, 1, 3, 2)
# User.users.append(player1)
# User.users.append(player2)
# User.users.append(player3)
# User.users.append(player4)
# User.users.append(player5)
# User.users.append(player6)
# User.users.append(player7)
chess = Chess()
while True:
    parts = input().strip().split()
    if len(parts) == 0:
        continue

    command = parts[0]

    if command == "register" and len(parts) == 3:
        User.register(parts[1], parts[2])
    elif command == "login" and len(parts) == 3:
        login_successful = User.login(parts[1], parts[2])
        if login_successful:
            chess.User_situ = UserSituation.LOGGEDIN
    elif command == "remove" and len(parts) == 3:
        User.remove(parts[1], parts[2])
    elif command == "new_game" and len(parts) == 3:
        chess.new_game(parts[1], parts[2])
    elif command == "list_users":
        print('\n'.join(sorted(user.username for user in User.users)))
    elif command == "help":
        if chess.User_situ == UserSituation.NOTHING:
            print(f"register [username] [password]")
            print(f"login [username] [password]")
            print(f"remove [username] [password]")
            print("list_users")
            print("help")
            print("exit")
        elif chess.User_situ == UserSituation.LOGGEDIN:
            print("new_game [username] [limit]")
            print("scoreboard")
            print("list_users")
            print("help")
            print("logout")
        elif chess.User_situ == UserSituation.PLAYING:
            print("select [x],[y]")
            print("deselect")
            print("move [x],[y]")
            print("next_turn")
            print("show_turn")
            print("undo")
            print("undo_number")
            print("show_moves [-all]")
            print("show_killed [-all]")
            print("show_board")
            print("help")
            print("forfeit")
    elif command =="logout":
        if chess.User_situ == UserSituation.LOGGEDIN:
            chess.User_situ = UserSituation.NOTHING
            print("logout successful")
        else:
            print("invalid command (LOG OUT age logged in nbud)")
    elif command == "exit":
        print("program ended")
        break
    elif command == "forfeit":
        chess.forfeit()
        chess.end_game()
    elif command == "scoreboard":
        if chess.User_situ == chess.User_situ.NOTHING:
            print("invalid command (SCOREBOARD dr sharayeti ke user situ nothing bashe")
        else:
            User.show_scoreboard()
        # player2.show_scoreboard()
    elif command == "show_board":
        # chess.initialize()
        chess.print()
    elif command == "random" and len(parts) == 2:
        try:
            count = int(parts[1])
            chess.random_board(count, Pawn)
        except ValueError:
            print("Invalid count. Please enter a valid number.")
    elif command == "move" and len(parts) == 2:
        if chess.User_situ==UserSituation.PLAYING:
            try:
                dest_x, dest_y = map(int, parts[1].split(","))
                if not (1 <= dest_x <= 8 and 1 <= dest_y <= 8):
                    print("wrong coordination")
                    continue
                success = chess.move(dest_y, dest_x)
                if success:
                    selected_piece = chess.selected_piece
                    if selected_piece:
                        if chess.move_res.captured_piece:
                            chess.moves.append(
                                f"{selected_piece} {selected_piece.prev_y},{selected_piece.prev_x} "
                                f"to {dest_x},{dest_y} destroyed {chess.move_res.captured_piece}"
                            )
                        else:
                            chess.moves.append(
                                f"{selected_piece} {selected_piece.prev_y},{selected_piece.prev_x} "
                                f"to {dest_x},{dest_y}"
                            )
                        # if chess.move_res.captured_piece:
                        #     chess.moves.append(
                        #         f"{selected_piece} {selected_piece.prev_y} {selected_piece.prev_x} "
                        #         f"to {dest_x},{dest_y} destroyed {chess.move_res.captured_piece}"
                        #     )

                        chess.last_move.append(f"{dest_x},{dest_y}")
                # else:
                #     print("Move failed.")
            except ValueError:
                print("Invalid input format. Use 'move x,y' where x and y are integers between 1 and 8.")
        else:
            print("invalid command (MOVE age playing nbud)")
    elif command == "place":
        if chess.User_situ != UserSituation.PLAYING:
            print("invalid command (PLACE age playing nbud")
        else:
            selected_piece = chess.selected_piece
            r, c = CoordinatesHelper.cartesian_to_index(selected_piece.x, selected_piece.y)
            print(f"{r},{c}")
    elif command == "xplace":
        if chess.User_situ != UserSituation.PLAYING:
            print("invalid command (Xplace age playing nbud)")
        else:
            selected_piece = chess.selected_piece
            print(f"{selected_piece.x},{selected_piece.y}")
    elif command == "select" and len(parts) == 2:
        x, y = int(parts[1].split(",")[0]), int(parts[1].split(",")[1])
        y, x = x,y
        if chess.User_situ==UserSituation.PLAYING:
            if 1 <= y <= 8 and 1 <= x <= 8:
                chess.select(x, y, chess.board)
            else:
                print("wrong coordination")
        else:
            print("invalid command (SELECT age playing nbud")
    elif command == "next_turn":
        chess.next_turn()
    elif command == "show_turn":
        chess.show_turn()
    elif command == "show_moves":
        if len(parts) == 2 and parts[1] == "-all":
            chess.show_moves(True)
        elif len(parts) == 1:
            chess.show_moves()
        else:
            print("invalid command (SHOW MOVES")
    elif command == "last_move":
        chess.show_last_move()
    elif command == "undo" and len(parts)==1:
        if chess.User_situ==UserSituation.PLAYING:
            chess.undo()
        else:
            print("invalid command (UNDO age playing nbud")
    elif command == "undo_number":
        if chess.User_situ==UserSituation.PLAYING:
            current_player = chess.white_user if chess.turn == "w" else chess.black_user
            remaining_undos = 2 - current_player.undos
            print(f"you have {remaining_undos} undo moves")
        else:
            print("invalid command (UNDO NUMBER age playing nbud")
    elif command == "deselect":
        if chess.User_situ==UserSituation.PLAYING:
            if chess.Chess_situ == ChessSituation.SELECTED:
                chess.Chess_situ = ChessSituation.NOTHING
                print("deselected")
            else:
                print("no piece is selected")
        else:
            print("invalid command (DESELECT age playing nbud")
    elif command == "show_killed":
        if len(parts) == 2 and parts[1] == "-all":
            chess.show_killed(True)
        elif len(parts) == 1:
            chess.show_killed()
    else:
        print("invalid command")