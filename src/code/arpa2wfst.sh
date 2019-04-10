#!/bin/sh

## Transforms ARPA lm file into WFST format using Carmel

set -e 

INPUT="arpa.lang"  # arpa formatted input file
LAN_CODE="en" # language code for name-formatting purposes
ORDER=2  # LM order for name-formatting purposes
CARMEL_DIR="/usr/local"
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. >/dev/null 2>&1 && pwd )"
DATADIR=$BASEDIR/data
CODE_DIR="$BASEDIR/src/code"

while [ $# -gt 1 ]
do
key="$1"
case $key in
    -i|--input)
    INPUT="$2"
    shift # past argument
    ;;
    -l|--lang)
    LAN_CODE="$2"
    shift # past argument
    ;;
    -o|--order)
    ORDER="$2"
    shift # past argument
    ;;
    -c|--carmel)
    CARMEL_DIR="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift
done 


INPUT=$(readlink -f $INPUT)

cd $CODE_DIR
g++ makelmfsa.cpp -o makelmfsa
g++ makelmfsa_x.cpp -o makelmfsa_x


# create fsa/fst
./makelmfsa $INPUT
# ./makelmfsa_x $basedir/lms/$lang.$order.lm

$CARMEL_DIR/bin/carmel -n $INPUT.wfsa \
> $INPUT.norm

# prepare Viterbi decoding
$CARMEL_DIR/bin/carmel --project-right --project-identity-fsa -HJ $INPUT.wfsa \
> $INPUT.fsa.noe

if [ "$INPUT.wfsa" != "$BASEDIR/lms/$LAN_CODE.$ORDER.lm.wfsa" ]; then
    mv $INPUT.wfsa $BASEDIR/lms/$LAN_CODE.$ORDER.lm.wfsa
    mv $INPUT.norm $BASEDIR/lms/$LAN_CODE.$ORDER.lm.norm
    mv $INPUT.fsa.noe $BASEDIR/lms/$LAN_CODE.$ORDER.fsa.noe
fi

rm makelmfsa makelmfsa_x