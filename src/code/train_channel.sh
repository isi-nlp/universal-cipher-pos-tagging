#!/bin/bash

set -e


NC=50
ORD=3
RL="en"
IL="en"
ID=1
SEED=42
ITERS=10
IS_ELISA="-"
CA="" # clustering algorithm

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. >/dev/null 2>&1 && pwd )"
CODE_DIR="$BASEDIR/src/code"
# CARMEL_DIR defined above pipeline


echo $CODE_DIR


while [ $# -gt 1 ]
do
key="$1"
case $key in
    -c|--nc|--num_clusters)
    NC="$2"
    shift # past argument
    ;;
    -o|--order)
    ORD="$2"
    shift # past argument
    ;;
    -rl)
    RL="$2"
    shift # past argument
    ;;
    -il)
    IL="$2"
    shift # past argument
    ;;
    -id)
    ID="$2"
    shift # past argument
    ;;
    -s|--seed)
    SEED="$2"
    shift # past argument
    ;;
    -it|--iters)
    ITERS="$2"
    shift # past argument
    ;;
    -elisa|--elisa)
    IS_ELISA="$2"
    shift # past argument
    ;;
    -ca|--ca)
    CA="$2"
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


carmel="$CARMEL_DIR/bin/carmel"
data_dir="$EXP_DIR/data"

channel="$RL$ORD-$IL.$CA.$NC.$ITERS.$ID"

bash $CODE_DIR/create_fst.sh $NC > $EXP_DIR/models/$channel

$carmel -1 -R $SEED $EXP_DIR/models/$channel > $EXP_DIR/models/$channel.rnd
$carmel -HJn $EXP_DIR/models/$channel.rnd    > $EXP_DIR/models/$channel.norm
rm $EXP_DIR/models/$channel.rnd

cp $BASEDIR/lms/$RL.$ORD.lm.wfsa $EXP_DIR/models/$channel.lm

# head -10 $data_dir/$IL/$train_pref.$NC.$CA.carmel > $EXP_DIR/logs/$channel.in
# $EXP_DIR/logs/$channel.in $EXP_DIR/models/$channel.lm \

echo ":: $data_dir/output.$NC.$CA.carmel.10k"
echo ":: $channel"

# # train the channel model
$carmel --train-cascade -HJa -1 -M $ITERS -R $SEED -X 0.999999 \
$data_dir/output.$NC.$CA.carmel.10k \
$EXP_DIR/models/$channel.lm $EXP_DIR/models/$channel.norm \
2> $EXP_DIR/logs/$channel

mv $EXP_DIR/models/$channel.norm.trained $EXP_DIR/models/$channel

#rm $EXP_DIR/logs/$channel.in 
rm $EXP_DIR/models/$channel.norm \
$EXP_DIR/models/$channel.lm $EXP_DIR/models/$channel.lm.trained
