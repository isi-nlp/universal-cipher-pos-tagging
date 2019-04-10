#!/bin/sh

set -e 

UD_DIR="$HOME/ud-treebanks-v2.2"
ORDER=2
TAGSET="ud"   # tagset code [ud,ut]
LAN_CODES="en"
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DATADIR=$BASEDIR/lm_data
CODE_DIR="$BASEDIR/src/code"


if [ -z "$CARMEL_DIR"]; then
    CARMEL_DIR="/usr/local"
fi
if [ -z "$SRILM_DIR" ]; then
    SRILM_DIR="$HOME/srilm-1.7.2"
fi


while [ $# -gt 1 ]
do
key="$1"
case $key in
    -td|--tb_dir)
    UD_DIR="$2"
    shift # past argument
    ;;
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
    -carmel|--carmel)
    CARMEL_DIR="$2"
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

cd $CODE_DIR

g++ makelmfsa.cpp -o makelmfsa
g++ makelmfsa_x.cpp -o makelmfsa_x


LAN_CODES=(${LAN_CODES//,/ })

for lang in "${LAN_CODES[@]}"; do
    echo ""
    echo "Lang: $lang"
    mkdir -p $BASEDIR/lms/
    mkdir -p $DATADIR/$lang
    
    suf=""
    if [ $lang = "ja" ]||[ $lang = "ar" ]; then
        suf=".all"
    fi

    python3 conllu2txt.py -i $DATADIR/$lang/train.conllu$suf \
    -m ch -c 3 -tb $TAGSET > $DATADIR/$lang/train.upos.ch

    python3 conllu2txt.py -i $DATADIR/$lang/train.conllu$suf \
    -m tag -c 3 -tb $TAGSET > $DATADIR/$lang/train.upos

    # run LM 
    #-addsmooth -kn  \
    $SRILM_DIR/bin/i686-m64/ngram-count -text $DATADIR/$lang/train.upos.ch -order $ORDER \
    -addsmooth 1 \
    -lm $BASEDIR/lms/$lang.$ORDER.lm
    grep -vP "^$" < $BASEDIR/lms/$lang.$ORDER.lm > temp
    mv temp $BASEDIR/lms/$lang.$ORDER.lm

    # create fsa/fst
    ./makelmfsa $BASEDIR/lms/$lang.$ORDER.lm
    # ./makelmfsa_x $basedir/lms/$lang.$ORDER.lm

    $CARMEL_DIR/bin/carmel -n $BASEDIR/lms/$lang.$ORDER.lm.wfsa \
    > $BASEDIR/lms/$lang.$ORDER.lm.norm

    # prepare Viterbi decoding
    $CARMEL_DIR/bin/carmel --project-right --project-identity-fsa -HJ $BASEDIR/lms/$lang.$ORDER.lm.wfsa \
    > $BASEDIR/lms/$lang.$ORDER.fsa.noe
    
done


rm makelmfsa makelmfsa_x