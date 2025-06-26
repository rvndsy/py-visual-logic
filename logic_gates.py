from enum import Enum

class GateType(Enum):
    INPUT = 0
    OUTPUT = 1
    AND = 2
    OR = 3
    NOT = 4
    XOR = 5
    NOR = 6
    NAND = 7
GateInputCount = {
    GateType.INPUT: 0,
    GateType.OUTPUT: 1,
    GateType.AND: 2,
    GateType.OR: 2,
    GateType.NOT: 1,
    GateType.XOR: 2,
    GateType.NOR: 2,
    GateType.NAND: 2,
}

class Node:
    outputNodes: list[list]
    inputNodes: list[list]
    state: bool
    INPUT_COUNT = 1
    OUTPUT_COUNT = 1
    GATE_TYPE: GateType

    # Constructor
    def __init__(self) -> None:
        self.inputNodes = [[] for i in range(self.INPUT_COUNT)]
        self.outputNodes = [[]]
        self.state = False
        return

    # Add a next node (receives this nodes output)
    def addOutputNode(self, node: 'Node') -> None:
        self.outputNodes[0].append(node)
        return

    # Add a next node (receives this nodes output)
    def addInputNodeAt(self, node: 'Node', index:int) -> None:
        if index > self.INPUT_COUNT or index < 0:
            return
        self.inputNodes[index].append(node)
        return

    # Remove output node
    def removeOutputNode(self, node: 'Node') -> None:
        self.outputNodes[0].remove(node)
        return

    # Remove input node
    def removeInputNodeAt(self, node: 'Node | None', index: int = 0) -> None:
        if index > self.INPUT_COUNT or index < 0:
            return
        if node:
            self.inputNodes[index].remove(node)
        return

    # Update boolean (output) state of gate
    def updateState(self, *inputs: bool) -> None:
        inputStates = []
        for singleInputList in self.inputNodes:
            singleInputListOrState = False
            for input in singleInputList:
                if input.state:
                    singleInputListOrState = True
                    break
            inputStates.append(singleInputListOrState)
        self.state = self.logicFn(*inputStates)
        print(self, " -> ", self.state)
        print(self.inputNodes)
        print(inputStates)

    # Placeholder for the function that will do the logic
    def logicFn(self, *inputs: bool) -> bool:
        return self.state # placeholder value

class Input(Node):
    GATE_TYPE = GateType.INPUT
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def updateState(self, *inputs: bool) -> None:
        if len(inputs) != 1:
            return
        self.state = inputs[0]
        return

class Output(Node):
    GATE_TYPE = GateType.OUTPUT
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    outputNodes = []
    def logicFn(self, *inputs: bool) -> bool:
        return inputs[0]

class OR(Node):
    GATE_TYPE = GateType.OR
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logicFn(self, *inputs: bool) -> bool:
        return inputs[0] | inputs[1]

class AND(Node):
    GATE_TYPE = GateType.AND
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logicFn(self, *inputs: bool) -> bool:
        return inputs[0] & inputs[1]

class NOT(Node):
    GATE_TYPE = GateType.NOT
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    state = True
    def logicFn(self, *inputs: bool) -> bool:
        return (not inputs[0])

class XOR(Node):
    GATE_TYPE = GateType.XOR
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logicFn(self, *inputs: bool) -> bool:
        return inputs[0] ^ inputs[1]

class NOR(Node):
    GATE_TYPE = GateType.NOR
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logicFn(self, *inputs: bool) -> bool:
        return not (inputs[0] or inputs[1])

class NAND(Node):
    GATE_TYPE = GateType.NAND
    INPUT_COUNT = GateInputCount[GATE_TYPE]
    def logicFn(self, *inputs: bool) -> bool:
        return not (inputs[0] and inputs[1])

#class BUFFER(Node):
#    GATE_TYPE = GateType.BUFFER
#    INPUT_COUNT = GateInputCount[GATE_TYPE]
#    delayedInputState: bool = False
#    def logicFn(self, *inputs: bool) -> bool:
#        self.state = self.delayedInputState
#        self.delayedInputState = inputs[0]
#        return self.state

def connectOutToInAt(outputNode: 'Node', inputNode: 'Node', inputIndex: int = 0) -> None:
    outputNode.addOutputNode(inputNode)
    inputNode.addInputNodeAt(outputNode, inputIndex)
    return

def removeOutAndInAt(outputNode: 'Node', inputNode: 'Node', inputIndex: int = 0) -> None:
    outputNode.removeOutputNode(inputNode)
    inputNode.removeInputNodeAt(outputNode, inputIndex)
    return

# DFS (loops are going to be a problem...)
def recursiveUpdate(start_node: 'Node') -> None:

    def recursive_update_single(node: 'Node') -> None:
        if node is None:
            return
        node.updateState()
        for nodeList in node.outputNodes:
            for node in nodeList:
                recursive_update_single(node)
        return

    start_node.updateState()
    recursive_update_single(start_node);
    return

GateClass = {
    GateType.INPUT: Input,
    GateType.OUTPUT: Output,
    GateType.AND: AND,
    GateType.OR: OR,
    GateType.NOT: NOT,
    GateType.XOR: XOR,
    GateType.NOR: NOR,
    GateType.NAND: NAND,
}
