def tokenize(expression):
    tokens = []
    current_number = ""
    
    for char in expression:
        if char.isdigit() or char == '.':
            current_number += char
        elif char in "+-*/()":
            if current_number:
                tokens.append(float(current_number))
                current_number = ""
            tokens.append(char)
            
    if current_number:
        tokens.append(float(current_number))
        
    return tokens


def infix_to_postfix(tokens):
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    output = []
    stack = []
    
    for token in tokens:
        if isinstance(token, float):
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while (stack and stack[-1] != '(' and 
                   precedence.get(stack[-1], 0) >= precedence.get(token, 0)):
                output.append(stack.pop())
            stack.append(token)
            
    while stack:
        output.append(stack.pop())
        
    return output


def evaluate_postfix(postfix_tokens):
    stack = []
    
    for token in postfix_tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            b = stack.pop()
            a = stack.pop() 
            
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                if b == 0: й
                    return "Помилка: ділення на нуль!"
                stack.append(a / b)
                
    return stack[0]


def calc(expression):
    tokens = tokenize(expression)
    postfix = infix_to_postfix(tokens)
    result = evaluate_postfix(postfix)
    return result


while True:
    expr = input("Введіть вираз (або 'stop' для виходу): ")
    
    if expr.lower() == 'stop':
        break
    
    print("Результат:", calc(expr)) 