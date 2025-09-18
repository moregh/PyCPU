#!/usr/bin/env python3
"""
Simple Decompiler for 64KiB CPU
Converts machine code (list of integers) back to assembly source code
"""

from typing import List, Dict, Tuple, Optional


class CPUDecompiler:
    """Decompiler for the 8-bit CPU instruction set"""
    
    def __init__(self):
        # Instruction set mapping: opcode -> (name, length, description)
        self.instructions = {
            0: ("HLT", 0, "Halt - stops the processor"),
            1: ("CLR", 0, "Clear - resets A, X and Y registers to 0"),
            2: ("NOP", 0, "No Operation - does nothing but increase the tick counter"),
            3: ("AAX", 0, "Add A and X - Adds register A to register X and store the value in register A"),
            4: ("AAY", 0, "Add A and Y - Adds register A to register Y and store the value in register A"),
            5: ("AXY", 0, "Add X and Y - Adds register X to register Y and store the value in register X"),
            6: ("SAX", 0, "Subtract A and X - Subtracts register X from register A and store the value in register A"),
            7: ("SAY", 0, "Subtract A and Y - Subtracts register Y from register A and store the value in register A"),
            8: ("SXY", 0, "Subtract X and Y - Subtracts register Y from register X and store the value in register X"),
            9: ("INA", 0, "Increment A - Adds 1 to value of A register"),
            10: ("INX", 0, "Increment X - Adds 1 to value of X register"),
            11: ("INY", 0, "Increment Y - Adds 1 to value of Y register"),
            12: ("DEA", 0, "Decrement A - Subtracts 1 from value of A register"),
            13: ("DEX", 0, "Decrement X - Subtracts 1 from value of X register"),
            14: ("DEY", 0, "Decrement Y - Subtracts 1 from value of Y register"),
            15: ("NAX", 0, "AND A & X - ANDs A and X and saves the result in A"),
            16: ("NAY", 0, "AND A & Y - ANDs A and Y and saves the result in A"),
            17: ("NXY", 0, "AND X & Y - ANDs X and Y and saves the result in X"),
            18: ("OAX", 0, "OR A & X - ORs A and X and saves the result in A"),
            19: ("OAY", 0, "OR A & Y - ORs A and Y and saves the result in A"),
            20: ("OXY", 0, "OR X & Y - ORs X and Y and saves the result in X"),
            21: ("XAX", 0, "XOR A and X - XORs A and X and saves the result in A"),
            22: ("XAY", 0, "XOR A and Y - XORs A and Y and saves the result in A"),
            23: ("XXY", 0, "XOR X and Y - XORs X and Y and saves the result in X"),
            24: ("BLA", 0, "Bit Shift Left A - Bit-shift A register left by 1 (double)"),
            25: ("BLX", 0, "Bit Shift Left X - Bit-shift X register left by 1 (double)"),
            26: ("BLY", 0, "Bit Shift Left Y - Bit-shift Y register left by 1 (double)"),
            27: ("BRA", 0, "Bit Shift Right A - Bit-shift A register right by 1 (half)"),
            28: ("BRX", 0, "Bit Shift Right X - Bit-shift X register right by 1 (half)"),
            29: ("BRY", 0, "Bit Shift Right Y - Bit-shift Y register right by 1 (half)"),
            30: ("EAX", 0, "Equal A and X - Compares A and X for equality and sets Zero flag if true"),
            31: ("EAY", 0, "Equal A and Y - Compares A and Y for equality and sets Zero flag if true"),
            32: ("EXY", 0, "Equal X and Y - Compares X and Y for equality and sets Zero flag if true"),
            33: ("JMP", 2, "Jump - Jump to specified memory location"),
            34: ("JNZ", 2, "Jump Not Zero - Jump to specified memory location if the Zero flag was not set"),
            35: ("JMZ", 2, "Jump if Zero - Jump to specified memory location if the Zero flag was set"),
            36: ("JNN", 2, "Jump Not Negative - Jump to specified memory location if the Negative flag was not set"),
            37: ("JMN", 2, "Jump if Negative - Jump to specified memory location if the Negative flag was set"),
            38: ("JNO", 2, "Jump Not Overflow - Jump to specified memory location if the Overflow flag was not set"),
            39: ("JMO", 2, "Jump if Overflow - Jump to specified memory location if the Overflow flag was set"),
            40: ("JFA", 0, "Jump Forward A - sets PC to its current value plus the value of the A register"),
            41: ("JFX", 0, "Jump Forward X - sets PC to its current value plus the value of the X register"),
            42: ("JFY", 0, "Jump Forward Y - sets PC to its current value plus the value of the Y register"),
            43: ("JBA", 0, "Jump Backward A - sets PC to its current value minus the value of the A register"),
            44: ("JBX", 0, "Jump Backward X - sets PC to its current value minus the value of the X register"),
            45: ("JBY", 0, "Jump Backward Y - sets PC to its current value minus the value of the Y register"),
            46: ("JAD", 2, "Jump to Memory Address - Sets program counter to address at specified memory location"),
            47: ("WPC", 2, "Write Program Counter - writes the current value of the program counter to specified memory location"),
            48: ("RPC", 2, "Read Program Counter - reads a 2-byte value from specified memory location and sets PC"),
            49: ("LDA", 1, "Load A - loads A register with a specified value"),
            50: ("LDX", 1, "Load X - loads X register with a specified value"),
            51: ("LDY", 1, "Load Y - loads Y register with a specified value"),
            52: ("CAX", 0, "Copy A to X - Copies A register into X register"),
            53: ("CAY", 0, "Copy A to Y - Copies A register into Y register"),
            54: ("CXY", 0, "Copy X to Y - Copies X register into Y register"),
            55: ("CYX", 0, "Copy Y to X - Copies Y register into X register"),
            56: ("CXA", 0, "Copy X to A - Copies X register into A register"),
            57: ("CYA", 0, "Copy Y to A - Copies Y register into A register"),
            58: ("CAZ", 1, "Conditional Load A if Zero - Load A with immediate value if Zero flag is set"),
            59: ("NAZ", 1, "Conditional Load A if Not Zero - Load A with immediate value if Zero flag is not set"),
            60: ("CAO", 1, "Conditional Load A if Overflow - Load A with immediate value if Overflow flag is set"),
            61: ("NAO", 1, "Conditional Load A if Not Overflow - Load A with immediate value if Overflow flag is not set"),
            62: ("CAN", 1, "Conditional Load A if Negative - Load A with immediate value if Negative flag is set"),
            63: ("NAN", 1, "Conditional Load A if Not Negative - Load A with immediate value if Negative flag is not set"),
            64: ("CXZ", 1, "Conditional Load X if Zero - Load X with immediate value if Zero flag is set"),
            65: ("NXZ", 1, "Conditional Load X if Not Zero - Load X with immediate value if Zero flag is not set"),
            66: ("CXO", 1, "Conditional Load X if Overflow - Load X with immediate value if Overflow flag is set"),
            67: ("NXO", 1, "Conditional Load X if Not Overflow - Load X with immediate value if Overflow flag is not set"),
            68: ("CXN", 1, "Conditional Load X if Negative - Load X with immediate value if Negative flag is set"),
            69: ("NXN", 1, "Conditional Load X if Not Negative - Load X with immediate value if Negative flag is not set"),
            70: ("CYZ", 1, "Conditional Load Y if Zero - Load Y with immediate value if Zero flag is set"),
            71: ("NYZ", 1, "Conditional Load Y if Not Zero - Load Y with immediate value if Zero flag is not set"),
            72: ("CYO", 1, "Conditional Load Y if Overflow - Load Y with immediate value if Overflow flag is set"),
            73: ("NYO", 1, "Conditional Load Y if Not Overflow - Load Y with immediate value if Overflow flag is not set"),
            74: ("CYN", 1, "Conditional Load Y if Negative - Load Y with immediate value if Negative flag is set"),
            75: ("NYN", 1, "Conditional Load Y if Not Negative - Load Y with immediate value if Negative flag is not set"),
            76: ("WMA", 2, "Write Memory A - writes the value of register A to specified memory location"),
            77: ("WMX", 2, "Write Memory X - writes the value of register X to specified memory location"),
            78: ("WMY", 2, "Write Memory Y - writes the value of register Y to specified memory location"),
            79: ("RMA", 2, "Read Memory A - reads the value of specified memory location to register A"),
            80: ("RMX", 2, "Read Memory X - reads the value of specified memory location to register X"),
            81: ("RMY", 2, "Read Memory Y - reads the value of specified memory location to register Y"),
            82: ("RMI", 0, "Read Memory Indexed - reads memory[X + Y*256] into A register"),
            83: ("WMI", 0, "Write Memory Indexed - writes A register to memory[X + Y*256]"),
            84: ("RMO", 2, "Read Memory Offset - reads memory[base_addr + X] into A register"),
            85: ("WMO", 2, "Write Memory Offset - writes A register to memory[base_addr + X]"),
            86: ("FIL", 1, "Fill - Fill A bytes starting at (X,Y) with value from parameter"),
            87: ("CMP", 2, "Compare Memory - Compare A bytes at (X,Y) with bytes at specified address"),
            88: ("CPY", 2, "Copy Memory - Copy A bytes from source (X,Y) to destination address"),
        }
        
        # Common memory addresses for better readability
        self.memory_labels = {
            0xEE00: "SP_LOW",
            0xEE01: "SP_HIGH", 
            0xEE02: "FP_LOW",
            0xEE03: "FP_HIGH",
            0xEE10: "SYSTEM_FLAGS",
            0xEE11: "EXIT_CODE",
            0xEE80: "STACK_BASE_LOW",
            0xEE81: "STACK_BASE_HIGH",
            0xEE90: "TEMP_STORE",
            0xF000: "GPU_CTRL_START",
            0xF060: "GPU_FRAMEBUFFER",
        }
    
    def bytes_to_address(self, high_byte: int, low_byte: int) -> int:
        """Convert two bytes to 16-bit address"""
        return (high_byte << 8) | low_byte
    
    def format_address(self, address: int) -> str:
        """Format address with label if known, otherwise as hex"""
        if address in self.memory_labels:
            return self.memory_labels[address]
        return f"${address:04X}"
    
    def format_immediate(self, value: int) -> str:
        """Format immediate value"""
        if 32 <= value <= 126:  # Printable ASCII
            return f"{value}    ; '{chr(value)}'"
        return str(value)
    
    def find_jump_targets(self, machine_code: List[int]) -> Dict[int, str]:
        """Find all jump targets to create labels"""
        targets = {}
        pc = 0
        label_counter = 1
        
        while pc < len(machine_code):
            if pc >= len(machine_code):
                break
                
            opcode = machine_code[pc]
            if opcode not in self.instructions:
                pc += 1
                continue
                
            name, length, _ = self.instructions[opcode]
            
            # Check if this is a jump instruction
            if name in ["JMP", "JNZ", "JMZ", "JNN", "JMN", "JNO", "JMO", "JAD", "WPC", "RPC"]:
                if pc + 2 < len(machine_code):
                    target = self.bytes_to_address(machine_code[pc + 1], machine_code[pc + 2])
                    if target not in targets and target < len(machine_code):
                        targets[target] = f"LABEL_{label_counter}"
                        label_counter += 1
            
            pc += 1 + length
        
        return targets
    
    def decompile(self, machine_code: List[int], include_comments: bool = True, 
                  include_addresses: bool = False) -> str:
        """
        Decompile machine code to assembly source
        
        Args:
            machine_code: List of integers representing machine code
            include_comments: Include instruction descriptions as comments
            include_addresses: Include memory addresses in output
            
        Returns:
            Decompiled assembly source code as string
        """
        if not machine_code:
            return "; Empty program\n"
        
        # Find jump targets for labels
        jump_targets = self.find_jump_targets(machine_code)
        
        lines = []
        pc = 0
        
        # Add header comment
        lines.append("; Decompiled assembly code")
        lines.append(f"; Original size: {len(machine_code)} bytes")
        lines.append("")
        
        while pc < len(machine_code):
            # Add label if this address is a jump target
            if pc in jump_targets:
                lines.append(f":{jump_targets[pc]}")
            
            # Check if we have enough bytes for an instruction
            if pc >= len(machine_code):
                break
                
            opcode = machine_code[pc]
            
            # Handle unknown opcodes
            if opcode not in self.instructions:
                addr_str = f"[${pc:04X}] " if include_addresses else ""
                lines.append(f"{addr_str}    ; Unknown opcode: {opcode}")
                pc += 1
                continue
            
            name, length, description = self.instructions[opcode]
            
            # Build instruction line
            addr_str = f"[${pc:04X}] " if include_addresses else ""
            instruction_parts = [name]
            
            # Add parameters based on instruction length
            if length == 1:
                if pc + 1 < len(machine_code):
                    param = machine_code[pc + 1]
                    instruction_parts.append(self.format_immediate(param))
                else:
                    instruction_parts.append("?? ; Missing parameter")
                    
            elif length == 2:
                if pc + 2 < len(machine_code):
                    high_byte = machine_code[pc + 1]
                    low_byte = machine_code[pc + 2]
                    address = self.bytes_to_address(high_byte, low_byte)
                    
                    # Use label if this address is a known jump target
                    if address in jump_targets:
                        instruction_parts.append(jump_targets[address])
                    else:
                        instruction_parts.append(self.format_address(address))
                else:
                    instruction_parts.append("?? ; Missing address")
            
            # Format the complete line
            instruction_str = " ".join(instruction_parts)
            comment_str = f"    ; {description}" if include_comments else ""
            line = f"{addr_str}{instruction_str:<20}{comment_str}"
            lines.append(line)
            
            pc += 1 + length
        
        # Add any remaining bytes as data
        if pc < len(machine_code):
            lines.append("")
            lines.append("; Remaining data:")
            while pc < len(machine_code):
                addr_str = f"[${pc:04X}] " if include_addresses else ""
                lines.append(f"{addr_str}    ; Data: {machine_code[pc]}")
                pc += 1
        
        return "\n".join(lines)
    
    def decompile_to_file(self, machine_code: List[int], output_file: str, **kwargs):
        """Decompile and save to file"""
        assembly_code = self.decompile(machine_code, **kwargs)
        with open(output_file, 'w') as f:
            f.write(assembly_code)
        print(f"Decompiled assembly saved to: {output_file}")


def main(code):
    """Main decompiler function"""
    decompiler = CPUDecompiler()
    
    print("=== CPU Decompiler ===")
    print(f"Decompiling {len(code)} bytes of machine code...")
    print()
    
    result = decompiler.decompile(code, include_comments=True, include_addresses=False)
    for idx, line in enumerate(result.split("\n")):
        print(f"{idx+1:04}: {line}")


if __name__ == "__main__":
    import argparse
    import ast
    import sys
    
    parser = argparse.ArgumentParser(
        description="Decompile CPU machine code to assembly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python decompiler.py "[49, 237, 76, 238, 1, 0]"
  python decompiler.py --file input.txt
  python decompiler.py --output result.asm "[49, 237, 76]"
  python decompiler.py --no-comments --addresses "[49, 237, 76]"
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "code", 
        nargs="?",
        help="Python list of integers as string, e.g., '[49, 237, 76, 238, 1]'"
    )
    input_group.add_argument(
        "--file", "-f",
        help="Read machine code from file (one integer per line or Python list format)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: print to stdout)"
    )
    
    # Formatting options
    parser.add_argument(
        "--no-comments", 
        action="store_true",
        help="Disable instruction description comments"
    )
    parser.add_argument(
        "--addresses", 
        action="store_true",
        help="Include memory addresses in output"
    )
    parser.add_argument(
        "--clean",
        action="store_true", 
        help="Clean output (no comments, no addresses) - equivalent to --no-comments"
    )
    
    args = parser.parse_args()
    
    # Parse input code
    machine_code = []
    
    try:
        if args.file:
            # Read from file
            with open(args.file, 'r') as f:
                content = f.read().strip()
                
            # Try to parse as Python list first
            try:
                machine_code = ast.literal_eval(content)
                if not isinstance(machine_code, list):
                    raise ValueError("File content is not a list")
            except (ValueError, SyntaxError):
                # Parse as one integer per line
                lines = content.splitlines()
                machine_code = []
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        try:
                            machine_code.append(int(line))
                        except ValueError:
                            print(f"Error: Invalid integer on line {line_num}: '{line}'", file=sys.stderr)
                            sys.exit(1)
        else:
            # Parse from command line argument
            try:
                machine_code = ast.literal_eval(args.code)
                if not isinstance(machine_code, list):
                    raise ValueError("Input must be a list")
            except (ValueError, SyntaxError) as e:
                print(f"Error: Invalid Python list format: {e}", file=sys.stderr)
                print("Example: '[49, 237, 76, 238, 1]'", file=sys.stderr)
                sys.exit(1)
        
        # Validate machine code
        if not machine_code:
            print("Error: Empty machine code provided", file=sys.stderr)
            sys.exit(1)
            
        for i, value in enumerate(machine_code):
            if not isinstance(value, int) or not (0 <= value <= 255):
                print(f"Error: Invalid byte value at position {i}: {value} (must be 0-255)", file=sys.stderr)
                sys.exit(1)
    
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Set up decompiler options
    include_comments = not (args.no_comments or args.clean)
    include_addresses = args.addresses and not args.clean
    
    # Decompile
    decompiler = CPUDecompiler()
    
    try:
        result = decompiler.decompile(
            machine_code, 
            include_comments=include_comments,
            include_addresses=include_addresses
        )
        
        # Output result
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"Decompiled assembly saved to: {args.output}")
        else:
            print(result)
            
    except Exception as e:
        print(f"Error during decompilation: {e}", file=sys.stderr)
        sys.exit(1)
