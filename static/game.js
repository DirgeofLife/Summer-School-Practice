const DIRECTION_MAP = {
  ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
  w: 'up', W: 'up', s: 'down', S: 'down', a: 'left', A: 'left', d: 'right', D: 'right',
};

const GAP = 8;
const CONTAINER_SIZE = 400;
const TILE_SIZE = (CONTAINER_SIZE - GAP * 5) / 4;

const Game = {
  sessionId: null,
  score: 0,
  gameOver: false,
  won: false,
  moving: false,
};

function tilePosition(row, col) {
  return {
    top: GAP + row * (TILE_SIZE + GAP),
    left: GAP + col * (TILE_SIZE + GAP),
  };
}

function tileClass(value) {
  if (value <= 2048) return 'tile tile-' + value;
  return 'tile tile-2048 tile-super';
}

function createTileElement(value, row, col) {
  var el = document.createElement('div');
  el.className = tileClass(value);
  el.textContent = value;
  el.style.width = TILE_SIZE + 'px';
  el.style.height = TILE_SIZE + 'px';
  var pos = tilePosition(row, col);
  el.style.top = pos.top + 'px';
  el.style.left = pos.left + 'px';
  return el;
}

function renderBoard(newGrid, oldGrid) {
  var container = document.getElementById('board-container');

  // Gather existing elements into a pool keyed by position
  var pool = {}; // "r,c" → {el, value}
  var existing = container.querySelectorAll('.tile');
  for (var i = 0; i < existing.length; i++) {
    var el = existing[i];
    var r = Math.round((parseFloat(el.style.top) - GAP) / (TILE_SIZE + GAP));
    var c = Math.round((parseFloat(el.style.left) - GAP) / (TILE_SIZE + GAP));
    pool[r + ',' + c] = { el: el, value: parseInt(el.textContent) || 0 };
  }

  var usedKeys = {};

  for (var r = 0; r < 4; r++) {
    for (var c = 0; c < 4; c++) {
      var val = newGrid[r][c];
      if (!val) continue;

      var key = r + ',' + c;
      var isMerged = false;
      var el;

      // Check if an element at this position can be reused
      var existing = pool[key];
      if (existing && existing.value === val) {
        // Same value at same position — reuse, no animation
        el = existing.el;
        usedKeys[key] = true;
      } else if (existing && oldGrid && oldGrid[r][c] > 0 && val > oldGrid[r][c]) {
        // Value at this position doubled — merge, reuse with pulse
        isMerged = true;
        el = existing.el;
        el.textContent = val;
        el.className = tileClass(val);
        usedKeys[key] = true;
      } else {
        // Moved tile or new spawn — create new element
        el = createTileElement(val, r, c);
        el.classList.add('tile-new');
        container.appendChild(el);
      }

      // Update position
      var pos = tilePosition(r, c);
      el.style.top = pos.top + 'px';
      el.style.left = pos.left + 'px';

      if (isMerged) {
        el.classList.add('tile-merged');
      }
    }
  }

  // Remove elements that are no longer needed
  for (var key in pool) {
    if (!usedKeys[key]) {
      pool[key].el.remove();
    }
  }
}

document.addEventListener('animationend', function(e) {
  e.target.classList.remove('tile-new', 'tile-merged');
});

function updateScore(s) {
  Game.score = s;
  document.getElementById('score').textContent = s;
}

function showMessage(text) {
  document.getElementById('message-text').textContent = text;
  document.getElementById('message-overlay').classList.remove('hidden');
}

function hideMessage() {
  document.getElementById('message-overlay').classList.add('hidden');
}

async function newGame() {
  var resp = await fetch('/api/game/new', { method: 'POST' });
  var data = await resp.json();
  Game.sessionId = data.session_id;
  Game.score = 0;
  Game.gameOver = false;
  Game.won = false;
  Game.moving = false;

  updateScore(0);
  hideMessage();
  renderBoard(data.state.board, null);
}

async function makeMove(direction) {
  if (Game.moving || Game.gameOver) return;
  Game.moving = true;

  var oldBoard = null;
  try {
    var sr = await fetch('/api/game/' + Game.sessionId + '/state');
    if (sr.ok) {
      var sd = await sr.json();
      oldBoard = sd.board;
    }
  } catch (e) {}

  try {
    var resp = await fetch('/api/game/' + Game.sessionId + '/move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ direction: direction }),
    });
    if (!resp.ok) { Game.moving = false; return; }
    var data = await resp.json();

    if (data.moved) {
      renderBoard(data.state.board, oldBoard);
      updateScore(data.state.score);

      if (data.state.won && !Game.won) {
        Game.won = true;
        showMessage('You Win!');
      }
      if (data.state.game_over) {
        Game.gameOver = true;
        showMessage('Game Over!');
      }
    }
  } catch (e) {}
  Game.moving = false;
}

document.addEventListener('keydown', function(e) {
  var d = DIRECTION_MAP[e.key];
  if (!d) return;
  e.preventDefault();
  makeMove(d);
});

document.getElementById('new-game-btn').addEventListener('click', newGame);
document.getElementById('message-close-btn').addEventListener('click', hideMessage);

var tsX = 0, tsY = 0;
document.addEventListener('touchstart', function(e) {
  tsX = e.touches[0].clientX;
  tsY = e.touches[0].clientY;
}, { passive: true });
document.addEventListener('touchend', function(e) {
  var dx = e.changedTouches[0].clientX - tsX;
  var dy = e.changedTouches[0].clientY - tsY;
  if (Math.abs(dx) < 30 && Math.abs(dy) < 30) return;
  makeMove(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up'));
});

(async function() {
  var sid = localStorage.getItem('game2048_session');
  if (sid) {
    try {
      var r = await fetch('/api/game/' + sid + '/state');
      if (r.ok) {
        var d = await r.json();
        Game.sessionId = sid;
        updateScore(d.score);
        Game.won = d.won;
        Game.gameOver = d.game_over;
        renderBoard(d.board, null);
        if (d.game_over) showMessage('Game Over!');
        return;
      }
    } catch (e) {}
  }
  await newGame();
})();

window.addEventListener('beforeunload', function() {
  if (Game.sessionId) localStorage.setItem('game2048_session', Game.sessionId);
});
