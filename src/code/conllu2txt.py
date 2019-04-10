import sys
from utils import *
import pdb
import argparse


if __name__ == "__main__":
  parser = argparse.ArgumentParser() 
  parser.add_argument("--input","-i", type=str, default=None, help="input conllu file")
  parser.add_argument("--mode" ,"-m", type=str, default="ch", help="Tag mode [ch,tag]")
  parser.add_argument("--col"  ,"-c", type=int, default=1, help="Column to extract [0-9]")
  parser.add_argument("--tb"   ,"-tb", type=str, default="ud", help="Treebank name [ud,ut]")
  parser.add_argument("--lid","-lid", action='store_true', help="Keep lang_id from text")

  args = parser.parse_args()

  text=""
  idx = args.col
  mode = args.mode

  mapper = upos2char if args.tb=="ud" else ut2char

  count = 1

  for line in open(args.input,'r'):
    line = line.strip("\n")
    if line=='': continue
    cols = line.split('\t')
    if cols[0]=="1" and text!='':
      print(text.strip(' '))
      text=''
      count = 1
    token = ''
    datum = cols[idx]
    if idx==1 and not args.lid:
      datum = datum[:-3]

    if mode=='ch' and idx==3:
      datum = mapper[datum]
    
    token = datum.strip(' ')

    all_dig = True
    for sw in token.split(' '):
      if not sw.isdigit():
        all_dig=False
        break
    token = token.replace(" ","") if all_dig else token.replace(" ","_")
    text += " "+token

    # print("|",token,"|")
    count += 1

  print(text.strip(' '))


