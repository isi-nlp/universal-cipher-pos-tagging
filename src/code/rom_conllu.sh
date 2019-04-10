#!/bin/bash

lang=$1
input=$2
output=$3
UR_DIR=$4

cut -f 2 $input | $UR_DIR/bin/uroman.pl -l $lang | \
awk -F'\t' '{OFS = FS} FNR==NR{a[NR]=$1;next}{$2=a[FNR]}1' \
/dev/stdin $input > temp

cut -f 3 temp | $UR_DIR/bin/uroman.pl -l $lang | \
awk -F'\t' '{OFS = FS} FNR==NR{a[NR]=$1;next}{$3=a[FNR]}1' \
/dev/stdin temp > $output

rm temp