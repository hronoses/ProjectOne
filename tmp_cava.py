i = 0
def palindrome_chain_length(n):
    global i
    if str(n) == str(n)[::-1]:
        return i
    else:
        i += 1
        val = n + int(str(n)[::-1])
        return palindrome_chain_length(val)

print palindrome_chain_length(0)
l = [2, 3, 5, 7, 11, 101, 131, 151, 0, 1, 4, 9, 121, 484, 676, 10201, 12321]
for f in l:
    print palindrome_chain_length(f)
# print palindrome_chain_length(82208)