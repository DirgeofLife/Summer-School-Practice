---
name: three-d-2048-q-learning
description: 在六面三维 2048 中实现、训练、调试可复现的 Q-learning Agent；用于维护状态、动作、奖励、训练指标和游戏引擎适配器。
---

# 三维 2048 Q-learning Agent

## 适用范围

使用本 skill 处理 src/game_2048/agent/ 中的强化学习代码，或将六面三维游戏引擎接入 Agent。
不使用它修改浏览器渲染、棋子动画或游戏规则本身。

## 固定接口

- 状态 s：6 个面、每面 4×4 的方块数值；Agent 内部用 log2(tile) 编码，空位为 0。
- 动作 a：left、right、up、down、w、s，依次表示水平面四方向与竖直面两个方向。
- 转移：游戏引擎实现 SixDirectionGameEngine.reset() 与 move(action)，返回新状态、是否移动、合并得分增量。
- 奖励 r：有效合并的分数增益、最大方块进步、无效操作惩罚、胜利奖励、终局惩罚；具体权重只在 configs/agent.toml 修改。

## 训练与调试

1. 使用 uv run pytest 验证 Agent 核心逻辑。
2. 训练时固定 seed，并把每回合奖励、得分、步数、最大方块和 epsilon 写为 JSON。
3. 调整奖励前，检查每个奖励分量是否能解释 Agent 行为；不得只依据总奖励判断。
4. Q-table 的状态编码或动作顺序改变时，必须重新训练，不能复用旧表。
5. 游戏引擎尚未完成时，用测试 fake engine 验证接口，不为方便训练而修改真实游戏规则。
