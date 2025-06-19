class Node:
    # GUI
    xpos: int
    ypos: int
    # Logic
    output_nodes: list
    input_nodes: list
    state: bool
    INPUT_COUNT = 0

    # Constructor
    def __init__(self, xpos: int, ypos: int) -> None:
        self.xpos = xpos
        self.ypos = ypos
        self.input_nodes = [None] * self.INPUT_COUNT
        self.output_nodes = []
        self.state = False
        return

    def update_location(self, xpos: int, ypos: int) -> None:
        self.xpos = xpos
        self.ypos = ypos
        return

    # Add a next node (receives this nodes output)
    def add_output_nodes(self, node: 'Node') -> None:
        self.output_nodes.append(node)
        return

    # Add a next node (receives this nodes output)
    def add_input_node_at(self, node: 'Node', index:int) -> None:
        if index > self.INPUT_COUNT:
            return
        self.input_nodes[index] = node
        return

    # Update boolean (output) state of gate
    def update_state(self) -> None:
        inputs = [input.state for input in self.input_nodes]
        self.state = self.logic_fn(*inputs)

    # Placeholder for the function that will do the logic
    def logic_fn(self, *inputs: bool) -> bool:
        return False # placeholder value

class Input(Node):
    INPUT_COUNT = 0
    def update_state(self, *inputs: bool) -> None:
        if len(inputs) != self.INPUT_COUNT:
            self.state = False
        self.state = inputs[0]

class Output(Node):
    INPUT_COUNT = 1
    def logic_fn(self, *inputs: bool) -> bool:
        if len(inputs) == 0:
            return False
        for input in inputs:
            if input == True:
                return True
        return False

class OR(Node):
    INPUT_COUNT = 2
    def logic_fn(self, *inputs: bool) -> bool:
        if len(inputs) == 0:
            return False
        if len(inputs) == 1:
            return inputs[0] | False
        return inputs[0] | inputs[1]

class AND(Node):
    INPUT_COUNT = 2
    def logic_fn(self, *inputs: bool) -> bool:
        if len(inputs) == 0:
            return False
        if len(inputs) == 1:
            return inputs[0] & False
        return inputs[0] & inputs[1]

class NOT(Node):
    INPUT_COUNT = 1
    def logic_fn(self, *inputs: bool) -> bool:
        if len(inputs) == 0:
            return False
        return (not inputs[0])

def connect_out_to_in_at(output_node: 'Node', input_node: 'Node', input_index: int = 0) -> None:
    output_node.add_output_nodes(input_node)
    input_node.add_input_node_at(output_node, input_index)
    return
