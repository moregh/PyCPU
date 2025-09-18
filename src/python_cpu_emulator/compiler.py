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
    MACRO_DEF = "MACRO_DEF"
    MACRO_END = "MACRO_END"
    MACRO_CALL = "MACRO_CALL"
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


@dataclass
class Macro:
    name: str
    parameters: List[str]
    body: List[str]  # Lines of macro body
    line: int


class CompilerError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")


class Lexer:
    """Tokenizes assembly source code with macro support"""
    
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
                    (self.current_char().isalpha() or self.current_char() == '_')):  # type: ignore
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
                
                # Check for special keywords
                if identifier.upper() in ['CONST', 'CONSTANT']:
                    self.tokens.append(Token(TokenType.CONSTANT_DEF, identifier, line, column))
                elif identifier.upper() in ['VAR', 'VARIABLE']:
                    self.tokens.append(Token(TokenType.VARIABLE_DEF, identifier, line, column))
                elif identifier.upper() == 'MACRO':
                    self.tokens.append(Token(TokenType.MACRO_DEF, identifier, line, column))
                elif identifier.upper() == 'ENDMACRO':
                    self.tokens.append(Token(TokenType.MACRO_END, identifier, line, column))
                elif identifier.upper() in NameToOpcode:
                    self.tokens.append(Token(TokenType.INSTRUCTION, identifier.upper(), line, column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, line, column))
            
            # Handle multi-character operators
            elif char == '>' and self.peek_char() == '>':
                self.advance()  # consume first >
                self.advance()  # consume second >
                self.tokens.append(Token(TokenType.IDENTIFIER, '>>', line, column))
            
            elif char == '<' and self.peek_char() == '<':
                self.advance()  # consume first 
                self.advance()  # consume second 
                self.tokens.append(Token(TokenType.IDENTIFIER, '<<', line, column))
            
            # Handle single-character operators and symbols
            elif char in '+-*/()&|^~%':  # type: ignore
                self.tokens.append(Token(TokenType.IDENTIFIER, char, line, column))  # type: ignore
                self.advance()
            
            else:
                raise CompilerError(f"Unexpected character: {char}", line, column)
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


class Parser:
    """Parses tokens with macro support"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.symbols: Dict[str, Symbol] = {}
        self.macros: Dict[str, Macro] = {}
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
        """Evaluate arithmetic and bitwise expressions and resolve symbols"""
        # Handle symbol substitution first
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
        
        # Handle simple decimal numbers (including negative)
        if value.lstrip('-').isdigit():
            return int(value)
        
        try:
            # Create a working copy for symbol substitution
            expr = value.strip()
            
            # Replace all known symbols with their numeric values
            # Sort by length (descending) to handle longer symbol names first
            sorted_symbols = sorted(self.symbols.items(), key=lambda x: len(x[0]), reverse=True)
            for symbol_name, symbol in sorted_symbols:
                if isinstance(symbol.value, int) and symbol_name in expr:
                    # Use word boundaries to avoid partial replacements
                    import re
                    pattern = r'\b' + re.escape(symbol_name) + r'\b'
                    expr = re.sub(pattern, str(symbol.value), expr)
            
            # Handle hex numbers in expressions
            import re
            hex_pattern = r'\$([0-9A-Fa-f]+)'
            expr = re.sub(hex_pattern, lambda m: str(int(m.group(1), 16)), expr)
            
            # Handle character literals in expressions
            char_pattern = r"'(.?)'"
            def replace_char(match):
                char_str = match.group(1)
                return str(self.char_to_ascii(char_str))
            expr = re.sub(char_pattern, replace_char, expr)
            
            # Clean up whitespace around operators
            expr = re.sub(r'\s+', ' ', expr)
            
            # Now evaluate the expression safely
            # Check if expression contains any operators we support
            supported_ops = ['+', '-', '*', '//', '/', '%', '**', 
                            '>>', '<<', '&', '|', '^']
            
            has_operators = any(op in expr for op in supported_ops)
            
            if has_operators:
                # Create a restricted namespace for eval
                allowed_names = {
                    "__builtins__": {},
                }
                
                # Validate that expression only contains safe characters and operators
                import re
                # Allow numbers, operators, parentheses, and whitespace
                safe_pattern = r'^[0-9+\-*/()&|^<>\s%]+$'
                if not re.match(safe_pattern, expr):
                    raise ValueError(f"Expression contains unsafe characters: {expr}")
                
                # Evaluate the expression
                result = eval(expr, allowed_names, {})
                
                # Ensure result is an integer
                if isinstance(result, (int, float)):
                    return int(result)
                else:
                    raise ValueError("Expression did not evaluate to a number")
            else:
                # No operators, should be a simple number
                return int(expr)
                
        except Exception as e:
            raise CompilerError(f"Cannot evaluate expression: {value} (Error: {str(e)})")
        
    def char_to_ascii(self, char_str: str) -> int:
        """Convert character literal to ASCII value"""
        if len(char_str) == 1:
            return ord(char_str)
        elif len(char_str) == 2 and char_str[0] == '\\':
            escape_chars = {
                'n': 10, 't': 9, 'r': 13, '\\': 92, "'": 39, '"': 34, '0': 0,
            }
            if char_str[1] in escape_chars:
                return escape_chars[char_str[1]]
            else:
                return ord(char_str[1])
        else:
            raise CompilerError(f"Invalid character literal: {char_str}")
    
    def parse_value(self) -> Union[int, str]:
        """Parse a value or expression (number, hex, character, symbol, or complex expression)"""
        # Collect tokens that form a complete expression
        expression_parts = []
        
        while (self.current_token().type in [TokenType.NUMBER, TokenType.HEX_NUMBER, 
                                            TokenType.CHARACTER, TokenType.IDENTIFIER] and
            self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.COMMENT]):
            
            token = self.current_token()
            expression_parts.append(token.value)
            self.advance()
            
            # Stop if we hit a newline, comment, or EOF
            if (self.current_token().type in [TokenType.NEWLINE, TokenType.EOF, TokenType.COMMENT]):
                break
        
        if not expression_parts:
            raise CompilerError("Expected value or expression", 
                            self.current_token().line, self.current_token().column)
        
        # Join the parts and evaluate as expression
        expression_str = ' '.join(expression_parts)
        
        # Handle simple single values
        if len(expression_parts) == 1:
            single_value = expression_parts[0]
            
            if single_value.lstrip('-').isdigit():
                return int(single_value)
            elif single_value.startswith('$'):
                return int(single_value[1:], 16)
            elif len(single_value) >= 2 and single_value.startswith("'") and single_value.endswith("'"):
                return self.char_to_ascii(single_value[1:-1])
            elif single_value in self.symbols:
                symbol = self.symbols[single_value]
                if isinstance(symbol.value, int):
                    return symbol.value
                else:
                    return self.evaluate_expression(str(symbol.value))
            else:
                return single_value
    
        # Handle complex expressions
        try:
            return self.evaluate_expression(expression_str)
        except:
            raise CompilerError(f"Cannot evaluate expression: {expression_str}")
    
    def parse_constant_definition(self):
        """Parse constant definition: CONST NAME value"""
        const_token = self.current_token()
        self.advance()
        
        name_token = self.expect_token(TokenType.IDENTIFIER)
        value_str = ""
        
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
    
    def parse_macro_definition(self):
        """Parse macro definition: MACRO name param1 param2 ... body ... ENDMACRO"""
        macro_token = self.current_token()
        self.advance()
        
        # Get macro name
        name_token = self.expect_token(TokenType.IDENTIFIER)
        macro_name = name_token.value
        
        # Parse parameters
        parameters = []
        while (self.current_token().type == TokenType.IDENTIFIER):
            param_token = self.current_token()
            parameters.append(param_token.value)
            self.advance()
        
        # Skip to newline after macro header
        self.skip_newlines()
        
        # Collect macro body until ENDMACRO
        body_lines = []
        while (self.current_token().type != TokenType.MACRO_END and 
               self.current_token().type != TokenType.EOF):
            
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                continue
            
            # Collect tokens until newline to form a line
            line_tokens = []
            while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.MACRO_END]):
                line_tokens.append(self.current_token().value)
                self.advance()
            
            if line_tokens:
                body_lines.append(' '.join(line_tokens))
        
        # Expect ENDMACRO
        if self.current_token().type != TokenType.MACRO_END:
            raise CompilerError("Expected ENDMACRO to close macro definition", 
                              macro_token.line, macro_token.column)
        self.advance()
        
        # Store macro
        self.macros[macro_name] = Macro(macro_name, parameters, body_lines, macro_token.line)
    
    def expand_macro(self, macro_name: str, args: List[str]) -> List[str]:
        """Expand a macro with given arguments"""
        if macro_name not in self.macros:
            raise CompilerError(f"Undefined macro: {macro_name}")
        
        macro = self.macros[macro_name]
        
        if len(args) != len(macro.parameters):
            raise CompilerError(f"Macro {macro_name} expects {len(macro.parameters)} arguments, got {len(args)}")
        
        # Create parameter substitution map
        param_map = dict(zip(macro.parameters, args))
        
        # Expand macro body
        expanded_lines = []
        for line in macro.body:
            expanded_line = line
            # Replace parameters with arguments
            for param, arg in param_map.items():
                expanded_line = expanded_line.replace(param, arg)
            expanded_lines.append(expanded_line)
        
        return expanded_lines
    
    def parse_macro_call(self, macro_name: str):
        """Parse and expand a macro call"""
        # Collect arguments
        args = []
        while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.COMMENT]):
            args.append(self.current_token().value)
            self.advance()
        
        # Expand macro
        expanded_lines = self.expand_macro(macro_name, args)
        
        # Parse expanded lines as if they were inline code
        for line in expanded_lines:
            if line.strip():
                # Re-tokenize and parse the expanded line
                sub_lexer = Lexer(line + '\n')
                sub_tokens = sub_lexer.tokenize()
                
                # Remove EOF token
                if sub_tokens and sub_tokens[-1].type == TokenType.EOF:
                    sub_tokens.pop()
                
                # Parse the tokens
                old_pos = self.pos
                old_tokens = self.tokens
                
                self.tokens = sub_tokens
                self.pos = 0
                
                # Parse this line
                while self.pos < len(self.tokens):
                    if self.current_token().type == TokenType.NEWLINE:
                        self.advance()
                        continue
                    elif self.current_token().type == TokenType.COMMENT:
                        self.advance()
                        continue
                    elif self.current_token().type == TokenType.LABEL:
                        self.parse_label()
                    elif self.current_token().type == TokenType.INSTRUCTION:
                        self.parse_instruction()
                    elif self.current_token().type == TokenType.IDENTIFIER:
                        # Could be a macro call or unknown instruction
                        identifier = self.current_token().value
                        if identifier in self.macros:
                            self.advance()
                            self.parse_macro_call(identifier)
                        else:
                            raise CompilerError(f"Unknown identifier: {identifier}", 
                                              self.current_token().line, self.current_token().column)
                    else:
                        self.advance()
                
                # Restore original token stream
                self.tokens = old_tokens
                self.pos = old_pos
    
    def validate_instruction_parameters(self, instruction_name: str, params: List[Union[int, str]], line: int):
        """Validate instruction parameters"""
        if instruction_name not in NameToOpcode:
            raise CompilerError(f"Unknown instruction: {instruction_name}", line)
        
        opcode = NameToOpcode[instruction_name]
        instruction_class = InstructionSet[opcode]
        expected_length = instruction_class.length
        
        if expected_length == 2:
            if len(params) != 1:
                raise CompilerError(f"Instruction {instruction_name} expects 1 address parameter, got {len(params)}", line)
            param = params[0]
            if isinstance(param, int):
                if not (0 <= param <= 65535):
                    raise CompilerError(f"Address parameter for {instruction_name} must be 0-65535, got {param}", line)
        elif expected_length == 1:
            if len(params) != 1:
                raise CompilerError(f"Instruction {instruction_name} expects 1 parameter, got {len(params)}", line)
            param = params[0]
            if isinstance(param, int):
                if not (0 <= param <= 255):
                    raise CompilerError(f"Parameter for {instruction_name} must be 0-255, got {param}", line)
        elif expected_length == 0:
            if len(params) != 0:
                raise CompilerError(f"Instruction {instruction_name} expects no parameters, got {len(params)}", line)
    
    def parse_instruction(self):
        """Parse an instruction with its parameters"""
        instr_token = self.current_token()
        instruction_name = instr_token.value
        self.advance()
        
        parameters = []
        
        while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.COMMENT]):
            param_value = self.parse_value()
            parameters.append(param_value)
        
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
        
        self.labels[label_name] = len(self.instructions)
        self.symbols[label_name] = Symbol(label_name, len(self.instructions), 'label', label_token.line)
    
    def parse(self):
        """Main parsing method with macro support"""
        # First pass: collect macro definitions
        while self.current_token().type != TokenType.EOF:
            self.skip_newlines()
            
            if self.current_token().type == TokenType.EOF:
                break
            elif self.current_token().type == TokenType.COMMENT:
                self.advance()
            elif self.current_token().type == TokenType.MACRO_DEF:
                self.parse_macro_definition()
            elif self.current_token().type == TokenType.CONSTANT_DEF:
                self.parse_constant_definition()
            else:
                # Skip non-macro definitions for now
                self.advance()
        
        # Second pass: parse everything else including macro calls
        self.pos = 0  # Reset to beginning
        
        while self.current_token().type != TokenType.EOF:
            self.skip_newlines()
            
            if self.current_token().type == TokenType.EOF:
                break
            elif self.current_token().type == TokenType.COMMENT:
                self.advance()
            elif self.current_token().type == TokenType.LABEL:
                self.parse_label()
            elif self.current_token().type == TokenType.CONSTANT_DEF:
                # Already parsed in first pass
                while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF]):
                    self.advance()
            elif self.current_token().type == TokenType.MACRO_DEF:
                # Skip macro definitions in second pass
                while (self.current_token().type != TokenType.MACRO_END and 
                       self.current_token().type != TokenType.EOF):
                    self.advance()
                if self.current_token().type == TokenType.MACRO_END:
                    self.advance()
            elif self.current_token().type == TokenType.VARIABLE_DEF:
                # Skip for now (not implemented)
                while (self.current_token().type not in [TokenType.NEWLINE, TokenType.EOF]):
                    self.advance()
            elif self.current_token().type == TokenType.INSTRUCTION:
                self.parse_instruction()
            elif self.current_token().type == TokenType.IDENTIFIER:
                # Could be a macro call
                identifier = self.current_token().value
                if identifier in self.macros:
                    self.advance()
                    self.parse_macro_call(identifier)
                else:
                    raise CompilerError(f"Unknown identifier: {identifier}", 
                                      self.current_token().line, self.current_token().column)
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
                
                for param in instruction['parameters']:
                    if isinstance(param, int):
                        if instruction_class.length == 2 and len(instruction['parameters']) == 1:
                            # Single address parameter becomes two bytes
                            high_byte = (param >> 8) & 0xFF
                            low_byte = param & 0xFF
                            self.machine_code.extend([high_byte, low_byte])
                        else:
                            # Single byte parameter
                            self.machine_code.append(param & 0xFF)
                    else:
                        raise CompilerError(f"Unresolved symbol: {param}")
        
        return self.machine_code


class AdvancedCompiler:
    """Main compiler class with macro support"""
    
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
            
            # Parsing with macro expansion
            parser = Parser(tokens)
            parser.parse()
            
            if self.verbose:
                print(f"Parsed {len(parser.instructions)} instructions")
                print(f"Found {len(parser.symbols)} symbols")
                print(f"Defined {len(parser.macros)} macros")
            
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


# Backward compatibility functions
def compile(filename: str, verbose=False) -> Data:
    """Main compile function for backward compatibility"""
    compiler = AdvancedCompiler(verbose=verbose)
    return compiler.compile_file(filename)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CPU Assembly Compiler with Macro Support")
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