import parser, sys, os
from constants import METHODS_DELIMITER, INDENT
from datetime import datetime

f = None

main_name = 'main'
file_name = None
file_extension = None
path_file_name = None

file_head = ['#!/usr/bin/env python3', ' ', '#', '# Generated at ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") , '# ', '']

file_footer = [
    'if __name__ == "__main__":',
    '    _%main_name%()']


def get_file_name(_file_name):
    global path_file_name, file_name, file_extension
    file_name, file_extension = os.path.splitext(os.path.basename(_file_name))
    path_file_name, file_extension = os.path.splitext(_file_name)


def set_main_name(name):
    global file_footer
    file_footer = [w.replace('%main_name%', name) for w in file_footer]


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
    import_section, bodies = parser.parse(_file_name)

    create_file(_file_name)

    write(file_head)
    write(import_section)
    write()
    method_name = "main"
    main_exists = False

    for body in bodies:
        for _function in body['functions']:
            if not main_exists:
                method_name = "main" if _function['name'] is None else _function['name']
                if method_name == 'main':
                    main_exists = True

            write([f'def _{method_name}():'])
            write(_function['lines'], 1)
            write()

    if main_exists:
        set_main_name('main')
    else:
        set_main_name(method_name)
    write(file_footer)

    close_file()


if __name__ == "__main__":
    _file_name = None

    if len(sys.argv) <= 1:
        print('Not enough arguments! ')
        exit()

    generate(sys.argv[1])
