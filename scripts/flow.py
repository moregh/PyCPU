#!/usr/bin/env python3
"""
Assembly Control Flow Analyzer - Sequential Parse Version
Accurately parses assembly files by scanning sequentially and tracking all labels and jumps
"""

import argparse
import re
import sys
from typing import Dict, List, Set, Tuple, Optional


class ControlFlowAnalyzer:
    """Analyzes control flow in assembly programs and generates DOT graphs"""
    
    def __init__(self):
        # Jump instructions that affect control flow
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
        }
        
        # Instructions that end execution flow
        self.terminal_instructions = {'HLT'}
        
        # Our CPU's instruction set
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

        # Common macro patterns
        self.macro_patterns = {
            'CALL': self.expand_call_macro,
            'PUSH': self.expand_push_macro,
            'POP': self.expand_pop_macro,
            'MEMSET_CALL': self.expand_memset_call_macro,
            'MEMCPY_CALL': self.expand_memcpy_call_macro,
            'MEMCMP_CALL': self.expand_memcmp_call_macro,
        }
    
    def expand_call_macro(self, parts: List[str]) -> List[str]:
        """Expand CALL macro: CALL function -> WPC RET_ADDR_LOW; JMP function"""
        if len(parts) >= 2:
            function_name = parts[1]
            return [
                "WPC RET_ADDR_LOW",
                f"JMP {function_name}"
            ]
        return [" ".join(parts)]  # Return as-is if malformed
    
    def expand_push_macro(self, parts: List[str]) -> List[str]:
        """Expand PUSH macro: PUSH value -> LDA value; JMP PUSH_A"""
        if len(parts) >= 2:
            value = parts[1]
            return [
                f"LDA {value}",
                "JMP PUSH_A"
            ]
        return [" ".join(parts)]
    
    def expand_pop_macro(self, parts: List[str]) -> List[str]:
        """Expand POP macro: POP -> JMP POP_A"""
        return ["JMP POP_A"]
    
    def expand_memset_call_macro(self, parts: List[str]) -> List[str]:
        """Expand MEMSET_CALL macro"""
        if len(parts) >= 4:
            addr, value, count = parts[1], parts[2], parts[3]
            return [
                f"LDA {count}",
                "JMP PUSH_A",
                f"LDA {value}",
                "JMP PUSH_A",
                f"LDA {addr} >> 8",
                "JMP PUSH_A",
                f"LDA {addr} & 255",
                "JMP PUSH_A",
                "WPC RET_ADDR_LOW",
                "JMP MEMSET"
            ]
        return [" ".join(parts)]
    
    def expand_memcpy_call_macro(self, parts: List[str]) -> List[str]:
        """Expand MEMCPY_CALL macro"""
        if len(parts) >= 4:
            dest, src, count = parts[1], parts[2], parts[3]
            return [
                f"LDA {count}",
                "JMP PUSH_A",
                f"LDA {src} >> 8",
                "JMP PUSH_A",
                f"LDA {src} & 255",
                "JMP PUSH_A",
                f"LDA {dest} >> 8",
                "JMP PUSH_A",
                f"LDA {dest} & 255",
                "JMP PUSH_A",
                "WPC RET_ADDR_LOW",
                "JMP MEMCPY"
            ]
        return [" ".join(parts)]
    
    def expand_memcmp_call_macro(self, parts: List[str]) -> List[str]:
        """Expand MEMCMP_CALL macro"""
        if len(parts) >= 4:
            ptr1, ptr2, count = parts[1], parts[2], parts[3]
            return [
                f"LDA {count}",
                "JMP PUSH_A",
                f"LDA {ptr2} >> 8",
                "JMP PUSH_A", 
                f"LDA {ptr2} & 255",
                "JMP PUSH_A",
                f"LDA {ptr1} >> 8",
                "JMP PUSH_A",
                f"LDA {ptr1} & 255",
                "JMP PUSH_A",
                "WPC RET_ADDR_LOW",
                "JMP MEMCMP"
            ]
        return [" ".join(parts)]
    
    def parse_assembly_file(self, filename: str) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Parse assembly file, expand macros, and extract all labels and jumps
        
        Returns:
            Tuple of (all_labels, jumps_dict)
        """
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Assembly file not found: {filename}")
        
        # First pass: expand macros and collect all lines
        expanded_lines = []
        current_label = None
        all_labels = []
        
        for line_num, line in enumerate(lines, 1):
            original_line = line.rstrip()
            clean_line = line.split(';')[0].strip()
            
            if not clean_line:
                continue
            
            # Check for label definition
            label_match = re.match(r'^:(\w+)', clean_line)
            if label_match:
                label_name = label_match.group(1)
                all_labels.append(label_name)
                current_label = label_name
                continue
            
            # Skip constants and macro definitions
            if re.match(r'^\s*(CONST|CONSTANT|MACRO|ENDMACRO)\s+', clean_line, re.IGNORECASE):
                continue
            
            # Parse instruction
            parts = clean_line.split()
            if not parts:
                continue
            
            instruction = parts[0].upper()
            
            # Expand macros
            if instruction in self.macro_patterns:
                expanded = self.macro_patterns[instruction](parts)
                expanded_lines.extend([(current_label, exp_line) for exp_line in expanded])
            else:
                # Regular instruction
                expanded_lines.append((current_label, clean_line))
        
        # Second pass: find all jumps
        jumps_dict = {}
        
        for current_label, line in expanded_lines:
            if not current_label:
                continue
                
            parts = line.split()
            if len(parts) < 2:
                continue
            
            instruction = parts[0].upper()
            
            # Check if this is a jump instruction
            if instruction in self.jump_instructions:
                target = parts[1]
                jump_type = self.jump_instructions[instruction]
                
                if current_label not in jumps_dict:
                    jumps_dict[current_label] = []
                
                jumps_dict[current_label].append((target, jump_type))
        
        return all_labels, jumps_dict
    
    def build_control_flow_graph(self, all_labels: List[str], jumps_dict: Dict[str, List[str]]) -> Dict[str, List[Tuple[str, str]]]:
        """Build control flow graph from labels and jumps"""
        
        graph = {}
        
        # Initialize all labels as nodes
        for label in all_labels:
            graph[label] = []
        
        # Add jump edges
        for source_label, jump_list in jumps_dict.items():
            if source_label in graph:
                for target, jump_type in jump_list:
                    # Add target to graph if it doesn't exist (external reference)
                    if target not in graph:
                        graph[target] = []
                    
                    edge = (target, jump_type)
                    if edge not in graph[source_label]:
                        graph[source_label].append(edge)
        
        # Add fall-through edges between consecutive labels
        # This is more sophisticated - we need to check if labels are terminal
        for i in range(len(all_labels) - 1):
            current_label = all_labels[i]
            next_label = all_labels[i + 1]
            
            # Check if current label has any jumps
            has_unconditional_jump = False
            has_any_jump = False
            
            if current_label in jumps_dict:
                for target, jump_type in jumps_dict[current_label]:
                    has_any_jump = True
                    if jump_type == 'unconditional':
                        has_unconditional_jump = True
                        break
            
            # Add fall-through in these cases:
            # 1. Label has no jumps at all (pure fall-through)
            # 2. Label only has conditional jumps (can fall through if condition fails)
            # 3. Label is an internal function label (like MEMCPY_LOOP)
            should_fall_through = (
                not has_any_jump or 
                (has_any_jump and not has_unconditional_jump) or
                self.is_internal_label(current_label, next_label)
            )
            
            if should_fall_through:
                edge = (next_label, 'fallthrough')
                if edge not in graph[current_label]:
                    graph[current_label].append(edge)
        
        return graph
    
    def is_internal_label(self, current_label: str, next_label: str) -> bool:
        """Check if these are internal labels within the same function"""
        # Common patterns for internal labels within functions
        if any(pattern in current_label.upper() for pattern in ['_LOOP', '_OK', '_DONE', '_CONTINUE', '_READ', '_UPDATE']):
            # If the next label also looks internal and they share a prefix, they're related
            current_prefix = current_label.split('_')[0]
            next_prefix = next_label.split('_')[0]
            
            if current_prefix == next_prefix:
                return True
            
            # Special cases for common internal flow patterns
            if (current_prefix in ['MEMSET', 'MEMCPY', 'MEMCMP', 'PUSH', 'POP'] and
                next_prefix in ['MEMSET', 'MEMCPY', 'MEMCMP', 'PUSH', 'POP']):
                return True
        
        return False
    
    def generate_dot(self, graph: Dict[str, List[Tuple[str, str]]], 
                    program_name: str = "assembly_program") -> str:
        """Generate Graphviz DOT format from control flow graph"""
        
        dot_lines = [
            f'digraph "{program_name}" {{',
            '    rankdir=TB;',
            '    node [shape=box, style="rounded,filled"];',
            ''
        ]
        
        # Get all nodes
        all_nodes = set(graph.keys())
        for edges in graph.values():
            for target, _ in edges:
                all_nodes.add(target)
        
        # Add node definitions with styling
        for node in sorted(all_nodes):
            if node in ["ENTRY", "START", "INIT", "USER_MAIN", "_START"]:
                dot_lines.append(f'    "{node}" [fillcolor=lightgreen, label="{node}\\n(Entry Point)"];')
            elif any(keyword in node.upper() for keyword in ["MEMSET", "MEMCPY", "MEMCMP", "PUSH", "POP"]):
                dot_lines.append(f'    "{node}" [fillcolor=lightblue, label="{node}\\n(Library)"];')
            elif any(keyword in node.upper() for keyword in ["ERROR", "FAIL"]):
                dot_lines.append(f'    "{node}" [fillcolor=pink];')
            elif any(keyword in node.upper() for keyword in ["SUCCESS", "VICTORY", "WIN", "CLEANUP", "EXIT", "DONE"]):
                dot_lines.append(f'    "{node}" [fillcolor=lightcyan];')
            elif any(keyword in node.upper() for keyword in ["LOOP", "REPEAT", "CONTINUE", "RETRY"]):
                dot_lines.append(f'    "{node}" [fillcolor=lightyellow];')
            elif any(keyword in node.upper() for keyword in ["DEAD", "UNREACHABLE", "ORPHANED"]):
                dot_lines.append(f'    "{node}" [fillcolor=lightgray];')
            else:
                dot_lines.append(f'    "{node}" [fillcolor=white];')
        
        dot_lines.append('')
        
        # Add edges with styling
        dot_lines.append('    // Control flow edges')
        for source in sorted(graph.keys()):
            for target, edge_type in graph[source]:
                if edge_type == 'unconditional':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=red, label="JMP", penwidth=2];')
                elif edge_type == 'conditional':
                    dot_lines.append(f'    "{source}" -> "{target}" [color=blue, label="conditional"];')
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
        all_labels, jumps_dict = self.parse_assembly_file(filename)
        graph = self.build_control_flow_graph(all_labels, jumps_dict)
        
        import os
        program_name = os.path.splitext(os.path.basename(filename))[0]
        
        return self.generate_dot(graph, program_name)


def main():
    parser = argparse.ArgumentParser(
        description="Generate control flow graphs for CPU assembly programs with macro expansion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flow_analyzer.py program.asm
  python flow_analyzer.py --output flow.dot program.asm
  python flow_analyzer.py --render program.asm
  python flow_analyzer.py --format png --output flow.png program.asm
        """
    )
    
    parser.add_argument('input_file', help='Assembly source file to analyze')
    parser.add_argument('--output', '-o', help='Output file path (default: <input_name>.dot)')
    parser.add_argument('--render', '-r', action='store_true', help='Render the DOT file to an image using Graphviz')
    parser.add_argument('--format', '-f', choices=['png', 'svg', 'pdf', 'ps', 'dot'], default='png', help='Output format when rendering (default: png)')
    parser.add_argument('--view', '-v', action='store_true', help='Open the rendered output with default viewer')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    try:
        analyzer = ControlFlowAnalyzer()
        
        if args.verbose:
            print(f"Analyzing assembly file: {args.input_file}")
        
        dot_content = analyzer.analyze_file(args.input_file)
        
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
            try:
                import subprocess
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as temp_dot:
                    temp_dot.write(dot_content)
                    temp_dot_path = temp_dot.name
                
                cmd = ['dot', f'-T{args.format}', temp_dot_path, '-o', output_file]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Error rendering with Graphviz: {result.stderr}", file=sys.stderr)
                    sys.exit(1)
                
                os.unlink(temp_dot_path)
                print(f"Control flow graph rendered to: {output_file}")
                
                if args.view:
                    if sys.platform.startswith('darwin'):
                        subprocess.run(['open', output_file])
                    elif sys.platform.startswith('linux'):
                        subprocess.run(['xdg-open', output_file])
                    elif sys.platform.startswith('win'):
                        subprocess.run(['start', output_file], shell=True)
                
            except FileNotFoundError:
                print("Error: Graphviz 'dot' command not found. Please install Graphviz.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error during rendering: {e}", file=sys.stderr)
                sys.exit(1)
        
        else:
            with open(output_file, 'w') as f:
                f.write(dot_content)
            print(f"Control flow DOT file saved to: {output_file}")
            
            if args.verbose:
                print("\nDOT content preview:")
                print(dot_content[:500] + "..." if len(dot_content) > 500 else dot_content)
    
    except Exception as e:
        print(f"Error analyzing assembly file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()