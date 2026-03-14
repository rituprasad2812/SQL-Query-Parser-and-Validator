from schema import SCHEMA

class SemanticAnalyzer:
    def __init__(self):
        self.schema = SCHEMA
        self.errors = []
    
    def analyze(self, ast):
        """Main analysis function"""
        self.errors = []  # Reset errors
        
        # Check if table exists
        if not self.check_table_exists(ast.table):
            self.errors.append(f"Table '{ast.table}' does not exist")
            return False  # Can't continue without valid table
        
        # Check columns
        if ast.columns != ['*']:
            for col in ast.columns:
                if not self.check_column_exists(ast.table, col):
                    self.errors.append(f"Column '{col}' does not exist in table '{ast.table}'")
        
        # Check WHERE condition
        if ast.where:
            self.check_condition(ast.table, ast.where)
        
        # Return result
        if self.errors:
            return False
        return True
    
    def check_table_exists(self, table_name):
        """Check if table exists in schema"""
        return table_name in self.schema
    
    def check_column_exists(self, table_name, column_name):
        """Check if column exists in table"""
        if table_name not in self.schema:
            return False
        return column_name in self.schema[table_name]
    
    def check_condition(self, table_name, condition):
        """Check WHERE condition validity"""
        # Check if column exists
        if not self.check_column_exists(table_name, condition.left):
            self.errors.append(f"Column '{condition.left}' does not exist in table '{table_name}'")
            return
        
        # Get column type
        col_type = self.schema[table_name][condition.left]
        
        # Check type compatibility
        if col_type == 'INT':
            if not condition.right.isdigit():
                self.errors.append(f"Type mismatch: Column '{condition.left}' is INT but compared with '{condition.right}'")
        elif col_type == 'VARCHAR':
            if condition.right.isdigit():
                self.errors.append(f"Type mismatch: Column '{condition.left}' is VARCHAR but compared with number")
        
        # Check next condition (for AND/OR)
        if condition.next_condition:
            self.check_condition(table_name, condition.next_condition)
    
    def get_errors(self):
        """Return all errors found"""
        return self.errors