from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .game import Board
from .game3d import Board3D
from .models import (
    Direction,
    GameState,
    GameState3D,
    MoveRequest,
    MoveResponse,
    MoveResponse3D,
)
from .sessions import sessions, sessions3d

app = FastAPI(title="2048 Game")

static_dir = Path(__file__).parent.parent.parent / "static"


@app.post("/api/game/new")
async def new_game() -> dict:
    session_id = str(uuid4())
    sessions[session_id] = Board()
    return {"session_id": session_id, "state": sessions[session_id].to_dict()}


@app.post("/api/game/{session_id}/move")
async def make_move(session_id: str, req: MoveRequest) -> MoveResponse:
    board = sessions.get(session_id)
    if board is None:
        raise HTTPException(404, "Session not found")
    moved = board.slide(req.direction.value)
    return MoveResponse(state=GameState(**board.to_dict()), moved=moved)


@app.get("/api/game/{session_id}/state")
async def get_state(session_id: str) -> GameState:
    board = sessions.get(session_id)
    if board is None:
        raise HTTPException(404, "Session not found")
    return GameState(**board.to_dict())


@app.post("/api/game3d/new")
async def new_game3d() -> dict:
    session_id = str(uuid4())
    sessions3d[session_id] = Board3D()
    return {"session_id": session_id, "state": sessions3d[session_id].to_dict()}


@app.post("/api/game3d/{session_id}/move")
async def make_move3d(session_id: str, req: MoveRequest) -> MoveResponse3D:
    board = sessions3d.get(session_id)
    if board is None:
        raise HTTPException(404, "Session not found")
    moved = board.slide(req.direction.value)
    return MoveResponse3D(state=GameState3D(**board.to_dict()), moved=moved)


@app.get("/api/game3d/{session_id}/state")
async def get_state3d(session_id: str) -> GameState3D:
    board = sessions3d.get(session_id)
    if board is None:
        raise HTTPException(404, "Session not found")
    return GameState3D(**board.to_dict())


app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
