from enum import Enum

class GateType(Enum):
    INPUT = 0
    OUTPUT = 1
    AND = 2
    OR = 3
    NOT = 4
GateInputCount = {
    GateType.INPUT: 0,
    GateType.OUTPUT: 1,
    GateType.AND: 2,
    GateType.OR: 2,
    GateType.NOT: 1,
}
GateStrings = {
    GateType.INPUT: "IN",
    GateType.OUTPUT: "OUT",
    GateType.AND: "AND",
    GateType.OR:  "OR",
    GateType.NOT: "NOT",
}

class Node:
    outputNodes: list
    inputNodes: list
    state: bool
    INPUT_COUNT = 0
    GATE_TYPE: GateType

    # Constructor
    def __init__(self, xpos: int, ypos: int) -> None:
        self.xpos = xpos
        self.ypos = ypos
        self.inputNodes = [None] * self.INPUT_COUNT
        self.outputNodes = []
        self.state = False
        return

    # TODO: Thing that doesn't belong here
    def update_location(self, xpos: int, ypos: int) -> None:
        self.xpos = xpos
        self.ypos = ypos
        return

    # Add a next node (receives this nodes output)
    def add_output_nodes(self, node: 'Node') -> None:
        self.outputNodes.append(node)
        return

    # Add a next node (receives this nodes output)
    def add_input_node_at(self, node: 'Node', index:int) -> None:
        if index > self.INPUT_COUNT:
            return
        self.inputNodes[index] = node
        return

    # Update boolean (output) state of gate
    def update_state(self) -> None:
        if self is None: return
        inputs = []
        for input in self.inputNodes:
            if input is None:
                inputs.append(False)
            else:
                inputs.append(input.state)
        self.state = self.logic_fn(*inputs)

    # Placeholder for the function that will do the logic
    def logic_fn(self, *inputs: bool) -> bool:
        return False # placeholder value

class Input(Node):
    GATE_TYPE = GateType.INPUT
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def update_state(self, *inputs: bool) -> None:
        if len(inputs) != 1:
            return
        self.state = inputs[0]
        return

class Output(Node):
    GATE_TYPE = GateType.OUTPUT
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logic_fn(self, *inputs: bool) -> bool:
        return inputs[0]

class OR(Node):
    GATE_TYPE = GateType.OR
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logic_fn(self, *inputs: bool) -> bool:
        return inputs[0] | inputs[1]

class AND(Node):
    GATE_TYPE = GateType.AND
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logic_fn(self, *inputs: bool) -> bool:
        return inputs[0] & inputs[1]

class NOT(Node):
    GATE_TYPE = GateType.NOT
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logic_fn(self, *inputs: bool) -> bool:
        return (not inputs[0])

def connect_out_to_in_at(output_node: 'Node', input_node: 'Node', input_index: int = 0) -> None:
    output_node.add_output_nodes(input_node)
    input_node.add_input_node_at(output_node, input_index)
    return

# DFS (loops are going to be a problem...)
def recursive_update(start_node: 'Node') -> None:

    def recursive_update_single(node: 'Node') -> None:
        if node is None or node is start_node:
            return
        print(type(node), ": ", node.state)
        node.update_state()
        for next_node in node.outputNodes:
            recursive_update_single(next_node)
        return

    recursive_update_single(start_node);
    return

