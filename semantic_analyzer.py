from schema import SCHEMA
from parser import SelectStatement, InsertStatement, UpdateStatement, DeleteStatement

class SemanticAnalyzer:
    def __init__(self):
        self.schema = SCHEMA
        self.errors = []
    
    def analyze(self, ast):
        self.errors = []
        
        if not self.check_table_exists(ast.table):
            self.errors.append(f"Table '{ast.table}' does not exist")
            return False
        
        if isinstance(ast, SelectStatement):
            self.analyze_select(ast)
        elif isinstance(ast, InsertStatement):
            self.analyze_insert(ast)
        elif isinstance(ast, UpdateStatement):
            self.analyze_update(ast)
        elif isinstance(ast, DeleteStatement):
            self.analyze_delete(ast)
        
        return len(self.errors) == 0
    
    def analyze_select(self, ast):
        # Check columns
        if ast.columns != ['*']:
            for col in ast.columns:
                if not self.check_column_in_any_table(col, ast):
                    self.errors.append(f"Column '{col}' does not exist")
        
        # Check JOINs
        for join in ast.joins:
            if not self.check_table_exists(join.table):
                self.errors.append(f"Table '{join.table}' does not exist")
        
        # Check WHERE
        if ast.where:
            self.check_condition(ast.table, ast.where)
        
        # Check GROUP BY
        if ast.group_by:
            for col in ast.group_by:
                if not self.check_column_in_any_table(col, ast):
                    self.errors.append(f"GROUP BY column '{col}' does not exist")
        
        # Check ORDER BY
        if ast.order_by:
            for col, direction in ast.order_by:
                if not self.check_column_in_any_table(col, ast):
                    self.errors.append(f"ORDER BY column '{col}' does not exist")
    
    def check_column_in_any_table(self, column, ast):
        # Check in main table
        if self.check_column_exists(ast.table, column):
            return True
        # Check in joined tables
        for join in ast.joins:
            if self.check_column_exists(join.table, column):
                return True
        return False
    
    def analyze_insert(self, ast):
        for col in ast.columns:
            if not self.check_column_exists(ast.table, col):
                self.errors.append(f"Column '{col}' does not exist in table '{ast.table}'")
        if len(ast.columns) != len(ast.values):
            self.errors.append(f"Column count ({len(ast.columns)}) doesn't match value count ({len(ast.values)})")
    
    def analyze_update(self, ast):
        for col, val in ast.assignments:
            if not self.check_column_exists(ast.table, col):
                self.errors.append(f"Column '{col}' does not exist in table '{ast.table}'")
        if ast.where:
            self.check_condition(ast.table, ast.where)
    
    def analyze_delete(self, ast):
        if ast.where:
            self.check_condition(ast.table, ast.where)
    
    def check_table_exists(self, table_name):
        return table_name in self.schema
    
    def check_column_exists(self, table_name, column_name):
        if table_name not in self.schema:
            return False
        return column_name in self.schema[table_name]
    
    def check_condition(self, table_name, condition):
        if not self.check_column_exists(table_name, condition.left):
            self.errors.append(f"Column '{condition.left}' does not exist in table '{table_name}'")
            return
        col_type = self.schema[table_name][condition.left]
        if col_type == 'INT':
            if not condition.right.isdigit():
                self.errors.append(f"Type mismatch: Column '{condition.left}' is INT but compared with '{condition.right}'")
        elif col_type == 'VARCHAR':
            if condition.right.isdigit():
                self.errors.append(f"Type mismatch: Column '{condition.left}' is VARCHAR but compared with number")
        if condition.next_condition:
            self.check_condition(table_name, condition.next_condition)
    
    def get_errors(self):
        return self.errors