# Whisper-sub-MT

Subtitle generation with open-source OpenAI Whisper package and Machine Translation using Helsinki NLP MT model. A comprehensive solution for audio transcription, subtitle generation, and machine translation.

## Whisper Transcription

Whisper is an integral part of this project, providing accurate transcriptions of audio content. The transcriptions serve as a foundation for subsequent operations like subtitle generation and translation.

[Whisper](https://github.com/openai/whisper#whisper) is a general-purpose speech recognition model. It is trained on a large dataset of diverse audio and is also a multitasking model that can perform multilingual speech recognition, speech translation, and language identification.

This repo uses the medium model for transcription as it served as the fastest and most accurate model during the tests. More models are available [here](https://github.com/openai/whisper#available-models-and-languages).

## SRT Generation

Once the audio content is transcribed, this project facilitates the generation of SRT (SubRip Subtitle)/ VTT files. These files can be used across various platforms and media players to display subtitles for the corresponding audio or video content.

## Machine Translation using Helsinki NLP models

To make the content globally accessible, the project integrates machine translation capabilities powered by Helsinki NLP models. There are wide array of models available from [Helsinki NLP](https://huggingface.co/Helsinki-NLP) by University of Helsinki.

---

Please refer to the respective sections or documentation for detailed usage, setup instructions, and contributions.
