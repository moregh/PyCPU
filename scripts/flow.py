#!/usr/bin/env python3
"""
Assembly Control Flow Analyzer - Updated Version
Generates Graphviz DOT files showing control flow between labels in assembly programs
Compatible with our CPU emulator's instruction set and macro system
"""

import argparse
import re
import sys
from typing import Dict, List, Set, Tuple, Optional


class ControlFlowAnalyzer:
    """Analyzes control flow in assembly programs and generates DOT graphs"""
    
    def __init__(self):
        # Jump instructions that affect control flow (from our instruction set)
        self.jump_instructions = {
            'JMP': 'unconditional',
            'JNZ': 'conditional', 
            'JMZ': 'conditional',
            'JNN': 'conditional',
            'JMN': 'conditional', 
            'JNO': 'conditional',
            'JMO': 'conditional',
            'JFA': 'relative',
            'JFX': 'relative',
            'JFY': 'relative',
            'JBA': 'relative',
            'JBX': 'relative',
            'JBY': 'relative',
            'JAD': 'indirect',
            'RPC': 'indirect',
            'CALL': 'call'  # Our macro-generated calls
        }
        
        # Instructions that end execution flow
        self.terminal_instructions = {'HLT'}
        
        # Instructions that can be function calls
        self.call_instructions = {'WPC', 'JAD', 'CALL'}
        
        # Our CPU's complete instruction set for validation
        self.cpu_instructions = {
            'HLT', 'CLR', 'NOP', 'AAX', 'AAY', 'AXY', 'SAX', 'SAY', 'SXY',
            'INA', 'INX', 'INY', 'DEA', 'DEX', 'DEY', 'NAX', 'NAY', 'NXY',
            'OAX', 'OAY', 'OXY', 'XAX', 'XAY', 'XXY', 'BLA', 'BLX', 'BLY',
            'BRA', 'BRX', 'BRY', 'EAX', 'EAY', 'EXY', 'JMP', 'JNZ', 'JMZ',
            'JNN', 'JMN', 'JNO', 'JMO', 'JFA', 'JFX', 'JFY', 'JBA', 'JBX',
            'JBY', 'JAD', 'WPC', 'RPC', 'LDA', 'LDX', 'LDY', 'CAX', 'CAY',
            'CXY', 'CYX', 'CXA', 'CYA', 'CAZ', 'NAZ', 'CAO', 'NAO', 'CAN',
            'NAN', 'CXZ', 'NXZ', 'CXO', 'NXO', 'CXN', 'NXN', 'CYZ', 'NYZ',
            'CYO', 'NYO', 'CYN', 'NYN', 'WMA', 'WMX', 'WMY', 'RMA', 'RMX',
            'RMY', 'RMI', 'WMI', 'RMO', 'WMO', 'FIL', 'CMP', 'CPY'
        }
        
        # Common macro names that might affect control flow
        self.macro_patterns = {
            'CALL', 'PUSH', 'POP', 'IF_ZERO', 'IF_NOT_ZERO', 'WHILE_NOT_ZERO',
            'FOR_COUNT', 'FUNCTION_ENTER', 'FUNCTION_EXIT', 'MEMSET_CALL',
            'MEMCPY_CALL', 'MEMCMP_CALL'
        }
    
    def parse_assembly_file(self, filename: str) -> Tuple[Dict[str, int], List[Tuple[int, str, int]]]:
        """
        Parse assembly file and extract labels and instructions
        
        Returns:
            Tuple of (label_positions, instruction_list)
        """
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Assembly file not found: {filename}")
        
        labels = {}
        instructions = []
        current_address = 0
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            
            # Remove comments and whitespace
            line = line.split(';')[0].strip()
            if not line:
                continue
            
            # Check for label definition
            label_match = re.match(r'^:(\w+)', line)
            if label_match:
                label_name = label_match.group(1)
                labels[label_name] = current_address
                continue
            
            # Check for constant/macro definitions (don't affect control flow)
            if re.match(r'^\s*(CONST|CONSTANT|MACRO|ENDMACRO)\s+', line, re.IGNORECASE):
                continue
            
            # Parse instruction line
            parts = line.split()
            if not parts:
                continue
                
            instruction = parts[0].upper()
            
            # Check if this is a known instruction or macro
            if instruction in self.cpu_instructions or instruction in self.macro_patterns:
                instructions.append((current_address, original_line.strip(), line_num))
                current_address += 1
            else:
                # Could be a macro call or unknown instruction
                # Treat as potential control flow instruction
                instructions.append((current_address, original_line.strip(), line_num))
                current_address += 1
        
        return labels, instructions
    
    def extract_jump_targets(self, instructions: List[Tuple[int, str, int]], 
                           labels: Dict[str, int]) -> Dict[int, List[Tuple[str, str]]]:
        """
        Extract jump targets from instructions
        
        Returns:
            Dict mapping source address to list of (target_label, jump_type) tuples
        """
        jumps = {}
        
        for addr, instruction_line, line_num in instructions:
            # Parse instruction
            clean_line = instruction_line.split(';')[0].strip()
            parts = clean_line.split()
            if not parts:
                continue
                
            opcode = parts[0].upper()
            
            # Handle macro-generated control flow
            if opcode == 'CALL' and len(parts) > 1:
                target = parts[1]
                if addr not in jumps:
                    jumps[addr] = []
                jumps[addr].append((target, 'call'))
                continue
            
            # Handle conditional macros
            if opcode in ['IF_ZERO', 'IF_NOT_ZERO', 'IF_NEGATIVE', 'IF_NOT_NEGATIVE'] and len(parts) > 1:
                target = parts[1]
                if addr not in jumps:
                    jumps[addr] = []
                jumps[addr].append((target, 'conditional'))
                continue
            
            # Handle standard jump instructions
            if opcode not in self.jump_instructions:
                continue
                
            jump_type = self.jump_instructions[opcode]
            
            # Extract target for direct jumps
            if jump_type in ['unconditional', 'conditional', 'call'] and len(parts) > 1:
                target = parts[1]
                
                # Handle different target formats
                if target.startswith('$'):
                    # Hex address - convert to label if possible
                    try:
                        target_addr = int(target[1:], 16)
                        target_label = self.find_label_at_address(target_addr, labels)
                        if not target_label:
                            target_label = f"ADDR_{target_addr:04X}"
                    except ValueError:
                        target_label = target
                elif target.isdigit():
                    # Decimal address
                    target_addr = int(target)
                    target_label = self.find_label_at_address(target_addr, labels)
                    if not target_label:
                        target_label = f"ADDR_{target_addr:04X}"
                else:
                    # Assume it's a label name
                    target_label = target
                
                if addr not in jumps:
                    jumps[addr] = []
                jumps[addr].append((target_label, jump_type))
            
            elif jump_type == 'relative':
                # Relative jumps - target determined at runtime
                if addr not in jumps:
                    jumps[addr] = []
                jumps[addr].append(("RELATIVE_TARGET", jump_type))
                
            elif jump_type == 'indirect':
                # Indirect jumps - target determined at runtime
                if addr not in jumps:
                    jumps[addr] = []
                jumps[addr].append(("INDIRECT_TARGET", jump_type))
        
        return jumps
    
    def find_label_at_address(self, address: int, labels: Dict[str, int]) -> Optional[str]:
        """Find label at specific address"""
        for label, addr in labels.items():
            if addr == address:
                return label
        return None
    
    def build_control_flow_graph(self, labels: Dict[str, int], 
                               instructions: List[Tuple[int, str, int]]) -> Dict[str, List[Tuple[str, str]]]:
        """
        Build control flow graph between labels
        
        Returns:
            Dict mapping source labels to list of (target_label, edge_type) tuples
        """
        # Build address to instruction mapping
        addr_to_instruction = {}
        for addr, instruction_line, line_num in instructions:
            clean_line = instruction_line.split(';')[0].strip()
            if clean_line:
                addr_to_instruction[addr] = clean_line.split()[0].upper()
        
        # Build address to label mapping
        address_to_label = self.build_address_to_label_map(labels, instructions)
        jumps = self.extract_jump_targets(instructions, labels)
        
        # Add entry point if not present
        all_labels = set(labels.keys())
        if "__MAIN" not in all_labels and "USER_MAIN" not in all_labels and "INIT" not in all_labels:
            if 0 in address_to_label:
                all_labels.add("__ENTRY")
                labels["__ENTRY"] = 0
                address_to_label[0] = "__ENTRY"
        
        graph = {}
        
        # Initialize graph with all labels
        for label in all_labels:
            graph[label] = []
        
        # Process each instruction to find control flow between labels
        for addr, instruction_line, line_num in instructions:
            clean_line = instruction_line.split(';')[0].strip()
            if not clean_line:
                continue
                
            opcode = clean_line.split()[0].upper()
            source_label = address_to_label.get(addr, f"ADDR_{addr:04X}")
            
            # Handle jumps from this instruction
            if addr in jumps:
                for target_label_or_addr, jump_type in jumps[addr]:
                    # Add edge if it doesn't already exist
                    edge = (target_label_or_addr, jump_type)
                    if source_label not in graph:
                        graph[source_label] = []
                    if edge not in graph[source_label]:
                        graph[source_label].append(edge)
            
            # Handle fall-through to next instruction
            next_addr = addr + 1
            if (opcode not in self.terminal_instructions and 
                opcode != 'JMP' and  # Unconditional jump doesn't fall through
                not opcode.startswith('CALL') and  # Function calls might not fall through
                next_addr in address_to_label):
                
                next_label = address_to_label[next_addr]
                
                # Only add fall-through edge if we're moving to a different label
                if next_label != source_label:
                    edge = (next_label, 'fallthrough')
                    if source_label not in graph:
                        graph[source_label] = []
                    if edge not in graph[source_label]:
                        graph[source_label].append(edge)
        
        # Remove empty nodes that have no incoming or outgoing edges
        all_targets = set()
        for source_edges in graph.values():
            for target, _ in source_edges:
                all_targets.add(target)
        
        filtered_graph = {}
        for label, edges in graph.items():
            if edges or label in all_targets or label in ["__ENTRY", "__MAIN", "USER_MAIN", "INIT"]:
                filtered_graph[label] = edges
        
        return filtered_graph
    
    def build_address_to_label_map(self, labels: Dict[str, int], 
                                 instructions: List[Tuple[int, str, int]]) -> Dict[int, str]:
        """Build a map from each instruction address to its controlling label"""
        address_to_label = {}
        
        # Add entry point if address 0 doesn't have a label
        all_labels = dict(labels)
        if 0 not in all_labels.values():
            if any(addr == 0 for addr, _, _ in instructions):
                all_labels["__ENTRY"] = 0
        
        # Sort labels by address
        sorted_labels = sorted(all_labels.items(), key=lambda x: x[1])
        
        # For each instruction, find which label controls it
        for addr, instruction_line, line_num in instructions:
            controlling_label = None
            
            # Find the most recent label at or before this address
            for label, label_addr in reversed(sorted_labels):
                if label_addr <= addr:
                    controlling_label = label
                    break
            
            if controlling_label is None:
                # This shouldn't happen if we have __ENTRY, but just in case
                controlling_label = f"ORPHAN_{addr:04X}"
            
            address_to_label[addr] = controlling_label
        
        return address_to_label
    
    def generate_dot(self, graph: Dict[str, List[Tuple[str, str]]], 
                    program_name: str = "assembly_program") -> str:
        """Generate Graphviz DOT format from control flow graph"""
        
        dot_lines = [
            f'digraph "{program_name}" {{',
            '    rankdir=TB;',
            '    node [shape=box, style=rounded];',
            ''
        ]
        
        # Define node styles
        dot_lines.extend([
            '    // Node styles',
            '    node [shape=box, style="rounded,filled"];',
            ''
        ])
        
        # Collect all nodes
        all_nodes = set()
        for source in graph:
            all_nodes.add(source)
            for target, _ in graph[source]:
                all_nodes.add(target)
        
        # Add node definitions with styling
        for node in sorted(all_nodes):
            if node in ["__ENTRY", "__MAIN", "USER_MAIN", "INIT"]:
                dot_lines.append(f'    "{node}" [fillcolor=lightgreen, label="{node}\\n(Entry Point)"];')
            elif node.startswith("ADDR_") or node.startswith("ORPHAN_"):
                dot_lines.append(f'    "{node}" [fillcolor=red, label="{node}\\n(Broken Code!)"];')
            elif node in ["RELATIVE_TARGET", "INDIRECT_TARGET"]:
                dot_lines.append(f'    "{node}" [fillcolor=orange, shape=ellipse];')
            elif any(mem_func in node for mem_func in ["MEMSET", "MEMCPY", "MEMCMP", "PUSH", "POP"]):
                dot_lines.append(f'    "{node}" [fillcolor=lightblue, label="{node}\\n(Library)"];')
            else:
                dot_lines.append(f'    "{node}" [fillcolor=lightcyan];')
        
        dot_lines.append('')
        
        # Add edges with styling
        dot_lines.append('    // Control flow edges')
        for source in sorted(graph.keys()):
            for target, edge_type in graph[source]:
                if edge_type == 'unconditional':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=red, label="JMP", penwidth=2];')
                elif edge_type == 'conditional':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=blue, label="conditional"];')
                elif edge_type == 'call':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=green, label="CALL", penwidth=2];')
                elif edge_type == 'fallthrough':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=gray, style=dashed];')
                elif edge_type == 'relative':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=orange, label="relative"];')
                elif edge_type == 'indirect':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=purple, label="indirect"];')
                else:
                    dot_lines.append(f'    "{source}" -> "{target}";')
        
        dot_lines.append('}')
        return '\n'.join(dot_lines)
    
    def analyze_file(self, filename: str) -> str:
        """Analyze assembly file and return DOT format"""
        labels, instructions = self.parse_assembly_file(filename)
        graph = self.build_control_flow_graph(labels, instructions)
        
        # Extract program name from filename
        import os
        program_name = os.path.splitext(os.path.basename(filename))[0]
        
        return self.generate_dot(graph, program_name)


def main():
    parser = argparse.ArgumentParser(
        description="Generate control flow graphs for CPU assembly programs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flow_analyzer.py program.asm
  python flow_analyzer.py --output flow.dot program.asm
  python flow_analyzer.py --render program.asm
  python flow_analyzer.py --format png --output flow.png program.asm

Output formats (with --render):
  png, svg, pdf, ps, dot (default: png)
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Assembly source file to analyze'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: <input_name>.dot)'
    )
    
    parser.add_argument(
        '--render', '-r',
        action='store_true',
        help='Render the DOT file to an image using Graphviz'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['png', 'svg', 'pdf', 'ps', 'dot'],
        default='png',
        help='Output format when rendering (default: png)'
    )
    
    parser.add_argument(
        '--view', '-v',
        action='store_true',
        help='Open the rendered output with default viewer'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = ControlFlowAnalyzer()
        
        if args.verbose:
            print(f"Analyzing assembly file: {args.input_file}")
        
        # Generate DOT content
        dot_content = analyzer.analyze_file(args.input_file)
        
        # Determine output filename
        if args.output:
            output_file = args.output
        else:
            import os
            base_name = os.path.splitext(args.input_file)[0]
            if args.render:
                output_file = f"{base_name}.{args.format}"
            else:
                output_file = f"{base_name}.dot"
        
        if args.render:
            # Render using Graphviz
            try:
                import subprocess
                import tempfile
                import os
                
                # Write DOT content to temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as temp_dot:
                    temp_dot.write(dot_content)
                    temp_dot_path = temp_dot.name
                
                # Render with Graphviz
                cmd = ['dot', f'-T{args.format}', temp_dot_path, '-o', output_file]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Error rendering with Graphviz: {result.stderr}", file=sys.stderr)
                    sys.exit(1)
                
                # Clean up temp file
                os.unlink(temp_dot_path)
                
                print(f"Control flow graph rendered to: {output_file}")
                
                # Open with default viewer if requested
                if args.view:
                    if sys.platform.startswith('darwin'):  # macOS
                        subprocess.run(['open', output_file])
                    elif sys.platform.startswith('linux'):  # Linux
                        subprocess.run(['xdg-open', output_file])
                    elif sys.platform.startswith('win'):  # Windows
                        subprocess.run(['start', output_file], shell=True)
                
            except FileNotFoundError:
                print("Error: Graphviz 'dot' command not found. Please install Graphviz.", file=sys.stderr)
                print("On Ubuntu/Debian: sudo apt-get install graphviz", file=sys.stderr)
                print("On macOS: brew install graphviz", file=sys.stderr)
                print("On Windows: Download from https://graphviz.org/download/", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error during rendering: {e}", file=sys.stderr)
                sys.exit(1)
        
        else:
            # Just save DOT file
            with open(output_file, 'w') as f:
                f.write(dot_content)
            print(f"Control flow DOT file saved to: {output_file}")
            
            if args.verbose:
                print("\nDOT content preview:")
                print(dot_content[:500] + "..." if len(dot_content) > 500 else dot_content)
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing assembly file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()