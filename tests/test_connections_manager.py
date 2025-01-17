from fastapi.testclient import TestClient
from fastapi import WebSocket
import pytest
from app.exceptions import *
from app.routers.matches import manager as manager2


def test_connect_player_to_game_success(app, manager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        manager.create_game_connection(1)
        manager.connect_player_to_game(1, 1, websocket)

        assert 1 in manager._games[1]
        assert websocket == manager._games[1][1]


def test_connect_player_to_game_raise_exceptions(app, manager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        with pytest.raises(GameConnectionDoesNotExist):
            manager.connect_player_to_game(1, 1, websocket)

    manager.create_game_connection(1)

    with client.websocket_connect("/wsTestRoute") as websocket:
        manager.connect_player_to_game(1, 1, websocket)

    with client.websocket_connect("/wsTestRoute") as websocket:
        with pytest.raises(PlayerAlreadyConnected):
            manager.connect_player_to_game(1, 1, websocket)


def test_disconnect_player_from_game_success(app, manager):
    manager.create_game_connection(1)

    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        manager.connect_player_to_game(1, 1, websocket)
        manager.connect_player_to_game(1, 2, websocket)

    manager.disconnect_player_from_game(1, 1)

    assert 1 not in manager._games[1]
    assert 2 in manager._games[1]

    manager.disconnect_player_from_game(1, 2)

    assert 2 not in manager._games[1]


def test_disconnect_player_from_game_raise_exceptions(manager):

    with pytest.raises(GameConnectionDoesNotExist):
        manager.disconnect_player_from_game(1, 1)

    manager.create_game_connection(1)

    with pytest.raises(PlayerNotConnected):
        manager.disconnect_player_from_game(1, 2)


def test_send_message_to_player_success(app, manager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        manager.create_game_connection(1)
        manager.connect_player_to_game(1, 1, websocket)
        await manager.send_to_player(1, 1, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        data = websocket.receive_json()
        assert {"msg": "data"} == data


def test_send_message_to_player_raise_exceptions(app, manager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        manager.create_game_connection(1)
        manager.connect_player_to_game(1, 1, websocket)
        with pytest.raises(GameConnectionDoesNotExist):
            await manager.send_to_player(2, 1, {"msg": "data"})
        with pytest.raises(PlayerNotConnected):
            await manager.send_to_player(1, 2, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute"):
        pass


def test_broadcast_to_game_success(app, manager):
    manager.create_game_connection(1)

    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        manager.connect_player_to_game(1, 1, websocket)
        await manager.broadcast_to_game(1, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute") as websocket:
        data = websocket.receive_json()
        assert {"msg": "data"} == data


def test_broadcast_to_game_raise_exceptions(app, manager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        with pytest.raises(GameConnectionDoesNotExist):
            await manager.broadcast_to_game(1, {"msg": "data"})

    client = TestClient(app)

    with client.websocket_connect("/wsTestRoute"):
        pass


def test_create_websocket_connection(app, manager):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
        manager2.create_game_connection(1)

    client = TestClient(app)

    with client.websocket_connect("/matches/1/ws/1") as websocket:
        data = websocket.receive_json()
        assert data == {"Error": "Conexión a la partida 1 no existe"}

    with client.websocket_connect("/wsTestRoute") as websocket:
        manager2.connect_player_to_game(1, 1, websocket)

    with client.websocket_connect("/matches/1/ws/1") as websocket:
        data = websocket.receive_json()
        assert data == {
            "Error": "Jugador 1 ya tiene una conexión activa a la partida 1"
        }

    assert 1 not in manager._games

def test_add_anonymous_connection_remove_anonymous_connection(app):
    @app.websocket("/wsTestRoute")
    async def wsTestRoute(websocket: WebSocket):
        await websocket.accept()
    
    client = TestClient(app)
    with client.websocket_connect("/wsTestRoute") as websocket:
        manager2.add_anonymous_connection(websocket)
        assert len(manager2._connections)

        manager2.remove_anonymous_connection(websocket)
        assert not len(manager2._connections)
        
        # Raises ValueError but is handled
        manager2.remove_anonymous_connection(websocket)
        assert not len(manager2._connections)

def test_create_connection(client):
    with client.websocket_connect("/matches/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"key": "MATCHES_LIST", "payload": {"matches": []}}