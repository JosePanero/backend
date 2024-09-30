from sqlalchemy.exc import NoResultFound
from typing import List
from app.models.models import Boards
from app.utils.utils import validate_color, validate_turn, validate_board

class BoardService:
    """
    Servicio para realizar operaciones CRUD sobre la tabla de Boards
    Metodos:
            - __init__
            - create_board
            - get_all_boards
            - get_board_by_id
            - update_ban_color
            - delete_board
    """
    def __init__(self, db):
        """ Constructor de la clase, guardamos en el atributo
            db: La session de la base de datos."""
        self.db = db

    def create_board(self, match_id : int, ban_color : str = None, current_player : int = None, next_player_turn : int = None):
        """
        Crea un nuevo tablero en la base de datos.
        Args:
            match_id: Id de la partida a la cual pertenece el tablero.
        Returns:
            new_board: Tablero creado.
        """
        new_board = Boards(match_id=match_id)
        if ban_color:
            validate_color(ban_color)
            new_board.ban_color = ban_color
        if current_player:
            validate_turn(current_player, next_player_turn, new_board.id)
            new_board.current_player = current_player
        if next_player_turn:
            validate_turn(current_player, next_player_turn, new_board.id)
            new_board.next_player_turn = next_player_turn
    
        self.db.add(new_board)
        self.db.commit()
        return new_board
    
    def get_all_boards(self) -> List[Boards]:
        """
        Obtiene todos los tableros de la base de datos.
        Returns:
            boards: Lista de tableros.
        """
        boards = self.db.query(Boards).all()
        return boards

    def get_board_by_id(self, board_id : int) -> Boards:
        """
        Obtiene un tablero de la base de datos por su id.
        Args:
            board_id: Id del tablero.
        Returns:
            board: Tablero.
        """
        board = self.db.query(Boards).filter(Boards.id == board_id).one()
        validate_board(board.id)
        return board

    def update_ban_color(self, board_id : int, ban_color : str):
        """
        Actualiza el color del ban de un tablero.
        Args:
            board_id: Id del tablero.
            ban_color: Color del ban.
        """
        validate_color(ban_color)
        
        board = self.db.query(Boards).filter(Boards.id == board_id).one()
        board.ban_color = ban_color
        self.db.commit()
    
    def delete_board(self, board_id : int):
        """
        Elimina un tablero de la base de datos.
        Args:
            board_id: Id del tablero.
        """
        board = self.db.query(Boards).filter(Boards.id == board_id).one()
        validate_board(board.id)
        self.db.delete(board)
        self.db.commit()
        
    def update_turn(self, board_id : int, current_player : int, next_player_turn : int):
        """
        Actualiza el turno de los jugadores.
        Args:
            board_id: Id del tablero.
        """
        validate_turn(current_player, next_player_turn, board_id)
        board = self.db.query(Boards).filter(Boards.id == board_id).one()
        board.current_player = board.next_player_turn
        self.db.commit()