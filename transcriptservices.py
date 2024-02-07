from subtitle import Subtitle
from translator import Translator
from pathlib import Path
from whisper.utils import get_writer
from pysrt import SubRipItem
import whisper
import time
import logging
import torch

logging.basicConfig(filename='/home/ubuntu/final-v2/sqs-testing-v1.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        
        
        for language in target_languages:
            try:
                logging.info(f"Started Translating file to {language}")
                start_time = time.time()

                if language in ['spa', 'fra', 'hin', 'ita', 'kan']:
                    translator = Translator(src_language='eng', tgt_language=language, recipe='helsinki-nlp')
                else:
                    translator = Translator(src_language='eng', tgt_language=language, recipe='facebook-mbart', flavour='large')

                translated_subs = translator.translate(subs.subs)
                TranscriptService.export_to_webvtt(subrip_items=translated_subs, output_file_path=dir_path / f'{Path(object_key).stem}_{language}.vtt')

                logging.info(f"Translated in {time.time() - start_time:.2f} seconds")

            except Exception as e:
                logging.error(f"Could not translate to {language}. {e}")
    

    def get_transcript(self, object_key, output_audio_path, languages, dir_path):
        output_audio_path = Path(output_audio_path)

        transcript = self.model.transcribe(output_audio_path, verbose=False, language="en")


        vtt_writer = get_writer("vtt", dir_path)
        output_vtt = f"{Path(object_key).stem}_en.vtt"
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