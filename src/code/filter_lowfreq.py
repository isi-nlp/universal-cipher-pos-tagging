import os,sys
import argparse
from collections import Counter
import re
import pdb

filters_detailed = [
  ("url" , [re.compile(r'^https?[:/]{1,3}(www\.)?[a-z]+(\.?[a-z]+\/?)+.*?$',re.UNICODE),
            re.compile(r'^[wW]{3}\.[a-zA-Z]+(\.?[A-Z]+\/?)+.*?$',re.UNICODE),
            re.compile(r'^([a-zA-Z][^@])[a-zA-Z.]+\.com$',re.UNICODE),
             ]),
  ('email', [re.compile(r'^[-a-zA-Z0-9_.]+\@([a-zA-Z0-9]+\.)+[a-zA-Z]+$',re.UNICODE) ]),
  ("00:00"           , [re.compile(r'[0-9](:[0-9]{2})+',re.UNICODE),
                         re.compile(r'[0-9](:[0-9]{2})*[aApP][mM]$',re.UNICODE),
                         re.compile(r'[0-9]hour$',re.UNICODE),] ),
  ("00km", [re.compile(r'[0-9]km$',re.UNICODE)]),
  ("00kg", [re.compile(r'[0-9]kg$',re.UNICODE)]),
  ("haha", [re.compile(r'^haha$',re.UNICODE),
            re.compile(r'^wkwk$',re.UNICODE)]),

]

filters = [
  ("snUser"           , [re.compile(r'^[@]([0-9]*[-a-zA-Z._]+[0-9]*[!?]?)+$',re.UNICODE)] ),
  ("hashTag"          , [re.compile(r'^[#][-a-zA-Z._]{3,}[0-9]*[!?]?$',re.UNICODE),
                         re.compile(r'^[#][0-9]+[-a-zA-Z._]{3,}[!?]?$',re.UNICODE),
                         re.compile(r'^[#][0-9]+[-a-zA-Z._]{3,}[0-9]+[!?]?$',re.UNICODE), ]),
  ("twoDigitNum"      , [re.compile(r'^[0-9]{2}$',re.UNICODE)] ),
  ("fourDigitNum"     , [re.compile(r'^[0-9]{4}$',re.UNICODE)] ),
  ("hasDigitAndAlpha" , [re.compile(r'[0-9].*[a-zA-Z]',re.UNICODE) ,
                         re.compile(r'[a-zA-Z].*[0-9]',re.UNICODE) ]) ,
  ("hasDigitAndDash"  , [re.compile(r'[0-9]-[0-9]',re.UNICODE)] ),
  ("hasDigitAndSlash" , [re.compile(r'[0-9]/[0-9]',re.UNICODE)] ),
  ("hasDigitAndComma" , [re.compile(r'[0-9],[0-9]',re.UNICODE)] ),
  ("hasDigitAndPeriod" , [re.compile(r'[0-9][.][0-9]',re.UNICODE)] ),
  ("isHour"           , [re.compile(r'[0-9]:[0-9]',re.UNICODE),
                         re.compile(r'[0-9][aApP][mM]$',re.UNICODE)] ),
  ("othernum"         , [re.compile(r'^[0-9]+$',re.UNICODE)] ),
  ("allCaps"          , [re.compile(r'^[A-Z]+$',re.UNICODE)] ),
  ("capPeriod"        , [re.compile(r'^[A-Z][.]$',re.UNICODE)] ),
  ("initCap"          , [re.compile(r'^[A-Z][a-z]+$',re.UNICODE)] ),
  ("lowercase"        , [re.compile(r'^[a-z]$',re.UNICODE)] ),
]

is_prob_word = re.compile(r"^([a-zA-Z]+[-._',&]?)+$",re.UNICODE)


def get_filter_tag(word,filter_list):
  for tag,reg_list in filter_list:
    for reg in reg_list:
      if reg.search(word)!=None:
        return tag
  return word





if __name__ == "__main__":
  parser = argparse.ArgumentParser() 
  #parser.add_argument("--l","-l", type=str, help="Language -aaa-")
  parser.add_argument("--input","-i", type=str, help="Input file")
  parser.add_argument("--mode","-m", type=str, default="train", help="Mode [train,eval]")
  parser.add_argument("--vocab","-v", type=str, default=None, help="Filtered vocabulary")
  parser.add_argument("--thr","-t", type=int, default=3, help="Cut-off threshold")
  #parser.add_argument("--sent_len","-sl", type=int, default=190, help="Filter threshold for long sentences")
  parser.add_argument("--dom","-d", type=str, default=None, help="Test domain (valid only for outd exps)")
  parser.add_argument("--aggr","-aggr", action='store_true', help="Perform aggresive filtering (threshold oriented)")
  parser.add_argument("--ign_emp","-ig", action='store_true', help="Ignore empty lines/sentences.")
  parser.add_argument("--lower","-low", action='store_true', help="Lowercase all text")
  args = parser.parse_args()

  vocab = set()

  # load input
  data = open(args.input,'r').read().split('\n')
  data = [line for line in data]
  if data[-1] == '': data = data[:-1]

  ### aggressive filtering mode
  
  ## train mode
  # create vocabulary
  if args.mode == "train":
    vocab = Counter()
    for sent in data:
      if sent=='': continue
      if args.lower: sent = sent.lower()
      vocab.update(sent.split(' '))
    filt = []
    count = 0

    for x,y in vocab.most_common():
      # if aggresive, evth below threshold is ignored
      if y<=args.thr and args.aggr:
        break
      if len(x)>40:
        continue
      # if not aggressive, evth be;pw thre that is not a word is ignored
      if y<=args.thr and is_prob_word.search(x)==None:
        continue

      # all possible urls, email and hours are ignored
      if get_filter_tag(x,filters_detailed)!=x:
        continue
      filt.append([x,y])
      if count%100000 == 0:
        print('->',count)
      count += 1
    #filt = [[x,y] for x,y in vocab.most_common() if y>args.thr]
    dom_pref = '' if args.dom==None else '.'+args.dom
    vocab_fn = os.path.join(os.path.dirname(args.input),"vocab"+dom_pref)
    open(vocab_fn,'w').write('\n'.join(["%s\t%d" % (w,f) for w,f in filt]) + '\n')
    vocab = set([x for x,y in filt])

    del filt

  # eval mode
  # load vocabulary
  else:
    if args.vocab==None:
      print("Error: Filtered vocabulary file not specified!\nCheck arguments list with -h option")
      sys.exit(1)
    elif not os.path.exists(args.vocab):
      print("Error: Filtered vocabulary file does not exist!")
      sys.exit(1)  
    else:
      for line in open(args.vocab,'r'):
        line = line.strip('\n').strip(' ')
        if line=='': continue
        w,f = line.split('\t')
        vocab.add(w)
    #
  #END-IF-MODE
  
  outfile = open(args.input+".filt",'w')
  count = 0

  # filter data
  for sent in data:
    if sent=='' and not args.ign_emp:
      print('',file=outfile)
      continue

    new_sent = []
    if args.lower:
      sent = sent.lower()
    sent_tok = sent.split(' ')
    #if args.ign_emp and len(sent_tok)>args.sent_len-1:
    #  continue
    for word in sent_tok:
      if word in vocab:
        new_sent.append(word)
      else:
        tag = get_filter_tag(word,filters_detailed)
        if tag!=word:
          new_sent.append(tag)
          continue
        tag = get_filter_tag(word,filters)
        if tag==word:
          tag = 'unk'
        new_sent.append("<"+tag+">")
      #END-IF-VOCAB
    #END-FOR-W
    new_sent.append("#eos")
    print(' '.join(new_sent),file=outfile)

    if count % 100000 == 0:
      print("->",count)
    count+=1
  #END-FOR-SENT






