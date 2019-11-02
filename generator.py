import parser, sys
from constants import METHODS_DELIMITER, INDENT

f = None

main_name = 'main'

file_head = ['#!/usr/bin/env python3']

main_method = ['def _%main_name%():']

default_lines = [
    'if __name__ == "__main__":',
    '    _%main_name%()']


def set_main_name(name=main_name):
    global main_name, main_method, default_lines
    main_name = name
    main_method = [w.replace('%main_name%', main_name) for w in main_method]
    default_lines = [w.replace('%main_name%', main_name) for w in default_lines]


def create_file(file_name):
    global f
    f = open(file_name + ".py", "w+")
    print(file_name + ".py created!")


def close_file():
    global f
    f.close()


def write(lines=METHODS_DELIMITER, lvl=0):
    [f.write("%s%s\r\n" % (INDENT * lvl, line)) for line in lines]


def generate(_from, _file_name):
    set_main_name()

    import_section, body = parser.parse(_from + _file_name + '.bpmn')

    create_file(_from + _file_name)

    write(file_head)
    write(import_section)
    write()

    write(main_method)
    write(body, 1)
    write()
    write(default_lines)

    close_file()


if __name__ == "__main__":
    _from = None
    _file_name = None

    if len(sys.argv) <= 2:
        print('Not enough arguments! ')
        exit()

    for arg in sys.argv:
        pair = arg.split('=')
        if len(pair) is 2 and 'from' in pair[0]:
            _from = pair[1]
        if len(pair) is 2 and 'file-name' in pair[0]:
            _file_name = pair[1]

    if _from and _file_name:
        generate(_from, _file_name)
