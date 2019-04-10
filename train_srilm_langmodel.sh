#!/bin/sh

set -e 

ORDER=2
INPUT="file.pos"
TAGSET="ud"   # tagset code [ud,ut]
LAN_CODE="en"
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
    -i|--input)
    INPUT="$2"
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
    LAN_CODE="$2"
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


echo ""
echo "Lang: $LAN_CODE"
mkdir -p $BASEDIR/lms/
mkdir -p $DATADIR/$LAN_CODE

cp $INPUT $DATADIR/$LAN_CODE/train.upos
python3 src/code/pos2char.py -ts $TAGSET < $INPUT > $DATADIR/$LAN_CODE/train.upos.ch

# run LM 
#-addsmooth -kn  \
$SRILM_DIR/bin/i686-m64/ngram-count -text $DATADIR/$LAN_CODE/train.upos.ch -order $ORDER \
-addsmooth 1 \
-lm $BASEDIR/lms/$LAN_CODE.$ORDER.lm
grep -vP "^$" < $BASEDIR/lms/$LAN_CODE.$ORDER.lm > temp
mv temp $BASEDIR/lms/$LAN_CODE.$ORDER.lm


# create fsa/fst
./makelmfsa $BASEDIR/lms/$LAN_CODE.$ORDER.lm

$CARMEL_DIR/bin/carmel -n $BASEDIR/lms/$LAN_CODE.$ORDER.lm.wfsa \
> $BASEDIR/lms/$LAN_CODE.$ORDER.lm.norm

# prepare Viterbi decoding
$CARMEL_DIR/bin/carmel --project-right --project-identity-fsa -HJ $BASEDIR/lms/$LAN_CODE.$ORDER.lm.wfsa \
> $BASEDIR/lms/$LAN_CODE.$ORDER.fsa.noe