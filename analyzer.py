
_body = []
_import_section = []


def search_for_imports(line, _import_section):
    if line.startswith('import') or (line.startswith('from ') and ' import ' in line):
        _import_section.append(line)
        return None
    return line


def copy(body):
    global _body
    for line in body:
        _body.append(line)


def analyze(body):
    global _body, _import_section

    [search_for_imports(line, _import_section) for line in body]

    copy(body)

    return _import_section, _body


if __name__ == "__main__":
    analyze([])