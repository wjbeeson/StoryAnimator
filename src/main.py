import numpy as np

from datetime import datetime

from nw import nw, TimeStampNode, align

#
# test 1: all words correct
#

r1,r2 = nw(
    "this is a test".split(" "),
    [TimeStampNode('this',1), TimeStampNode('is',2),TimeStampNode('a',3),TimeStampNode('test',4)]
)

timestamps =align(r1, r2)

print(r1,"\n",r2)
print(timestamps)

#
# test 2: extra word
#

r1,r2 = nw(
    "this is a test".split(" "),
    [TimeStampNode('this',1), TimeStampNode('is',2),TimeStampNode('a',3),TimeStampNode('great',3.5), TimeStampNode('test',4)]
)

print(r1,"\n",r2)
print(timestamps)
pass

#
# test 3: deleted word
#

r1,r2 = nw(
    "this is a test".split(" "),
    [TimeStampNode('this',1), TimeStampNode('is',2), TimeStampNode('test',4)]
)

print(r1,"\n",r2)
timestamps = align(r1, r2)
print(timestamps)

#
# test 4: deleted first word
#

r1,r2 = nw(
    "this is a test".split(" "),
    [ TimeStampNode('is',2), TimeStampNode('a',3), TimeStampNode('test',4)]
)


print(r1,"\n",r2)
timestamps = align(r1, r2)
print(timestamps)

#
# test 5: deleted final word
#

r1,r2 = nw(
    "this is a test".split(" "),
    [ TimeStampNode('this',1), TimeStampNode('is',2), TimeStampNode('a',3)]
)


print(r1,"\n",r2)
timestamps = align(r1, r2)
print(timestamps)

pass
x = "GATTACA"
y = "GCATGCU"
#print(nw(x, y))
# G-ATTACA
# GCA-TGCU

np.random.seed(42)
x = np.random.choice(['A', 'T', 'G', 'C'], 50)
y = np.random.choice(['A', 'T', 'G', 'C'], 50)

#print(nw(x, y, gap = 0))
# ----G-C--AGGCAAGTGGGGCACCCGTATCCT-T-T-C-C-AACTTACAAGGGT-C-CC-----CGT-T
# GTGCGCCAGAGG-AAGT----CA--C-T-T--TATATCCGCG--C--AC---GGTACTCCTTTTTC-TA-

#print(nw(x, y, gap = 1))
# GCAG-GCAAGTGG--GGCAC-CCGTATCCTTTC-CAAC-TTACAAGGGTCC-CCGT-T-
# G-TGCGCCAGAGGAAGTCACTTTATATCC--GCGC-ACGGTAC-----TCCTTTTTCTA

#print(nw(x, y, gap = 2))
# GCAGGCAAGTGG--GGCAC-CCGTATCCTTTCCAACTTACAAGGGTCCCCGTT
# GTGCGCCAGAGGAAGTCACTTTATATCC-GCGCACGGTAC-TCCTTTTTC-TA


with open("sample_text1.txt",'r') as f:
    input_text1 = f.read()

with open("sample_text2.txt", 'r') as f:
    input_text2 = f.read()

tokens1 = input_text1.split(" ")
tokens2 = input_text2.split(" ")

now = datetime.now()

result1,result2 = nw(tokens1,tokens2,gap=3)

print(f"elapsed = {datetime.now()-now}")

print( result1[:100] )
print( result2[:100])

