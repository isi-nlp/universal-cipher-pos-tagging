import sys
from utils import *
import pdb
import argparse


if __name__ == "__main__":
  parser = argparse.ArgumentParser() 
  parser.add_argument("--ts"   ,"-ts", type=str, default="ud", help="Tagset name [ud,ut]")

  args = parser.parse_args()

  mapper = upos2char if args.ts=="ud" else ut2char

  for line in sys.stdin:
    line = line.strip("\n")
    if line=='': continue
    mapped = [mapper[tag] for tag in line.split(" ") ]
    print(" ".join(mapped))

    


