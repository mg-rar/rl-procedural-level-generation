from collections import deque

import numpy as np

from network.agent import D3QNAgent
from network.environment import GenEnv, Stage


def train(n_episodes=100, eps_start=1.0, eps_end=0.01, eps_decay=0.995, target_update=10):
    env = GenEnv()

    agent: dict[Stage, D3QNAgent] = {}
    recover = False
    for (stage, (obs, act)) in env.agent_spaces.items():
        agent[stage] = D3QNAgent(state_size=obs, action_size=act)
        try:
            agent[stage].load(f"models/{stage.name}")
            recover = True
        except:
            recover = False

    wall_scores = []
    enemy_scores = []
    item_scores = []
    solver_scores = []

    wall_scores_window = deque(maxlen=100)
    enemy_scores_window = deque(maxlen=100)
    item_scores_window = deque(maxlen=100)
    solver_scores_window = deque(maxlen=100)
    eps = eps_start

    if not recover:
        for _ in range(0, 20):
            print(f'\r walls pretrain score '
                  f'{pretrain_walls(env, agent[Stage.WALLS])}',
                  end="")
        print()
        for _ in range(0, 20):
            print(f'\r enemy pretrain score '
                  f'{pretrain_enemy(env, agent[Stage.WALLS], agent[Stage.ENEMY])}',
                  end="")
        print()
        for _ in range(0, 20):
            print(f'\r item pretrain score '
                  f'{pretrain_items(env, agent[Stage.WALLS], agent[Stage.ENEMY], agent[Stage.ITEM])}',
                  end="")
        print()

    for i_episode in range(1, n_episodes + 1):
        env.render = i_episode % 50 == 0

        state, _ = env.reset()
        wall = generator_episode(env, agent[Stage.WALLS], state, eps)

        state, _ = env.advance()
        wall_solver = solver_episode(env, agent[Stage.SOLVER], state, eps)
        wall_reward = 100 if wall_solver[5] else -100
        agent[Stage.WALLS].step(wall[0], wall[1], wall_reward, wall[3], True)

        state, _ = env.advance()
        enemy = generator_episode(env, agent[Stage.ENEMY], state, eps)

        state, _ = env.advance()
        item = generator_episode(env, agent[Stage.ITEM], state, eps)

        state, _ = env.advance()
        solver = solver_episode(env, agent[Stage.SOLVER], state, eps, render_first=True)

        reward = 100 if solver[5] else -100
        agent[Stage.ENEMY].step(enemy[0], enemy[1], reward, enemy[3], True)
        agent[Stage.ITEM].step(item[0], item[1], reward, item[3], True)

        wall_scores_window.append(wall[4])
        enemy_scores_window.append(enemy[4])
        item_scores_window.append(item[4])
        solver_scores_window.append(solver[4] + wall_solver[4])
        eps = max(eps_end, eps_decay * eps)
        print(f"\rEpisode {i_episode}\tAverage Score: "
              f"W: {np.mean(wall_scores_window):.2f} "
              f"E: {np.mean(enemy_scores_window):.2f} "
              f"I: {np.mean(item_scores_window):.2f} "
              f"S: {np.mean(solver_scores_window):.2f}", end="")

        if i_episode % target_update == 0:
            for a in agent.values():
                a.update_target_network()
        if i_episode % 100 == 0:
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(wall_scores_window + enemy_scores_window + item_scores_window + solver_scores_window)))
        # if i_episode % 200 == 0:
        #     for (stage, _) in env.agent_spaces.items():
        #         agent[stage].save(f"models/{stage.name}")


def pretrain_walls(env: GenEnv, agent: D3QNAgent, eps: float = 1.0):
    score = 0
    state, _ = env.reset()
    while True:
        action = agent.act(state, eps=eps)
        next_state, reward, stage_done, _, _ = env.step(action)
        agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        score += reward
        if stage_done:
            break
    return score


def pretrain_enemy(env: GenEnv, wall_agent: D3QNAgent, enemy_agent: D3QNAgent, eps: float = 1.0):
    score = 0
    state, _ = env.reset()
    while True:
        action = wall_agent.act(state, eps=eps)
        next_state, reward, stage_done, _, _ = env.step(action)
        wall_agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        if stage_done:
            break
    state, _ = env.advance()
    state, _ = env.advance()
    while True:
        action = enemy_agent.act(state, eps=eps)
        next_state, reward, stage_done, _, _ = env.step(action)
        enemy_agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        score += reward
        if stage_done:
            break
    return score


def pretrain_items(env: GenEnv, wall_agent: D3QNAgent, enemy_agent: D3QNAgent, item_agent: D3QNAgent, eps: float = 1.0):
    score = 0
    state, _ = env.reset()
    while True:
        action = wall_agent.act(state, eps=eps)
        next_state, reward, stage_done, _, _ = env.step(action)
        wall_agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        if stage_done:
            break
    state, _ = env.advance()
    state, _ = env.advance()
    while True:
        action = enemy_agent.act(state, eps=eps)
        next_state, reward, stage_done, _, _ = env.step(action)
        enemy_agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        if stage_done:
            break
    state, _ = env.advance()
    while True:
        action = item_agent.act(state, eps=eps)
        next_state, reward, stage_done, _, _ = env.step(action)
        item_agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        score += reward
        if stage_done:
            break
    return score


def generator_episode(env: GenEnv, agent: D3QNAgent, state: np.array, eps: float = 1.0):
    score = 0
    while True:
        action = agent.act(state, eps)
        next_state, reward, stage_done, _, _ = env.step(action)
        if stage_done:
            break
        agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        score += reward
    return state, action, reward, next_state, score


def solver_episode(env: GenEnv, agent: D3QNAgent, state: np.array, eps: float = 1.0, render_first: bool = False):
    score = 0
    old_delay = env.game.render_delay
    if render_first:
        env.render = True
        env.game.render_delay = 0
    while True:
        action = agent.act(state, eps)
        next_state, reward, truncated, stage_done, _ = env.step(action)
        env.render = False
        env.game.render_delay = old_delay
        agent.step(state, action, reward, next_state, stage_done)
        state = next_state
        score += reward
        completed = stage_done
        if truncated or stage_done:
            break
    return state, action, reward, next_state, score, completed


def main():
    train(n_episodes=10000)
    print("Score obtained:")


if __name__ == '__main__':
    main()
