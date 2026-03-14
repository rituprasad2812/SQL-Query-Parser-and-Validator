import streamlit as st
import graphviz
from lexer import Lexer
from parser import Parser, SelectStatement, InsertStatement, UpdateStatement, DeleteStatement
from semantic_analyzer import SemanticAnalyzer
from schema import SCHEMA

st.title("SQL Query Parser & Validator")
st.write("Enter your SQL query below to analyze it")

# Display available tables
st.subheader("Available Database Tables")
cols = st.columns(len(SCHEMA))
for idx, (table_name, columns) in enumerate(SCHEMA.items()):
    with cols[idx]:
        st.write(f"**{table_name}**")
        for col_name, col_type in columns.items():
            st.write(f"- `{col_name}` ({col_type})")

st.divider()

# Text area for SQL input
query = st.text_area("SQL Query:", height=100, placeholder="SELECT name FROM students WHERE age > 18")

# Analyze button
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

                # Handle different statement types
                if hasattr(ast, 'columns'):
                    st.write(f"**Columns:** {', '.join(ast.columns)}")
                if hasattr(ast, 'table'):
                    st.write(f"**Table:** {ast.table}")
                if hasattr(ast, 'values'):
                    st.write(f"**Values:** {', '.join(ast.values)}")
                if hasattr(ast, 'assignments'):
                    st.write(f"**Assignments:** {ast.assignments}")
                if hasattr(ast, 'where'):
                    st.write(f"**Where Condition:** {ast.where if ast.where else 'None'}")
                
                st.success("Syntax is correct")

                # Visualize Parse Tree
                st.write("**Parse Tree:**")
                dot = graphviz.Digraph()
                dot.attr(bgcolor='transparent')
                dot.attr('edge', color='white')
                dot.attr('node', fontcolor='black')
                dot.attr('node', shape='ellipse', style='filled', fillcolor='lightblue')

                if isinstance(ast, SelectStatement):
                    dot.node('ROOT', 'SELECT')
                    dot.node('COLS', 'COLUMNS')
                    dot.edge('ROOT', 'COLS')
                    for i, col in enumerate(ast.columns):
                        dot.node(f'col_{i}', col, fillcolor='lightgreen')
                        dot.edge('COLS', f'col_{i}')
                    dot.node('FROM', 'FROM')
                    dot.edge('ROOT', 'FROM')
                    dot.node('TABLE', ast.table, fillcolor='lightyellow')
                    dot.edge('FROM', 'TABLE')
                    if ast.where:
                        dot.node('WHERE', 'WHERE')
                        dot.edge('ROOT', 'WHERE')
                        dot.node('COND', str(ast.where), fillcolor='lightpink')
                        dot.edge('WHERE', 'COND')

                elif isinstance(ast, InsertStatement):
                    dot.node('ROOT', 'INSERT')
                    dot.node('INTO', 'INTO')
                    dot.edge('ROOT', 'INTO')
                    dot.node('TABLE', ast.table, fillcolor='lightyellow')
                    dot.edge('INTO', 'TABLE')
                    dot.node('COLS', 'COLUMNS')
                    dot.edge('ROOT', 'COLS')
                    for i, col in enumerate(ast.columns):
                        dot.node(f'col_{i}', col, fillcolor='lightgreen')
                        dot.edge('COLS', f'col_{i}')
                    dot.node('VALS', 'VALUES')
                    dot.edge('ROOT', 'VALS')
                    for i, val in enumerate(ast.values):
                        dot.node(f'val_{i}', str(val), fillcolor='lightpink')
                        dot.edge('VALS', f'val_{i}')

                elif isinstance(ast, UpdateStatement):
                    dot.node('ROOT', 'UPDATE')
                    dot.node('TABLE', ast.table, fillcolor='lightyellow')
                    dot.edge('ROOT', 'TABLE')
                    dot.node('SET', 'SET')
                    dot.edge('ROOT', 'SET')
                    for i, (col, val) in enumerate(ast.assignments):
                        dot.node(f'assign_{i}', f'{col} = {val}', fillcolor='lightgreen')
                        dot.edge('SET', f'assign_{i}')
                    if ast.where:
                        dot.node('WHERE', 'WHERE')
                        dot.edge('ROOT', 'WHERE')
                        dot.node('COND', str(ast.where), fillcolor='lightpink')
                        dot.edge('WHERE', 'COND')

                elif isinstance(ast, DeleteStatement):
                    dot.node('ROOT', 'DELETE')
                    dot.node('FROM', 'FROM')
                    dot.edge('ROOT', 'FROM')
                    dot.node('TABLE', ast.table, fillcolor='lightyellow')
                    dot.edge('FROM', 'TABLE')
                    if ast.where:
                        dot.node('WHERE', 'WHERE')
                        dot.edge('ROOT', 'WHERE')
                        dot.node('COND', str(ast.where), fillcolor='lightpink')
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

# Sidebar with examples
st.sidebar.title("Example Queries")
st.sidebar.subheader("SELECT")
st.sidebar.code("SELECT * FROM students", language="sql")
st.sidebar.code("SELECT name, age FROM students WHERE age > 18", language="sql")

st.sidebar.subheader("INSERT")
st.sidebar.code("INSERT INTO students (name, age, department) VALUES ('John', 20, 'CS')", language="sql")

st.sidebar.subheader("UPDATE")
st.sidebar.code("UPDATE students SET age = 21 WHERE name = 'John'", language="sql")

st.sidebar.subheader("DELETE")
st.sidebar.code("DELETE FROM students WHERE age < 18", language="sql")