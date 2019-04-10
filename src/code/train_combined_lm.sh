#!/bin/sh

set -e 


ORDER=2
TAGSET="ud"   # tagset code [ud,ut]
LAN_CODES="en"
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. >/dev/null 2>&1 && pwd )"
DATADIR=$BASEDIR/lm_data
CODE_DIR="$BASEDIR/src/code"
EXP_DIR="$BASEDIR/exp-cipher"

if [ -z "$CARMEL_DIR" ]; then
    CARMEL_DIR="/usr/local"
fi
if [ -z "$SRILM_DIR" ]; then
    SRILM_DIR="$HOME/srilm-1.7.2"
fi


while [ $# -gt 1 ]
do
key="$1"
case $key in
    -ts|--tagset)
    TAGSET="$2"
    shift # past argument
    ;;
    -ord|--order)
    ORDER="$2"
    shift # past argument
    ;;
    -l|--lang)
    LAN_CODES="$2"
    shift # past argument
    ;;
    -sri|--sridir)
    SRILM_DIR="$2"
    shift # past argument
    ;;
    -c|--carmel)
    CARMEL_DIR="$2"
    shift # past argument
    ;;
    -exp|--exp_dir)
    EXP_DIR="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift
done 

export CARMEL_DIR=$CARMEL_DIR
export SRILM_DIR=$SRILM_DIR

LAN_CODES=(${LAN_CODES//,/ })
mkdir -p $EXP_DIR/lm

cd $CODE_DIR
g++ makelmfsa.cpp -o makelmfsa
g++ makelmfsa_x.cpp -o makelmfsa_x


echo "" > temp_accum
for lang in "${LAN_CODES[@]}"; do
    cat $DATADIR/$lang/train.upos.ch >> temp_accum
done

#-addsmooth -kn  \
$SRILM_DIR/bin/i686-m64/ngram-count -text temp_accum -order $ORDER \
-addsmooth 1 \
-lm $EXP_DIR/lm/comb.$ORDER.lm
grep -vP "^$" < $EXP_DIR/lm/comb.$ORDER.lm > temp
mv temp $EXP_DIR/lm/comb.$ORDER.lm

# create fsa/fst
./makelmfsa $EXP_DIR/lm/comb.$ORDER.lm
# ./makelmfsa_x $basedir/lms/$lang.$ORDER.lm

$CARMEL_DIR/bin/carmel -n $EXP_DIR/lm/comb.$ORDER.lm.wfsa \
> $EXP_DIR/lm/comb.$ORDER.lm.norm

# prepare Viterbi decoding
$CARMEL_DIR/bin/carmel --project-right --project-identity-fsa -HJ $EXP_DIR/lm/comb.$ORDER.lm.wfsa \
> $EXP_DIR/lm/comb.$ORDER.fsa.noe


rm makelmfsa makelmfsa_x