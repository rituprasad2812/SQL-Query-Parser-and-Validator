import streamlit as st
import graphviz
from lexer import Lexer
from parser import Parser, SelectStatement, InsertStatement, UpdateStatement, DeleteStatement
from semantic_analyzer import SemanticAnalyzer
from schema import SCHEMA
from optimizer import QueryOptimizer

st.title("SQL Query Parser & Validator")

# Display available tables at top (fixed position)
st.subheader("Available Database Tables")
cols = st.columns(len(SCHEMA))
for idx, (table_name, columns) in enumerate(SCHEMA.items()):
    with cols[idx]:
        st.write(f"**{table_name}**")
        for col_name, col_type in columns.items():
            st.write(f"- `{col_name}` ({col_type})")

st.divider()

# Create tabs below the tables
tab1, tab2 = st.tabs(["Analysis", "Optimization"])

with tab1:
    st.write("Enter your SQL query below to analyze it")
    
    query = st.text_area("SQL Query:", height=100, placeholder="SELECT name FROM students WHERE age > 18")
    
    if st.button("Analyze Query"):
        if query.strip():
            try:
                # Step 1: Lexical Analysis
                with st.container():
                    st.subheader("Step 1: Lexical Analysis (Tokenization)")
                    lexer = Lexer(query)
                    tokens = lexer.tokenize()

                    token_display = ", ".join([f"{t.type}({t.value})" for t in tokens])
                    st.code(token_display, language="text")
                    st.success(f"{len(tokens)} tokens generated")

                # Step 2: Syntax Analysis
                with st.container():
                    st.subheader("Step 2: Syntax Analysis (Parsing)")
                    parser = Parser(tokens)
                    ast = parser.parse()

                    if hasattr(ast, 'columns'):
                        st.write(f"**Columns:** {', '.join(ast.columns)}")
                    if hasattr(ast, 'table'):
                        st.write(f"**Table:** {ast.table}")
                    if hasattr(ast, 'joins') and ast.joins:
                        for join in ast.joins:
                            st.write(f"**Join:** {join}")
                    if hasattr(ast, 'values'):
                        st.write(f"**Values:** {', '.join(ast.values)}")
                    if hasattr(ast, 'assignments'):
                        st.write(f"**Assignments:** {ast.assignments}")
                    if hasattr(ast, 'where'):
                        st.write(f"**Where Condition:** {ast.where if ast.where else 'None'}")
                    if hasattr(ast, 'group_by') and ast.group_by:
                        st.write(f"**Group By:** {', '.join(ast.group_by)}")
                    if hasattr(ast, 'having') and ast.having:
                        st.write(f"**Having:** {ast.having}")
                    if hasattr(ast, 'order_by') and ast.order_by:
                        order_str = ', '.join([f"{col} {dir}" for col, dir in ast.order_by])
                        st.write(f"**Order By:** {order_str}")
                    
                    st.success("Syntax is correct")

                    # Visualize Parse Tree
                    st.write("**Parse Tree:**")
                    dot = graphviz.Digraph()
                    dot.attr(bgcolor='transparent')
                    dot.attr('edge', color='white')
                    dot.attr('node', fontcolor='black', shape='circle', style='filled', width='0.7', height='0.7')
                    dot.attr(rankdir='TB')
                    dot.attr(splines='line')

                    if isinstance(ast, SelectStatement):
                        dot.node('ROOT', 'SELECT', fillcolor='lightblue')
                        dot.node('COLS', 'COLS', fillcolor='lightgreen')
                        dot.node('FROM', 'FROM', fillcolor='lightyellow')
                        dot.edge('ROOT', 'COLS')
                        dot.edge('ROOT', 'FROM')
                        
                        for i, col in enumerate(ast.columns):
                            dot.node(f'col_{i}', col, fillcolor='white')
                            dot.edge('COLS', f'col_{i}')
                        
                        dot.node('TABLE', ast.table, fillcolor='white')
                        dot.edge('FROM', 'TABLE')
                        
                        for i, join in enumerate(ast.joins):
                            dot.node(f'JOIN_{i}', 'JOIN', fillcolor='lightcyan')
                            dot.edge('ROOT', f'JOIN_{i}')
                            dot.node(f'JTYPE_{i}', join.join_type, fillcolor='white')
                            dot.node(f'JTABLE_{i}', join.table, fillcolor='white')
                            dot.node(f'JON_{i}', 'ON', fillcolor='lightpink')
                            dot.edge(f'JOIN_{i}', f'JTYPE_{i}')
                            dot.edge(f'JOIN_{i}', f'JTABLE_{i}')
                            dot.edge(f'JOIN_{i}', f'JON_{i}')
                            dot.node(f'JCOND_{i}', str(join.condition), fillcolor='white')
                            dot.edge(f'JON_{i}', f'JCOND_{i}')
                        
                        if ast.where:
                            dot.node('WHERE', 'WHERE', fillcolor='lightpink')
                            dot.edge('ROOT', 'WHERE')
                            
                            def add_cond_tree(cond, parent, count=0):
                                op_id = f'op_{count}'
                                dot.node(op_id, cond.operator, fillcolor='orange')
                                dot.edge(parent, op_id)
                                
                                left_id = f'left_{count}'
                                right_id = f'right_{count}'
                                dot.node(left_id, cond.left, fillcolor='white')
                                dot.node(right_id, str(cond.right), fillcolor='white')
                                dot.edge(op_id, left_id)
                                dot.edge(op_id, right_id)
                                
                                if cond.next_condition:
                                    logic_id = f'logic_{count}'
                                    dot.node(logic_id, cond.logical_op, fillcolor='orange')
                                    dot.edge('WHERE', logic_id)
                                    add_cond_tree(cond.next_condition, logic_id, count + 1)
                            
                            add_cond_tree(ast.where, 'WHERE')
                        
                        if ast.group_by:
                            dot.node('GROUPBY', 'GROUP', fillcolor='orange')
                            dot.edge('ROOT', 'GROUPBY')
                            dot.node('BY', 'BY', fillcolor='orange')
                            dot.edge('GROUPBY', 'BY')
                            for i, col in enumerate(ast.group_by):
                                dot.node(f'grp_{i}', col, fillcolor='white')
                                dot.edge('BY', f'grp_{i}')
                        
                        if ast.order_by:
                            dot.node('ORDERBY', 'ORDER', fillcolor='lightyellow')
                            dot.edge('ROOT', 'ORDERBY')
                            dot.node('OBYBY', 'BY', fillcolor='lightyellow')
                            dot.edge('ORDERBY', 'OBYBY')
                            for i, (col, dir) in enumerate(ast.order_by):
                                dot.node(f'ord_{i}', col, fillcolor='white')
                                dot.node(f'dir_{i}', dir, fillcolor='white')
                                dot.edge('OBYBY', f'ord_{i}')
                                dot.edge(f'ord_{i}', f'dir_{i}')

                    elif isinstance(ast, InsertStatement):
                        dot.node('ROOT', 'INSERT', fillcolor='lightblue')
                        dot.node('INTO', 'INTO', fillcolor='lightyellow')
                        dot.edge('ROOT', 'INTO')
                        dot.node('TABLE', ast.table, fillcolor='white')
                        dot.edge('INTO', 'TABLE')
                        
                        dot.node('COLS', 'COLS', fillcolor='lightgreen')
                        dot.edge('ROOT', 'COLS')
                        for i, col in enumerate(ast.columns):
                            dot.node(f'col_{i}', col, fillcolor='white')
                            dot.edge('COLS', f'col_{i}')
                        
                        dot.node('VALS', 'VALUES', fillcolor='lightpink')
                        dot.edge('ROOT', 'VALS')
                        for i, val in enumerate(ast.values):
                            dot.node(f'val_{i}', str(val), fillcolor='white')
                            dot.edge('VALS', f'val_{i}')

                    elif isinstance(ast, UpdateStatement):
                        dot.node('ROOT', 'UPDATE', fillcolor='lightblue')
                        dot.node('TABLE', ast.table, fillcolor='white')
                        dot.edge('ROOT', 'TABLE')
                        
                        dot.node('SET', 'SET', fillcolor='lightgreen')
                        dot.edge('ROOT', 'SET')
                        for i, (col, val) in enumerate(ast.assignments):
                            dot.node(f'eq_{i}', '=', fillcolor='orange')
                            dot.edge('SET', f'eq_{i}')
                            dot.node(f'col_{i}', col, fillcolor='white')
                            dot.node(f'val_{i}', str(val), fillcolor='white')
                            dot.edge(f'eq_{i}', f'col_{i}')
                            dot.edge(f'eq_{i}', f'val_{i}')
                        
                        if ast.where:
                            dot.node('WHERE', 'WHERE', fillcolor='lightpink')
                            dot.edge('ROOT', 'WHERE')
                            dot.node('COND', str(ast.where), fillcolor='white')
                            dot.edge('WHERE', 'COND')

                    elif isinstance(ast, DeleteStatement):
                        dot.node('ROOT', 'DELETE', fillcolor='lightblue')
                        dot.node('FROM', 'FROM', fillcolor='lightyellow')
                        dot.edge('ROOT', 'FROM')
                        dot.node('TABLE', ast.table, fillcolor='white')
                        dot.edge('FROM', 'TABLE')
                        
                        if ast.where:
                            dot.node('WHERE', 'WHERE', fillcolor='lightpink')
                            dot.edge('ROOT', 'WHERE')
                            dot.node('COND', str(ast.where), fillcolor='white')
                            dot.edge('WHERE', 'COND')

                    st.graphviz_chart(dot)

                # Step 3: Semantic Analysis
                with st.container():
                    st.subheader("Step 3: Semantic Analysis (Validation)")
                    analyzer = SemanticAnalyzer()
                    is_valid = analyzer.analyze(ast)

                    if is_valid:
                        st.success("Query is VALID! All checks passed.")
                    else:
                        st.error("ERRORS DETECTED IN SEMANTIC ANALYSIS PHASE:")
                        for error in analyzer.get_errors():
                            st.write(f"{error}")
                        st.info("**Note: Lexical and Syntax phases passed, but semantic validation failed.**")

            except SyntaxError as e:
                st.error(f"ERROR DETECTED IN SYNTAX ANALYSIS PHASE:")
                st.write(f"{str(e)}")
                st.info("**Note: Lexical analysis passed, but syntax parsing failed.**")
            except Exception as e:
                st.error(f"ERROR DETECTED IN LEXICAL ANALYSIS PHASE:")
                st.write(f"{str(e)}")
        else:
            st.warning("Please enter a query")

with tab2:
    st.write("Enter your SQL query below to get optimization suggestions")
    
    opt_query = st.text_area("SQL Query for Optimization:", height=100, placeholder="SELECT * FROM students", key="opt_query")
    
    if st.button("Optimize Query"):
        if opt_query.strip():
            try:
                lexer = Lexer(opt_query)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                
                optimizer = QueryOptimizer()
                results = optimizer.optimize(ast)
                
                if results['warnings']:
                    st.subheader("Warnings")
                    for warning in results['warnings']:
                        st.warning(warning)
                
                if results['good_practices']:
                    st.subheader("Good Practices")
                    for practice in results['good_practices']:
                        st.success(practice)
                
                if results['suggestions']:
                    st.subheader("Optimization Suggestions")
                    for suggestion in results['suggestions']:
                        st.info(suggestion)
                
                optimized = optimizer.get_optimized_query(ast)
                if optimized:
                    st.subheader("Optimized Query")
                    st.code(optimized, language="sql")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a query")

# Sidebar with examples
st.sidebar.title("Example Queries")

st.sidebar.subheader("For Analysis")
st.sidebar.code("SELECT name, age FROM students WHERE age > 18", language="sql")
st.sidebar.code("SELECT name FROM students JOIN enrollments ON student_id = student_id", language="sql")
st.sidebar.code("SELECT department FROM students GROUP BY department", language="sql")
st.sidebar.code("INSERT INTO students (name, age, department) VALUES ('John', 20, 'CS')", language="sql")
st.sidebar.code("UPDATE students SET age = 21 WHERE name = 'John'", language="sql")
st.sidebar.code("DELETE FROM students WHERE age < 18", language="sql")

st.sidebar.divider()

st.sidebar.subheader("For Optimization (Unoptimized Queries)")
st.sidebar.code("SELECT * FROM students", language="sql")
st.sidebar.caption("⚠️ Uses SELECT * - inefficient")

st.sidebar.code("SELECT * FROM students JOIN enrollments ON student_id = student_id", language="sql")
st.sidebar.caption("⚠️ SELECT * with JOIN - very bad")

st.sidebar.code("DELETE FROM students", language="sql")
st.sidebar.caption("⚠️ No WHERE - deletes ALL rows!")

st.sidebar.code("UPDATE students SET age = 21", language="sql")
st.sidebar.caption("⚠️ No WHERE - updates ALL rows!")

st.sidebar.code("SELECT name FROM students", language="sql")
st.sidebar.caption("⚠️ No WHERE - returns ALL rows")