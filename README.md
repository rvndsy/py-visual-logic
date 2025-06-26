## Overview

The graphical interface has two main parts: toolbars and an area where to make logical circuits.

The toolbar on the top has two buttons that allow the user to save and load schematics they have made (stored in JSON format), a drop-down menu to load some pre-implemented examples and a button to clear all elements on the scene. The toolbar on the left side allows the user to place down any new logic gate or an input or output.

The center area is where the user can build logical circuits from the most basic logic gates. Elements can be moved around, connected together and disconnected with mouse left-click and nodes can be deleted with right-click. By left-clicking on the "Input" nodes the user can toggle their boolean state (1 or 0). The "Output" nodes must be connected to display the end result of the logic circuit (1 or 0). Multiple "Input" or "Output" nodes can be placed and the flow of logic is intended to go from left to right.

This app was made in Python using the PyQt6 library.

## How to run

Run the provided executable `py-visual-logic.exe` by double clicking on in.

To run the app from the terminal/commandline then you must run `main.py` (for example `python main.py`).

## The node system

File `main.py` just launches the main PyQt6 application by creating a new `Window()` object. File `window.py` contains every graphical element (Window, Scene, Connections, etc.), their interactions and functions to load and save schematics to JSON files. File `logic_gates.py` contains the core implementation of logic gates and enables the correct flow of logic. Graphical node graph in `window.py` and the node graph in `logic_gates.py` are two separate graphs that are maintained in parellel but when logic has to be evaluated then only the graph from `logic_gates.py` is used.


## Implemented node types
