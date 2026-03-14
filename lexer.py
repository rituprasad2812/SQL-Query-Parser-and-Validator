class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self, query):
        self.query = query
        self.pos = 0
        self.current_char = self.query[0] if query else None
    
    def advance(self):
        """Move to next character"""
        self.pos += 1
        if self.pos < len(self.query):
            self.current_char = self.query[self.pos]
        else:
            self.current_char = None
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines"""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def read_word(self):
        """Read a word (keyword or identifier)"""
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result
    
    def read_number(self):
        """Read a number"""
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return result
    
    def read_string(self):
        """Read a string literal 'text' """
        quote = self.current_char  # ' or "
        self.advance()  # skip opening quote
        result = ''
        while self.current_char and self.current_char != quote:
            result += self.current_char
            self.advance()
        self.advance()  # skip closing quote
        return result
    
    def tokenize(self):
        """Main function: convert query to list of tokens"""
        tokens = []
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'INSERT', 'UPDATE', 'DELETE', 'INTO', 'VALUES', 'SET']
        
        while self.current_char:
            # Skip spaces
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Read words (keywords or identifiers)
            if self.current_char.isalpha():
                word = self.read_word()
                if word.upper() in keywords:
                    tokens.append(Token('KEYWORD', word.upper()))
                else:
                    tokens.append(Token('IDENTIFIER', word))
                continue
            
            # Read numbers
            if self.current_char.isdigit():
                num = self.read_number()
                tokens.append(Token('NUMBER', num))
                continue
            
            # Read strings
            if self.current_char in ["'", '"']:
                string = self.read_string()
                tokens.append(Token('STRING', string))
                continue
            
            # Operators and symbols
            if self.current_char == '=':
                tokens.append(Token('OPERATOR', '='))
                self.advance()
            elif self.current_char == '>':
                tokens.append(Token('OPERATOR', '>'))
                self.advance()
            elif self.current_char == '<':
                tokens.append(Token('OPERATOR', '<'))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token('COMMA', ','))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token('STAR', '*'))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token('LPAREN', '('))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token('RPAREN', ')'))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token('SEMICOLON', ';'))
                self.advance()
            else:
                # Unknown character - skip it
                self.advance()
        
        return tokens