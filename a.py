b = []
while True:
    a = input()
    if (a.count(' ') == 1):
        b.append(a)
    if a == '0':
        break

for i in b:
    print(i)
