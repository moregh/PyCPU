# CPU Programming Examples

This document contains annotated code examples demonstrating programming techniques for the 8-bit CPU emulator. All example files are available as `.cpu` assembly files in the examples directory.

## Assembly Language Conventions

- **Comments**: Use semicolon (`;`) prefix, extend to end of line
- **Labels**: Use colon prefix (`:LABEL`) for jump targets
- **Addresses**: Use dollar prefix (`$1000`) for hexadecimal memory addresses
- **Values**: Use decimal numbers directly (`42`, `255`)

## Basic Examples

### Hello World Display

Demonstrates writing text to the GPU framebuffer for display output.

```assembly
; hello.cpu - Display "HELLO WORLD" on screen

:START
    LDY 240       ; $F0 - high byte of GPU memory
    LDX 96        ; $60 - low byte of GPU memory  
    
    ; Write "HELLO WORLD" character by character
    LDA 72        ; 'H'
    WMI           ; Write to framebuffer
    INX           ; Move to next position
    
    LDA 69        ; 'E'
    WMI
    INX
    
    LDA 76        ; 'L'
    WMI
    INX
    
    LDA 76        ; 'L'
    WMI
    INX
    
    LDA 79        ; 'O'
    WMI
    INX
    
    LDA 32        ; ' ' (space)
    WMI
    INX
    
    LDA 87        ; 'W'
    WMI
    INX
    
    LDA 79        ; 'O'
    WMI
    INX
    
    LDA 82        ; 'R'
    WMI
    INX
    
    LDA 76        ; 'L'
    WMI
    INX
    
    LDA 68        ; 'D'
    WMI
    
    HLT           ; Stop execution
```

**Key Concepts:**
- GPU framebuffer starts at `$F060`
- Use indexed memory write (`WMI`) with Y=high byte, X=low byte
- ASCII character codes for text display

### Counter Program

Demonstrates register overflow handling and long-running computation.

```assembly
; counters.cpu - Count until all registers overflow

:START
:A_INCREMENTER
    INA           ; Increment A register
    JNO START     ; If no overflow, continue
    
:X_INCREMENTER  
    INX           ; A overflowed, increment X
    JNO START     ; If X no overflow, restart
    
:Y_INCREMENTER
    INY           ; X overflowed, increment Y  
    JNO START     ; If Y no overflow, restart
    
:EXIT
    HLT           ; All registers overflowed, halt
```

**Key Concepts:**
- Register overflow detection with `JNO` (Jump if No Overflow)
- Cascading counter implementation
- Long-running computation (33+ million ticks)

## Intermediate Examples

### Fibonacci Sequence Calculator

Calculates Fibonacci numbers with overflow tracking to handle large results.

```assembly
; fibonacci.cpu - Calculate 12th Fibonacci number

:START
    LDY 12        ; Calculate 12th Fibonacci number
    LDA 0         ; First Fibonacci number (F0)
    LDX 1         ; Second Fibonacci number (F1)

:LOOP
    WMA $100      ; Store current A value
    AAX           ; A = A + X (next Fibonacci number)
    JMO OVERFLOW  ; Handle overflow if occurred
    
:CONTINUE
    RMX $100      ; X = previous A value
    DEY           ; Decrement counter
    JNZ LOOP      ; Continue if not done
    
:COMPLETE
    RMY $200      ; Load overflow count into Y
    HLT           ; Finished - result in A, overflows in Y
    
:OVERFLOW
    RMX $200      ; Load overflow counter
    INX           ; Increment overflow count
    WMX $200      ; Store overflow counter
    JMP CONTINUE  ; Return to main calculation
```

**Program Structure:**
- **Initialization**: Set up registers and counters
- **Main Loop**: Calculate next Fibonacci number, check for overflow
- **Overflow Handler**: Track number of overflows in memory
- **Completion**: Result in A register, overflow count in Y register

**Key Concepts:**
- Memory usage for temporary storage (`$100`, `$200`)
- Overflow detection and handling
- Loop control with conditional jumps
- Multi-byte result handling

### Pattern Generator

Creates alternating patterns in GPU memory for visual display.

```assembly
; pattern.cpu - Generate alternating space/asterisk pattern

:INIT
    LDA 32        ; Start with space character
    LDX 96        ; Low byte of GPU start ($60)
    LDY 240       ; High byte of GPU start ($F0)

:WRITE_LOOP
    WMI           ; Write character to memory[Y*256 + X]
    
    ; Toggle between space (32) and asterisk (42)
    WMX $0910     ; Save X temporarily
    LDX 32        ; Load space value
    SAX           ; A = A - 32
    JMZ SET_ASTERISK ; If A was space, change to asterisk
    
    LDA 32        ; A was asterisk, change to space
    JMP RESTORE_X
    
:SET_ASTERISK
    LDA 42        ; Set to asterisk character
    
:RESTORE_X
    RMX $0910     ; Restore X position
    
    ; Advance to next position
    INX           ; Increment X (column)
    JNO WRITE_LOOP ; Continue if no overflow
    
    ; X overflowed, move to next row
    LDX 0         ; Reset X to start of row
    INY           ; Increment Y (row)
    JNO WRITE_LOOP ; Continue if Y didn't overflow
    
    ; Filled entire display
    HLT
```

**Key Concepts:**
- Conditional logic with character toggling
- 2D coordinate management (X,Y addressing)
- Full screen memory filling
- Temporary memory storage for register preservation

## Programming Techniques

### Memory Management

```assembly
; Temporary storage
WMA $1000     ; Store A register at address $1000
RMA $1000     ; Restore A register from address $1000

; Indexed addressing for arrays/buffers
LDY $10       ; High byte of base address
LDX 50        ; Offset within array
RMI           ; Read memory[base + offset] into A
```

### Loop Patterns

```assembly
; Counted loop
LDY 10        ; Loop counter
:LOOP_START
    ; Loop body here
    DEY           ; Decrement counter
    JNZ LOOP_START ; Continue if not zero

; Conditional loop
:LOOP_START
    ; Loop body
    ; Set flags based on condition
    JNZ LOOP_START ; Continue while condition true
```

### Subroutine Simulation

```assembly
; Save return address
WPC $1FF0     ; Store program counter

; Call subroutine
JMP SUBROUTINE

; Return from subroutine
:SUBROUTINE
    ; Subroutine code here
    RPC $1FF0     ; Restore and jump to return address
```

## Error Handling Patterns

### Overflow Management

```assembly
AAX           ; Perform addition
JMO HANDLE_OVERFLOW ; Jump if overflow occurred
; Normal processing continues here

:HANDLE_OVERFLOW
; Increment overflow counter, adjust result, etc.
JMP CONTINUE_PROCESSING
```

### Bounds Checking

```assembly
; Check if value exceeds maximum
EAX           ; Compare A with X (maximum value)
JMZ WITHIN_BOUNDS ; Equal is OK
; Additional logic for greater than check
JMP ERROR_HANDLER

:WITHIN_BOUNDS
; Safe to proceed
```

## Performance Considerations

- **Memory Access**: Direct register operations are faster than memory reads/writes
- **Loop Optimization**: Minimize memory operations inside tight loops
- **Flag Usage**: Plan instruction sequences to avoid unnecessary flag operations
- **Jump Efficiency**: Use relative jumps when possible for shorter instruction sequences

## Debugging Techniques

1. **Strategic Halts**: Place `HLT` instructions to examine register states
2. **Memory Dumps**: Store intermediate values in known memory locations
3. **Counter Variables**: Use memory locations to track loop iterations or function calls
4. **Character Output**: Write debug values as ASCII characters to the display

These examples demonstrate the fundamental programming patterns needed to write effective programs for the CPU emulator. Each example builds upon basic concepts to create more sophisticated programs.