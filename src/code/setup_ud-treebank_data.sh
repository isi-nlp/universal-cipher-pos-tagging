#!/bin/sh

set -e


BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../.. >/dev/null 2>&1 && pwd )"
CODE_DIR="$BASEDIR/src/code"
UR_DIR="$BASEDIR/src/uroman"
UD_DIR="$HOME/ud-treebanks-v2.2"
data_dir=$BASEDIR/lm_data

# format UD
langs="en da nl de fr it es pt ja cs ru pl ar fa id hi"


while [ $# -gt 1 ]
do
key="$1"
case $key in
    -td|--tb_dir) # treebank directory
    UD_DIR="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift
done 


########################################################################################


for lang in $langs; do
	mkdir -p $data_dir/$lang;
done

split="train"
# english treebanks
cat $UD_DIR/UD_English-EWT/en_ewt-ud-$split.conllu \
$UD_DIR/UD_English-GUM/en_gum-ud-$split.conllu \
$UD_DIR/UD_English-LinES/en_lines-ud-$split.conllu \
$UD_DIR/UD_English-ParTUT/en_partut-ud-$split.conllu \
> $data_dir/en/$split.conllu

# Danish
cp $UD_DIR/UD_Danish-DDT/da_ddt-ud-$split.conllu \
$data_dir/da/$split.conllu

# Dutch
cat $UD_DIR/UD_Dutch-Alpino/nl_alpino-ud-$split.conllu \
$UD_DIR/UD_Dutch-LassySmall/nl_lassysmall-ud-$split.conllu \
> $data_dir/nl/$split.conllu

# german
cp $UD_DIR/UD_German-GSD/de_gsd-ud-$split.conllu \
$data_dir/de/$split.conllu


# french treebanks
cat $UD_DIR/UD_French-GSD/fr_gsd-ud-$split.conllu \
$UD_DIR/UD_French-ParTUT/fr_partut-ud-$split.conllu \
$UD_DIR/UD_French-Sequoia/fr_sequoia-ud-$split.conllu \
$UD_DIR/UD_French-Spoken/fr_spoken-ud-$split.conllu \
> $data_dir/fr/$split.conllu

# spanish
cat $UD_DIR/UD_Spanish-AnCora/es_ancora-ud-$split.conllu \
$UD_DIR/UD_Spanish-GSD/es_gsd-ud-$split.conllu \
> $data_dir/es/$split.conllu

# italian
cat $UD_DIR/UD_Italian-ISDT/it_isdt-ud-$split.conllu \
$UD_DIR/UD_Italian-ParTUT/it_partut-ud-$split.conllu \
$UD_DIR/UD_Italian-PoSTWITA/it_postwita-ud-$split.conllu \
> $data_dir/it/$split.conllu

# portuguese
cat $UD_DIR/UD_Portuguese-Bosque/pt_bosque-ud-$split.conllu \
$UD_DIR/UD_Portuguese-GSD/pt_gsd-ud-$split.conllu \
> $data_dir/pt/$split.conllu


# japanese
cat $UD_DIR/UD_Japanese-GSD/ja_gsd-ud-$split.conllu \
$UD_DIR/UD_Japanese-BCCWJ/ja_bccwj-ud-$split.conllu \
> $data_dir/ja/$split.conllu.all

cat $UD_DIR/UD_Japanese-GSD/ja_gsd-ud-$split.conllu \
> $data_dir/ja/$split.conllu


# czech
cat $UD_DIR/UD_Czech-PDT/cs_pdt-ud-$split.conllu \
$UD_DIR/UD_Czech-CAC/cs_cac-ud-$split.conllu \
$UD_DIR/UD_Czech-FicTree/cs_fictree-ud-$split.conllu \
> $data_dir/cs/$split.conllu

# russian
cat $UD_DIR/UD_Russian-GSD/ru_gsd-ud-$split.conllu \
$UD_DIR/UD_Russian-SynTagRus/ru_syntagrus-ud-$split.conllu \
$UD_DIR/UD_Russian-Taiga/ru_taiga-ud-$split.conllu \
> $data_dir/ru/$split.conllu

# polish
cat $UD_DIR/UD_Polish-LFG/pl_lfg-ud-$split.conllu \
$UD_DIR/UD_Polish-SZ/pl_sz-ud-$split.conllu \
> $data_dir/pl/$split.conllu


# arabic
cat $UD_DIR/UD_Arabic-PADT/ar_padt-ud-$split.conllu \
$UD_DIR/UD_Arabic-NYUAD/ar_nyuad-ud-$split.conllu \
> $data_dir/ar/$split.conllu.all

cat $UD_DIR/UD_Arabic-PADT/ar_padt-ud-$split.conllu \
> $data_dir/ar/$split.conllu

# persian
cp $UD_DIR/UD_Persian-Seraji/fa_seraji-ud-$split.conllu \
$data_dir/fa/$split.conllu


# Indonesian
cp $UD_DIR/UD_Indonesian-GSD/id_gsd-ud-$split.conllu \
$data_dir/id/$split.conllu

# hindi
cp $UD_DIR/UD_Hindi-HDTB/hi_hdtb-ud-$split.conllu \
$data_dir/hi/$split.conllu


for lang in $langs; do
	echo "lang- split :: $lang - $split"
	grep -v "^#" $data_dir/$lang/$split.conllu | grep -v "^\s*$" | \
	grep -vP "^[0-9]+-[0-9]+" > temp1
	
	cp temp1 temp2
	if [ $lang = "ja" ] || [ $lang = "fa" ] || [ $lang = "ar" ] || [ $lang = "ru" ] || [ $lang = "hi" ]; then
		bash $CODE_DIR/rom_conllu.sh $lang temp1 temp2 $UR_DIR
	fi

	mv temp2 $data_dir/$lang/$split.conllu
	rm temp1

	if [ $lang = "ja" ] || [ $lang = "ar" ]; then
		grep -v "^#" $data_dir/$lang/$split.conllu.all | grep -v "^\s*$" | \
		grep -vP "^[0-9]+-[0-9]+" > temp1

		mv temp1 $data_dir/$lang/$split.conllu.all
	fi
done

