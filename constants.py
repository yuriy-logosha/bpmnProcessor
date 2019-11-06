INDENT = " " * 4
METHODS_DELIMITER=["", ""]
NAMESPACE = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
      'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
      'dc': 'http://www.omg.org/spec/DD/20100524/DC',
      'di': 'http://www.omg.org/spec/DD/20100524/DI'}

EXCLUSIVEGATEWAY = '{http://www.omg.org/spec/BPMN/20100524/MODEL}exclusiveGateway'
TASK = '{http://www.omg.org/spec/BPMN/20100524/MODEL}task'

START = "bpmn:startEvent"
END = "bpmn:endEvent"
START_TAG = "{http://www.omg.org/spec/BPMN/20100524/MODEL}startEvent"
END_TAG = "{http://www.omg.org/spec/BPMN/20100524/MODEL}endEvent"

COLLABORATION = 'bpmn:collaboration'
PARTICIPANT = 'bpmn:participant'
PROCESS = 'bpmn:process'
LANESET = 'bpmn:laneSet'
LANE = 'bpmn:lane'
FLOWNODEREF = 'bpmn:flowNodeRef'
INCOMING = 'bpmn:incoming'
OUTGOING = 'bpmn:outgoing'
STANDARDLOOPCHARACTERISTICS = 'bpmn:standardLoopCharacteristics'