#!/bin/bash

# this is an example of using Monolingual SpokenVocab

#source env/bin/activate # replace this with your env
input_fname=$1

lng=en
voice_root=vocab/audio
wrd_vocab_fpath=vocab/vocab.$lng.txt
save_path=output/$input_fname


python -W ignore generate_speech.py \
  --voice-root $voice_root \
  --wrd-vocab-fpath $wrd_vocab_fpath \
  --input-file $input_fname \
  --chosen-spk spk2 \
  --save-path $save_path \
  --save-audio
