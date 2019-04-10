from label_dictionary import LabelDictionary
from collections import defaultdict
from utils import *
import os,sys
import argparse
import pdb
import numpy as np


START="<s>"
END="</s>"


if __name__ == "__main__":
  parser = argparse.ArgumentParser() 
  parser.add_argument("--input","-i", type=str, help="Cluster dict")
  parser.add_argument("--baseline","-b", type=str, default="brown", help="Clustering model used")
  parser.add_argument("--mode","-m", type=str, help="train / eval")
  parser.add_argument("--mapper","-v", type=str, help="label dict")
  parser.add_argument("--clt_vocab","-c", type=str, help="cluster vocab")
  parser.add_argument("--nclusters","-nc", type=int, default=50, help="number of clusters")
  parser.add_argument("--output_pref","-op", type=str,default="train",help="output filename prefix")
  parser.add_argument("--subs","-subs", type=int,default=10000,help="subsample size for carmel")
  
  args = parser.parse_args()
  
  np.random.seed(42)
  w2cid = {}

  if args.mode == 'train':

    cl2cid = LabelDictionary()
    mapper_fn = os.path.join(os.path.dirname(args.clt_vocab),'clt.mapper')

    output_file = open(args.clt_vocab+".norm",'w')

    for line in open(args.clt_vocab,'r'):
      line = line.strip('\n')
      if line=='': continue
      w,c = '',''
      if args.baseline=='brown':
        c,w,_ = line.split('\t')
      elif args.baseline=='clark':
        w,c,_ = line.split(' ')
      elif args.baseline[0] in "lp":
        w,c = line.split('\t')
      elif args.baseline == "marlin":
        w,c = line.split(' ')

      cid = cl2cid.add(c)
      w2cid[w] = str(cid)
      print("%s\t%d" % (w,cid),file=output_file)
    ##
    saveObject(w2cid,mapper_fn)

  else:
    if args.mapper==None:
      print("Error: LabelDictionary object not specified!\nCheck arguments list with -h option")
      sys.exit(1)
    elif not os.path.exists(args.mapper):
      print("Error: LabelDictionary object does not exist!")
      sys.exit(1)
    else:
      w2cid = uploadObject(args.mapper)
  ##
  

  # pdb.set_trace()

  outfile        = open(os.path.join(os.path.dirname(args.input), "%s.%d.%s.ctag" % (args.output_pref,args.nclusters,args.baseline) ),'w')
  outfile_carmel = open(os.path.join(os.path.dirname(args.input), "%s.%d.%s.carmel" % (args.output_pref,args.nclusters,args.baseline) ),'w')
  outfile_carmel_10k = open(os.path.join(os.path.dirname(args.input), "%s.%d.%s.carmel.10k" % (args.output_pref,args.nclusters,args.baseline) ),'w')
  lines = []
  
  for line in open(args.input,'r'):
    line = line.strip('\n')
    if line=='': continue
    clts = []
    for w in line.split(' '):
      if w == '#eos': continue
      if w not in w2cid:
        clts.append(w2cid["<unk>"])
      else:  
        clts.append(w2cid[w])
    print(" ".join(clts),file=outfile)

    clts = [START] + clts + [END]
    txt = " ".join(['"%s"' % x for x in clts])
    lines.append(txt)
    print("",file=outfile_carmel)
    print(txt,file=outfile_carmel)
    # print(" ".join(clts),file=outfile_carmel)

  ##
  idxs = np.arange(len(lines))
  np.random.shuffle(idxs)
  for idx in idxs[:args.subs]:
    print("",file=outfile_carmel_10k)
    print(lines[idx],file=outfile_carmel_10k)
  ##