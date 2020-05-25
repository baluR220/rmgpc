'''Start auto trigger's litener process via daemon on startup.'''
import os
import subprocess
from config import WORK_DIR, INTERPRETER


def run_prog():
    '''Start new auto trigger's listener process as stated in auto.txt file.'''
    path_file = os.path.join(WORK_DIR, 'auto.txt')
    prog = os.path.join(WORK_DIR, 'auto.py')
    with open(path_file, 'r') as file:
        for line in file.readlines():
            line = line.strip().split(' ')
            _seq_name = line[0]
            _input_pin = line[1]
            _state = line[2]
            _relief = line[3]
            subprocess.Popen([
                INTERPRETER, prog, _seq_name, _input_pin, _state, _relief])


if __name__ == '__main__':
    run_prog()
