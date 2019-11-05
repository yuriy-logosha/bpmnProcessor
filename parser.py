import sys
import xml.etree.ElementTree as ET
from utils import reverse
from analyzer import search_for_imports_in
from constants import INDENT, NAMESPACE, EXCLUSIVEGATEWAY, TASK, START, END, COLLABORATION, PARTICIPANT, PROCESS, INCOMING, OUTGOING, STANDARDLOOPCHARACTERISTICS
from datetime import datetime

root: ET = None
collaboration: ET = None
participants: ET = None
proc: ET = None
start: ET = None
end: ET = None
target: ET = None

_lines = []
_import_section = []


def read_file(file):
    global root, proc, start, end
    root = ET.parse(file).getroot()
    _collaboration = root.findall(COLLABORATION, NAMESPACE)
    if _collaboration:
        collaboration = _collaboration[0]
        participants = collaboration.findall(PARTICIPANT, NAMESPACE)
    proc = root.findall(PROCESS, NAMESPACE)[0]
    start = proc.findall(START, NAMESPACE)[0]
    end = proc.findall(END, NAMESPACE)[0]


def get_by_id(id):
    global proc
    return proc.findall("./*[@id='"+id+"']", NAMESPACE)[0]


def get_id(el):
    return el.attrib['id']


def get_process_ref(el):
    return el.attrib['processRef']


def get_target_ref(el):
    return el.attrib['targetRef']


def get_name(el):
    return el.attrib['name']


def get_incomings(el):
    return el.findall(INCOMING, NAMESPACE)


def get_outgoings(el):
    return el.findall(OUTGOING, NAMESPACE)


def is_loop(el):
    return len(el.findall(STANDARDLOOPCHARACTERISTICS, NAMESPACE)) > 0


def get_first_outgoing_text(el):
    return get_outgoings(el)[0].text


def get_el_from_flow(el_sequence_flow):
    return get_by_id(get_target_ref(el_sequence_flow))


def get_target(el):
    el_sequence_flow = get_by_id(get_first_outgoing_text(el))
    return get_el_from_flow(el_sequence_flow)


def get_double_incoming(el):
    global end
    t = get_target(el)
    while t and t != end:
        if len(get_incomings(t)) >= 2:
            return t
        t = get_target(el)


def find_friend(me, friend, all=[]):
    global end
    if friend and ((friend in all) or friend is end):
        return False
    if friend and friend is me:
        return True

    all.append(friend)
    friend = get_target(friend)
    return find_friend(me, friend, all)


def iterate_from_node(next_node, _end=None):
    while next_node and next_node != end and next_node != _end:
        resolve_target(next_node, 1)
        next_node = get_target(next_node)


def resolve_target(_target, _indent=0):
    global target, _import_section
    if _target.tag == EXCLUSIVEGATEWAY:
        _lines.append("%sif %s:" % (INDENT * _indent, search_for_imports_in(get_name(_target), _import_section)))
        outgoings = get_outgoings(_target)
        flows = [get_by_id(outgoings[0].text), get_by_id(outgoings[1].text)]
        if 'Y' not in get_name(flows[1]):
            reverse(flows)

        next_node = get_el_from_flow(flows[1])
        endif = get_double_incoming(next_node)
        iterate_from_node(next_node, endif)

        _lines.append('%selse:' % (INDENT * _indent))

        iterate_from_node(get_el_from_flow(flows[0]), endif)
        target = endif

    elif _target.tag == TASK and is_loop(_target):
        _lines.append("%swhile %s:" % (INDENT * _indent, search_for_imports_in(get_name(_target), _import_section)))
        outgoings = get_outgoings(_target)
        out1 = find_friend(_target, get_el_from_flow(get_by_id(outgoings[0].text)))
        # out2 = find_friend(_target, get_el_from_flow(get_by_id(outgoings[1].text)))
        if out1:
            iterate_from_node(get_el_from_flow(get_by_id(outgoings[0].text)), _target)
            target = get_by_id(get_target_ref(get_by_id(outgoings[1].text)))
        else:
            iterate_from_node(get_el_from_flow(get_by_id(outgoings[1].text)), _target)
            target = get_el_from_flow(get_by_id(outgoings[0].text))
    else:
        _name_text = get_name(_target)
        for t in _name_text.split('\n'):
            _lines.append('%s%s' % (INDENT * _indent, t))
        target = get_target(_target)


def parse(file_name):
    global start, end, target, _lines, _import_section
    print('%s Parsing %s' % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), file_name))
    read_file(file_name)

    target = get_target(start)
    while target and target != end:
        resolve_target(target)

    print(*_lines, sep = "\n")
    print('%s %s successfully parsed.' % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), file_name))
    return _import_section, _lines


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pair = sys.argv[1].split('=')
        if len(pair) is 2 and 'file' in pair[0]:
            file = pair[1]
            parse(file)