ff = open("record.txt", 'a+')
f2 = open("record with no №.txt", "r+", encoding='utf-8')
f2.write("12")
f2.write("12")
f2.write("12")
f2.write("12")
for raw in f2:
    print(raw)
f2.close()