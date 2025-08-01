# Examples
Example software for the CPU

## About
This document contains annotated code snippets demonstrating how to perform certain tasks on
the CPU. The individual files are available as [NAME].cpu within this folder.

**NOTE**: Comments must be removed from the code before attempting to run it as these are
not recognised by the compiler (yet).

## Fibonacci Sequence

Calculates the 15th Fibonacci number and saves the result in registers A (lower byte) and
Y (upper byte).

```commandline
fibonacci.cpu

LDY 14              # Loads the Y register with value 14
LDA 0               # Loads the A register with value 0
LDX 1               # Loads the X register with value 1
WMA 0 100           # Write value of register A to memory location 100
AAX                 # Adds A and X registers and stores in A register
JMO 0 24            # If A register overflowed, jump to memory location 24
RMX 0 100           # Load register X with value at memory location 100
DEY                 # Decrement register Y by 1
JNZ 0 6             # If Y is NOT zero (i.e. we're not finished), loop back to the start
RMY 0 200           # Load register Y with value at memory location 200
HLT                 # Halts the CPU
RMX 0 200           # Load register X with value at memory location 200
INX                 # Increment register X by 1
WMX 0 200           # Write value of register X to memory location 200
JMP 0 12            # Jump to memory location 12
```
The above code is made up of 4 distinct sections:
- initialisation
- main loop 
- overflow handling
- completion and output

#### Initialisation
```commandline
LDY 14              # Loads the Y register with value 14
LDA 0               # Loads the A register with value 0
LDX 1               # Loads the X register with value 1
```
This sets the initial status of the registers ready to perform a loop. We want the 15th
Fibonacci number, but load Y with *15 - 1 = 14* because we start with the 0th Fibonacci 
number (0) pre-loaded. The A register will contain the currently calculated number, the X
register will be used for holding previous numbers, and Y register is the loop counter.

#### Main Loop
```commandline
WMA 0 100           # Write value of register A to memory location 100
AAX                 # Adds A and X registers and stores in A register
JMO 0 24            # If A register overflowed, jump to memory location 24
RMX 0 100           # Load register X with value at memory location 100
DEY                 # Decrement register Y by 1
JNZ 0 6             # If Y is NOT zero (i.e. we're not finished), loop back to the start
```
This is where the actual calculation takes place. We store the value of the A register in to
memory location 100 so we can use it later. Then we add the values of the A and X registers
together and store the result in A. If the result of this calculation overflowed, we jump to
memory location 24 where the overflow handling routine lives. If we didn't overflow, or we
have returned from the overflow handling routine, we read the value we stored in memory
location 100 earlier into the X register (the previous value of the A register). Then we
decrement the Y register by 1, as this stores the number of iterations of the loop we are
doing. If the result of this operation isn't zero, we jump back to the start, at memory
location 6. If it is zero, we carry on to the next section.

#### Completion and Output
```commandline
RMY 0 200           # Load register Y with value at memory location 200
HLT                 # Halts the CPU
```
The number of times the A register overflowed has been stored in memory location 200, so we
now read this back from memory into the Y register. Then we are complete, so halt the CPU.

#### Overflow Handling
```commandline
RMX 0 200           # Load register X with value at memory location 200
INX                 # Increment register X by 1
WMX 0 200           # Write value of register X to memory location 200
JMP 0 12            # Jump to memory location 12
```
We load the value from memory location which holds the number of times we have overflowed in
to the X register. We then increment the X register by 1, save it back to memory location
200, and jump back to memory location 12, continuing the main loop.