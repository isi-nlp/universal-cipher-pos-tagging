#!/bin/bash

set -e

# POSIX variable
OPTIND=1

NCPUS=4
BASELINE="brown" # clark, anchor, emb-loc-mon
NCLUSTERS=500

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. >/dev/null 2>&1 && pwd )"
EXP_DIR="$BASEDIR/exp-cipher"

while [ $# -gt 1 ]
do
key="$1"
case $key in
    -i|--input)
    INPUT="$2"
    shift # past argument
    ;;    
    -b|--b|--baseline)
    BASELINE="$2"
    shift # past argument
    ;;
    -nj|--njobs)
    NCPUS="$2"
    shift # past argument
    ;;
    -nc|--nclusters)
    NCLUSTERS="$2"
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


clt_out="$EXP_DIR/$BASELINE-$NCLUSTERS"
mkdir -p $clt_out


## run clustering algorithm

if [ $BASELINE = "brown" ]; then
    if [ ! -d "$BASEDIR/src/brown" ]; then
        ln -s "$BASEDIR/src/brown-cluster" "$BASEDIR/src/brown"
    fi

    src/brown/wcluster --text $INPUT \
            --threads $NCPUS --c $NCLUSTERS --rand 42 \
            --output_dir $clt_out
    mv $clt_out/paths $clt_out/clusters.brown
fi


if [ $BASELINE = "marlin" ]; then
    src/marlin/marlin_count --text $INPUT \
    --bigrams $clt_out/bigrams --words $clt_out/words --rank-limit -1
    
    $model_dir/marlin_cluster --bigrams $clt_out/bigrams --words $clt_out/words \
    --output $clt_out/clusters --rand 42 --c $NCLUSTERS --alpha 0.0 2> $clt_out/log
fi

