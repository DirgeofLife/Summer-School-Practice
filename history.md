# 项目对话记录

## 2026-08-03

- **用户需求**：读取项目程序，获取前端启动代码。
- **主要结论**：
  - 架构：FastAPI 后端（`src/game_2048/main.py`，包名 `game_2048`）+ 静态前端（`static/`），前后端分离。
  - 前端由后端 StaticFiles 挂载在 `/` 托管，无独立前端 dev server。
  - 前端入口：`/` → `index.html`（2D），`/3d.html`（3D）。
  - 启动命令：`uv run uvicorn game_2048.main:app --reload --host 127.0.0.1 --port 8000`，浏览器打开 http://127.0.0.1:8000。

## 2026-08-03（升级为三维 2048）

- **用户需求**：把 2D 2048 升级为真正在三维空间内的游戏，新增上下移动的坐标轴（6 方向移动）。
- **主要修改**：
  - 后端新增 `src/game_2048/game3d.py`：`Board3D` 4×4×4 棋盘，6 方向滑动（left/right/up/down/forward/back），含合并计分、胜利/结束判定、`to_dict`。
  - `models.py`：`Direction` 增加 `forward`/`back`；新增 `GameState3D`、`MoveResponse3D`。
  - `sessions.py`：新增 `sessions3d`；`main.py` 新增 `/api/game3d/new`、`/api/game3d/{id}/move`、`/api/game3d/{id}/state`。
  - 前端新增 `static/3d-game.html`：Three.js 渲染 4 层堆叠的 4×4×4 立体格子；WASD/方向键 4 向，Q/E 或 ▲▼ 按钮换层，拖拽旋转、滚轮缩放；滑动动画采用"新旧线按索引配对"修正了 2D 版 `3d.html` 的交叉配对缺陷。
  - `index.html` 增加"3D 版"导航链接。
- **主要结论**：
  - 新页面入口 `/3d-game.html`；旧 `/3d.html` 保留（仍是 2D 棋盘 3D 皮肤）。
  - 测试新增 `tests/test_game3d.py`，全部 30 个测试通过（`uv run pytest`）。
  - 踩坑：Windows 下 uvicorn `--reload`（WatchFiles）检测到后端文件变更后重载卡死，旧 worker 残留占用 8000 端口；需手动清理孤儿进程后以不带 `--reload` 方式重启。前端静态文件无需重启。

## 2026-08-03（3D 布局优化）

- **用户需求**：修改 3D 版布局 —— ①棋盘改为透明；②棋子应位于棋盘上方，之前卡在板子中间。
- **主要修改**（`static/3d-game.html`）：
  - 层板改为半透明玻璃质感：`transparent: true, opacity: 0.18`、`depthWrite: false`，并加 EdgesGeometry 描边提升轮廓辨识度；格子薄板透明度 0.10→0.16。
  - 新增 `PIECE_LIFT = 0.5` 常量，在 `gridToWorld` 的 y 上叠加，使棋子中心抬升到层板上方（立方体底面约高出层板顶 0.04），不再嵌入板中；格子薄板在调用处覆写 y，不受影响。
  - 数字精灵补上 `sprite.scale = 0.75`（此前未设 scale，默认 1 世界单位过大），位置调整到 `y=0.6`，保证不穿过上层板。
- **主要结论**：纯前端静态改动，刷新浏览器即可生效，无需重启后端。
