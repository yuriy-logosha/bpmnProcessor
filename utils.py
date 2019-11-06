
def build_function(_name=None, _proc=None, _start=None, _end=None) -> object:
    return {'name': _name, 'proc': _proc, 'start': _start, 'end': _end, 'lines': []}


def reverse(i):
    a, b = 0, 1
    i[b], i[a] = i[a], i[b]