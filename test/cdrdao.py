import os
import string
pipe = os.popen4 ("cdrdao scanbus")
tab = []

res = " "
while res !="":
    res = pipe[1].readline()
    #res= string.strip (res)
    tab.append(res)

for elem in tab:
    print "------------------------"
    print elem