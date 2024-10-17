from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from app.exceptions import *
from app.cruds.match import MatchService
from app.cruds.player import PlayerService
from app.connection_manager import manager
from app.database import get_db
from app.models.enums import ReasonWinning
from app.models.models import Players, Matches
from app.routers.matches import give_movement_card_to_player, give_shape_card_to_player, notify_all_players_movements_received, notify_movement_card_to_player

router = APIRouter(prefix="/matches")

async def playerWinner(match_id: int, reason: ReasonWinning, db: Session):
    match_service = MatchService(db)
    player_service = PlayerService(db) 
    
    players = player_service.get_players_by_match(match_id)[0]
    player_id = players.id
    player_service.delete_player(player_id)
    match_service.update_match(match_id, "FINISHED", 0)
    reason_winning = reason.value
    
    msg = {"key": "WINNER", "payload": {"player_id": player_id, "Reason": reason_winning}}
    
    try:
        await manager.broadcast_to_game(match_id, msg)
    except RuntimeError as e:
        # Manejar el caso en que el WebSocket ya esté cerrado
        print(f"Error al enviar mensaje: {e}")

@router.delete("/{match_id}/left/{player_id}")
async def leave_player(player_id: int, match_id: int, db: Session = Depends(get_db)):
    try:
        match_service = MatchService(db)
        player_service = PlayerService(db)
        try:
            player_to_delete = player_service.get_player_by_id(player_id)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Player not found with id: {player_id}") 
               
        match_to_leave = match_service.get_match_by_id(match_id)

        player_name = player_to_delete.player_name
        player_match = player_to_delete.match_id

        if player_match != match_id:
            raise HTTPException(status_code=404, detail="Player not in match")

        # IN LOBBY
        if match_to_leave.state == "WAITING":
            if player_to_delete.is_owner:
                raise HTTPException(status_code=400, detail="Owner cannot leave match")
                
        match_to_leave = match_service.get_match_by_id(match_id)
        player_service.delete_player(player_id)

        try:
            manager.disconnect_player_from_game(match_id, player_id)
        except PlayerNotConnected:
            # El jugador ya ha sido desconectado, no hacer nada
            pass
        
        match_service.update_match(match_id, match_to_leave.state, match_to_leave.current_players - 1)
        
        msg = {"key": "PLAYER_LEFT", "payload": {"name": player_name}}
        
        try:
            await manager.broadcast_to_game(match_id, msg)
        except RuntimeError as e:
            # Manejar el caso en que el WebSocket ya esté cerrado
            print(f"Error al enviar mensaje: {e}")

        if (match_to_leave.current_players) == 1 and match_to_leave.state == "STARTED":
            await playerWinner(match_id, ReasonWinning.FORFEIT, db)
        
        return {"player_id": player_id, "players": player_name}

    except PlayerNotConnected as e:
        raise HTTPException(
            status_code=404, detail="Player not connected to match")
    except GameConnectionDoesNotExist as e:
        raise HTTPException(status_code=404, detail="Match not found")
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Match not found")
    

def end_turn_logic(player: Players, match:Matches, db: Session):
    match_service = MatchService(db)
    player_service = PlayerService(db)
    
    if player.turn_order != match.current_player_turn:
        raise HTTPException(status_code=403, detail=f"It's not player {player.player_name}'s turn")
    
    if match.current_player_turn == match.current_players:
        match_service.update_turn(match.id, turn=1)
    else:
        match_service.update_turn(match.id, match.current_player_turn + 1) 
    
    next_player = player_service.get_player_by_turn(turn_order= match.current_player_turn, match_id= match.id)
    
    return next_player


@router.patch("/{match_id}/end-turn/{player_id}", status_code=200)
async def end_turn(match_id: int, player_id: int, db: Session = Depends(get_db)):
    try:
        player = PlayerService(db).get_player_by_id(player_id)
    except:
        raise HTTPException(status_code=404, detail=f"Player not found")
    try:
        match = MatchService(db).get_match_by_id(match_id)
    except:
        raise HTTPException(status_code=404, detail=f"Match not found")
    
    next_player = end_turn_logic(player, match, db)
    
    movs = give_movement_card_to_player(player_id, db)
    notify_movement_card_to_player(player_id, movs, db)
    notify_all_players_movements_received(player, match)
    
    await give_shape_card_to_player(next_player.id, db, is_init=False)
    
    msg = {
        "key": "END_PLAYER_TURN", 
        "payload": {
            "current_player_name": player.player_name,
            "next_player_name": next_player.player_name,
            "next_player_turn": next_player.turn_order
        }
    }
    await manager.broadcast_to_game(match_id, msg)
    
