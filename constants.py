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
COLLABORATION = 'bpmn:collaboration'
PARTICIPANT = 'bpmn:participant'
PROCESS = 'bpmn:process'
INCOMING = 'bpmn:incoming'
OUTGOING = 'bpmn:outgoing'
STANDARDLOOPCHARACTERISTICS = 'bpmn:standardLoopCharacteristics'