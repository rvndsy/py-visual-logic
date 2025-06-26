from logic_gates import *
import uuid, json, sys, os
from PyQt6.QtCore import Qt, QSize, QLineF, QRectF, QPointF
from PyQt6.QtGui import ( 
    QAction,
    QPixmap,
    QPainter,
    QPen,
    QColor,
    QBrush,
    QPainterPath,
    QIcon,
)
from PyQt6.QtWidgets import (
    QGraphicsTextItem,
    QMainWindow,
    QToolBar,
    QFileDialog,
    QMenu,
    QToolButton,
)
from PyQt6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsEllipseItem,
)

def resolvePath(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path

PIXMAP_FILES_DICT = {
    GateType.INPUT: resolvePath("symbols/IN.png"),
    GateType.OUTPUT: resolvePath("symbols/OUT.png"),
    GateType.AND: resolvePath("symbols/AND_ANSI.png"),
    GateType.OR:  resolvePath("symbols/OR_ANSI.png"),
    GateType.NOT: resolvePath("symbols/NOT_ANSI.png"),
    GateType.XOR: resolvePath("symbols/XOR_ANSI.png"),
    GateType.NOR: resolvePath("symbols/NOR_ANSI.png"),
    GateType.NAND: resolvePath("symbols/NAND_ANSI.png"),
}

class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PyQt App")

        self.scene = Scene(0, 0, 0, 0)

        actionToolbar = QToolBar(parent=self)
        actionToolbar.setIconSize(QSize(16, 16))
        self.addToolBar(actionToolbar)
        openFileBtn = QAction("Save file", self)
        openFileBtn.triggered.connect(self.toolbarSaveFileBtnClicked)
        actionToolbar.addAction(openFileBtn)
        loadFileBtn = QAction("Load file", self)
        loadFileBtn.triggered.connect(self.toolbarLoadFileBtnClicked)
        actionToolbar.addAction(loadFileBtn)

        exampleMenuBtn = QToolButton()
        exampleMenuBtn.setText("Load example")
        exampleMenuBtn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        exampleMenuBtn.setMenu(ExampleMenu(scene=self.scene))
        actionToolbar.addWidget(exampleMenuBtn)

        clearSceneBtn = QAction("Clear scene", self)
        clearSceneBtn.triggered.connect(lambda: self.scene.clear())
        actionToolbar.addAction(clearSceneBtn)

        logicGateToolbar = QToolBar(parent=self)
        logicGateToolbar.setIconSize(QSize(64, 64))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, logicGateToolbar)

        for gate_type in GateType:
            icon = QIcon(PIXMAP_FILES_DICT[gate_type])
            action = QAction(icon, gate_type.name.capitalize(), self)
            action.triggered.connect(lambda checked, gt=gate_type: self.logicGateBtnClicked(gt))
            logicGateToolbar.addAction(action)


        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(view)
        return

    def toolbarSaveFileBtnClicked(self, s) -> None:
        fileName = QFileDialog.getSaveFileName(
            self,
            caption="Save File",
            #filter="JSON Files (*.json)",
        )
        print("Selected file: ", fileName)
        if fileName[0] is not '':
            saveNodeGraph(self.scene, fileName[0])

    def toolbarLoadFileBtnClicked(self, s) -> None:
        fileName = QFileDialog.getOpenFileName(
            self,
            caption="Open File",
            #filter="JSON Files (*.json)",
        )
        print("Selected file: ", fileName)
        if fileName[0] is not '':
            loadNodeGraph(self.scene, fileName[0])

    def logicGateBtnClicked(self, gate_type):
        print(f"Gate button clicked: {gate_type}")
        self.scene.addNodeItem(DraggableNode(gate_type, int(self.scene.width()/2), int(self.scene.height()/2)))

    #def updateScene(self):
    #    for item in self.scene.items():
    #        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    #        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

# https://stackoverflow.com/questions/65831884/how-to-connect-two-qgraphicsitem-by-drawing-line-between-them-using-mouse
class ConnectionLine(QGraphicsLineItem):
    LINE_WIDTH = 4
    LINE_COLOR = QColor("black")
    lineBrush = QBrush(QColor("red"))
    start: 'ConnectionPoint | None'
    end: 'ConnectionPoint | None'
    def __init__(self, p1: 'ConnectionPoint', p2: 'ConnectionPoint | QPointF'):
        super().__init__()
        self.start = p1
        self.end = None
        if isinstance(p2, QPointF):
            self._line = QLineF(p1.scenePos(), p2)
        else:
            self._line = QLineF(p1.scenePos(), p2.scenePos())
        self.setLine(self._line)
        self.setPenParams(self.LINE_COLOR, self.LINE_WIDTH)

    def connectionPoints(self) -> tuple['ConnectionPoint | None', 'ConnectionPoint | None']:
        return self.start, self.end

    def setPenParams(self, color: QColor, width: int) -> None:
        pen = QPen(color)
        pen.setWidth(width)
        self.setPen(pen)
        return

    def setP2(self, p2):
        self._line.setP2(p2)
        self.setLine(self._line)

    def setStart(self, start):
        self.start = start
        self.updateLine(start)

    def setEnd(self, end):
        self.end = end
        self.updateLine(end)

    def updateLine(self, source):
        if source == self.start:
            self._line.setP1(source.scenePos())
        else:
            self._line.setP2(source.scenePos())
        self.setLine(self._line)

    def getOppositePointOf(self, point: 'ConnectionPoint'):
        if self.start != point:
            return self.start
        else:
            return self.end

class ConnectionPoint(QGraphicsEllipseItem):
    DIAMETER = 10
    lines: list[ConnectionLine]
    pointBrush = QBrush(QColor("black"))

    isInput: bool
    logicGateNode: Node
    orderIndex: int
    parentDraggableNode: 'DraggableNode'

    def __init__(self, parent: 'DraggableNode', isInput, orderIndex):
        super().__init__(-self.DIAMETER/2, -self.DIAMETER/2, self.DIAMETER, self.DIAMETER, parent)
        self.lines = []
        self.isInput = isInput
        self.logicGateNode = parent.logicGateNode
        self.parentDraggableNode = parent
        self.orderIndex = orderIndex
        # this flag **must** be set after creating self.lines!
        self.setFlags(self.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.setBrush(self.pointBrush)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, enabled=False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, enabled=False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, enabled=False)

    def addLine(self, lineItem: ConnectionLine):
        for existingLine in self.lines:
            existingPoints = existingLine.connectionPoints()
            lineItemPoints = lineItem.connectionPoints()
            if existingPoints == lineItemPoints or existingPoints[::-1] == lineItemPoints: # can be flipped if line started from the other end
                # another line with the same connection points already exists
                return False
        endPoint = lineItem.connectionPoints()[1]
        if endPoint:
            # can't connect out to out and in to in
            if endPoint.isInput == self.isInput:
                return False
            endPoint.lines.append(lineItem)
        self.lines.append(lineItem)
        return True

    def removeLine(self, lineItem):
        for existingLine in self.lines:
            existingPoints = existingLine.connectionPoints()
            lineItemPoints = lineItem.connectionPoints()
            if existingPoints == lineItemPoints or existingPoints[::-1] == lineItemPoints: # can be flipped if line started from the other end
                scene = self.scene()
                if scene:
                    scene.removeItem(existingLine)
                    self.lines.remove(existingLine)
                    return True
        return False

    def itemChange(self, change, value):
        for line in self.lines:
            line.updateLine(self)
        return super().itemChange(change, value)

class DraggableNode(QGraphicsItem):
    gateType: GateType
    pixmap: QPixmap
    logicGateNode: Node
    gateType: GateType
    outputPoints: list[ConnectionPoint]
    inputPoints: list[ConnectionPoint]
    stateIndicator: QGraphicsTextItem
    id = None #UUID

    def __init__(self, gateType: GateType, x: int , y: int, state: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid.uuid4()
        self.outputPoints = []
        self.inputPoints = []
        self.pixmap = QPixmap(PIXMAP_FILES_DICT[gateType])

        self.rect = QRectF(0, 0, float(self.pixmap.width()), float(self.pixmap.height()))
        self.setFlags(self.GraphicsItemFlag.ItemIsMovable)
        self.setPos(x, y)

        self.gateType = gateType
        self.logicGateNode = GateClass[gateType]()
        self.logicGateNode.state = state

        if gateType == GateType.INPUT:
            self.stateIndicator = QGraphicsTextItem("1", self)
            self.stateIndicator.setX(self.boundingRect().center().x() - self.stateIndicator.boundingRect().center().x() - 12)
            self.stateIndicator.setY(self.boundingRect().center().y() - self.stateIndicator.boundingRect().center().y())
        if gateType == GateType.OUTPUT:
            self.stateIndicator = QGraphicsTextItem("0", self)
            self.stateIndicator.setX(self.boundingRect().center().x() - self.stateIndicator.boundingRect().center().x() + 12)
            self.stateIndicator.setY(self.boundingRect().center().y() - self.stateIndicator.boundingRect().center().y())

        if GateInputCount[gateType] == 1:
            connectionPoint = ConnectionPoint(self, True, 0)
            self.inputPoints.append(connectionPoint)
            connectionPoint.setX(0 + ConnectionPoint.DIAMETER - 3)
            connectionPoint.setY(self.getCenterY())
        if GateInputCount[gateType] == 2:
            connectionPoint = ConnectionPoint(self, True, 0)
            self.inputPoints.append(connectionPoint)
            connectionPoint.setX(0 + ConnectionPoint.DIAMETER)
            connectionPoint.setY(self.getCenterY() - 9.5)
            connectionPoint = ConnectionPoint(self, True, 1)
            self.inputPoints.append(connectionPoint)
            connectionPoint.setX(0 + ConnectionPoint.DIAMETER)
            connectionPoint.setY(self.getCenterY() + 9.5)

        # Assuming just 1 output for now...
        if gateType != GateType.OUTPUT:
            connectionPoint = ConnectionPoint(self, False, 0)
            connectionPoint.setX(float(self.pixmap.width()) - ConnectionPoint.DIAMETER/2)
            connectionPoint.setY(self.getCenterY())
            self.outputPoints.append(connectionPoint)

    def getCenterY(self) -> float:
        return float(self.pixmap.height())/2

    def paint(self, painter: QPainter | None, option, widget = None):
        if painter is not None:
            painter.drawPixmap(0, 0, self.pixmap)

    def boundingRect(self):
        return QRectF(self.pixmap.rect())

    def updateState(self, state: bool) -> None:
        self.logicGateNode.updateState(state)
        self.setStateIndicator(self.logicGateNode.state)
        return

    def setStateIndicator(self, state: bool) -> None:
        if not self.stateIndicator:
            return
        if state:
            self.stateIndicator.setPlainText("1")
        else:
            self.stateIndicator.setPlainText("0")
        return

    def getState(self) -> bool:
        return self.logicGateNode.state

class Scene(QGraphicsScene):
    startConnectionPoint = newConnectionLine = None
    draggableNodeList: list[DraggableNode | None] = []

    wasMouseMoved: bool = False

    def addNodeItem(self, item: DraggableNode | None) -> None:
        super().addItem(item)
        self.draggableNodeList.append(item)
        return

    def connectionPointAt(self, pos) -> ConnectionPoint | None:
        mask = QPainterPath()
        mask.setFillRule(Qt.FillRule.WindingFill)
        for item in self.items(pos):
            if mask.contains(pos):
                # ignore objects hidden by others
                return None
            if isinstance(item, ConnectionPoint):
                return item
            if not isinstance(item, ConnectionLine):
                mask.addPath(item.shape().translated(item.scenePos()))

    def connectionLineAt(self, pos) -> ConnectionLine | None:
        mask = QPainterPath()
        mask.setFillRule(Qt.FillRule.WindingFill)
        for item in self.items(pos):
            if mask.contains(pos):
                # ignore objects hidden by others
                return None
            if isinstance(item, ConnectionLine):
               return item

    def draggableNodeAt(self, pos) -> DraggableNode | None:
        mask = QPainterPath()
        mask.setFillRule(Qt.FillRule.WindingFill)
        for item in self.items(pos):
            if mask.contains(pos):
                # ignore objects hidden by others
                return None
            if isinstance(item, DraggableNode):
               return item

    def mousePressEvent(self, event):
        print("[MOUSE] Pressed")
        if event and event.button() == Qt.MouseButton.LeftButton:
            cursorConnectionPoint = self.connectionPointAt(event.scenePos())
            cursorConnectionLine = self.connectionLineAt(event.scenePos())
            # create a new line
            if cursorConnectionPoint:
                self.startConnectionPoint = cursorConnectionPoint
                self.newConnectionLine = ConnectionLine(cursorConnectionPoint, event.scenePos())
                self.addItem(self.newConnectionLine)
                return
            # destroy an existing line
            elif cursorConnectionLine:
                points = cursorConnectionLine.connectionPoints()
                if points[0] and points[1]:
                    print("[MOUSE PRESSED] ", points[0])
                    print("[MOUSE PRESSED] ", points[1])
                    self.disconnectPoints(points[0], points[1], cursorConnectionLine)

        self.wasMouseMoved = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        #print("[MOUSE] Move\n\n")
        if event and self.newConnectionLine:
            item = self.connectionPointAt(event.scenePos())
            if (item and item != self.startConnectionPoint and self.startConnectionPoint):
                cursorPos = item.scenePos()
            else:
                cursorPos = event.scenePos()
            self.newConnectionLine.setP2(cursorPos)
            return
        self.wasMouseMoved = True
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        print("[MOUSE] Release")
        if not event:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            endConnectionPoint = self.connectionPointAt(event.scenePos())
            cursorDraggableNode = self.draggableNodeAt(event.scenePos())

            if self.newConnectionLine and endConnectionPoint and self.startConnectionPoint and endConnectionPoint != self.startConnectionPoint and endConnectionPoint.isInput != self.startConnectionPoint.isInput:
                if not self.connectPoints(self.startConnectionPoint, endConnectionPoint, self.newConnectionLine):
                    # delete the connection if it exists; remove the following line if this feature is not required
                    print("Something went wrong...\n\n\n")

                    self.disconnectPoints(self.startConnectionPoint, endConnectionPoint, self.newConnectionLine)
            else:
                self.removeItem(self.newConnectionLine)

            if not self.wasMouseMoved and cursorDraggableNode and cursorDraggableNode.gateType == GateType.INPUT:
                cursorDraggableNode.updateState(not cursorDraggableNode.getState())
                recursiveUpdate(cursorDraggableNode.logicGateNode)
                printAllStates(self.draggableNodeList)
                self.updateAllInputsOutputs()

        if event.button() == Qt.MouseButton.RightButton:
            cursorDraggableNode = self.draggableNodeAt(event.scenePos())

            if cursorDraggableNode:
                self.deleteDraggableNode(cursorDraggableNode)

        self.wasMouseMoved = False
        self.startConnectionPoint = self.newConnectionLine = None
        super().mouseReleaseEvent(event)

    def disconnectPoints(self, p1: ConnectionPoint, p2: ConnectionPoint, givenLine: ConnectionLine | None) -> None:
        commonLine = self.getCommonLine(p1, p2)
        if commonLine:
            if p1.logicGateNode and p2.logicGateNode:
                self.disconnectLogic(p1, p2)
            p1.removeLine(commonLine)
            p2.removeLine(commonLine)
            self.removeItem(commonLine)
        if commonLine != givenLine and givenLine:
            givenLinePoints = givenLine.connectionPoints()
            if givenLinePoints:
                if givenLinePoints[0]:
                    givenLinePoints[0].removeLine(givenLine)
                if givenLinePoints[1]:
                    givenLinePoints[1].removeLine(givenLine)
            self.removeItem(givenLine)
        return

    def arePointsConnected(self, p1: ConnectionPoint, p2: ConnectionPoint) -> bool:
        commonLine = self.getCommonLine(p1, p2)
        if commonLine:
            return True
        return False

    def doPointsBelongToLine(self, p1: ConnectionPoint, p2: ConnectionPoint, givenLine: ConnectionLine) -> bool:
        commonLine = self.getCommonLine(p1, p2)
        return commonLine == givenLine

    def getCommonLine(self, p1: ConnectionPoint, p2: ConnectionPoint) -> ConnectionLine | None:
        for line1 in p1.lines:
            for line2 in p2.lines:
                if line1 == line2:
                    return line1
        return None

    def connectPoints(self, p1: ConnectionPoint, p2: ConnectionPoint, givenLine: ConnectionLine | None) -> bool:
        if not p2 or not p1 or p2 == p1 or p2.isInput == p1.isInput:
            print("[ConnectPoints()] Initial check failed")
            return False

        if self.getCommonLine(p1, p2):
            print("[ConnectPoints()] Points and line are already connected")
            return False

        print("[ConnectPoints()] Connecting")
        if not givenLine:
            print("[ConnectPoints()] Creating a new line")
            givenLine = ConnectionLine(p1, p2)
        if p1.addLine(givenLine) and p2.addLine(givenLine):
            print("[ConnectPoints()] Line already exists. Connecting start and end")
            if not givenLine.start:
                givenLine.setStart(p1)
            if not givenLine.end:
                givenLine.setEnd(p2)
        else:
            print("[ConnectPoints()] Could not add line to start or end")
            return False
        self.addItem(givenLine)

        if p1.logicGateNode and p2.logicGateNode:
            print("[ConnectPoints()] Connecting logic")
            self.connectLogic(p1, p2)
        else: 
            print("[ConnectPoints()] start or end does not have a logic gate attached")
            return False
        print("[ConnectPoints()] All good!")
        return True

    def findInputOutput(self, p1: ConnectionPoint, p2: ConnectionPoint) -> tuple[ConnectionPoint, ConnectionPoint]:
        if p1.isInput:
            return (p1, p2)
        else:
            return (p2, p1)

    def connectLogic(self, p1: ConnectionPoint, p2: ConnectionPoint) -> None:
        sortedConnections = self.findInputOutput(p1, p2)
        inputPoint = sortedConnections[0]
        outputPoint = sortedConnections[1]
        logicGateOutput = outputPoint.logicGateNode
        logicGateInput = inputPoint.logicGateNode

        connectOutToInAt(logicGateOutput, logicGateInput, inputPoint.orderIndex)
        recursiveUpdate(logicGateOutput)
        printAllStates(self.draggableNodeList)
        self.updateAllInputsOutputs()
        return

    def disconnectLogic(self, p1: ConnectionPoint, p2: ConnectionPoint) -> None:
        sortedConnections = self.findInputOutput(p1, p2)
        inputPoint = sortedConnections[0]
        outputPoint = sortedConnections[1]
        logicGateOutput = outputPoint.logicGateNode
        logicGateInput = inputPoint.logicGateNode

        removeOutAndInAt(logicGateOutput, logicGateInput, inputPoint.orderIndex)

        recursiveUpdate(logicGateOutput)
        recursiveUpdate(logicGateInput)
        printAllStates(self.draggableNodeList)
        self.updateAllInputsOutputs()

        return

    def updateAllInputsOutputs(self) -> None:
        for draggableNode in self.draggableNodeList:
            if not draggableNode:
                continue
            if draggableNode.gateType == GateType.INPUT or draggableNode.gateType == GateType.OUTPUT:
                draggableNode.updateState(draggableNode.getState())

    def deleteDraggableNode(self, draggableNode: DraggableNode) -> None:
        if not draggableNode:
            return
        for point in draggableNode.outputPoints + draggableNode.inputPoints:
            for line in point.lines:
                if line.start and line.end:
                    self.disconnectPoints(line.start, line.end, line)
                if line:
                    self.removeItem(line)
            point = None

        self.removeItem(draggableNode)
        self.draggableNodeList.remove(draggableNode)
        return

    def clear(self):
        self.startConnectionPoint = None
        self.newConnectionLine = None
        self.draggableNodeList = []
        super().clear()



def printAllStates(draggableNodeList: list[DraggableNode | None]) -> None:
    print("\n==== STATES ====")
    for draggableNode in draggableNodeList:
        if draggableNode and draggableNode.logicGateNode:
            node = draggableNode.logicGateNode
            print(node, " is ", node.state)
            print("  Inputs:")
            for singleInputList in node.inputNodes:
                for input in singleInputList:
                    if input:
                        print("\t", input)
            print("  Outputs:")
            for singleOutputList in node.outputNodes:
                for output in singleOutputList:
                    if output:
                        print("\t", output)
        print("")
    return


def saveNodeGraph(scene: Scene, filename):
    data = {"nodes": [], "connections": []}

    for node in scene.draggableNodeList:
        if not node:
            continue
        data["nodes"].append({
            "id": str(node.id),
            "type": node.gateType.name,
            "x": node.x(),
            "y": node.y(),
            "state": getattr(node, "state", False),
            "inputs": len(node.inputPoints),
            "outputs": len(node.inputPoints),
        })

        for output in node.outputPoints:
            for line in output.lines:
                input = line.getOppositePointOf(output)
                if not input:
                    continue
                data["connections"].append({
                    "from_node": str(node.id),
                    "from_output": output.orderIndex,
                    "to_node": str(input.parentDraggableNode.id),
                    "to_input": input.orderIndex
                })

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def loadNodeGraph(scene: Scene, filename):
    with open(filename, "r") as f:
        data = json.load(f)

    uuidToNode = {} # keep track of nodes and their uuids for connections

    scene.clear()

    # Create nodes
    for node_data in data["nodes"]:
        gateType = GateType[node_data["type"]]
        x = node_data["x"]
        y = node_data["y"]
        state = node_data.get("state", False)

        node = DraggableNode(gateType, x, y, state)
        node.id = uuid.UUID(node_data["id"])
        scene.addNodeItem(node)

        uuidToNode[node.id] = node

    # Connect connection points
    for connectionPoint in data["connections"]:
        fromId = uuid.UUID(connectionPoint["from_node"])
        toId = uuid.UUID(connectionPoint["to_node"])
        fromOutputIndex = connectionPoint["from_output"]
        toInputIndex = connectionPoint["to_input"]

        fromNode = uuidToNode[fromId]
        toNode = uuidToNode[toId]
        outputPoint = fromNode.outputPoints[fromOutputIndex]
        inputPoint = toNode.inputPoints[toInputIndex]

        scene.connectPoints(outputPoint, inputPoint, givenLine=None)


class ExampleMenu(QMenu):
    scene: Scene

    def __init__(self, scene: Scene, parent=None):
        super().__init__(parent)

        self.scene = scene

        self.addAction("8-bit full adder", lambda: loadNodeGraph(self.scene, resolvePath("examples/8bit-adder.json")))
        self.addAction("4-to-1 multiplexer", lambda: loadNodeGraph(self.scene, resolvePath("examples/4bit-multiplexer.json")))
        self.addAction("XOR from NAND", lambda: loadNodeGraph(self.scene, resolvePath("examples/XOR-from-NAND.json")))
        self.addAction("XOR from AND, NOT, OR", lambda: loadNodeGraph(self.scene, resolvePath("examples/XOR-from-AND-NOT-OR.json")))

        return
