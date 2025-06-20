from logic_gates import *

if __name__ == "__main__":
    input1 = Input(0, 0)
    input2 = Input(0, 0)
    input3 = Input(0, 0)
    output = Output(0, 0)
    or_gate = OR(0, 0)
    and_gate = AND(0, 0)

    #input1.update_state(False)
    #input2.update_state(True)
    #connect_out_to_in_at(input1, or_gate, 0)
    #connect_out_to_in_at(input2, or_gate, 1)
    #connect_out_to_in_at(or_gate, output)
    #or_gate.update_state()
    #output.update_state()

    connect_out_to_in_at(input1, or_gate, 0)
    connect_out_to_in_at(input2, or_gate, 1)
    connect_out_to_in_at(or_gate, and_gate, 0)
    connect_out_to_in_at(input3, and_gate, 1)
    connect_out_to_in_at(and_gate, output)

    input1.update_state(False)
    input2.update_state(True)
    input3.update_state(True)
    recursive_update(input1)

    print("Input 1: ", input1.state)
    print("Input 2: ", input2.state)
    print("Input 3: ", input3.state)
    print("OR:      ", or_gate.state)
    print("AND:     ", and_gate.state)
    print("Output:  ",output.state)
