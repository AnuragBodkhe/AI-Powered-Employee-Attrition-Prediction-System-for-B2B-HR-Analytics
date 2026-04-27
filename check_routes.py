import ast, re, sys
with open('flask_app/server.py', encoding='utf-8') as f:
    src = f.read()

try:
    ast.parse(src)
    print("Syntax: OK")
except SyntaxError as e:
    print("Syntax ERROR:", e)
    sys.exit(1)

routes = re.findall(r"@app\.route\([\"'](.*?)[\"']", src)
funcs  = re.findall(r"^def (\w+)\(", src, re.MULTILINE)

print("Routes:", routes)
print("Functions:", funcs)

if "logout" in funcs:
    print("logout function: FOUND")
else:
    print("logout function: MISSING")
if "/logout" in routes:
    print("/logout route: FOUND")
else:
    print("/logout route: MISSING")
