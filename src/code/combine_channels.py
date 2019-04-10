"""
Combine channel tables
"""

import os,sys
import argparse
import pdb
import numpy as np
import subprocess as sp
from utils import *
from collections import defaultdict
from label_dictionary import LabelDictionary
from multiprocessing import Pool
import re

import warnings
warnings.filterwarnings("ignore")

regex = re.compile(r'\(0 \(0 "(?P<T>[A-Z])" "(?P<C>[0-9]+)" (?P<P>[-.0-9e^]+)\)\)')


if __name__ == "__main__":
  parser = argparse.ArgumentParser() 
  parser.add_argument("--il","-il",type=str, default=500, help="Incident language")
  parser.add_argument("--rl"          ,"-rl", type=str, default=None, help="Related Languages")
  parser.add_argument("--num_clusters","-nc",type=int, default=500, help="Number of clusters")
  parser.add_argument("--iters","-it",type=int, default=500, help="Number of iterations")
  parser.add_argument("--ca"    ,"-ca", type=str, default="br", help="Clutering algorithm [brown,anchor,]")
  parser.add_argument("--exp_dir"      ,"-exp", type=str, default='', help="Experiment folder")
  args = parser.parse_args()

  #rls = "en.de.fr.it.es.ja.ar.cs.ru.sw-hcs".split('.')
  rls = args.rl.split(",")
  il = args.il

  if il[:2]=='tl':
      il = 'tl'
  p_c_t = np.zeros([17,500])
  t2id = LabelDictionary()
  for rl in rls:
    if il==rl: continue
    model = "%s/models/%s2-%s.%s.%d.%d" % (args.exp_dir,rl,il,args.ca,args.num_clusters,args.iters)
    temp = np.zeros([17,500])

    for line in open(model,'r'):
      line = line.strip('\n')
      if line=='' or line=='0': continue
      match = regex.match(line)
      if match==None:
        # print("not found!",line)
        # pdb.set_trace()
        continue
      # pdb.set_trace()
      t = match.group("T")
      c = int(match.group("C"))
      ps = match.group("P")
      if t=="<s>" or t=="</s>":
        continue
      if ps[0]!="e":
        p = float(ps)
      else:
        p = np.exp(float(ps[2:]))
      tid = t2id.add(t)
      p_c_t[tid,c] += p
      temp[tid,c] = p
    #END-FOR-LINE

  #END-FOR-RLS
  
  # normalize
  for t in range(17):
    # print(t2id.get_label_name(t),p_c_t[t,:].sum(),len(rls), (p_c_t[t,:]/len(rls)).sum() )
    p_c_t[t,:] /= p_c_t[t,:].sum()

  # print out result
  outfile_fn = "%s/models/%s.%s.%d.500.comb" % (args.exp_dir,il,args.ca,args.num_clusters)
  outfile = open(outfile_fn,'w')
  print("0",file=outfile)
  print('(0 (0 "<s>" "<s>" 1))',file=outfile)
  print('(0 (0 "</s>" "</s>" 1))',file=outfile)
  for t in range(17):
    for c in range(500):
      tag = t2id.get_label_name(t)
      prob = str(p_c_t[t,c])
      print('(0 (0 "%s" "%d" %s))' % (tag,c,prob ), file=outfile )
      if p_c_t[t,c]==0:
        print(il,tag,c)
  outfile.close()

  for rl in rls:
    model_name = "%s/models/%s2-%s.%s.%d.500.comb" % (args.exp_dir,rl,il,args.ca,args.num_clusters)
    sp.Popen(["cp",outfile_fn,model_name])
  







