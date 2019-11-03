import parser, sys, os
from constants import METHODS_DELIMITER, INDENT
from datetime import datetime

f = None

main_name = 'main'
file_name = None
file_extension = None
path_file_name = None

file_head = ['#!/usr/bin/env python3', ' ', '#', '# Generated at ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") , '# ', '']

main_method = ['def _%main_name%():']

default_lines = [
    'if __name__ == "__main__":',
    '    _%main_name%()']


def get_file_name(_file_name):
    global path_file_name, file_name, file_extension
    file_name, file_extension = os.path.splitext(os.path.basename(_file_name))
    path_file_name, file_extension = os.path.splitext(_file_name)


def set_main_name(name=main_name):
    global main_name, main_method, default_lines
    main_name = name
    main_method = [w.replace('%main_name%', main_name) for w in main_method]
    default_lines = [w.replace('%main_name%', main_name) for w in default_lines]


def create_file(_file_name):
    global f, path_file_name
    f = open(path_file_name + ".py", "w+")
    print("%s %s.py created!" % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), path_file_name))


def close_file():
    global f
    f.close()


def write(lines=METHODS_DELIMITER, lvl=0):
    [f.write("%s%s\r\n" % (INDENT * lvl, line)) for line in lines]


def generate(_file_name):
    global file_name
    get_file_name(_file_name)
    set_main_name(file_name)
    import_section, body = parser.parse(_file_name)

    create_file(_file_name)

    write(file_head)
    write(import_section)
    write()

    write(main_method)
    write(body, 1)
    write()
    write(default_lines)

    close_file()


if __name__ == "__main__":
    _file_name = None

    if len(sys.argv) <= 1:
        print('Not enough arguments! ')
        exit()

    generate(sys.argv[1])
