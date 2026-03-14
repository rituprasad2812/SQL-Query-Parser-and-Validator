from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Test query
query = "SELECT name, age FROM students WHERE age > 18"

print("Query:", query)
print("\n" + "="*50)

# Step 1: Tokenize
lexer = Lexer(query)
tokens = lexer.tokenize()
print("\n✅ Step 1: LEXICAL ANALYSIS")
print(f"   Tokens generated: {len(tokens)}")

# Step 2: Parse
parser = Parser(tokens)
ast = parser.parse()
print("\n✅ Step 2: SYNTAX ANALYSIS")
print(f"   Columns: {ast.columns}")
print(f"   Table: {ast.table}")
print(f"   Where: {ast.where}")

# Step 3: Semantic Analysis
analyzer = SemanticAnalyzer()
is_valid = analyzer.analyze(ast)

print("\n✅ Step 3: SEMANTIC ANALYSIS")
if is_valid:
    print("   🎉 Query is VALID!")
else:
    print("   ❌ Errors found:")
    for error in analyzer.get_errors():
        print(f"      - {error}")

print("\n" + "="*50)