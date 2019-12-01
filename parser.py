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

build_file =    lambda _name, _functions: {'name': _name, 'functions': _functions, 'lines':[]}
processRef =    lambda el: el.attrib['processRef']
targetRef =     lambda el: el.attrib['targetRef']
name =          lambda el: el.attrib['name'] if 'name' in el.attrib else ""
get_incomings = lambda el: el.findall(INCOMING, NAMESPACE)
get_outgoings = lambda el: el.findall(OUTGOING, NAMESPACE)
is_loop =       lambda el:len(el.findall(STANDARDLOOPCHARACTERISTICS, NAMESPACE)) > 0
el_from_flow =  lambda el_sequence_flow: by_id(targetRef(el_sequence_flow))
findall =       lambda el, key: el.findall(key, NAMESPACE)
get_target =    lambda el: el_from_flow(by_id(get_first_outgoing_text(el)))
get_first_outgoing_text =   lambda el: get_outgoings(el)[0].text
el_from_flow_by_id =        lambda id: el_from_flow(by_id(id))


def build_functions(_proc, _name):
    _functions = []
    __laneset = findall(_proc, LANESET)
    if len(__laneset) > 0:
        _laneset = __laneset[0]
        _lanes = _laneset.findall(LANE, NAMESPACE)
        for _lane in _lanes:
            _refs = build_refs(_lane, _proc)
            _functions.append(build_function(name(_lane), _proc, get_by_tag(START_TAG, _refs), get_by_tag(END_TAG, _refs)))
    else:
        _functions.append(build_function(_name, _proc, findall(_proc, START)[0], findall(_proc, END)[0]))
    return _functions


def read_file(_file):
    global root, _current
    root = ET.parse(_file).getroot()
    collaborations = findall(root, COLLABORATION)
    if collaborations:
        participants = findall(collaborations[0], PARTICIPANT)
        for participant in participants:
            proc = by_id(processRef(participant), root)
            _files.append(build_file(name(participant), build_functions(proc, name(participant))))

        _current = _files[0]
        return

    proc = findall(root, PROCESS)[0]
    _current = build_file('Noname', build_functions(proc, 'main'))
    _files.append(_current)


def build_refs(_lane, _proc):
    refs = []
    _refs = _lane.findall(FLOWNODEREF, NAMESPACE)
    for _ref in _refs:
        _el = findall(_proc, f"./*[@id='{_ref.text}']")[0]
        refs.append(_el)
    return refs


def by_id(id, scope=None):
    global _current, root
    if not scope:
        return _current['proc'].findall(f"./*[@id='{id}']", NAMESPACE)[0]
    return root.findall(f"./*[@id='{id}']", NAMESPACE)[0]
        

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


def iterate_from_node(next_node, _end=None, idx=0):
    global target
    while next_node and next_node != _current['end'] and next_node != _end:
        resolve_target(next_node, idx + 1)
        if next_node != target:
            next_node = target
        else:
            next_node = _end


def resolve_target(_target, _indent=0):
    global target, _import_section, _current
    outgoings = get_outgoings(_target)
    if _target.tag == EXCLUSIVEGATEWAY:
        _current['lines'].append("%sif %s:" % (INDENT * _indent, name(_target)))
        flows = [by_id(outgoings[0].text), by_id(outgoings[1].text)]
        if 'Y' not in name(flows[1]):
            reverse(flows)

        next_node = el_from_flow(flows[1])
        endif = get_double_incoming(next_node)
        target = endif
        iterate_from_node(next_node, endif, _indent)

        if el_from_flow(flows[0]) != endif:
            _current['lines'].append('%selse:' % (INDENT * _indent))
            iterate_from_node(el_from_flow(flows[0]), endif, _indent)

    elif _target.tag == TASK and is_loop(_target):
        _name = name(_target)
        tmplt = '%s%s:' % (INDENT * _indent, _name) if "for " in _name and " in " in _name else "%swhile %s:" % (INDENT * _indent, _name)
        _current['lines'].append(tmplt)
        el0 = el_from_flow_by_id(outgoings[0].text)
        el1 = el_from_flow_by_id(outgoings[1].text) if len(outgoings) > 1 else None
        if len(outgoings) == 2:
            loop0 = is_loop(el0)
            loop1 = is_loop(el1)
            if loop0 or loop1:
                iterate_from_node(el0 if loop0 else el1, _target, _indent + 1)
                target = el1 if loop0 else el0
            else:
                out1 = find_friend(_target, el0)
                iterate_from_node(el0 if out1 else el1, _target, _indent + 1)
                target = el1 if out1 else el0
        elif len(outgoings) == 1:
            iterate_from_node(el0, _target, _indent + 1)
    else:
        _name_text = name(_target)
        for _text_line in _name_text.split('\n'):
            _text = search_for_imports(_text_line, _import_section)
            if _text:
                _current['lines'].append('%s%s' % (INDENT * _indent, _text))
        target = get_target(_target)


def parse(file_name):
    global _current, target, _import_section
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