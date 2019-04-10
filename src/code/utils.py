import pickle
from sklearn.metrics import classification_report,\
                            accuracy_score, v_measure_score, \
                            precision_score, recall_score, f1_score
from collections import defaultdict, Counter
import subprocess as sp
import unicodedata
import pdb
import pickle
import sys
sys.path.append("cpos")

# UDv2 & UTv2 support
upos2char = {
  "NOUN"  :'N',
  "PROPN" :'O',
  "ADJ" :'A',
  "ADV" :'R',
  "ADP" :"I",
  "AUX" :"B",
  "CCONJ" :"C",
  "SCONJ" :"J",
  "DET" :"D",
  "INTJ"  :'T',
  "NUM" :"M",
  "PART"  :"F",
  "PRON"  :"P",
  "PUNCT" :"E",
  "SYM" :"Y",
  "VERB"  :"V",
  "X"   :"X",
}


char2upos = {v:k for k,v in upos2char.items() }

ut2char = {
  "NOUN"  :'N',
  "PROPN" :'O',
  "ADJ" :'A',
  "ADV" :'R',
  "ADP" :"I",
  "AUX" :"B",
  "CONJ" :"C",
  "DET" :"D",
  "INTJ"  :'T',
  "NUM" :"M",
  "PRT"  :"F",
  "PRON"  :"P",
  "." :"E",
  "SYM" :"Y",
  "VERB"  :"V",
  "X"   :"X",
}

char2ut = {v:k for k,v in ut2char.items() }


MAX_LINES_DECODE=20000
# MAX_LINES_DECODE=10

mapper = {
  'en' : ['en','fr','de','es','it','ar','ja','cs','ru','sw-hcs'],
  'fr' : ['fr','de','es','ja','ar','it','en','cs','ru','sw-hcs'],
  'fa' : ['fa','fr','de,''es','ja','cs','ar','it','en','ru','sw-hcs'],
  'sw-hcs' : ['sw-hcs','de','fr','es','ja','ar', 'it','en','cs','ru'],
  #'tl-elisa' : ['id','fr','es','ja','it','en','cs','ru','sw-hcs'],
  #'tl-elisa' : ['fr','es','ja','it','en','cs','ru','sw-hcs'],
  'si-elisa' : ['de','fr','es','ja','ar', 'it','en','cs','ru','sw-hcs'],
  'rw-elisa' : ['de','fr','es','ja','ar', 'it','en','cs','ru','sw-hcs']
}

default_rls = ['en','de','fr','es','it','ja','ar','cs','ru','sw-hcs']


def saveObject(obj, name='model'):
  with open(name + '.pickle', 'wb') as fd:
    pickle.dump(obj, fd, protocol=pickle.HIGHEST_PROTOCOL)


def uploadObject(obj_name):
  # Load tagger
  with open(obj_name, 'rb') as fd:
    obj = pickle.load(fd)
  return obj


def test_punct(token):
  for c in token:
    if unicodedata.category(c)[0] != 'P':
      return False
  return True


def test_num(token):
  for c in token:
    if unicodedata.category(c)[0] != 'N':
      return False
  return True


def ground_tag(tk,tag,pos_tagset="ud"):
  mapper = char2ut if pos_tagset=="ut" else char2upos
  if tk.isdigit() or test_num(tk):
    return mapper["M"]
  else:
    is_punct = test_punct(tk)
    # false negatives
    if is_punct:
      return mapper["E"]
    # false positives
    elif tag==mapper["E"] and not is_punct:
      return "X"
    # the rest
    return tag


def evaluate_core(gold_fn,pred_fn):
  gold,pred = [],[]
  count = 1
  gls = []
  for line in open(gold_fn,'r'):
    gold.extend(line.strip('\n').split(' '))
    gls.append(line.strip('\n').split(' '))
    if count>=MAX_LINES_DECODE:
      break
    count += 1
  count = 0
  for line in open(pred_fn,'r'):
    pline = line.strip('\n').split(' ')
    pred.extend(pline)
    if len(pline)!= len(gls[count]):
      print("->",count,len(gls[count]), len(pline))
      print(gls[count])
      print(pline)
      print("-"*50)
      pdb.set_trace()
    count += 1
  return gold,pred


def evaluate(gold_fn,pred_fn,report=True):
  gold,pred = evaluate_core(gold_fn,pred_fn)

  acc = accuracy_score(gold,pred)
  if report:
    print("ACC: %.4f" % acc )
    print("VM : %.4f" % v_measure_score(gold,pred))
    print(classification_report(gold,pred,digits=4))
  return acc

def evaluate_all_metrics(gold_fn,pred_fn):
  gold,pred = evaluate_core(gold_fn,pred_fn)
  acc = accuracy_score(gold,pred)
  p = precision_score(gold,pred)
  r = recall_score(gold,pred)
  f1 = f1_score(gold,pred)
  support = Counter(gold)




def eval_lexicon(lexicon_fn,pred_fn,words_fn,report=True):
  # read lexicon
  lexicon = defaultdict(set)
  for line in open(lexicon_fn,'r'):
    line= line.strip('\t')
    if line=='': continue
    w,pos,_ = line.split("\t")
    if pos=='PRT': pos = 'PART'
    lexicon[w].add(pos)

  # read pred file
  gold,pred = [],[]
  pred_vocab = defaultdict(set)
  predpos_lines = open(pred_fn,'r').read().strip('\n').split('\n')
  word_lines = open(words_fn,'r').read().strip('\n').split('\n')
  for wform_line,pred_line in zip(word_lines,predpos_lines):
    wforms = wform_line.lower().split(" ")[:-1]
    ptags = pred_line.split(" ")
    for w,pos in zip(wforms,ptags):
      if w not in lexicon: continue
      pred_vocab[w].add(pos)
  #

  #compare
  correct = 0.0
  for w,pred_pos_list in pred_vocab.items():
    if len(pred_pos_list & lexicon[w])>0:
      correct += 1
  acc = correct / len(pred_vocab)
  if report:
    print("ACC: %.4f" % acc )
    print("Inters. size: ",len(pred_vocab) )
  return acc


def get_ppl(channel,wlm,wcm):
  fn = 'logs/%s.%d.%d.dec' % (channel,wlm,wcm)

  lines = open(fn,'r').read().strip('\n').split('\n')
  
  idx = lines[-1].rfind("^")
  pl_sc = float(lines[-1][idx+1:].strip(' '))

  tmp = lines[-1][:idx]
  idx = tmp.rfind("^")
  idx2 = tmp.rfind(" ")
  pt_sc = float(tmp[idx+1:idx2].strip(' '))

  return pl_sc,pt_sc


def decoder_acc(channel,conf,wlm,wcm):
  rl,order,il,c_alg,cl,IS_ELISA = conf.split('.')
  IS_ELISA = bool(int(IS_ELISA))
  lm_file = "lms/%s.%s.fsa.noe" % (rl,order)
  acc = 0.0
    
  # cases     sw si           ta tl
  if IS_ELISA:
    test_file = "data/%s/test.elisa.%s.carmel" % (il,cl) if c_alg=="br" else \
          "data/%s/test.elisa.%s.%s.carmel" % (il,cl,c_alg)
    test_wf_file = "data/%s/test.elisa.true.filt" % (il)
    lexicon_fn = "data/%s/lexicon.elisa" % (il)

    agms = ["sh","decode.sh","-lm",lm_file,
        "-ch",channel,
        "-i",test_file,
        "-wlm",str(wlm),
        "-wcm",str(wcm)
        ]
    pobj = sp.Popen(agms)
    while pobj.wait(): continue

    acc = eval_lexicon(lexicon_fn, '%s.%s.%d.%d.decoded' % (test_file,channel,wlm,wcm),test_wf_file,False)

  else:
    test_file = "data/%s/test.%s.carmel" % (il,cl) if c_alg=="br" else \
          "data/%s/test.%s.%s.carmel" % (il,cl,c_alg)
    goldfn = "data/%s/test.upos" % (il)

    agms = ["sh","decode.sh","-lm",lm_file,
        "-ch",channel,
        "-i",test_file,
        "-wlm",str(wlm),
        "-wcm",str(wcm)
        ]
    pobj = sp.Popen(agms)
    while pobj.wait(): continue

    # if args.dec_ch:
    acc = evaluate(goldfn,'%s.%s.%d.%d.decoded' % (test_file,channel,wlm,wcm),False)

  return acc


def post_process(tk_rom_fn, dec_fn,out_fn,pos_tagset="ud"):
  outfile     = open(out_fn,'w')
  toks_rom_file = open(tk_rom_fn,'r')
  tags_file   = open(dec_fn,'r')
  
  for tag_line in tags_file:
    tags = tag_line.split()
    tok_rom_line = toks_rom_file.readline().strip('\n') # raw, romanized text, always in txt format
    tok_roms = tok_rom_line.split()

    ntags=[]
    for tk,tag in zip(tok_roms,tags):
      ntags.append( ground_tag(tk,tag,pos_tagset) )
    #
    # what if carmel could not decode input? fallback to all nouns
    if ntags==[]:
      ntags = ["NOUN"]*len(tok_roms)

    print(" ".join(ntags), file=outfile)


  #END-FOR