
_body = []
_import_section = []


def search_for_imports_in(line, _import_section):
    if '.' in line:
        left = line.split('.')[0]
        right = left.split(' ')[len(left.split(' '))-1|0]
        _import_section.append('import %s' % (right))
    return line


def copy(body):
    global _body
    for line in body:
        _body.append(line)


def analyze(body):
    global _body, _import_section

    [search_for_imports_in(line, _import_section) for line in body]

    copy(body)

    return _import_section, _body


if __name__ == "__main__":
    analyze([])