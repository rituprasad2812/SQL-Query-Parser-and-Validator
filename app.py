import streamlit as st
import graphviz
from lexer import Lexer
from parser import Parser
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
            st.subheader("Step 1: Lexical Analysis (Tokenization)")
            lexer = Lexer(query)
            tokens = lexer.tokenize()

            token_display = ", ".join([f"{t.type}({t.value})" for t in tokens])
            st.code(token_display, language="text")
            st.success(f"✅ {len(tokens)} tokens generated")

            # Step 2: Syntax Analysis
            st.subheader("Step 2: Syntax Analysis (Parsing)")
            parser = Parser(tokens)
            ast = parser.parse()

            st.write(f"**Columns:** {', '.join(ast.columns)}")
            st.write(f"**Table:** {ast.table}")
            st.write(f"**Where Condition:** {ast.where if ast.where else 'None'}")
            st.success("✅ Syntax is correct")

            # Visualize Parse Tree
            st.write("**Parse Tree:**")
            dot = graphviz.Digraph()
            dot.attr(bgcolor='transparent')
            dot.attr('edge', color='white')
            dot.attr('node', fontcolor='black')
            dot.attr('node', shape='ellipse', style='filled', fillcolor='lightblue')

            # Root node
            dot.node('SELECT_STMT', 'SELECT')

            # Columns branch
            dot.node('COLS', 'COLUMNS')
            dot.edge('SELECT_STMT', 'COLS')
            for i, col in enumerate(ast.columns):
                dot.node(f'col_{i}', col, fillcolor='lightgreen')
                dot.edge('COLS', f'col_{i}')

            # FROM branch
            dot.node('FROM', 'FROM')
            dot.edge('SELECT_STMT', 'FROM')
            dot.node('TABLE', ast.table, fillcolor='lightyellow')
            dot.edge('FROM', 'TABLE')

            # WHERE branch (if exists)
            if ast.where:
                dot.node('WHERE', 'WHERE')
                dot.edge('SELECT_STMT', 'WHERE')

                # Build condition tree
                def add_condition(cond, parent_id, count=0):
                    cond_id = f'cond_{count}'
                    dot.node(cond_id, cond.operator, fillcolor='lightpink')
                    dot.edge(parent_id, cond_id)

                    # Left side (column)
                    left_id = f'left_{count}'
                    dot.node(left_id, cond.left, fillcolor='white')
                    dot.edge(cond_id, left_id)

                    # Right side (value)
                    right_id = f'right_{count}'
                    dot.node(right_id, str(cond.right), fillcolor='white')
                    dot.edge(cond_id, right_id)

                    # Handle AND/OR
                    if cond.next_condition:
                        logic_id = f'logic_{count}'
                        dot.node(logic_id, cond.logical_op, fillcolor='orange')
                        dot.edge('WHERE', logic_id)
                        add_condition(cond.next_condition, logic_id, count + 1)

                add_condition(ast.where, 'WHERE')

            st.graphviz_chart(dot)

            # Step 3: Semantic Analysis
            st.subheader("Step 3: Semantic Analysis (Validation)")
            analyzer = SemanticAnalyzer()
            is_valid = analyzer.analyze(ast)

            if is_valid:
                st.success("🎉 Query is VALID! All checks passed.")
            else:
                st.error("❌ Query has errors:")
                for error in analyzer.get_errors():
                    st.write(f"- {error}")

        except SyntaxError as e:
            st.error(f"❌ Syntax Error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("Please enter a query")

# Sidebar with examples
st.sidebar.title("Example Queries")
st.sidebar.code("SELECT * FROM students", language="sql")
st.sidebar.code("SELECT name, age FROM students WHERE age > 18", language="sql")
st.sidebar.code("SELECT name FROM students WHERE department = 'CS'", language="sql")
st.sidebar.code("SELECT name, age FROM students WHERE age > 18 AND department = 'CS'", language="sql")