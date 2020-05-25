'''Set pin modes acording to saved pin layout and modes.
'''
import os
from config import WORK_DIR


def set_mode(pin, state):
    '''Set pin mode

    in: pin number, pin mode.
    out: command for raspbian biult-in 'gpio' program.

    '''
    if state == 'I':
        state = 'in'
    elif state == 'O':
        state = 'out'
    else:
        state = 'in'
    os.system('gpio -g mode %s %s' % (pin, state))


if __name__ == '__main__':
    path_file = os.path.join(WORK_DIR, 'set_mode.txt')
    with open(path_file, 'r') as file:
        for line in file.readlines():
            pin, state = line.strip().split(' ')
            set_mode(pin, state)
