#!/bin/bash
set -e

LM="lm_fst_file"
CHANNEL=""
INPUT=""
MAX_LINES=20000
DEC_CH="False"
W_LM=1
W_CM=1

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. >/dev/null 2>&1 && pwd )"
CODE_DIR="$BASEDIR/src/code"

while [ $# -gt 1 ]
do
key="$1"
case $key in
    -lm|--lm)
    LM="$2"
    shift # past argument
    ;;
    -ch|--channel)
    CHANNEL="$2"
    shift # past argument
    ;;
    -i|--input)
    INPUT="$2"
    shift # past argument
    ;;
    -max|--max)
    MAX_LINES="$2"
    shift # past argument
    ;;
    -wlm|--wlm)
    W_LM="$2"
    shift # past argument
    ;;
    -wcm|--wcm)
    W_CM="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift
done 


carmel="$CARMEL_DIR/bin/carmel"
data_dir="$EXP_DIR/data"
basedir="build"

mkdir -p $EXP_DIR/models/

awk 'NF>0' $INPUT > $EXP_DIR/logs/$CHANNEL.temp.noe.cmpl
mv $EXP_DIR/logs/$CHANNEL.temp.noe.cmpl $EXP_DIR/logs/$CHANNEL.temp.noe

# decipher with Viterbi decoding
# head -10 $EXP_DIR/logs/$CHANNEL.temp.noe | \
if [ $W_LM = 0 ]; then
    cat $EXP_DIR/logs/$CHANNEL.temp.noe | \
    $carmel -qbsriWIEk 1 --exponents=$W_CM,1 \
    $EXP_DIR/models/$CHANNEL \
    > $EXP_DIR/logs/$CHANNEL.$W_LM.$W_CM.temp.dec 2> $EXP_DIR/logs/$CHANNEL.$W_LM.$W_CM.dec
else
    cat $EXP_DIR/logs/$CHANNEL.temp.noe | \
    $carmel -qbsriWIEk 1 --exponents=$W_LM,$W_CM,1 \
    $LM $EXP_DIR/models/$CHANNEL \
    > $EXP_DIR/logs/$CHANNEL.$W_LM.$W_CM.temp.dec 2> $EXP_DIR/logs/$CHANNEL.$W_LM.$W_CM.dec
fi

python3 $CODE_DIR/clean_map_decode.py $EXP_DIR/logs/$CHANNEL.$W_LM.$W_CM.temp.dec $INPUT.$CHANNEL.$W_LM.$W_CM.decoded
rm $EXP_DIR/logs/$CHANNEL.$W_LM.$W_CM.temp.dec
rm $EXP_DIR/logs/$CHANNEL.temp.noe
