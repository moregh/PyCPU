import os
import sys
from typing import Dict, List, Union, Optional
from dataclasses import dataclass
from enum import Enum

# Add the src directory to the path for imports
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..')
sys.path.insert(0, src_dir)

try:
    from .instructions import InstructionSet, NameToOpcode
    from .types import Data
except ImportError:
    # Fallback for direct execution
    from python_cpu_emulator.instructions import InstructionSet, NameToOpcode
    from python_cpu_emulator.types import Data


class TokenType(Enum):
    LABEL = "LABEL"
    INSTRUCTION = "INSTRUCTION"
    CONSTANT_DEF = "CONSTANT_DEF"
    VARIABLE_DEF = "VARIABLE_DEF"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    HEX_NUMBER = "HEX_NUMBER"
    CHARACTER = "CHARACTER"
    STRING = "STRING"
    COMMENT = "COMMENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


@dataclass
class Symbol:
    name: str
    value: Union[int, str]
    type: str  # 'constant', 'variable', 'label'
    line: int


class CompilerError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")


class Lexer:
    """Tokenizes assembly source code"""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self):
        if self.pos < len(self.source) and self.source[self.pos] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t': # type: ignore
            self.advance()
    
    def read_number(self) -> str:
        start_pos = self.pos
        if self.current_char() == '-':
            self.advance()
        
        while self.current_char() and self.current_char().isdigit(): # type: ignore
            self.advance()
        
        return self.source[start_pos:self.pos]
    
    def read_hex_number(self) -> str:
        start_pos = self.pos
        self.advance()  # Skip '$'
        
        while (self.current_char() and 
               self.current_char() in '0123456789ABCDEFabcdef'): # type: ignore
            self.advance()
        
        return self.source[start_pos:self.pos]
    
    def read_identifier(self) -> str:
        start_pos = self.pos
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() in '_')): # type: ignore
            self.advance()
        
        return self.source[start_pos:self.pos]
    
    def read_character(self) -> str:
        self.advance()  # Skip opening quote
        start_pos = self.pos
        
        if self.current_char() == '\\':
            self.advance()  # Skip backslash
            if self.current_char() is not None:
                self.advance()  # Skip escaped character
        elif self.current_char() is not None:
            self.advance()  # Regular character
        
        value = self.source[start_pos:self.pos]
        
        if self.current_char() == "'":
            self.advance()  # Skip closing quote
        else:
            raise CompilerError("Unterminated character literal", self.line, self.column)
        
        return value
    
    def read_string(self) -> str:
        self.advance()  # Skip opening quote
        start_pos = self.pos
        
        while self.current_char() is not None and self.current_char() != '"':
            if self.current_char() == '\\':
                self.advance()  # Skip backslash
                if self.current_char() is not None:
                    self.advance()  # Skip escaped character
            else:
                self.advance()
        
        value = self.source[start_pos:self.pos]
        
        if self.current_char() == '"':
            self.advance()  # Skip closing quote
        else:
            raise CompilerError("Unterminated string literal", self.line, self.column)
        
        return value
    
    def read_comment(self) -> str:
        start_pos = self.pos
        while self.current_char() is not None and self.current_char() != '\n':
            self.advance()
        return self.source[start_pos:self.pos]
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            char = self.current_char()
            line, column = self.line, self.column
            
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, line, column))
                self.advance()
            
            elif char == ';':
                comment = self.read_comment()
                self.tokens.append(Token(TokenType.COMMENT, comment, line, column))
            
            elif char == ':':
                self.advance()
                if (self.current_char() and 
                    (self.current_char().isalpha() or self.current_char() == '_')): # type: ignore
                    label = self.read_identifier()
                    self.tokens.append(Token(TokenType.LABEL, label, line, column))
                else:
                    raise CompilerError("Invalid label format", line, column)
            
            elif char == '$':
                hex_num = self.read_hex_number()
                self.tokens.append(Token(TokenType.HEX_NUMBER, hex_num, line, column))
            
            elif char == "'":
                char_literal = self.read_character()
                self.tokens.append(Token(TokenType.CHARACTER, char_literal, line, column))
            
            elif char == '"':
                string_literal = self.read_string()
                self.tokens.append(Token(TokenType.STRING, string_literal, line, column))
            
            elif (char.isdigit() or  # type: ignore
                  (char == '-' and self.peek_char() is not None and self.peek_char().isdigit())): # type: ignore
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number, line, column))
            
            elif char.isalpha() or char == '_': # type: ignore
                identifier = self.read_identifier()
                
                # Check for constant/variable definitions
                if identifier.upper() in ['CONST', 'CONSTANT']:
                    self.tokens.append(Token(TokenType.CONSTANT_DEF, identifier, line, column))
                elif identifier.upper() in ['VAR', 'VARIABLE']:
                    self.tokens.append(Token(TokenType.VARIABLE_DEF, identifier, line, column))
                elif identifier.upper() in NameToOpcode:
                    self.tokens.append(Token(TokenType.INSTRUCTION, identifier.upper(), line, column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, line, column))
            
            else:
                raise CompilerError(f"Unexpected character: {char}", line, column)
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


class Parser:
    """Parses tokens into an intermediate representation"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.symbols: Dict[str, Symbol] = {}
        self.instructions = []
        self.labels: Dict[str, int] = {}
    
    def current_token(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.pos]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def expect_token(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            raise CompilerError(f"Expected {token_type.value}, got {token.type.value}", 
                              token.line, token.column)
        self.advance()
        return token
    
    def skip_newlines(self):
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def evaluate_expression(self, value: str) -> int:
        """Evaluate simple arithmetic expressions and resolve symbols"""
        # Handle symbol substitution
        if value in self.symbols:
            symbol = self.symbols[value]
            if isinstance(symbol.value, int):
                return symbol.value
            else:
                return self.evaluate_expression(str(symbol.value))
        
        # Handle character literals
        if len(value) >= 2 and value.startswith("'") and value.endswith("'"):
            char_value = value[1:-1]
            return self.char_to_ascii(char_value)
        
        # Handle hex numbers
        if value.startswith('$'):
            return int(value[1:], 16)
        
        # Handle decimal numbers
        if value.lstrip('-').isdigit():
            return int(value)
        
        # Simple arithmetic expression evaluation
        try:
            # Replace symbols in expression
            expr = value
            for symbol_name, symbol in self.symbols.items():
                if isinstance(symbol.value, int):
                    expr = expr.replace(symbol_name, str(symbol.value))
            
            # Evaluate simple expressions (only +, -, *, /)
            if any(op in expr for op in ['+', '-', '*', '/']):
                return eval(expr)  # Simple eval for basic arithmetic
            
            return int(expr)
        except:
            raise CompilerError(f"Cannot evaluate expression: {value}")
    
    def char_to_ascii(self, char_str: str) -> int:
        """Convert character literal to ASCII value"""
        if len(char_str) == 1:
            return ord(char_str)
        elif len(char_str) == 2 and char_str[0] == '\\':
            escape_chars = {
                'n': 10,   # newline
                't': 9,    # tab
                'r': 13,   # carriage return
                '\\': 92,  # backslash
                "'": 39,   # single quote
                '"': 34,   # double quote
                '0': 0,    # null
            }
            if char_str[1] in escape_chars:
                return escape_chars[char_str[1]]
            else:
                return ord(char_str[1])  # Treat as literal character
        else:
            raise CompilerError(f"Invalid character literal: {char_str}")
    
    def parse_value(self) -> Union[int, str]:
        """Parse a value (number, hex, character, or symbol)"""
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return int(token.value)
        
        elif token.type == TokenType.HEX_NUMBER:
            self.advance()
            return int(token.value[1:], 16)  # Skip '$' prefix
        
        elif token.type == TokenType.CHARACTER:
            self.advance()
            return self.char_to_ascii(token.value)
        
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            if token.value in self.symbols:
                symbol = self.symbols[token.value]
                if isinstance(symbol.value, int):
                    return symbol.value
                else:
                    return self.evaluate_expression(str(symbol.value))
            else:
                # Return as string for later resolution (could be a label)
                return token.value
        
        else:
            raise CompilerError(f"Expected value, got {token.type.value}", token.line, token.column)
    
    def parse_constant_definition(self):
        """Parse constant definition: CONST NAME value"""
        const_token = self.current_token()
        self.advance()  # Skip CONST
        
        name_token = self.expect_token(TokenType.IDENTIFIER)
        value_str = ""
        
        # Collect all tokens until newline to form the value expression
        while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.COMMENT]):
            value_str += self.current_token().value
            self.advance()
        
        if not value_str.strip():
            raise CompilerError("Constant definition missing value", const_token.line, const_token.column)
        
        try:
            value = self.evaluate_expression(value_str.strip())
            self.symbols[name_token.value] = Symbol(name_token.value, value, 'constant', name_token.line)
        except:
            raise CompilerError(f"Invalid constant value: {value_str}", const_token.line, const_token.column)
    
    def parse_variable_definition(self):
        """Parse variable definition: VAR NAME value"""
        var_token = self.current_token()
        self.advance()  # Skip VAR
        
        name_token = self.expect_token(TokenType.IDENTIFIER)
        value_str = ""
        
        # Collect all tokens until newline to form the value expression
        while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.COMMENT]):
            value_str += self.current_token().value
            self.advance()
        
        if not value_str.strip():
            raise CompilerError("Variable definition missing value", var_token.line, var_token.column)
        
        try:
            value = self.evaluate_expression(value_str.strip())
            self.symbols[name_token.value] = Symbol(name_token.value, value, 'variable', name_token.line)
        except:
            raise CompilerError(f"Invalid variable value: {value_str}", var_token.line, var_token.column)
    
    def validate_instruction_parameters(self, instruction_name: str, params: List[Union[int, str]], line: int):
        """Validate instruction parameters against instruction requirements"""
        if instruction_name not in NameToOpcode:
            raise CompilerError(f"Unknown instruction: {instruction_name}", line)
        
        opcode = NameToOpcode[instruction_name]
        instruction_class = InstructionSet[opcode]
        expected_length = instruction_class.length
        
        # For instructions that take 2-byte addresses, expect 1 logical parameter
        # For instructions that take individual bytes, expect exact byte count
        if expected_length == 2:
            # 2-byte instructions expect exactly 1 address parameter
            if len(params) != 1:
                raise CompilerError(
                    f"Instruction {instruction_name} expects 1 address parameter, got {len(params)}", 
                    line
                )
            # Validate the address parameter range
            param = params[0]
            if isinstance(param, int):
                if not (0 <= param <= 65535):
                    raise CompilerError(
                        f"Address parameter for {instruction_name} must be 0-65535, got {param}", 
                        line
                    )
        elif expected_length == 1:
            # 1-byte instructions expect exactly 1 byte parameter
            if len(params) != 1:
                raise CompilerError(
                    f"Instruction {instruction_name} expects 1 parameter, got {len(params)}", 
                    line
                )
            # Validate the byte parameter range
            param = params[0]
            if isinstance(param, int):
                if not (0 <= param <= 255):
                    raise CompilerError(
                        f"Parameter for {instruction_name} must be 0-255, got {param}", 
                        line
                    )
        elif expected_length == 0:
            # 0-byte instructions expect no parameters
            if len(params) != 0:
                raise CompilerError(
                    f"Instruction {instruction_name} expects no parameters, got {len(params)}", 
                    line
                )
    
    def parse_instruction(self):
        """Parse an instruction with its parameters"""
        instr_token = self.current_token()
        instruction_name = instr_token.value
        self.advance()
        
        parameters = []
        
        # Collect parameters until newline/comment/EOF
        while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.COMMENT]):
            param_value = self.parse_value()
            parameters.append(param_value)
        
        # Validate instruction and parameters
        self.validate_instruction_parameters(instruction_name, parameters, instr_token.line)
        
        self.instructions.append({
            'type': 'instruction',
            'name': instruction_name,
            'parameters': parameters,
            'line': instr_token.line
        })
    
    def parse_label(self):
        """Parse a label definition"""
        label_token = self.current_token()
        label_name = label_token.value
        self.advance()
        
        # Labels point to the next instruction position
        self.labels[label_name] = len(self.instructions)
        self.symbols[label_name] = Symbol(label_name, len(self.instructions), 'label', label_token.line)
    
    def parse(self):
        """Main parsing method"""
        while self.current_token().type != TokenType.EOF:
            self.skip_newlines()
            
            if self.current_token().type == TokenType.EOF:
                break
            elif self.current_token().type == TokenType.COMMENT:
                self.advance()
            elif self.current_token().type == TokenType.LABEL:
                self.parse_label()
            elif self.current_token().type == TokenType.CONSTANT_DEF:
                self.parse_constant_definition()
            elif self.current_token().type == TokenType.VARIABLE_DEF:
                self.parse_variable_definition()
            elif self.current_token().type == TokenType.INSTRUCTION:
                self.parse_instruction()
            else:
                token = self.current_token()
                raise CompilerError(f"Unexpected token: {token.value}", token.line, token.column)
            
            self.skip_newlines()


class CodeGenerator:
    """Generates final machine code from parsed instructions"""
    
    def __init__(self, instructions: List[Dict], symbols: Dict[str, Symbol]):
        self.instructions = instructions
        self.symbols = symbols
        self.machine_code = []
    
    def resolve_label_addresses(self):
        """Resolve label references to actual memory addresses"""
        # Update all instructions with resolved label addresses
        for instruction in self.instructions:
            if instruction['type'] == 'instruction':
                new_params = []
                for param in instruction['parameters']:
                    if isinstance(param, str) and param in self.symbols:
                        symbol = self.symbols[param]
                        if symbol.type == 'label':
                            new_params.append(symbol.value)
                        else:
                            new_params.append(param)
                    else:
                        new_params.append(param)
                instruction['parameters'] = new_params
    
    def generate(self) -> Data:
        """Generate final machine code"""
        self.resolve_label_addresses()
        
        for instruction in self.instructions:
            if instruction['type'] == 'instruction':
                instruction_name = instruction['name']
                opcode = NameToOpcode[instruction_name]
                instruction_class = InstructionSet[opcode]
                
                self.machine_code.append(opcode)
                
                # Convert parameters to bytes
                for param in instruction['parameters']:
                    if isinstance(param, int):
                        # For 2-byte address instructions, split into high/low bytes
                        if instruction_class.length == 2 and len(instruction['parameters']) == 1:
                            # Single address parameter becomes two bytes
                            high_byte = (param >> 8) & 0xFF
                            low_byte = param & 0xFF
                            self.machine_code.extend([high_byte, low_byte])
                        else:
                            # Single byte parameter
                            self.machine_code.append(param & 0xFF)
                    else:
                        # This shouldn't happen after symbol resolution
                        raise CompilerError(f"Unresolved symbol: {param}")
        
        return self.machine_code


class AdvancedCompiler:
    """Main compiler class combining all phases"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def compile_file(self, filename: str) -> Data:
        """Compile assembly file to machine code"""
        try:
            with open(filename, 'r') as f:
                source = f.read()
            return self.compile_source(source, filename)
        except FileNotFoundError:
            raise CompilerError(f"File not found: {filename}")
        except IOError as e:
            raise CompilerError(f"Error reading file {filename}: {e}")
    
    def compile_source(self, source: str, filename: str = "<source>") -> Data:
        """Compile assembly source code to machine code"""
        try:
            if self.verbose:
                print(f"Compiling {filename}...")
            
            # Lexical analysis
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            if self.verbose:
                print(f"Tokenized {len(tokens)} tokens")
            
            # Parsing
            parser = Parser(tokens)
            parser.parse()
            
            if self.verbose:
                print(f"Parsed {len(parser.instructions)} instructions")
                print(f"Found {len(parser.symbols)} symbols")
            
            # Code generation
            generator = CodeGenerator(parser.instructions, parser.symbols)
            machine_code = generator.generate()
            
            if self.verbose:
                print(f"Generated {len(machine_code)} bytes of machine code")
            
            return machine_code
            
        except CompilerError:
            raise
        except Exception as e:
            raise CompilerError(f"Internal compiler error: {e}")


# Legacy functions for backward compatibility
def read_file(filename: str) -> str:
    """Read file contents - legacy function"""
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    except IOError as e:
        raise IOError(f"Error reading file {filename}: {e}")
    except UnicodeDecodeError:
        raise ValueError(f"File {filename} is not a valid text file or contains invalid characters.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while reading {filename}: {e}")


def strip_comments_and_whitespace(code: str) -> list[str]:
    """Strip comments - legacy function"""
    lines = code.splitlines()
    stripped_lines = []
    for line in lines:
        line = line.split(";", 1)[0].strip()
        if line:
            stripped_lines.append(line)
    return stripped_lines


def addr_to_ints(addr: str) -> tuple[int, int]:
    """Convert address to high/low bytes - legacy function"""
    if not addr.startswith("$"):
        raise ValueError(f"Invalid address format: {addr}")
    try:
        int_addr = int(addr[1:], 16)
    except ValueError:
        raise ValueError(f"Invalid address: {addr}")
    if int_addr < 0 or int_addr > 0xFFFF:
        raise ValueError(f"Address out of range: {addr}")
    return (int_addr >> 8) & 0xFF, int_addr & 0X00FF


def int_to_addr(value: int) -> tuple[int, int]:
    """Convert integer to address bytes - legacy function"""
    return (value >> 8) & 0xFF, value & 0x00FF


def two_pass(code: str, verbose=False) -> Data:
    """Legacy two-pass compiler function"""
    compiler = AdvancedCompiler(verbose=verbose)
    return compiler.compile_source(code)


def compile(filename: str, verbose=False) -> Data:
    """Main compile function for backward compatibility"""
    compiler = AdvancedCompiler(verbose=verbose)
    return compiler.compile_file(filename)


# Additional convenience functions
def compile_file(filename: str, verbose: bool = False) -> Data:
    """Compile assembly file to machine code"""
    compiler = AdvancedCompiler(verbose=verbose)
    return compiler.compile_file(filename)


def compile_source(source: str, verbose: bool = False) -> Data:
    """Compile assembly source to machine code"""
    compiler = AdvancedCompiler(verbose=verbose)
    return compiler.compile_source(source)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced CPU Assembly Compiler")
    parser.add_argument("input_file", help="Assembly source file")
    parser.add_argument("-o", "--output", help="Output file for machine code")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--hex", action="store_true", help="Output in hexadecimal format")
    
    args = parser.parse_args()
    
    try:
        compiler = AdvancedCompiler(verbose=args.verbose)
        machine_code = compiler.compile_file(args.input_file)
        
        if args.output:
            with open(args.output, 'w') as f:
                if args.hex:
                    hex_output = ' '.join(f"{byte:02X}" for byte in machine_code)
                    f.write(hex_output)
                else:
                    f.write(str(machine_code))
            print(f"Compiled to {args.output}")
        else:
            if args.hex:
                hex_output = ' '.join(f"{byte:02X}" for byte in machine_code)
                print(hex_output)
            else:
                print(machine_code)
                
    except CompilerError as e:
        print(f"Compilation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)