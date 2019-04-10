import sys
from utils import char2upos

inputfn = sys.argv[1]
outputfn = sys.argv[2]
outfile = open(outputfn,'w')
for line in open(inputfn,'r'):
	line=line.strip('\n')
	if line=='': continue
	dec = [char2upos[c.strip('"')] for c in line.split()[1:-1] ]
	# assuming line always like this: <s> ...  </s> (#eos already strips while cl_tagging)
	print(" ".join(dec),file=outfile)