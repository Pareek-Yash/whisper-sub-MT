#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   app.py
@Modified:   2023/09/26 12:14:38
@Author  :   Yash Pareek 
@Version :   1.0
@Contact :   sroy10@uh.edu
@License :   MIT
@Desc    :   None
'''

import warnings
warnings.simplefilter('ignore')
import shutil
from flask import Flask, request, jsonify
from pathlib import Path
import os
import whisper
from pysrt import SubRipItem
from subtitle import Subtitle
from translator import Translator
from utils import Utils
from whisper.utils import get_writer

warnings.simplefilter('ignore')

class TranscriptService:
    def __init__(self):
        self.options = {
            "max_line_width": 24,
            "max_line_count": 3,
            "highlight_words": False
        }
        self.model = whisper.load_model("base").to('cuda')

    def translate_vtt(self, dir_path, object_key, target_languages):
        subs = Subtitle.load_webvtt(str(dir_path) + "/" + str(object_key))
        target_languages = ['spa', 'fra', 'zho', 'deu', 'rus']
        
        for language in target_languages:
            if language in ['spa', 'fra']:
                translator = Translator(src_language='eng', tgt_language=language, recipe='helsinki-nlp')
            else:
                translator = Translator(src_language='eng', tgt_language=language, recipe='facebook-mbart', flavour='large')

            translated_subs = translator.translate(subs.subs)
            TranscriptService.export_to_webvtt(subrip_items=translated_subs, output_file_path=dir_path / f'srt_filename_{language}.vtt')

    def get_transcript(self, object_key, languages):
        temp_filename = f'/home/ubuntu/mux/{object_key}'
        temp_filename_path = Path(temp_filename)

        transcript = self.model.transcribe(temp_filename, verbose=False, language="en")

        # Create a directory with object_key.stem
        dir_path = Path(f"/home/ubuntu/translator/transcripts/{temp_filename_path.stem}")
        dir_path.mkdir(parents=True, exist_ok=True)

        vtt_writer = get_writer("vtt", dir_path)
        output_vtt = f"srt_filename_en.vtt"
        vtt_writer(transcript, dir_path / output_vtt)

        self.translate_vtt(dir_path, output_vtt, languages)

    @staticmethod
    def export_to_webvtt(subrip_items: list[SubRipItem], output_file_path: str):
        lines = ['WEBVTT', '']

        formatted_lines = [
            f'{index}\n'
            f'{item.start.hours:02}:{item.start.minutes:02}:{item.start.seconds:02}.{item.start.milliseconds:03} --> '
            f'{item.end.hours:02}:{item.end.minutes:02}:{item.end.seconds:02}.{item.end.milliseconds:03}\n'
            f'{item.text}\n'
            for index, item in enumerate(subrip_items, start=1)
        ]

        lines.extend(formatted_lines)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(lines))


app = Flask(__name__)

@app.route('/generate-srt', methods=['POST'])
def generate_srt_endpoint():
    object_key = request.json.get('object_key')
    languages = ['spa', 'fra', 'zho', 'deu', 'rus']

    ts = TranscriptService()
    ts.get_transcript(object_key, languages)

    dir_path = f"/home/ubuntu/translator/transcripts/{Path(object_key).stem}"
    bucket = "mux-video-upload"
    uploaded = Utils.upload_files_to_s3(dir_path, bucket)

    # Clean up by deleting the directory and its contents
    shutil.rmtree(dir_path)

    return jsonify(uploaded)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)