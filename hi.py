

def calc(a, b, operation):
    if operation == "+":
        print(a + b)
    elif operation == "-":
        print(a - b)
    elif operation == "*":
        print(a * b)
    elif operation == "/":
        if b != 0:
             print (a // b)
        else:
            print("помилка")
 



while True:
    operation = input("Введіть операцію: ")
    if operation == "stop":
        break
    a = int(input("Введіть перше число: "))
    b = int(input("Введіть друге число: "))


    calc(a, b, operation)



