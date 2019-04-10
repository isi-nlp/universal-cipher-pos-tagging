#!/bin/bash

nclusters=$1
tagset="N O A R I B C J D T M F P E Y V X"
nc1=$(($nclusters - 1))

echo "S"
echo '(S (S "<s>" "<s>" 1))'
echo '(S (S "</s>" "</s>" 1))'
for tag in $tagset
do
    for nc in `seq 0 $nc1`
    do
        echo '(S (S "'$tag'" "'$nc'" 1))'
    done
done