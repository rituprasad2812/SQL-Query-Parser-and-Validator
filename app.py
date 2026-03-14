import streamlit as st
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

st.title("🔍 SQL Query Parser & Validator")
st.write("Enter your SQL query below to analyze it")

# Text area for SQL input
query = st.text_area("SQL Query:", height=100, placeholder="SELECT name FROM students WHERE age > 18")

# Analyze button
if st.button("Analyze Query"):
    if query.strip():
        try:
            # Step 1: Lexical Analysis
            st.subheader("📝 Step 1: Lexical Analysis (Tokenization)")
            lexer = Lexer(query)
            tokens = lexer.tokenize()
            
            token_display = ", ".join([f"{t.type}({t.value})" for t in tokens])
            st.code(token_display, language="text")
            st.success(f"✅ {len(tokens)} tokens generated")
            
            # Step 2: Syntax Analysis
            st.subheader("🌳 Step 2: Syntax Analysis (Parsing)")
            parser = Parser(tokens)
            ast = parser.parse()
            
            st.write(f"**Columns:** {', '.join(ast.columns)}")
            st.write(f"**Table:** {ast.table}")
            st.write(f"**Where Condition:** {ast.where if ast.where else 'None'}")
            st.success("✅ Syntax is correct")
            
            # Step 3: Semantic Analysis
            st.subheader("✔️ Step 3: Semantic Analysis (Validation)")
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
st.sidebar.title("📚 Example Queries")
st.sidebar.code("SELECT * FROM students", language="sql")
st.sidebar.code("SELECT name, age FROM students WHERE age > 18", language="sql")
st.sidebar.code("SELECT name FROM students WHERE department = 'CS'", language="sql")
st.sidebar.code("SELECT name, age FROM students WHERE age > 18 AND department = 'CS'", language="sql")