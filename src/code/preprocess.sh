#!/bin/bash

# preprocessing data

set -e

INPUT=""
ROM="false"
MODE="test"
IL="en"

EXP_DIR="$BASEDIR/exp-cipher"

while [ $# -gt 1 ]
do
key="$1"
case $key in
    -i|--input)
    INPUT="$2"
    shift # past argument
    ;;
    -rom|--rom)
    ROM="$2"
    shift # past argument
    ;;
	-m|--mode)
    MODE="$2"
    shift # past argument
    ;;
	-l|--lang)
    IL="$2"
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

datadir="$EXP_DIR/data"

# romanize if needed
if [ $ROM = "true" ]; then
    echo "romanizing"
    src/uroman/bin/uroman.pl < $INPUT > "$INPUT".roman
else
    cp $INPUT "$INPUT".roman
fi

echo "cleaning/filtering..."
#normalize / filter noise

src/code/replace-unicode-punctuation.perl < "$INPUT".roman > $datadir/$IL.clean

if [ $MODE = "train" ]; then
	python3 src/code/filter_lowfreq.py -i $datadir/$IL.clean -m train -ig
	mv $datadir/vocab $datadir/vocab.$IL
else
	python3 src/code/filter_lowfreq.py -i $datadir/$IL.clean -m eval -t 1 -v $datadir/vocab.$IL
fi

