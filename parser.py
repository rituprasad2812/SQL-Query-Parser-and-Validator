class ASTNode:
    """Base class for tree nodes"""
    pass


class SelectStatement(ASTNode):
    def __init__(self, columns, table, where=None):
        self.columns = columns  # List of column names or ['*']
        self.table = table      # Table name
        self.where = where      # Condition (optional)
    
    def __repr__(self):
        return f"SelectStatement(columns={self.columns}, table={self.table}, where={self.where})"


class Condition(ASTNode):
    def __init__(self, left, operator, right, logical_op=None, next_condition=None):
        self.left = left              # Column name
        self.operator = operator      # =, >, <, etc.
        self.right = right            # Value
        self.logical_op = logical_op  # AND, OR (optional)
        self.next_condition = next_condition  # For chaining conditions
    
    def __repr__(self):
        result = f"{self.left} {self.operator} {self.right}"
        if self.next_condition:
            result += f" {self.logical_op} {self.next_condition}"
        return result


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        """Move to next token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def expect(self, token_type):
        """Check if current token matches expected type"""
        if not self.current_token or self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token}")
        value = self.current_token.value
        self.advance()
        return value
    
    def parse(self):
        """Main parsing function"""
        if self.current_token.type == 'KEYWORD' and self.current_token.value == 'SELECT':
            return self.parse_select()
        else:
            raise SyntaxError("Query must start with SELECT")
    
    def parse_select(self):
        """Parse SELECT statement"""
        self.expect('KEYWORD')  # SELECT
        
        # Parse columns
        columns = self.parse_columns()
        
        # Expect FROM
        self.expect('KEYWORD')  # FROM
        
        # Parse table name
        table = self.expect('IDENTIFIER')
        
        # Check for WHERE clause (optional)
        where = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'WHERE':
            self.advance()  # Skip WHERE
            where = self.parse_condition()
        
        return SelectStatement(columns, table, where)
    
    def parse_columns(self):
        """Parse column list: name, age OR *"""
        columns = []
        
        # Check for SELECT *
        if self.current_token.type == 'STAR':
            self.advance()
            return ['*']
        
        # Parse column names
        while True:
            col = self.expect('IDENTIFIER')
            columns.append(col)
            
            # Check for comma (more columns)
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()  # Skip comma
            else:
                break
        
        return columns
    
    def parse_condition(self):
        """Parse WHERE condition: age > 18 AND department = 'CS'"""
        left = self.expect('IDENTIFIER')  # Column name
        operator = self.expect('OPERATOR')  # =, >, <, etc.
        
        # Get value (number or string)
        if self.current_token.type == 'NUMBER':
            right = self.current_token.value
            self.advance()
        elif self.current_token.type == 'STRING':
            right = self.current_token.value
            self.advance()
        else:
            raise SyntaxError(f"Expected value after operator, got {self.current_token}")
        
        condition = Condition(left, operator, right)
        
        # Check for AND/OR
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value in ['AND', 'OR']:
            logical_op = self.current_token.value
            self.advance()
            next_condition = self.parse_condition()  # Recursive call
            condition.logical_op = logical_op
            condition.next_condition = next_condition
        
        return condition