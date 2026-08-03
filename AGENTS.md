# 项目协作说明

所有后续任务开始前，必须先阅读并遵守 .codex/rules.md。

## 当前结构

- src/game_2048/：Python/FastAPI 后端及强化学习 Agent。
- static/：浏览器游戏可视化前端。
- configs/：可修改的运行参数，不放业务代码。
- .codex/skills/：本项目专用 Agent 技能说明。
- tests/：自动化测试。

## Agent 接入约定

三维游戏引擎完成后，以 game_2048.agent.contracts.SixDirectionGameEngine 为适配目标。
Agent 不得直接访问 FastAPI session 或前端 DOM；游戏端通过适配器提供棋盘状态与动作结果。
