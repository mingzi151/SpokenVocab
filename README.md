# SpokenVocab

The codebase is for EACL-finding paper [Generating Synthetic Speech from SpokenVocab for Speech Translation](https://arxiv.org/pdf/2210.08174.pdf). SpokenVocab is proposed as an alternative to TTS. It's a simple, fast and effective data augmentation that converts text to speech on the fly. Our experimental results show that synthetic speech generated via SpokenVocab works as well as TTS systems.


### Preparation
**Required package**: 

`pip install pydub numpy`

**SpokenVocab**: 

Stitching speech works for any languages as long as the language is supported by a TTS system (e.g, Google TTS, Azure TTS). You may also generate speeches for your vocabulary. 

[//]: # (For illustration purposes, we only include English in this repository. )

Required files (take English as an example):
- word vocabulary: `vocab/vocab.en.txt`
- SpokenVocab bank: download speeches from this [link](https://drive.google.com/file/d/1TM9M_GtleT55kCP893uHcuelukQZhsym/view?usp=share_link) for the above word vocabulary and unpact it under `./voice`

Structure of `vocab` (you may prepare a similar structure for your language or vocabulary)

    vocab
    ├── vocab.en.txt
    ├── vocab.be.txt
    ├── vocab.en-be.txt        
    ├── audio                       
    │    ├── en
    │    │   ├── spk0   # spk# contains speeches for vocab.en.txt
    │    │   ├── spk1
    │    │   ├── spk2            
    │    │   └── ...


The output is saved under `output/spk#/lang/crossfade` and wav files are named by timestamps.

**Currently supported languages and speakers**
- English 
  - Vocab size: 36765
  - Ten speakers (all aged between 20-40): 
    - spk0: US accent, female
    - spk1: US accent, male
    - spk2: US accent, female
    - spk3: US accent, male
    - spk4: US accent, male
    - spk5: UK accent, female
    - spk6: UK accent, male
    - spk7: UK accent, female
    - spk8: UK accent, male
    - spk9: UK accent, male
- Bengali
  - Vocab size: 33821
  - One speaker: 
    - spk0: female, aged between 20-40

Note that in the case of out-of-vocabulary words, the default tokens ("a" for English and "অইচি" Bengali) are used.


### Usage

#### Python
You can use SpokenVocab directly in your python code, shown as below:
###### monolingual
```
# you would want to put the file and vocab under the same directory
from generate_speech import SpokenVocab, generate_stitched_voice

# set arguments 
voice_root = "vocab/audio"
lng = "en"
wrd_vocab_fpath = f"vocab/vocab.{lng}.txt"
num_spk = 10
chosen_spk = "spk0"
crossfade = 100 # use this to control the "smoonthess" of the stitched speech
save_audio = True # or False if you don't want to save the wav file
save_path = "output"

# input sentence
sentence = "Nice to meet you all!"

# convert the above sentence to speech with spk0 
# save the wav to save_path/chosen_spk
spok_vocab = SpokenVocab(voice_root, wrd_vocab_fpath, lng=lng, num_spk=num_spk)
wav = generate_stitched_voice(sentence, spok_vocab, spk=chosen_spk, save_audio=save_audio,
                              save_path=save_path, crossfade=crossfade)
```
###### code-switching
```
# set arguments 
voice_root = "vocab/audio"
lngs = ["en", "be"]
wrd_vocab_fpaths = [f"vocab/vocab.{lngs[0]}.txt", f"vocab/vocab.{lngs[1]}.txt"]
num_spks = [1, 1]
chosen_spk = ["spk0", "spk0"]
save_audio = True
save_path = "output"
crossfade = 100

# input sentence
sentences = "Nice to সাক্ষাৎ করে ভালো লাগলো"

# convert code-switched text to speech
spok_vocab = MixSpokenVocab(voice_root, wrd_vocab_fpaths, lngs=lngs, num_spks=num_spks)
wav = generate_stitched_mix_voice(sentence, spok_vocab, spks=chosen_spk, save_audio=save_audio,
                                      save_path=save_path, crossfade=crossfade)
```

You may also retrieve the path of a speech given a word and a speaker:
```
word = "Morning"
spc_path = spok_vocab.get_speech(wrd=word, spk=chosen_spk)
```

#### Bash
You can use the code directly from the terminal in case you want to generate speech per a text file (e.g.,`input.txt`).

```bash run_spok_vocab.sh input.txt```



## Citation
Please cite if you use our code
```bibtex
@article{zhao2022generating,
  title={Generating Synthetic Speech from SpokenVocab for Speech Translation},
  author={Zhao, Jinming and Haffar, Gholamreza and Shareghi, Ehsan},
  journal={arXiv preprint arXiv:2210.08174},
  year={2022}
}
```




