from generate_speech import SpokenVocab, MixSpokenVocab, generate_stitched_voice, generate_stitched_mix_voice


def test_english():
    voice_root = "vocab/audio"
    lng = "en"
    wrd_vocab_fpath = f"vocab/vocab.{lng}.txt"
    num_spk = 10
    chosen_spk = "spk0"
    save_audio = True
    save_path = "output"
    crossfade = 100

    spok_vocab = SpokenVocab(voice_root, wrd_vocab_fpath, lng=lng, num_spk=num_spk)
    test_sentences = ["Nice to meet you all.", "What a lovely day."]
    for sentence in test_sentences:
        wav = generate_stitched_voice(sentence, spok_vocab, spk=chosen_spk, save_audio=save_audio,
                                      save_path=save_path, crossfade=crossfade)


def test_bengali():
    voice_root = "vocab/audio"
    lng = "be"
    wrd_vocab_fpath = f"vocab/vocab.{lng}.txt"
    num_spk = 1
    chosen_spk = "spk0"
    save_audio = True
    save_path = "output"
    crossfade = 100

    spok_vocab = SpokenVocab(voice_root, wrd_vocab_fpath, lng=lng, num_spk=num_spk)
    test_sentences = ["তোমাদের সাথে সাক্ষাৎ করে ভালো লাগলো", "কি একটি সুন্দর দিন."]
    for sentence in test_sentences:
        wav = generate_stitched_voice(sentence, spok_vocab, spk=chosen_spk, save_audio=save_audio,
                                      save_path=save_path, crossfade=crossfade)


def test_mix_engine_bengali():
    voice_root = "vocab/audio"
    lngs = ["en", "be"]
    wrd_vocab_fpaths = [f"vocab/vocab.{lngs[0]}.txt", f"vocab/vocab.{lngs[1]}.txt"]
    num_spks = [1, 1]
    chosen_spk = ["spk0", "spk0"]
    save_audio = True
    save_path = "output"
    crossfade = 100

    spok_vocab = MixSpokenVocab(voice_root, wrd_vocab_fpaths, lngs=lngs, num_spks=num_spks)
    test_sentences = ["Nice to সাক্ষাৎ করে ভালো লাগলো", "কি একটি সুন্দর দিন."]
    for sentence in test_sentences:
        wav = generate_stitched_mix_voice(sentence, spok_vocab, spks=chosen_spk, save_audio=save_audio,
                                          save_path=save_path, crossfade=crossfade)

test_english()
test_bengali()
test_mix_engine_bengali()