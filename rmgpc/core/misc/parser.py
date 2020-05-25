'''Check content of sequence to follow some rules in order to parse it
correctly on success.
'''
import os
from . import config

_pins = config.PIN_SET
_commands_list = ['on', 'off', 'imp']
_spec_symbols = ['/', '?', '<', '>', '*', '\\', '%', '@']


def _transcribe(command, pin, time=0):
    '''After succesfull spell check append parsed commands to script file.

    in: command, pin number, time for impiulse command.
    out: commands for raspbian built-in 'gpio' program.

    '''
    if command == 'on':
        out = '''gpio -g write %s 1''' % pin
    elif command == 'off':
        out = '''gpio -g write %s 0''' % pin
    elif command == 'imp':
        out = '''if gpio -g read %s | grep 0 > /dev/null
then gpio -g write %s 1
sleep %s
gpio -g write %s 0
else gpio -g write %s 0
sleep %s
gpio -g write %s 1
fi''' % (pin, pin, time, pin, pin, time, pin)
    else:
        raise Exception('Wrong command passed spell check!')
    return out


def spell_check(data, name):
    '''Check spell of user input: new sequence name and its content.

    in: sequence content, sequence name.
    out: if mistake was detected then false flag and wrong part are returned,
    if no mistakes were detected data is passed to _transcribe function.

    '''
    for char in name:
        if char in _spec_symbols:
            check_passed = False
            mistake = ', '.join(_spec_symbols)
            return (check_passed, mistake)
    name = name.replace(' ', '_') + '.sh'
    path_file = os.path.join(config.SEQ_DIR, name)
    try:
        data = data.strip().split(',')
    except Exception:
        check_passed, mistake = False, data[:5]
        return (check_passed, mistake)
    else:
        with open(path_file, 'w') as file:
            for line_raw in data:
                line = line_raw.strip().split(' ')
                command = line[0]
                if command not in _commands_list:
                    check_passed = False
                    mistake = line_raw
                    return (check_passed, mistake)
                else:
                    line = line[1].strip().split('_')
                    pin = line[0]
                    if pin not in _pins:
                        check_passed = False
                        mistake = line_raw
                        return (check_passed, mistake)
                    else:
                        if len(line) > 1:
                            if command != 'imp':
                                check_passed = False
                                mistake = line_raw
                                return (check_passed, mistake)
                            else:
                                time = line[1]
                                if not time.isdigit():
                                    check_passed = False
                                    mistake = line_raw
                                    return (check_passed, mistake)
                                else:
                                    if int(time) < 0:
                                        check_passed = False
                                        mistake = line_raw
                                        return (check_passed, mistake)
                                    else:
                                        out = _transcribe(command, pin, time)
                                        print(out, file=file)
                        else:
                            if command == 'imp':
                                check_passed = False
                                mistake = line_raw
                                return (check_passed, mistake)
                            else:
                                out = _transcribe(command, pin)
                                print(out, file=file)
        check_passed = True
        mistake = ''
        return (check_passed, mistake)
