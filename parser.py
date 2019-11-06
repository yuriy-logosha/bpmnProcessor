import sys
import xml.etree.ElementTree as ET
from utils import reverse, build_function
from analyzer import search_for_imports
from constants import INDENT, NAMESPACE, EXCLUSIVEGATEWAY, TASK, START, END, COLLABORATION, PARTICIPANT, PROCESS, \
    LANESET, LANE, FLOWNODEREF, INCOMING, OUTGOING, STANDARDLOOPCHARACTERISTICS, START_TAG, END_TAG
from datetime import datetime

root: ET = None
target: ET = None

_import_section = []

_files = []

_current = None


def read_file(file):
    global root, _current
    root = ET.parse(file).getroot()
    collaborations = findall(root, COLLABORATION)
    if collaborations:
        participants = findall(collaborations[0], PARTICIPANT)
        for participant in participants:
            proc = by_id(processRef(participant), root)
            _files.append(
                build_file(name(participant),
                           build_functions(proc, name(participant))))

        _current = _files[0]
        return

    proc = findall(root, PROCESS)[0]
    _current = build_file('Noname',
                          build_functions(proc, 'main'))
    _files.append(_current)


def build_file(_name, _functions):
    return {'name': _name, 'functions': _functions}


def build_functions(_proc, _name):
    _functions = []
    __laneset = findall(_proc, LANESET)
    if len(__laneset) > 0:
        _laneset = __laneset[0]
        _lanes = _laneset.findall(LANE, NAMESPACE)
        for _lane in _lanes:
            _refs = build_refs(_lane, _proc)
            _functions.append(
                build_function(
                    name(_lane), _proc=_proc, _start=get_by_tag(START_TAG, _refs), _end=get_by_tag(END_TAG, _refs))
            )
    else:
        _functions.append(build_function(
            _name, _proc=_proc, _start=_proc.findall(START, NAMESPACE)[0], _end=_proc.findall(END, NAMESPACE)[0]))
    return _functions


def build_refs(_lane, _proc):
    refs = []
    _refs = _lane.findall(FLOWNODEREF, NAMESPACE)
    for _ref in _refs:
        _el = _proc.findall("./*[@id='" + _ref.text + "']", NAMESPACE)[0]
        refs.append(_el)
    return refs


def by_id(id, scope=None):
    global _current
    if not scope:
        return _current['proc'].findall("./*[@id='" + id + "']", NAMESPACE)[0]
    return root.findall("./*[@id='"+id+"']", NAMESPACE)[0]


def processRef(el):
    return el.attrib['processRef']


def targetRef(el):
    return el.attrib['targetRef']


def name(el):
    return el.attrib['name'] if 'name' in el.attrib else ""


def get_incomings(el):
    return el.findall(INCOMING, NAMESPACE)


def get_outgoings(el):
    return el.findall(OUTGOING, NAMESPACE)


def is_loop(el):
    return len(el.findall(STANDARDLOOPCHARACTERISTICS, NAMESPACE)) > 0


def get_first_outgoing_text(el):
    return get_outgoings(el)[0].text


def el_from_flow(el_sequence_flow):
    return by_id(targetRef(el_sequence_flow))


def get_target(el):
    el_sequence_flow = by_id(get_first_outgoing_text(el))
    return el_from_flow(el_sequence_flow)


def get_double_incoming(el):
    global _current
    t = get_target(el)
    while t and t != _current['end']:
        if len(get_incomings(t)) >= 2:
            return t
        t = get_target(el)


def find_friend(me, friend, all=[]):
    global _current
    if friend and ((friend in all) or friend is _current['end']):
        return False
    if friend and friend is me:
        return True

    all.append(friend)
    friend = get_target(friend)
    return find_friend(me, friend, all)


def iterate_from_node(next_node, _end=None):
    while next_node and next_node != _current['end'] and next_node != _end:
        resolve_target(next_node, 1)
        next_node = get_target(next_node)


def resolve_target(_target, _indent=0):
    global target, _import_section, _current
    if _target.tag == EXCLUSIVEGATEWAY:
        _current['lines'].append("%sif %s:" % (INDENT * _indent, name(_target)))
        outgoings = get_outgoings(_target)
        flows = [by_id(outgoings[0].text), by_id(outgoings[1].text)]
        if 'Y' not in name(flows[1]):
            reverse(flows)

        next_node = el_from_flow(flows[1])
        endif = get_double_incoming(next_node)
        iterate_from_node(next_node, endif)

        _current['lines'].append('%selse:' % (INDENT * _indent))

        iterate_from_node(el_from_flow(flows[0]), endif)
        target = endif

    elif _target.tag == TASK and is_loop(_target):
        _current['lines'].append("%swhile %s:" % (INDENT * _indent, name(_target)))
        outgoings = get_outgoings(_target)
        out1 = find_friend(_target, el_from_flow(by_id(outgoings[0].text)))
        if out1:
            start_iterate_node = el_from_flow(by_id(outgoings[0].text))
            to_target = by_id(targetRef(by_id(outgoings[1].text)))
        else:
            start_iterate_node = el_from_flow(by_id(outgoings[1].text))
            to_target = el_from_flow(by_id(outgoings[0].text))

        iterate_from_node(start_iterate_node, _target)
        target = to_target

    else:
        _name_text = name(_target)
        for _text_line in _name_text.split('\n'):
            _text = search_for_imports(_text_line, _import_section)
            if _text:
                _current['lines'].append('%s%s' % (INDENT * _indent, _text))
        target = get_target(_target)


def parse(file_name):
    global _functions, _current, target, _import_section
    print('%s Parsing %s' % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), file_name))
    read_file(file_name)

    for _f in _files:
        for _func in _f['functions']:
            _current = _func
            target = get_target(_func['start'])
            while target and target != _func['end']:
                resolve_target(target)

            print('Method: %s' % _func['name'])
            print(*_func['lines'], sep="\n")

    print('%s %s successfully parsed.' % (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), file_name))
    return _import_section, _files


def findall(el, key):
    return el.findall(key, NAMESPACE)


def get_by_tag(tag_name, _refs):
    for _ref in _refs:
        if tag_name in _ref.tag:
            return _ref
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pair = sys.argv[1].split('=')
        if len(pair) is 2 and 'file' in pair[0]:
            file = pair[1]
            parse(file)