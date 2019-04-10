# UTagger: A Grounded Unsupervised Universal Part-of-Speech Tagger for Low-Resource Languages

This reposity contains the code neccesary to reproduce the results in the paper:

[1] A Grounded Unsupervised Universal Part-of-Speech Tagger for Low-Resource Languages. 
Ronald Cardenas, Ying Lin, Heng Ji and Jonathan May. NAACL 2019, Minneapolis, USA.



## Requirements

Training of Language Models is done with [SRILM v1.7.2](http://www.speech.sri.com/projects/srilm/download.html). However, any library that produces an ARPA file can be used.

For FST manipulation and cipher training, we use [Carmel](https://github.com/isi-nlp/carmel) (included as a submodule)

You will also need:
* Python 3.6
* NumPy >= 1.16.2
* SciPy >= 1.2.1
* lxml >= 4.3.3


## Setup

Initialize the submodules as follows:

```
git submodule update --init --recursive
```

Then build the code in `src/carmel`, `src/brown-cluster`, and `src/marlin` (see each folder's README file for reference).

## Using UTagger


0. Extract POS annotations from [UniversalDependencies](http://universaldependencies.org) treebanks

If you want to use annoations from UD treebanks, you can extract the POS sequences by running

```
./setup_ud-treebank_data.sh -td <ud-treebank-parent-folder>
```

This will extract only the POS tags of CONLLU train files for languages experimented with in [1].


1. Train POS language models

  *  From UD data

Training for several languages can be done by listing the iso-639-1 code of each language separated by commas. For instance, to train second order LMs for English and German, run:

```
./train_format_lm_ud.sh  -l en,de  -o 2
```

  * From POS token sequences (one sentence per line)

```
./train_srilm_langmodel.sh -i <pos-file> -o <order>
```

  * Reformating an already trained LM in ARPA format

Further down in the pipeline, Carmel reads trained language models in OpenFST format. Reformat an ARPA file as follows:

```
./src/code/arpa2wfst.sh -i <arpa-file> -l <lang-id> -o <order>
```

2. Train UTagger


```
./utagger -i sample.in -if txt -m train \
-lm_o 2 -pl en,de -ca brown -nc 500
```


3. Tag / eval

```
./utagger -i sample.in -if txt -m tag \
-lm_o 2 -pl en,de -ca brown -nc 500
```

