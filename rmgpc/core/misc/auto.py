'''Put auto trigger in listen state and wait for propriate input.
If relief is specified do relief on propriate input.

'''
import sys
import os
from subprocess import Popen, check_output

from config import SEQ_DIR


def loop_proc(pin, state, path):
    '''Loop function with no relief.

    in: input pin number, input pin state, path to bash script.
    out: new listen process.

    '''
    state_changed = True
    while True:
        p = check_output(['gpio', '-g', 'read', pin])
        if (state in p.decode('utf-8')):
            if state_changed:
                state_changed = False
                p = Popen(['bash', path])
                p.wait
        else:
            state_changed = True


def loop_proc_relief(pin, state, path, relief):
    '''Loop function with relief.

    in: input pin number, input pin state, path to bash script, path to
    script done on relief.
    out: new listen process.

    '''
    state_changed = True
    do_relief = False
    while True:
        p = check_output(['gpio', '-g', 'read', pin])
        if (state in p.decode('utf-8')):
            if state_changed:
                state_changed = False
                do_relief = True
                p = Popen(['bash', path])
                p.wait
        else:
            state_changed = True
            if do_relief:
                do_relief = False
                p = Popen(['bash', relief])
                p.wait


if __name__ == '__main__':

    _seq_name = sys.argv[1]
    _input_pin = sys.argv[2]
    _state = sys.argv[3]
    _relief = sys.argv[4]

    if _state == 'L':
        state = '0'
    else:
        state = '1'

    name = _seq_name + '.sh'
    path_file = os.path.join(SEQ_DIR, name)

    if _relief != 'no_relief':
        relief = _relief + '.sh'
        relief_path = os.path.join(SEQ_DIR, relief)
        loop_proc_relief(_input_pin, state, path_file, relief_path)
    else:
        loop_proc(_input_pin, state, path_file)
