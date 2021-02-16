import sys, re, os


file = open(sys.argv[1], 'r')
output = open(sys.argv[2], 'w')
sys.stdout = output
words = {}

for line in file:
  line = line.strip().lower().replace(',', '')
  for word in re.split(' ', line):
    if word not in words:
      words[word] = 1
    else:
      words[word] = words[word] + 1

words = dict(sorted(words.items(), key = lambda kv: kv[0]))
for key in list(words.keys()):
  print('%s %s'%(key, words[key]))
output.close()
