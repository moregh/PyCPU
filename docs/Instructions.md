# CPU Instruction Reference

| Name | Opcode (Dec) | Opcode (Hex) | Length | Flags | Description | Assembly Example |
|------|--------------|--------------|--------|-------|-------------|------------------|
| **Control Instructions** |
| HLT | 0 | 0x00 | 0 | H | Halt - stops the processor | `HLT` |
| CLR | 1 | 0x01 | 0 | - | Clear - resets A, X and Y registers to 0 | `CLR` |
| NOP | 2 | 0x02 | 0 | - | No Operation - does nothing but increase the tick counter | `NOP` |
| **Arithmetic Instructions** |
| AAX | 3 | 0x03 | 0 | Z,O | Add A and X - Adds register A to register X and store the value in register A | `AAX` |
| AAY | 4 | 0x04 | 0 | Z,O | Add A and Y - Adds register A to register Y and store the value in register A | `AAY` |
| AXY | 5 | 0x05 | 0 | Z,O | Add X and Y - Adds register X to register Y and store the value in register X | `AXY` |
| SAX | 6 | 0x06 | 0 | Z,N | Subtract A and X - Subtracts register X from register A and store the value in register A | `SAX` |
| SAY | 7 | 0x07 | 0 | Z,N | Subtract A and Y - Subtracts register Y from register A and store the value in register A | `SAY` |
| SXY | 8 | 0x08 | 0 | Z,N | Subtract X and Y - Subtracts register Y from register X and store the value in register X | `SXY` |
| INA | 9 | 0x09 | 0 | Z,O | Increment A - Adds 1 to value of A register | `INA` |
| INX | 10 | 0x0A | 0 | Z,O | Increment X - Adds 1 to value of X register | `INX` |
| INY | 11 | 0x0B | 0 | Z,O | Increment Y - Adds 1 to value of Y register | `INY` |
| DEA | 12 | 0x0C | 0 | Z,N | Decrement A - Subtracts 1 from value of A register | `DEA` |
| DEX | 13 | 0x0D | 0 | Z,N | Decrement X - Subtracts 1 from value of X register | `DEX` |
| DEY | 14 | 0x0E | 0 | Z,N | Decrement Y - Subtracts 1 from value of Y register | `DEY` |
| **Bitwise Instructions** |
| NAX | 15 | 0x0F | 0 | Z,N | AND A & X - ANDs A and X and saves the result in A | `NAX` |
| NAY | 16 | 0x10 | 0 | Z,N | AND A & Y - ANDs A and Y and saves the result in A | `NAY` |
| NXY | 17 | 0x11 | 0 | Z,N | AND X & Y - ANDs X and Y and saves the result in X | `NXY` |
| OAX | 18 | 0x12 | 0 | Z,N | OR A & X - ORs A and X and saves the result in A | `OAX` |
| OAY | 19 | 0x13 | 0 | Z,N | OR A & Y - ORs A and Y and saves the result in A | `OAY` |
| OXY | 20 | 0x14 | 0 | Z,N | OR X & Y - ORs X and Y and saves the result in X | `OXY` |
| XAX | 21 | 0x15 | 0 | Z,N | XOR A and X - XORs A and X and saves the result in A | `XAX` |
| XAY | 22 | 0x16 | 0 | Z,N | XOR A and Y - XORs A and Y and saves the result in A | `XAY` |
| XXY | 23 | 0x17 | 0 | Z,N | XOR X and Y - XORs X and Y and saves the result in X | `XXY` |
| BLA | 24 | 0x18 | 0 | Z,O | Bit Shift Left A - Bit-shift A register left by 1 (double) | `BLA` |
| BLX | 25 | 0x19 | 0 | Z,O | Bit Shift Left X - Bit-shift X register left by 1 (double) | `BLX` |
| BLY | 26 | 0x1A | 0 | Z,O | Bit Shift Left Y - Bit-shift Y register left by 1 (double) | `BLY` |
| BRA | 27 | 0x1B | 0 | Z | Bit Shift Right A - Bit-shift A register right by 1 (half) | `BRA` |
| BRX | 28 | 0x1C | 0 | Z | Bit Shift Right X - Bit-shift X register right by 1 (half) | `BRX` |
| BRY | 29 | 0x1D | 0 | Z | Bit Shift Right Y - Bit-shift Y register right by 1 (half) | `BRY` |
| **Comparison Instructions** |
| EAX | 30 | 0x1E | 0 | Z | Equal A and X - Compares A and X for equality and sets Zero flag if true | `EAX` |
| EAY | 31 | 0x1F | 0 | Z | Equal A and Y - Compares A and Y for equality and sets Zero flag if true | `EAY` |
| EXY | 32 | 0x20 | 0 | Z | Equal X and Y - Compares X and Y for equality and sets Zero flag if true | `EXY` |
| **Control Flow Instructions** |
| JMP | 33 | 0x21 | 2 | - | Jump - Jump to specified memory location | `JMP $1000` |
| JNZ | 34 | 0x22 | 2 | - | Jump Not Zero - Jump to specified memory location if the Zero flag was not set during the last operation | `JNZ $1000` |
| JMZ | 35 | 0x23 | 2 | - | Jump if Zero - Jump to specified memory location if the Zero flag was set during the last operation | `JMZ $1000` |
| JNN | 36 | 0x24 | 2 | - | Jump Not Negative - Jump to specified memory location if the Negative flag was not set during the last operation | `JNN $1000` |
| JMN | 37 | 0x25 | 2 | - | Jump if Negative - Jump to specified memory location if the Negative flag was set during the last operation | `JMN $1000` |
| JNO | 38 | 0x26 | 2 | - | Jump Not Overflow - Jump to specified memory location if the Overflow flag was not set during the last operation | `JNO $1000` |
| JMO | 39 | 0x27 | 2 | - | Jump if Overflow - Jump to specified memory location if the Overflow flag was set during the last operation | `JMO $1000` |
| JFA | 40 | 0x28 | 0 | - | Jump Forward A - sets PC to its current value plus the value of the A register (wraps around memory) | `JFA` |
| JFX | 41 | 0x29 | 0 | - | Jump Forward X - sets PC to its current value plus the value of the X register (wraps around memory) | `JFX` |
| JFY | 42 | 0x2A | 0 | - | Jump Forward Y - sets PC to its current value plus the value of the Y register (wraps around memory) | `JFY` |
| JBA | 43 | 0x2B | 0 | - | Jump Backward A - sets PC to its current value minus the value of the A register (wraps around memory) | `JBA` |
| JBX | 44 | 0x2C | 0 | - | Jump Backward X - sets PC to its current value minus the value of the X register (wraps around memory) | `JBX` |
| JBY | 45 | 0x2D | 0 | - | Jump Backward Y - sets PC to its current value minus the value of the Y register (wraps around memory) | `JBY` |
| JAD | 46 | 0x2E | 2 | - | Jump to Memory Address - Sets program counter to address at specified memory location (2 bytes) | `JAD $1000` |
| WPC | 47 | 0x2F | 2 | - | Write Program Counter - writes the current value of the program counter to the specified memory location (2 bytes) | `WPC $1000` |
| RPC | 48 | 0x30 | 2 | - | Read Program Counter - reads a 2-byte value from the specified memory location and sets the program counter to that value | `RPC $1000` |
| **Load/Store Instructions** |
| LDA | 49 | 0x31 | 1 | - | Load A - loads A register with a specified value | `LDA 42` |
| LDX | 50 | 0x32 | 1 | - | Load X - loads X register with a specified value | `LDX 42` |
| LDY | 51 | 0x33 | 1 | - | Load Y - loads Y register with a specified value | `LDY 42` |
| CAX | 52 | 0x34 | 0 | Z,N | Copy A to X - Copies A register into X register | `CAX` |
| CAY | 53 | 0x35 | 0 | Z,N | Copy A to Y - Copies A register into Y register | `CAY` |
| CXY | 54 | 0x36 | 0 | Z,N | Copy X to Y - Copies X register into Y register | `CXY` |
| CYX | 55 | 0x37 | 0 | Z,N | Copy Y to X - Copies Y register into X register | `CYX` |
| CXA | 56 | 0x38 | 0 | Z,N | Copy X to A - Copies X register into A register | `CXA` |
| CYA | 57 | 0x39 | 0 | Z,N | Copy Y to A - Copies Y register into A register | `CYA` |
| CAZ | 58 | 0x3A | 1 | - | Conditional Load A if Zero - Load A with immediate value if Zero flag is set | `CAZ 42` |
| NAZ | 59 | 0x3B | 1 | - | Conditional Load A if Not Zero - Load A with immediate value if Zero flag is not set | `NAZ 42` |
| CAO | 60 | 0x3C | 1 | - | Conditional Load A if Overflow - Load A with immediate value if Overflow flag is set | `CAO 42` |
| NAO | 61 | 0x3D | 1 | - | Conditional Load A if Not Overflow - Load A with immediate value if Overflow flag is not set | `NAO 42` |
| CAN | 62 | 0x3E | 1 | - | Conditional Load A if Negative - Load A with immediate value if Negative flag is set | `CAN 42` |
| NAN | 63 | 0x3F | 1 | - | Conditional Load A if Not Negative - Load A with immediate value if Negative flag is not set | `NAN 42` |
| CXZ | 64 | 0x40 | 1 | - | Conditional Load X if Zero - Load X with immediate value if Zero flag is set | `CXZ 42` |
| NXZ | 65 | 0x41 | 1 | - | Conditional Load X if Not Zero - Load X with immediate value if Zero flag is not set | `NXZ 42` |
| CXO | 66 | 0x42 | 1 | - | Conditional Load X if Overflow - Load X with immediate value if Overflow flag is set | `CXO 42` |
| NXO | 67 | 0x43 | 1 | - | Conditional Load X if Not Overflow - Load X with immediate value if Overflow flag is not set | `NXO 42` |
| CXN | 68 | 0x44 | 1 | - | Conditional Load X if Negative - Load X with immediate value if Negative flag is set | `CXN 42` |
| NXN | 69 | 0x45 | 1 | - | Conditional Load X if Not Negative - Load X with immediate value if Negative flag is not set | `NXN 42` |
| CYZ | 70 | 0x46 | 1 | - | Conditional Load Y if Zero - Load Y with immediate value if Zero flag is set | `CYZ 42` |
| NYZ | 71 | 0x47 | 1 | - | Conditional Load Y if Not Zero - Load Y with immediate value if Zero flag is not set | `NYZ 42` |
| CYO | 72 | 0x48 | 1 | - | Conditional Load Y if Overflow - Load Y with immediate value if Overflow flag is set | `CYO 42` |
| NYO | 73 | 0x49 | 1 | - | Conditional Load Y if Not Overflow - Load Y with immediate value if Overflow flag is not set | `NYO 42` |
| CYN | 74 | 0x4A | 1 | - | Conditional Load Y if Negative - Load Y with immediate value if Negative flag is set | `CYN 42` |
| NYN | 75 | 0x4B | 1 | - | Conditional Load Y if Not Negative - Load Y with immediate value if Negative flag is not set | `NYN 42` |
| **Memory Instructions** |
| WMA | 76 | 0x4C | 2 | - | Write Memory A - writes the value of register A to specified memory location | `WMA $1000` |
| WMX | 77 | 0x4D | 2 | - | Write Memory X - writes the value of register X to specified memory location | `WMX $1000` |
| WMY | 78 | 0x4E | 2 | - | Write Memory Y - writes the value of register Y to specified memory location | `WMY $1000` |
| RMA | 79 | 0x4F | 2 | - | Read Memory A - reads the value of specified memory location to register A | `RMA $1000` |
| RMX | 80 | 0x50 | 2 | - | Read Memory X - reads the value of specified memory location to register X | `RMX $1000` |
| RMY | 81 | 0x51 | 2 | - | Read Memory Y - reads the value of specified memory location to register Y | `RMY $1000` |
| RMI | 82 | 0x52 | 0 | Z,N | Read Memory Indexed - reads memory[X + Y*256] into A register | `RMI` |
| WMI | 83 | 0x53 | 0 | - | Write Memory Indexed - writes A register to memory[X + Y*256] | `WMI` |
| RMO | 84 | 0x54 | 2 | Z,N | Read Memory Offset - reads memory[base_addr + X] into A register, base_addr is provided as 2-byte parameter | `RMO $1000` |
| WMO | 85 | 0x55 | 2 | - | Write Memory Offset - writes A register to memory[base_addr + X], base_addr is provided as 2-byte parameter | `WMO $1000` |
| FIL | 86 | 0x56 | 1 | - | Fill - Fill A bytes starting at (X,Y) with value from parameter | `FIL 42` |
| CMP | 87 | 0x57 | 2 | Z | Compare Memory - Compare A bytes at (X,Y) with bytes at specified address, set Z flag if equal | `CMP $1000` |
| CPY | 88 | 0x58 | 2 | - | Copy Memory - Copy A bytes from source (X,Y) to destination address | `CPY $1000` |

## Assembly Language Notes

- **Addresses**: Use `$` prefix for hexadecimal addresses (e.g., `$1000`, `$FFFF`)
- **Immediate values**: Use decimal numbers directly (e.g., `42`, `255`)
- **Labels**: Use `:LABEL` syntax for defining jump targets
- **Comments**: Use `;` to start comments

## Flag Legend

- **Z**: Zero flag - set when result is zero
- **O**: Overflow flag - set when result exceeds 8-bit range
- **N**: Negative flag - set when result is negative (bit 7 set)
- **H**: Halt flag - set by HLT instruction
- **-**: No flags affected