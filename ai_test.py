import time
import numpy as np
from aworld_client_core import Core, config

core = Core()
actions = [
        'up',
        'left',
        'right',
        'down',
        'spacebar',
        'i'
        ]


def make_param(action_name):
    optional = {}
    if action_name == "up":
        optional["speed"] = 0.025
    elif action_name == "left":
        optional["angle"] = 0.01
    elif action_name == "right":
        optional["angle"] = 0.01
    elif action_name == "down":
        optional["speed"] = 0.005
    elif action_name == "i":
        optional["item_index"] = 0
    return optional

def think():
    cid = core.data.character_id
    probs = np.random.rand(len(actions))
    if cid and cid in core.data.characters:
        pc = core.data.characters[cid]
        terrain = core.data.terrain
        x = pc['x']
        y = pc['y']
        angle = pc['angle']
        fx = int(np.floor(x + np.cos(angle) * 0.025))
        fy = int(np.floor(y + np.sin(angle) * 0.025))
        if terrain.map[fy][fx] == 0:
            probs[actions.index('up')] = np.inf
        else:
            probs[actions.index('right')] = np.inf
    action = actions[probs.argmax()]
    return action

if __name__ == '__main__':
    core.spawn_thread(secure=False)
    core.send_key('login')

    while True:
        action = think()
        core.send_key(action, True, make_param(action))
        time.sleep(0.01)
        core.send_key(action, False)
