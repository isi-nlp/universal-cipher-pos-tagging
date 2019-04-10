#!/bin/sh
#SBATCH --time=50:00:00
#SBATCH --partition=isi

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. >/dev/null 2>&1 && pwd )"
BASELINE="brown"
NCLUSTERS=500
INPUT=""
EXP_DIR="$BASEDIR/exp-cipher"

while getopts "h?b:n:i:e:" opt; do
    case "$opt" in
    h|\?)
        show_help
        exit 0
        ;;
    b)  BASELINE=$OPTARG
        ;;
    n)  NCLUSTERS=$OPTARG
        ;;
    i)  INPUT=$OPTARG
        ;;
    e)
        EXP_DIR=$OPTARG
        ;;
    esac
done

clt_out="$EXP_DIR/$BASELINE-$NCLUSTERS"

if [ ! -f $clt_out/clt.mapper.pickle ]; then
    python3 $BASEDIR/src/code/tag_text.py -i $INPUT \
    -b $BASELINE -m train -c $clt_out/clusters.$BASELINE -op output -nc $NCLUSTERS
else
    python3 $BASEDIR/src/code/tag_text.py -i $INPUT \
    -b $BASELINE -m eval -v $clt_out/clt.mapper.pickle -op output -nc $NCLUSTERS
fi
