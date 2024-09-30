from app.database import Base
from typing import List
from .enums import Colors, Shapes, Movements, MatchState
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey

# ================================================ MATCHES MODELS =================================#

class Matches(Base):
    """
        Model of the Matches table in the database.
        Attributes:
            - id: int, primary key.
            - match_name: str, name of the match.
            - state: Enum State, indicates the state of the match.
            - current_players: int, amount of players in the match.
            - max_players: int, maximum amount of players in the match.
        Relationships:
            - players: List[Players], list of players in the match.
            - board: Boards, the board of the match.
    """
    __tablename__ = 'matches'
    __table_args__ = {'extend_existing': True}
    # --------------------------------- ATTRIBUTES -------------------------#
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_name: Mapped[str] = mapped_column(String(50))
    state: Mapped[str]
    is_public: Mapped[bool] = mapped_column(Boolean)
    current_players: Mapped[int] = mapped_column(Integer)
    max_players: Mapped[int] = mapped_column(Integer)

    # --------------------------------- RELATIONSHIPS -----------------------#
    players: Mapped[List["Players"]] = relationship("Players", back_populates="match",
                                                    cascade="all, delete-orphan",
                                                    foreign_keys="[Players.match_id]",
                                                    post_update=True,
                                                    passive_deletes=True)
    board: Mapped["Boards"] = relationship("Boards", back_populates="match",
                                           cascade="all, delete-orphan",
                                           uselist=False,
                                           post_update=True,
                                           passive_deletes=True)

    # --------------------------------- VALIDATORS -------------------------#
    @validates('state')
    def validate_state(self, key, state):
        if state not in MatchState._value2member_map_.keys():
            raise ValueError(f"State {state} is not a valid state")
        return state
    # --------------------------------- REPR --------------------------------#
    def __repr__(self):
        return (f"Match(id={self.id!r}, match_name={self.match_name!r}, "
                f"state={self.state!r}, is_public={self.is_public!r}, "
                f"max_players={self.max_players!r})")

# ================================================ PLAYERS MODELS =================================#

class Players(Base):
    """
        Model of the Players table in the database.
        Attributes:
            - id: int, primary key.
            - player_name: str, name of the player.
            - is_owner: bool, if the player is the owner of the match.
            - session_token: str, token of the player.
            - turn_order: int, order of the player's turn.
            - match_id: int, foreign key to the match the
        Relationships:
            - match: Matches, relationship to the match the player is in.
            - shape_cards: List[ShapeCards], relationship to the shape cards the player has.
            - movement_cards: List[MovementCards], relationship to the movement cards the player has.
    """
    __tablename__ = 'players'
    __table_args__ = {'extend_existing': True}
    # --------------------------------- ATTRIBUTES -------------------------#
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    player_name: Mapped[str] = mapped_column(String(50))
    is_owner: Mapped[bool] = mapped_column(Boolean)
    session_token: Mapped[str] = mapped_column(String)
    turn_order: Mapped[int] = mapped_column(Integer, nullable=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey('matches.id'), nullable=True)

    # --------------------------------- RELATIONSHIPS -----------------------#
    match: Mapped["Matches"] = relationship("Matches", back_populates="players", post_update=True)
    shape_cards: Mapped[List["ShapeCards"]] = relationship("ShapeCards", 
                                                           back_populates="owner",
                                                           cascade="all, delete-orphan",
                                                           post_update=True,
                                                           passive_deletes=True)
    movement_cards: Mapped[List["MovementCards"]] = relationship("MovementCards", 
                                                                 back_populates="owner",
                                                                 cascade="all, delete-orphan", 
                                                                 post_update=True,
                                                                 passive_deletes=True)

    # --------------------------------- VALIDATORS -------------------------#
    @validates('turn_order')
    def validate_turn_order(self, key, turn_order):
        if turn_order < 1 or turn_order > 4:
            raise ValueError(f"Turn order {turn_order} is not valid: must be between 1 and 4")
        return turn_order

    # --------------------------------- REPR -------------------------------#
    def __repr__(self):
        return (f"Player(id={self.id!r}, player_name={self.player_name!r}, "
                f"is_owner={self.is_owner!r}, match_id={self.match_id!r})")

# ================================================ BOARDS MODELS =================================#

class Boards(Base):
    """
        Model of the Boards table in the database.
        Attributes:
            - id: int, primary key.
            - ban_color: str, color banned in the match.
            - match_id: int, foreign key to the match.
            - current_player_turn: int, foreign key to the current player's turn.
            - next_player_turn: int, foreign key to the next player's turn.
        Relationships:
            - match: Matches, relationship to the match the board is in.
            - tiles: List[Tiles], relationship to the tiles in the board.
    """
    __tablename__ = 'boards'
    __table_args__ = {'extend_existing': True}
    # --------------------------------- ATTRIBUTES -------------------------#
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ban_color: Mapped[str] = mapped_column(String(50), nullable=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey('matches.id'))
    current_player_turn: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'), nullable=True)
    next_player_turn: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'), nullable=True)

    # --------------------------------- RELATIONSHIPS -----------------------#
    match: Mapped["Matches"] = relationship("Matches", back_populates="board", lazy='joined', post_update=True)
    tiles: Mapped[List["Tiles"]] = relationship("Tiles", back_populates="board", post_update=True, passive_deletes=True)

    # --------------------------------- VALIDATORS -------------------------#
    @validates('ban_color')
    def validate_ban_color(self, key, color):
        if color not in Colors._value2member_map_.keys():
            raise ValueError(f"Color {color} is not a valid color to ban, must be one of {Colors._value2member_map_.keys()}")
        return color

    # --------------------------------- REPR -------------------------------#
    def __repr__(self):
        return (f"Board(id={self.id!r}, match_id={self.match_id!r})")

# ================================================ TILES MODELS ===================================#

class Tiles(Base):
    """
        Model of the Tiles table in the database.
        Attributes:
            - id: int, primary key.
            - color: str, color of the tile.
            - positionX: int, x position of the tile.
            - positionY: int, y position of the tile.
            - board_id: int, foreign key to the board.
        Relationships:
            - board: Boards, relationship to the board the tile is in.
    """
    __tablename__ = 'tiles'
    __table_args__ = {'extend_existing': True}
    # --------------------------------- ATTRIBUTES -------------------------#
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    color: Mapped[Colors] = mapped_column(String)
    position_x: Mapped[int] = mapped_column(Integer)
    position_y: Mapped[int] = mapped_column(Integer)
    board_id: Mapped[int] = mapped_column(Integer, ForeignKey('boards.id'))

    # --------------------------------- RELATIONSHIPS -----------------------#
    board: Mapped["Boards"] = relationship("Boards", back_populates="tiles")

    # --------------------------------- VALIDATORS -------------------------#
    @validates('position_x', 'position_y')
    def validate_position(self, key, position):
        if position < 0 or position > 5:
            raise ValueError(f"Position {position} is out of bounds")
        return position
    
    @validates('color')
    def validate_color(self, key, color):
        if color not in Colors._value2member_map_:
            raise ValueError(f"Color {color} is not a valid color")
        return color

    # --------------------------------- REPR -------------------------------#
    def __repr__(self):
        return (f"Tile(id={self.id!r}, color={self.color!r}, "
                f"positionX={self.positionX!r}, positionY={self.positionY!r}, "
                f"board_id={self.board_id!r})")

# ================================================ SHAPECARDS MODELS ==============================#

class ShapeCards(Base):
    """
        Model of the ShapeCards table in the database.
        Attributes:
            - id: int, primary key.
            - shape_type: str, shape of the card.
            - is_hard: bool, if the card is hard.
            - is_visible: bool, if the card is visible.
            - is_blocked: bool, if the card is blocked.
            - player_owner: int, foreign key to the player that owns the card.
        Relationships:
            - owner: Players, relationship to the player that owns the card.
    """
    __tablename__ = 'shapeCards'
    __table_args__ = {'extend_existing': True}
    # --------------------------------- ATTRIBUTES -------------------------#
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shape_type: Mapped[int] # mapeamos int para identificar las cartas
    is_hard: Mapped[bool]
    is_visible: Mapped[bool]
    is_blocked: Mapped[bool]
    player_owner: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'))

    # --------------------------------- RELATIONSHIPS -----------------------#
    owner: Mapped["Players"] = relationship("Players", back_populates="shape_cards", post_update=True)

    # --------------------------------- VALIDATORS -------------------------#
    @validates('shape_type')
    def validate_shape(self, key, shape):
        if shape not in Shapes._value2member_map_.keys():
            raise ValueError(f"Shape {shape} is not valid shape type")
        return shape

    # -------------------------------- REPR -------------------------------#
    def __repr__(self):
        return (f"ShapeCard(id={self.id!r}, shape_type={self.shape_type!r}, "
                f"is_hard={self.is_hard!r}, is_visible={self.is_visible!r}, "
                f"is_blocked={self.is_blocked!r}, player_owner={self.player_owner!r})")

# ================================================ MOVEMENTCARDS MODELS ===========================#

class MovementCards(Base):
    """
        Model of the MovementCards table in the database.
        Attributes:
            - id: int, primary key.
            - mov_type: str, movement of the card.
            - player_owner: int, foreign key to the player that owns the card.
        Relationships:
            - owner: Players, relationship to the player that owns the card.
    """
    __tablename__ = 'movementCards'
    __table_args__ = {'extend_existing': True}
    # --------------------------------- ATTRIBUTES -------------------------#
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mov_type: Mapped[str]
    player_owner: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'), nullable = True)

    # --------------------------------- RELATIONSHIPS -----------------------#
    owner: Mapped["Players"] = relationship("Players", back_populates="movement_cards", post_update=True)

    # --------------------------------- VALIDATORS -------------------------#
    @validates('mov_type')
    def validate_movement(self, key, movement):
        if movement not in Movements._value2member_map_:
            raise ValueError(f"Movement {movement} is not valid mov type")
        return movement

    # --------------------------------- REPR -------------------------------#
    def __repr__(self):
        return (f"MovementCard(id={self.id!r}, mov_type={self.mov_type!r}, player_owner={self.player_owner!r})")

# =================================================================================================#