from logic_gates import *

if __name__ == "__main__":
    input1 = Input(0, 0)
    input2 = Input(0, 0)
    output = Output(0, 0)
    or_gate = OR(0, 0)
    and_gate = AND(0, 0)

    input1.update_state(False)
    input2.update_state(True)
    connect_out_to_in_at(input1, or_gate, 0)
    connect_out_to_in_at(input2, or_gate, 1)
    connect_out_to_in_at(or_gate, output)
    or_gate.update_state()
    output.update_state()
    print("Input 1: ", input1.state)
    print("Input 2: ", input2.state)
    print("Or:      ", or_gate.state)
    print("Output:  ",output.state)
