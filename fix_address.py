with open('redactor.py', 'r') as f:
    code = f.read()

code = code.replace(r'return f"[{self.faker.address().replace(\'\n\', \', \')}]"', 'address = self.faker.address().replace("\\n", ", ")\n            return f"[{address}]"')

with open('redactor.py', 'w') as f:
    f.write(code)
