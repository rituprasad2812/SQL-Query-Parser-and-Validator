class ASTNode:
    """Base class for tree nodes"""
    pass


class SelectStatement(ASTNode):
    def __init__(self, columns, table, joins=None, where=None, group_by=None, having=None, order_by=None):
        self.columns = columns
        self.table = table
        self.joins = joins or []
        self.where = where
        self.group_by = group_by
        self.having = having
        self.order_by = order_by
    
    def __repr__(self):
        return f"SelectStatement(columns={self.columns}, table={self.table}, joins={self.joins}, where={self.where}, group_by={self.group_by}, order_by={self.order_by})"


class JoinClause(ASTNode):
    def __init__(self, join_type, table, condition):
        self.join_type = join_type
        self.table = table
        self.condition = condition
    
    def __repr__(self):
        return f"{self.join_type} JOIN {self.table} ON {self.condition}"


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
        self.expect('KEYWORD')  # SELECT
        columns = self.parse_columns()
        self.expect('KEYWORD')  # FROM
        table = self.expect('IDENTIFIER')
        
        # Parse JOINs (optional)
        joins = []
        while self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value in ['JOIN', 'INNER', 'LEFT', 'RIGHT']:
            join = self.parse_join()
            joins.append(join)
        
        # Parse WHERE (optional)
        where = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'WHERE':
            self.advance()
            where = self.parse_condition()
        
        # Parse GROUP BY (optional)
        group_by = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'GROUP':
            self.advance()  # GROUP
            self.expect('KEYWORD')  # BY
            group_by = self.parse_group_by()
        
        # Parse HAVING (optional)
        having = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'HAVING':
            self.advance()
            having = self.parse_condition()
        
        # Parse ORDER BY (optional)
        order_by = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'ORDER':
            self.advance()  # ORDER
            self.expect('KEYWORD')  # BY
            order_by = self.parse_order_by()
        
        return SelectStatement(columns, table, joins, where, group_by, having, order_by)
    
    def parse_join(self):
        # Get join type
        join_type = 'INNER'
        if self.current_token.value in ['LEFT', 'RIGHT', 'INNER']:
            join_type = self.current_token.value
            self.advance()
        
        self.expect('KEYWORD')  # JOIN
        table = self.expect('IDENTIFIER')
        self.expect('KEYWORD')  # ON
        condition = self.parse_join_condition()
        
        return JoinClause(join_type, table, condition)
    
    def parse_join_condition(self):
        left = self.expect('IDENTIFIER')
        operator = self.expect('OPERATOR')
        right = self.expect('IDENTIFIER')
        return Condition(left, operator, right)
    
    def parse_group_by(self):
        columns = []
        while True:
            col = self.expect('IDENTIFIER')
            columns.append(col)
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()
            else:
                break
        return columns
    
    def parse_order_by(self):
        orders = []
        while True:
            col = self.expect('IDENTIFIER')
            direction = 'ASC'
            if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value in ['ASC', 'DESC']:
                direction = self.current_token.value
                self.advance()
            orders.append((col, direction))
            if self.current_token and self.current_token.type == 'COMMA':
                self.advance()
            else:
                break
        return orders
    
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