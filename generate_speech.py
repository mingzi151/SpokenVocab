# -*- coding: utf-8 -*-
# Created by Michelle on 16/4/2023

import string
import os
import difflib
from pydub import AudioSegment
import time
import argparse
import numpy as np
import warnings

# Disable all warnings
warnings.filterwarnings(action="ignore", category=RuntimeWarning)

spec_tokens = "@$%"
punctuation = string.punctuation
for tok in spec_tokens:
    punctuation = punctuation.replace(tok, "")


def read_arguments():
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice-root", type=str, default="vocab/audio")
    parser.add_argument("--wrd-vocab-fpath", type=str, default="vocab/")
    parser.add_argument("--save-path", type=str, default="")
    parser.add_argument("--save-audio", action='store_true')
    parser.add_argument("--lng", type=str, default="en")
    parser.add_argument("--num-spk", type=int, default=10)
    parser.add_argument("--chosen-spk", type=str, default="spk0")
    parser.add_argument("--input-file", type=str, default="")
    parser.add_argument("--crossfade", type=int, default=100)

    return parser.parse_args()


class SpokenVocab:

    def __init__(self, voice_root, wrd_vocab_fpath, lng="en", num_spk=10):
        self.file_type = "wav"
        self.default_token = "a"
        if lng == "be":
            self.default_token = "অইচি"
        self.lng = lng
        self.wrd_vocab_fpath = wrd_vocab_fpath
        self.num_spk = num_spk
        self.voice_path = self.build_voice_path(voice_root)
        self.wrd_vocab = self.build_word_vocab()

    def build_voice_path(self, voice_root):
        return {f"spk{i}": f"{voice_root}/{self.lng}/spk{i}"
                for i in range(self.num_spk)}

    def build_word_vocab(self):
        """build a word vocab and spoken vocab

        returns
        wrd_vocab: a list of words
        spok_vocab: dictionary whose keys are words and values are relative paths to the words.

        """

        with open(self.wrd_vocab_fpath, "r") as f:
            data = f.readlines()
        wrd_vocab = [item.strip("\n") for item in data]
        return wrd_vocab

    def get_speech(self, wrd, spk="spk0"):
        if wrd in self.voice_path[spk]:
            return self.voice_path[spk][wrd]
        else:
            print(f"{wrd} is OOV; returning the default word ")
            return self.voice_path[spk][self.default_token]


class MixSpokenVocab:

    def __init__(self, voice_root, wrd_vocab_fpaths, lngs=None, num_spks=None):
        if num_spks is None:
            num_spks = [1, 1]
        if lngs is None:
            lngs = ["en", "be"]

        self.file_type = "wav"

        assert len(lngs) == 2, "Currently only two languages are supported."
        self.lngs = lngs

        self.default_tokens = {}
        for lng in lngs:
            if lng == "en":
                default_token = "a"
            elif lng == "be":
                default_token = "অইচি"
            else:
                raise NotImplementedError("Language not supported")

            self.default_tokens[lng] = default_token

        self.wrd_vocab_fpaths = {lng: fpath for lng, fpath in zip(lngs, wrd_vocab_fpaths)}
        # breakpoint()
        self.num_spks = {lng: num_spk for lng, num_spk in zip(lngs, num_spks)}
        self.voice_paths = self.build_voice_paths(voice_root)
        self.wrd_vocabs = self.build_word_vocabs()

    def build_voice_paths(self, voice_root):

        voice_paths = {}
        # breakpoint()
        for lng in self.lngs:
            num_spk = self.num_spks[lng]
            voice_paths[lng] = {f"spk{i}": f"{voice_root}/{lng}/spk{i}"
                                for i in range(num_spk)}

        return voice_paths

    def build_word_vocabs(self):
        """build a word vocab and spoken vocab

        returns
        wrd_vocab: a list of words
        spok_vocabs: a dictionary of spok_vocab where the keys are languages

        """

        wrd_vocabs = {}
        for lng in self.lngs:
            wrd_vocab_fpaths = self.wrd_vocab_fpaths[lng]
            wrd_vocabs[lng] = wrd_vocab_fpaths

        return wrd_vocabs

    def get_speech(self, wrd, lng, spk="spk0"):
        if lng in self.voice_paths[lng]:
            if spk in self.voice_paths[lng][spk]:
                if wrd in self.voice_paths[lng][spk][wrd]:
                    return self.voice_paths[lng][spk][wrd]
        else:
            print("language, speaker or word is not supported; returning the default word")
            lng = self.lngs[0]
            spk = "spk0"
            wrd = self.default_tokens[lng]
            return self.voice_paths[lng][spk][wrd]


def normalize(sent):
    """normalise text """

    sent = sent.strip("\n")
    sent = sent.lower()
    sent = sent.translate(str.maketrans('', '', punctuation))
    for tok in spec_tokens:
        sent = sent.replace(tok, f" {tok} ")
    return sent


def find_voice_paths(sent, vocab, spk="spk0"):
    """ retrieve speech paths given a sentence """

    file_type = vocab.file_type
    default_tok = vocab.default_token
    full_voice_path = vocab.voice_path
    voice_path = full_voice_path[spk]
    wrd_vocab = vocab.wrd_vocab

    # preprocess text
    sent = normalize(sent)
    tokens = [tok for tok in sent.split() if tok]

    # retrieve speeches by tokens
    voice_fpaths = []
    for tok in tokens:
        fname = tok + "." + file_type
        voice_fpath = os.path.join(voice_path, fname)
        is_exist = os.path.exists(voice_fpath)

        if not is_exist:  # retrieve the most similar text to tok
            sim_toks = difflib.get_close_matches(tok, wrd_vocab, n=1)
            if sim_toks:
                sim_tok = sim_toks[0]
                fname = f"{sim_tok}.{file_type}"
            else:  # use default token if tok is a special symbol.
                fname = f"{default_tok}.{file_type}"
            voice_fpath = os.path.join(voice_path, fname)
            try:
                assert os.path.exists(voice_fpath), "voice file path must exit; something went wrong!"
            except Exception as e:
                print(f"error: {e}")
        voice_fpaths.append(voice_fpath)
    return voice_fpaths


def smooth_stitched_speech(waveform_list, crossfade=100):
    """ smooth transitions between speeches, controlled by crossfade. Crossfade of 100 gives the most natural sound. """

    if len(waveform_list) == 1:
        return waveform_list[0]
    elif len(waveform_list) == 0:
        raise Exception("waveform_list cannot be empty!!!")
    waveform = waveform_list[0]
    for each in waveform_list[1:]:
        waveform = waveform.append(each, crossfade)
    return waveform


def save_wav(wav, fpath, fname):
    """ save wav to disk """

    wav.export(os.path.join(fpath, fname), format="wav")


def generate_stitched_voice(sent, vocab, spk="spk0", save_audio=False, save_path="", crossfade=100):
    """ generate synthetic (stitched) speech on the fly """

    assert sent, "sent cannot be empty"
    voice_fpaths = find_voice_paths(sent, vocab, spk)

    # stitch speeches by paths on the fly
    waveform_list = []
    for file in voice_fpaths:
        waveform = AudioSegment.from_file(file, format="wav")
        waveform_list.append(waveform)

    # smooth transitions to make the speech more natural
    stitched_waveform = smooth_stitched_speech(waveform_list, crossfade)
    # (optional) save speech to disk
    if save_audio:
        out_path = os.path.join(save_path, spk)
        out_path = out_path + f"/{vocab.lng}/cf{str(crossfade)}"
        os.makedirs(out_path, exist_ok=True)
        fname = str(time.time()) + ".wav"
        save_wav(stitched_waveform, out_path, fname)

    waveform = np.asarray(stitched_waveform.get_array_of_samples())
    return waveform


def find_mix_voice_paths(sent, vocab, spks):
    """ retrieve speech paths given a code-mixed sentence """

    def check_english(item):
        if isinstance(item, str):
            return item.isalpha()
        return False

    lngs = vocab.lngs
    file_type = vocab.file_type
    default_tokens = vocab.default_tokens
    voice_paths = vocab.voice_paths
    wrd_vocabs = vocab.wrd_vocabs

    # preprocess text
    sent = normalize(sent)
    tokens = [tok for tok in sent.split() if tok]

    # retrieve speeches by tokens
    voice_fpaths = []
    for tok in tokens:
        en_idx = lngs.index("en")
        ot_idx = len(lngs)-1 - en_idx
        # breakpoint()
        if check_english(tok):
            lng = "en"
            spk = spks[en_idx]
        else:
            lng = lngs[ot_idx]
            spk = spks[ot_idx]

        default_tok = default_tokens[lng]
        full_voice_paths = voice_paths[lng]
        voice_path = full_voice_paths[spk]
        wrd_vocab = wrd_vocabs[lng]

        fname = tok + "." + file_type
        voice_fpath = os.path.join(voice_path, fname)
        is_exist = os.path.exists(voice_fpath)

        if not is_exist:  # retrieve the most similar text to tok
            sim_toks = difflib.get_close_matches(tok, wrd_vocab, n=1)
            if sim_toks:
                sim_tok = sim_toks[0]
                fname = f"{sim_tok}.{file_type}"
            else:  # use default token if tok is a special symbol.
                fname = f"{default_tok}.{file_type}"
            voice_fpath = os.path.join(voice_path, fname)
            try:
                assert os.path.exists(voice_fpath), "voice file path must exit; something went wrong!"
            except Exception as e:
                print(f"error: {e}")
        voice_fpaths.append(voice_fpath)
    return voice_fpaths


def generate_stitched_mix_voice(sent, vocab, spks, save_audio=False, save_path="", crossfade=100):
    """ generate synthetic (stitched) speech (for code-switching) on the fly """

    if spks is None:
        spks = ["spk0", "spk0"]
    assert sent, "sent cannot be empty"
    voice_fpaths = find_mix_voice_paths(sent, vocab, spks)

    # stitch speeches by paths on the fly
    waveform_list = []
    for file in voice_fpaths:
        waveform = AudioSegment.from_file(file, format="wav")
        waveform_list.append(waveform)

    # smooth transitions to make the speech more natural
    stitched_waveform = smooth_stitched_speech(waveform_list, crossfade)
    # (optional) save speech to disk
    if save_audio:
        out_path = os.path.join(save_path, "-".join(spks))
        out_path = out_path + f"/{'-'.join(vocab.lngs)}/cf{str(crossfade)}"
        os.makedirs(out_path, exist_ok=True)
        fname = str(time.time()) + ".wav"
        save_wav(stitched_waveform, out_path, fname)

    waveform = np.asarray(stitched_waveform.get_array_of_samples())
    return waveform


def read_txt(fname):
    with open(fname, "r") as f:
        data = f.readlines()
    return data


if __name__ == '__main__':
    # read arguments
    args = read_arguments()

    sentences = read_txt(args.input_file)

    spok_vocab = SpokenVocab(args.voice_root, args.wrd_vocab_fpath, lng=args.lng, num_spk=args.num_spk)
    for sentence in sentences:
        wav = generate_stitched_voice(sentence, spok_vocab, spk=args.chosen_spk, save_audio=args.save_audio,
                                      save_path=args.save_path, crossfade=args.crossfade)
