class ASTNode:
    """Base class for tree nodes"""
    pass


class SelectStatement(ASTNode):
    def __init__(self, columns, table, where=None):
        self.columns = columns
        self.table = table
        self.where = where
    
    def __repr__(self):
        return f"SelectStatement(columns={self.columns}, table={self.table}, where={self.where})"


class Condition(ASTNode):
    def __init__(self, left, operator, right, logical_op=None, next_condition=None):
        self.left = left
        self.operator = operator
        self.right = right
        self.logical_op = logical_op
        self.next_condition = next_condition
    
    def __repr__(self):
        result = f"{self.left} {self.operator} {self.right}"
        if self.next_condition:
            result += f" {self.logical_op} {self.next_condition}"
        return result


class InsertStatement(ASTNode):
    def __init__(self, table, columns, values):
        self.table = table
        self.columns = columns
        self.values = values
    
    def __repr__(self):
        return f"InsertStatement(table={self.table}, columns={self.columns}, values={self.values})"


class UpdateStatement(ASTNode):
    def __init__(self, table, assignments, where=None):
        self.table = table
        self.assignments = assignments
        self.where = where
    
    def __repr__(self):
        return f"UpdateStatement(table={self.table}, assignments={self.assignments}, where={self.where})"


class DeleteStatement(ASTNode):
    def __init__(self, table, where=None):
        self.table = table
        self.where = where
    
    def __repr__(self):
        return f"DeleteStatement(table={self.table}, where={self.where})"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def expect(self, token_type):
        if not self.current_token or self.current_token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token}")
        value = self.current_token.value
        self.advance()
        return value
    
    def parse(self):
        if self.current_token.type == 'KEYWORD':
            if self.current_token.value == 'SELECT':
                return self.parse_select()
            elif self.current_token.value == 'INSERT':
                return self.parse_insert()
            elif self.current_token.value == 'UPDATE':
                return self.parse_update()
            elif self.current_token.value == 'DELETE':
                return self.parse_delete()
        raise SyntaxError(f"Unexpected keyword: {self.current_token.value}")

    def parse_select(self):
        self.expect('KEYWORD')
        columns = self.parse_columns()
        self.expect('KEYWORD')
        table = self.expect('IDENTIFIER')
        where = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'WHERE':
            self.advance()
            where = self.parse_condition()
        return SelectStatement(columns, table, where)
    
    def parse_insert(self):
        self.expect('KEYWORD')
        self.expect('KEYWORD')
        table = self.expect('IDENTIFIER')
        self.expect('LPAREN')
        columns = []
        while True:
            col = self.expect('IDENTIFIER')
            columns.append(col)
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()
            else:
                break
        self.expect('RPAREN')
        self.expect('KEYWORD')
        self.expect('LPAREN')
        values = []
        while True:
            if self.current_token.type == 'NUMBER':
                values.append(self.current_token.value)
                self.advance()
            elif self.current_token.type == 'STRING':
                values.append(self.current_token.value)
                self.advance()
            else:
                raise SyntaxError(f"Expected value, got {self.current_token}")
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()
            else:
                break
        self.expect('RPAREN')
        return InsertStatement(table, columns, values)
    
    def parse_update(self):
        self.expect('KEYWORD')
        table = self.expect('IDENTIFIER')
        self.expect('KEYWORD')
        assignments = []
        while True:
            col = self.expect('IDENTIFIER')
            self.expect('OPERATOR')
            if self.current_token.type == 'NUMBER':
                val = self.current_token.value
                self.advance()
            elif self.current_token.type == 'STRING':
                val = self.current_token.value
                self.advance()
            else:
                raise SyntaxError(f"Expected value, got {self.current_token}")
            assignments.append((col, val))
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()
            else:
                break
        where = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'WHERE':
            self.advance()
            where = self.parse_condition()
        return UpdateStatement(table, assignments, where)
    
    def parse_delete(self):
        self.expect('KEYWORD')
        self.expect('KEYWORD')
        table = self.expect('IDENTIFIER')
        where = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'WHERE':
            self.advance()
            where = self.parse_condition()
        return DeleteStatement(table, where)
    
    def parse_columns(self):
        columns = []
        if self.current_token.type == 'STAR':
            self.advance()
            return ['*']
        while True:
            col = self.expect('IDENTIFIER')
            columns.append(col)
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()
            else:
                break
        return columns
    
    def parse_condition(self):
        left = self.expect('IDENTIFIER')
        operator = self.expect('OPERATOR')
        if self.current_token.type == 'NUMBER':
            right = self.current_token.value
            self.advance()
        elif self.current_token.type == 'STRING':
            right = self.current_token.value
            self.advance()
        else:
            raise SyntaxError(f"Expected value after operator, got {self.current_token}")
        condition = Condition(left, operator, right)
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value in ['AND', 'OR']:
            logical_op = self.current_token.value
            self.advance()
            next_condition = self.parse_condition()
            condition.logical_op = logical_op
            condition.next_condition = next_condition
        return condition