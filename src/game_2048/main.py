from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from .game import Board
from .models import Direction, GameState, MoveRequest, MoveResponse
from .sessions import sessions

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


app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
