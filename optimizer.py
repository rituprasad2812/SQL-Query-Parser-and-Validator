from parser import SelectStatement, InsertStatement, UpdateStatement, DeleteStatement

class QueryOptimizer:
    def __init__(self):
        self.suggestions = []
        self.warnings = []
        self.good_practices = []
    
    def optimize(self, ast):
        self.suggestions = []
        self.warnings = []
        self.good_practices = []
        
        if isinstance(ast, SelectStatement):
            self.optimize_select(ast)
        elif isinstance(ast, InsertStatement):
            self.optimize_insert(ast)
        elif isinstance(ast, UpdateStatement):
            self.optimize_update(ast)
        elif isinstance(ast, DeleteStatement):
            self.optimize_delete(ast)
        
        return {
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'good_practices': self.good_practices
        }
    
    def optimize_select(self, ast):
        # Check SELECT *
        if ast.columns == ['*']:
            self.warnings.append("Using SELECT * fetches all columns - inefficient")
            self.suggestions.append(f"Specify only needed columns: SELECT column1, column2 FROM {ast.table}")
        else:
            self.good_practices.append("Specific columns selected - Good practice!")
        
        # Check WHERE clause
        if not ast.where:
            self.warnings.append("No WHERE clause - returns all rows")
            self.suggestions.append("Add WHERE clause to filter data and improve performance")
        else:
            self.good_practices.append("WHERE clause used - filters data efficiently")
            # Suggest index on WHERE columns
            self.suggestions.append(f"Consider adding index: CREATE INDEX idx_{ast.where.left} ON {ast.table}({ast.where.left})")
        
        # Check JOINs
        if ast.joins:
            for join in ast.joins:
                self.suggestions.append(f"Add index on JOIN column: CREATE INDEX idx_{join.condition.left} ON {ast.table}({join.condition.left})")
                self.suggestions.append(f"Add index on JOIN column: CREATE INDEX idx_{join.condition.right} ON {join.table}({join.condition.right})")
            
            if ast.columns == ['*']:
                self.warnings.append("SELECT * with JOIN fetches all columns from all tables")
                self.suggestions.append("Specify columns with table alias: SELECT t1.col1, t2.col2")
        else:
            self.good_practices.append("No unnecessary JOINs - simple query")
        
        # Check GROUP BY
        if ast.group_by:
            if ast.columns == ['*']:
                self.warnings.append("SELECT * with GROUP BY is invalid")
                self.suggestions.append("Use aggregation functions: SELECT column, COUNT(*) FROM table GROUP BY column")
            else:
                self.good_practices.append("GROUP BY used correctly")
                for col in ast.group_by:
                    self.suggestions.append(f"Consider index for GROUP BY: CREATE INDEX idx_{col} ON {ast.table}({col})")
        
        # Check ORDER BY
        if ast.order_by:
            for col, direction in ast.order_by:
                self.suggestions.append(f"Add index for faster sorting: CREATE INDEX idx_{col} ON {ast.table}({col})")
            self.good_practices.append("ORDER BY used for sorted results")
        
        # Check HAVING without GROUP BY
        if ast.having and not ast.group_by:
            self.warnings.append("HAVING without GROUP BY - use WHERE instead")
            self.suggestions.append("Replace HAVING with WHERE for filtering non-aggregated data")
    
    def optimize_insert(self, ast):
        self.good_practices.append("INSERT statement - no major optimizations needed")
        self.suggestions.append("For bulk inserts, consider using batch INSERT or LOAD DATA")
        self.suggestions.append("Disable indexes before bulk insert, re-enable after for speed")
    
    def optimize_update(self, ast):
        if not ast.where:
            self.warnings.append("UPDATE without WHERE - will update ALL rows!")
            self.suggestions.append("Add WHERE clause to target specific rows")
        else:
            self.good_practices.append("WHERE clause used - targets specific rows")
            self.suggestions.append(f"Consider index on WHERE column: CREATE INDEX idx_{ast.where.left} ON {ast.table}({ast.where.left})")
    
    def optimize_delete(self, ast):
        if not ast.where:
            self.warnings.append("DELETE without WHERE - will delete ALL rows!")
            self.suggestions.append("Add WHERE clause to target specific rows")
            self.suggestions.append("Use TRUNCATE TABLE for deleting all rows (faster)")
        else:
            self.good_practices.append("WHERE clause used - targets specific rows")
            self.suggestions.append(f"Consider index on WHERE column: CREATE INDEX idx_{ast.where.left} ON {ast.table}({ast.where.left})")
    
    def get_optimized_query(self, ast):
        """Generate an optimized version of the query"""
        if not isinstance(ast, SelectStatement):
            return None
        
        # Build optimized query
        optimized = ""
        
        if ast.columns == ['*']:
            optimized = f"SELECT column1, column2 FROM {ast.table}"
        else:
            optimized = f"SELECT {', '.join(ast.columns)} FROM {ast.table}"
        
        if ast.joins:
            for join in ast.joins:
                optimized += f" {join.join_type} JOIN {join.table} ON {join.condition}"
        
        if ast.where:
            optimized += f" WHERE {ast.where}"
        
        if ast.group_by:
            optimized += f" GROUP BY {', '.join(ast.group_by)}"
        
        if ast.order_by:
            order_str = ', '.join([f"{col} {dir}" for col, dir in ast.order_by])
            optimized += f" ORDER BY {order_str}"
        
        return optimized