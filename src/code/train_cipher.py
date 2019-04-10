import os,sys
import argparse
from multiprocessing import Pool
import subprocess as sp
import numpy as np
from utils import *
import pdb


import warnings
warnings.filterwarnings("ignore")

PRIME_MOD = 19751


def run_train_channel(conf):
  rl,order,il,c_alg,cl,it,_id,IS_ELISA,exp_dir = conf.split('.')
  print(" running conf: ",conf)
  print("              ",rl,order,il,c_alg,cl,it,_id,IS_ELISA,exp_dir)
  
  IS_ELISA = bool(int(IS_ELISA))
  seed = (int(_id)+1) * PRIME_MOD * 100
  argums = ["bash","src/code/train_channel.sh",
             "-rl",rl,'-o',order,
             "-il",il,'-c',cl,
             "-it",it,'-id',_id,
             "-s",str(seed),
             "-exp",exp_dir
             ]

  if IS_ELISA:
    argums.extend(["-elisa","e"])
  if c_alg!="":
    argums.extend(["-ca",c_alg])

  pobj = sp.Popen(argums)
  while pobj.wait(): continue

  channel_name = "%s%s-%s.%s.%s.%s.%s" % (rl,order,il,c_alg,cl,it,_id)
  
  if not os.path.exists(exp_dir + "/logs/" + channel_name):
    return None

  lines = open(exp_dir + "/logs/" + channel_name,'r').read().strip('\n').split('\n')
  to_mine = ""
  for line in lines[-10:]:
    if line.startswith("Setting weights to model"):
      to_mine = line
      break
  idx = to_mine.rfind("^")
  print(to_mine,idx)
  score = float(to_mine[idx+1:].strip(' '))

  return [int(_id),score]



if __name__ == "__main__":
  parser = argparse.ArgumentParser() 
  parser.add_argument("--tokens"      ,"-tk" , type=str, default='', help="Input raw to tag --non-romanized, if applicable")
  parser.add_argument("--tokens_roman","-tkr", type=str, default='', help="Input raw to tag --romanized")
  parser.add_argument("--format"      ,"-fm" , type=str, default='txt', help="Format of input tokens [txt,bio]")
  parser.add_argument("--bio_delim"      ,"-bio_delim" , type=str, default=' ', help="Delimiter in BIO column format [' ', \n]")

  parser.add_argument("--output"      ,"-o", type=str, default='', help="Output file")
  parser.add_argument("--exp_dir"      ,"-exp", type=str, default='', help="Experiment folder")
  parser.add_argument("--il"          ,"-il", type=str, default='en', help="Incident Language")
  parser.add_argument("--rl"          ,"-rl", type=str, default=None, help="Related Language")
  parser.add_argument("--iter"        ,"-it", type=int, default=10, help="N. iterations per cipher run")
  parser.add_argument("--run_per_ch"  ,"-rc", type=int, default=100, help="N. runs per cipher conf")
  parser.add_argument("--lm_order"    ,"-lm", type=int, default=2, help="LM order")
  parser.add_argument("--baseline"    ,"-b",  type=str, default="brown", help="clustering algorithm [brown,ah,{l,p}{k,s}{100,300}{mono,multi}]")
  parser.add_argument("--num_clusters","-nc", type=int, default=500, help="Number of clusters on cipher side")
  parser.add_argument("--njobs"       ,"-j",  type=int, default=4, help="Number of jobs")
  parser.add_argument("--mode"        ,"-m",  type=str, default="train", help="mode [train,eval]")
  parser.add_argument("--test_data"   ,"-td", type=str, default="ud", help="which test data to evaluate [ud,elisa]")
  parser.add_argument("--dec_conf"    ,"-dc", type=str, default="1.1", help="weights for decoder (LM,CM)")
  parser.add_argument("--comb_table","-ct", action='store_true', help="Used combined cipher table channel model to decode")

  args = parser.parse_args()
  
  IS_ELISA = False
  CLUST_ALG = args.baseline


  if args.mode == "train":
    rl_list = []
    def_rfs = "en,de,fr,it,es,ja,ar,cs,ru,sw-hcs,hi"
    
    # No RL spec : default list
    if args.rl==None:
      rl_list = def_rfs.split(",")
    # Single RL spec : will run only one RL-IL pair
    elif ',' not in args.rl:
      rl_list = [args.rl]
    # Multiple RL spec: arg format "en.de.du.da", will run for RL-IL for all RL specified
    else:
      rl_list = args.rl.split(',')

    with Pool(args.njobs) as pool:
      for rl in rl_list:
        print()
        print("RL: ",rl)
        print("-"*60)
        conf_pref = "%s.%d.%s.%s.%d.%d" % (rl,args.lm_order,args.il,CLUST_ALG,args.num_clusters,args.iter)
        channel_name = "%s%d-%s.%s.%d.%d" % (rl,args.lm_order,args.il,CLUST_ALG,args.num_clusters,args.iter)
        # train channel      
        if "elisa" in args.il or args.il in ["ta","tl"]:
          IS_ELISA = True

        confs = ["%s.%d.%d.%s" % (conf_pref,_id,IS_ELISA,args.exp_dir) for _id in range(args.run_per_ch) ]
        res = pool.map(run_train_channel,confs)
        res = [x for x in res if x!=None]
        idxs = [x for x,y in res]
        idx = np.array([y for x,y in res]).argmin()
        print("best model:",res[idx])
        open("%s/logs/%s.scores" % (args.exp_dir,channel_name),'w').write('\n'.join(["%d %f" % (x,y) for x,y in res]))
        
        # clean directories
        to_rm = ["%s/logs/%s.%d" % (args.exp_dir,channel_name,_id) for _id in idxs if _id!=res[idx][0] ]
        if len(to_rm)>0:
          sp.run(["rm"] + to_rm)
        sp.run(["mv","%s/logs/%s.%d" % (args.exp_dir,channel_name,res[idx][0]),args.exp_dir + "/logs/"+channel_name])
        to_rm = ["%s/models/%s.%d" % (args.exp_dir,channel_name,_id) for _id in idxs if _id!=res[idx][0] ]
        if len(to_rm)>0:
          sp.run(["rm"] + to_rm)
        sp.run(["mv","%s/models/%s.%d" % (args.exp_dir,channel_name,res[idx][0]),args.exp_dir+"/models/"+channel_name])
      #END-FOR
    #END-WITH


  # eval & tag
  else:
    rl = args.rl
    lm_dir = "../../lms"
    if args.comb_table:
      rl = "comb" # placeholder for combination code
      lm_dir = args.exp_dir + "/lm"

    channel_name = "%s.%s.%d.%d.comb" % (args.il,args.baseline,args.num_clusters,args.iter)
    lm_file = "%s/%s.%d.fsa.noe" % (lm_dir,rl,args.lm_order)
    wlm,wcm = args.dec_conf.split(".")
    
    test_file = "%s/data/output.%d.%s.carmel" % (args.exp_dir,args.num_clusters,args.baseline)
    
    agms = ["bash","src/code/decode.sh","-lm",lm_file,
            "-ch",channel_name,
            "-i",test_file,
            "-wlm",wlm,
            "-wcm",wcm
            ]
    pobj = sp.Popen(agms)
    while pobj.wait(): continue

    outfile     = open(args.output,'w')
    outfile_rom = open(args.output+".roman",'w')
    toks_file   = open(args.tokens,'r')
    toks_rom_file = open(args.tokens_roman,'r')
    tags_file   = open("%s.%s.%s.%s.decoded" % \
      (test_file,channel_name,wlm,wcm), 'r' )

    
    for tag_line in tags_file:
      tags = tag_line.split()
      tok_rom_line = toks_rom_file.readline().strip('\n') # raw, romanized text, always in txt format
      tok_roms = tok_rom_line.split()
    
      if args.format == 'txt':
        tok_line = toks_file.readline().strip('\n')
        ntags=[]
        for tk,tag in zip(tok_roms,tags):
          ntags.append( ground_tag(tk,tag) )
        #
        pairs = zip(tok_line.split(),ntags)
        print(" ".join(["%s/%s"%(x,y) for x,y in pairs]), file=outfile)

        pairs = zip(tok_roms,ntags)
        print(" ".join(["%s/%s"%(x,y) for x,y in pairs]), file=outfile_rom)

      elif args.format == 'bio':
        idx = 0
        while(True):
          tok_line = toks_file.readline().strip('\n')
          if tok_line=='':
            print("",file=outfile)
            break
          tk = tok_roms[idx]
          tag = ground_tag(tk,tags[idx])
          print("%s%s%s" % (tok_line,args.bio_delim,tag),file=outfile)
          idx += 1
        #
      #

    #END-FOR
