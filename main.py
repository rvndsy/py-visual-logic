from PyQt6.QtWidgets import QApplication, QMainWindow
from logic_gates import *
from window import *
from PyQt6.QtWidgets import QStyleFactory
import sys

if __name__ == "__main__":
    #input1 = Input()
    #input2 = Input()
    #input3 = Input()
    #output = Output()
    #or_gate = OR()
    #and_gate = AND()

    ##input1.update_state(False)
    ##input2.update_state(True)
    ##connect_out_to_in_at(input1, or_gate, 0)
    ##connect_out_to_in_at(input2, or_gate, 1)
    ##connect_out_to_in_at(or_gate, output)
    ##or_gate.update_state()
    ##output.update_state()

    #input1.updateState(False)
    #input2.updateState(True)
    #input3.updateState(True)

    #connectOutToInAt(input1, or_gate, 0)
    #connectOutToInAt(input2, or_gate, 1)
    #connectOutToInAt(or_gate, and_gate, 0)
    #connectOutToInAt(input3, and_gate, 1)
    #connectOutToInAt(and_gate, output)

    #recursiveUpdate(input1)

    #print("Input 1: ", input1.state)
    #print("Input 2: ", input2.state)
    #print("Input 3: ", input3.state)
    #print("OR:      ", or_gate.state)
    #print("AND:     ", and_gate.state)
    #print("Output:  ",output.state)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())
