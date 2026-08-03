# 2048 游戏与强化学习 Agent

## 分支说明

- main：游戏主线开发。
- agent：与游戏引擎解耦的六动作 Q-learning Agent。

## Agent 结构

- src/game_2048/agent/contracts.py：三维游戏与 Agent 的稳定接口。
- src/game_2048/agent/environment.py：状态编码、动作执行和可解释奖励。
- src/game_2048/agent/q_learning.py：表格型 Q-learning 策略。
- src/game_2048/agent/training.py：训练循环及 JSON 指标导出。
- configs/agent.toml：训练与奖励参数。
- static/agent-dashboard.html：训练指标的独立可视化页面。

Agent 已经接入 Board3D。状态为 4×4×4 的 64 个格子，动作依次为 left、right、up、down、forward、back；前端中 forward/back 对应 Q/E。

在 game/ 仓库根目录执行：

    uv run python scripts/train_agent.py

训练会生成 artifacts/training_metrics.json；在浏览器打开 static/agent-dashboard.html 后选择该文件即可查看奖励和得分曲线。若需要使用其他游戏引擎适配器，可传入 --adapter package.module:factory。

## 验证

    uv run pytest
