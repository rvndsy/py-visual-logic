## Overview

The graphical interface has two main parts: toolbars and an area where to make logical circuits.

The toolbar on the top has two buttons that allow the user to save and load schematics they have made (stored in JSON format), a drop-down menu to load some pre-implemented examples and a button to clear all elements on the scene. The toolbar on the left side allows the user to place down any new logic gate or an input or output.

The center area is where the user can build logical circuits from the most basic logic gates. Elements can be moved around, connected together and disconnected with mouse left-click and nodes can be deleted with right-click. By left-clicking on the "Input" nodes the user can toggle their boolean state (1 or 0). The "Output" nodes must be connected to display the end result of the logic circuit (1 or 0). Multiple "Input" or "Output" nodes can be placed and the flow of logic is intended to go from left to right.

This app was made in Python using the PyQt6 library.

## How to run

Run the provided executable `py-visual-logic` by double clicking on in.

To run the app from the terminal/commandline you must run `main.py` (for example `python main.py`).

## The node system

File `main.py` just launches the main PyQt6 application by creating a new `Window()` object. File `window.py` contains every graphical element (Window, Scene, Connections, Draggable Nodes, etc.), their interactions and functions to load and save schematics to JSON files. File `logic_gates.py` contains the core implementation of logic gates and enables the correct flow of logic.

There are effectively two node systems. One is for graphical elements and the other is for the execution of logic. Interactions with graphical elements "builds" in parallel the underlying logical node network. The logical node network is made up of elements of a `Node` class where each type of node is a child of the `Node` class. Each `Node` has a 2D list of input and output nodes, a variable that holds the boolean state, a variable that holds what type of gate the node is and how many input and output connections the node has. One list in the input or output list of lists belongs to one connection.

When logic has to be evaluated two `Node` functions `updateState` and `logicFn` are used. `updateState` reads the list of inputs for each connection and passes the total state of each connection to `logicFn`. `logicFn` uses the one or two boolean values it received and returns the result of the mathematically appropriate AND, OR, NOT, etc. function as a single output. Nodes `Input` and `Output` are children of `Node` as well but they are implemented differently as their behaviour is supposed to be different from logic gates.

The evaluation of the graph is done recursively by starting at some `Node` and going down the output list of nodes until `Output` node is hit. Currently loops are an unsolved problem that will absolutely cause the application to crash.

## Implemented node types

The currently implemented types of nodes are:
- Input
- Output
- AND
- NOT
- OR
- XOR
- NOR
- NAND
