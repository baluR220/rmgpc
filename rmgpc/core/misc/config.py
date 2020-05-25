'''Different configuration options.'''
import os


PC_MODEL = 'Raspberry Pi 3b +'

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

SEQ_DIR = os.path.join(WORK_DIR, 'sequences')

PIN_SET = [str(x) for x in range(2, 28)]

INTERPRETER = '/var/www/venv/bin/python'
