# import gym
#
# envs = gym.envs.registry
# print(envs)
# print('Total envs available:', len(envs))
#
# 'CartPole-v0': EnvSpec(id='CartPole-v0', entry_point='gym.envs.classic_control.cartpole:CartPoleEnv', reward_threshold=195.0, nondeterministic=False, max_episode_steps=200, order_enforce=True, autoreset=False, disable_env_checker=False, apply_api_compatibility=False, kwargs={}, namespace=None, name='CartPole', version=0)
#
from time import sleep

import gym

env = gym.make('InvertedPendulum-v4')
# Uncomment following line to save video of our Agent interacting in this environment
# This can be used for debugging and studying how our agent is performing
# env = gym.wrappers.Monitor(env, './video/', force = True)
t = 0
while True:
    t += 1
    observation = env.reset()
    env.render()
    sleep(3)
    print(observation)
    action = env.action_space.sample()
    observation = env.step(action)
    reward = env.step(action)
    done = env.step(action)
    info = env.step(action)
    if done:
        print("Episode finished after {} timesteps".format(t + 1))
        sleep(10)
    break
env.close()

# import gym
# env = gym.make('CartPole-v1')
# env.reset()
#
# for i in range(1000):
#     env.step(env.action_space.sample())
#     env.render()
