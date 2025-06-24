from logic_gates import *
from typing import Dict
from PyQt6.QtCore import Qt, QSize, QLineF, QRectF
from PyQt6.QtGui import ( 
    QAction,
    QPixmap,
    QPainter,
    QPen,
    QColor,
    QBrush,
    QPainterPath,
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QToolBar,

)
from PyQt6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QGraphicsRectItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsLineItem,
    QGraphicsEllipseItem,
)

PIXMAP_FILES_DICT = {
    GateType.INPUT: "./symbols/IN.png",
    GateType.OUTPUT: "./symbols/OUT.png",
    GateType.AND: "./symbols/AND_ANSI.png",
    GateType.OR:  "./symbols/OR_ANSI.png",
    GateType.NOT: "./symbols/NOT_ANSI.png",
}

class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PyQt App")

        self.scene = Scene(0, 0, 400, 400)

        self.scene.addNodeItem(DraggableNode(GateType.NOT, 100, 100))
        self.scene.addNodeItem(DraggableNode(GateType.OR, 200, 300))
        self.scene.addNodeItem(DraggableNode(GateType.AND, 100, 200))
        self.scene.addNodeItem(DraggableNode(GateType.INPUT, 150, 50, state=True))
        self.scene.addNodeItem(DraggableNode(GateType.OUTPUT, 50, 150))

        toolbar = QToolBar(parent=self)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        openFileBtn = QAction("Open file", self)
        openFileBtn.setStatusTip("Open file")
        openFileBtn.triggered.connect(self.toolbarOpenFileBtnClicked)
        toolbar.addAction(openFileBtn)

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setCentralWidget(view)
        return
    
    def toolbarOpenFileBtnClicked(self, s) -> None:
        print("click ", s)

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
    def __init__(self, start, p2):
        super().__init__()
        self.start = start
        self.end = None
        self._line = QLineF(start.scenePos(), p2)
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

class ConnectionPoint(QGraphicsEllipseItem):
    DIAMETER = 10
    lines: list
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
        for existing in self.lines:
            if existing.connectionPoints() == lineItem.connectionPoints():
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
        for existing in self.lines:
            if existing.connectionPoints() == lineItem.connectionPoints():
                scene = self.scene()
                if scene:
                    scene.removeItem(existing)
                    self.lines.remove(existing)
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
    inputConnectionCount: int
    outputPoints: list[ConnectionPoint]
    inputPoints: list[ConnectionPoint]

    def __init__(self, gateType: GateType, x: int , y: int, state: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.pen = QPen(Qt.GlobalColor.black, 2)
        #self.connectionBrush = QBrush(QColor(214, 13, 36))
        self.rect = QRectF(0, 0, 100, 100)
        self.setFlags(self.GraphicsItemFlag.ItemIsMovable)
        self.setPos(x, y)

        self.gateType = gateType
        self.logicGateNode = GateClass[gateType]()
        self.logicGateNode.state = state

        self.outputPoints = []
        self.inputPoints = []
        self.pixmap = QPixmap(PIXMAP_FILES_DICT[gateType])

        self.inputConnectionCount = GateInputCount[gateType]
        if self.inputConnectionCount == 1:
            connectionPoint = ConnectionPoint(self, True, 0)
            self.inputPoints.append(connectionPoint)
            connectionPoint.setX(0 + ConnectionPoint.DIAMETER)
            connectionPoint.setY(self.getCenterY())
        if self.inputConnectionCount == 2:
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

class Scene(QGraphicsScene):
    startConnectionPoint = newConnectionLine = None
    draggableNodeList: list[DraggableNode | None] = []
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

    def mousePressEvent(self, event):
        if event is not None and event.button() == Qt.MouseButton.LeftButton:
            cursorConnectionPoint = self.connectionPointAt(event.scenePos())
            if cursorConnectionPoint:
                self.startConnectionPoint = cursorConnectionPoint
                self.newConnectionLine = ConnectionLine(cursorConnectionPoint, event.scenePos())
                self.addItem(self.newConnectionLine)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event and self.newConnectionLine:
            item = self.connectionPointAt(event.scenePos())
            if (item and item != self.startConnectionPoint and self.startConnectionPoint):
                    cursorPos = item.scenePos()
            else:
                cursorPos = event.scenePos()
            self.newConnectionLine.setP2(cursorPos)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event and self.newConnectionLine:
            endConnectionPoint = self.connectionPointAt(event.scenePos())
            if self.startConnectionPoint and endConnectionPoint and endConnectionPoint != self.startConnectionPoint:
                self.newConnectionLine.setEnd(endConnectionPoint)
                if self.startConnectionPoint.addLine(self.newConnectionLine):
                    self.connect(self.startConnectionPoint, endConnectionPoint)
                    endConnectionPoint.addLine(self.newConnectionLine)
                else:
                    # delete the connection if it exists; remove the following
                    # line if this feature is not required
                    self.removeConnection(self.startConnectionPoint, endConnectionPoint)
                    self.startConnectionPoint.removeLine(self.newConnectionLine)
                    self.removeItem(self.newConnectionLine)
            else:
                self.removeItem(self.newConnectionLine)
        self.startConnectionPoint = self.newConnectionLine = None
        super().mouseReleaseEvent(event)
        inputPoint: ConnectionPoint

    def findInputOutput(self, p1: ConnectionPoint, p2: ConnectionPoint) -> tuple[ConnectionPoint, ConnectionPoint]:
        if p1.isInput:
            return (p1, p2)
        else:
            return (p2, p1)

    def connect(self, p1: ConnectionPoint, p2: ConnectionPoint) -> None:
        sortedConnections = self.findInputOutput(p1, p2)
        inputPoint = sortedConnections[0]
        outputPoint = sortedConnections[1]
        logicGateOutput = outputPoint.logicGateNode
        logicGateInput = inputPoint.logicGateNode

        connectOutToInAt(logicGateOutput, logicGateInput, inputPoint.orderIndex)
        recursiveUpdate(logicGateOutput)
        printAllStates(self.draggableNodeList)
        return

    def removeConnection(self, p1: ConnectionPoint, p2: ConnectionPoint) -> None:
        sortedConnections = self.findInputOutput(p1, p2)
        inputPoint = sortedConnections[0]
        outputPoint = sortedConnections[1]
        logicGateOutput = outputPoint.logicGateNode
        logicGateInput = inputPoint.logicGateNode

        removeOutAndInAt(logicGateOutput, logicGateInput, inputPoint.orderIndex)

        recursiveUpdate(logicGateOutput)
        recursiveUpdate(logicGateInput)
        printAllStates(self.draggableNodeList)

        return






def printAllStates(draggableNodeList: list[DraggableNode | None]) -> None:
    print()
    print("==== STATES ====")
    for draggableNode in draggableNodeList:
        if draggableNode and draggableNode.logicGateNode:
            node = draggableNode.logicGateNode
            print(node, " is ", node.state)
            print("  Inputs:")
            for singleInputList in node.inputNodes:
                for input in singleInputList:
                    if input: print("\t", input, " is ", input.state)
            print("  Outputs:")
            for singleOutputList in node.outputNodes:
                for output in singleOutputList:
                    if output: print("\t", output, " is ", output.state)
    return
