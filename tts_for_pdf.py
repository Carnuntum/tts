import typing
from typing import List, Optional, Union
from TTS.api import TTS
import pdfminer.high_level as pdfm
from pathlib import Path
import re
from natsort import natsorted
import subprocess

class PdfProcessor:
    def __init__(self, pdf_path: str = ""):
        self.pdf_path = pdf_path
        
    def read_pages(self, page_range: Optional[List[int]] = None, replace_args: Optional[List[str]] = None, t_string: Optional[str] = None) -> List[str]:
        """read given range of pages from pdf, remove stripping whitespaces and replacing optional given arguments.
        """
        
        book = []
        if page_range is not None:
            pages = list(range(page_range[0], page_range[1]))
        
            for page in pages:
                p_text = pdfm.extract_text(pdf_file=self.pdf_path, page_numbers=[page])
                p_text = p_text.replace(
                "\t", " "
                ).replace(
                    "\n" , " "
                ).replace(
                    "\x0c", ""
                ).replace(
                    "”", "\""    
                ).replace(
                    "“", "\""    
                ).strip()
                
                book.append(p_text)

            repl_expr = None
            if replace_args is not None:
                repl_expr = []
            
                for arg in replace_args:
                    repl_expr.append(f""".replace("{arg}", "")""")
                
                repl_expr = "".join(repl_expr)
                print(repl_expr)
            if book and repl_expr:
                for page in book:
                    page = eval('page' + repl_expr)
                
        return book
        
class ttsProcessor:
    def __init__(self, book: List[str], 
                 output_path: Optional[str|Path] = None, 
                 model_name: Optional[str] = None, 
                 vocoder_name: Optional[str] = None, 
                 speaker_index: Optional[int] = None,
                 use_cuda: bool = True) -> None:
        
        self.book = book,
        self.output_path = output_path
        self.model_name = model_name,
        self.vocoder_name = vocoder_name,
        self.speaker_index = speaker_index,
        self.use_cuda = use_cuda
        
    def write_chunks(self) -> None:
        """takes the book list of strings as input and splits it in 20 pages chunks
        """
        book = self.book[0]
        
        slice_dict = {}
        for idx in list(range(0, len(book)-1, 20)):
            if idx + 20 > len(book)-1:
                slice_dict[str(idx)] = len(book)
            else:
                slice_dict[str(idx)] = idx + 20
                
        for key, value in slice_dict.items():
            if self.output_path:
                if isinstance(self.output_path, str):
                    with open("/".join([str(self.output_path), f"book{key}-{value}.txt"]), "w") as f:
                        f.write("".join(book[int(key):int(value)]))
                    
                else:
                    with Path(self.output_path / f"book{key}-{value}.txt").open('w') as f:
                        f.write("".join(book[int(key):int(value)]))
                    
    def synthesize_text_chunks(self):
        """generates text to speech conversion with given parameters from the ttsProcessor class.
        """
        files_path = self.output_path
        model = self.model_name[0]
        vocoder = f'--vocoder_name "{self.vocoder_name[0]}"' if self.vocoder_name[0] is not None else ""
        speaker = f"--speaker_idx p{self.speaker_index[0]}" if self.speaker_index[0] is not None else "" 
        cuda = "--use_cuda USE_CUDA" if self.use_cuda else ""
        
        file_list = natsorted([file for file in Path(str(files_path)).iterdir() if '.txt' in file.name])
        
        for file in file_list:
            command = f'tts --text \"$(cat "{file}")\" --model_name "{model}" {vocoder} {cuda} --out_path "{file.parent/file.name.replace(".txt", ".wav")}" {speaker}'
            print(command)
            exitcode = subprocess.run(command, shell=True)
            print(f"\n\n Process exited with {exitcode}. \n\n")
            
    def merge_audio_chunks(self, file_name: Optional[str] = "output.wav"):
        """combines generated audio files to one. ffmpeg has to be installed for that.
        """
        path = self.output_path
        
        audio_list = natsorted([file for file in Path(str(path)).iterdir() if '.wav' in file.name])
        
        if Path(str(path) + "/wav_list.config").exists():
            Path(str(path) + "/wav_list.config").unlink()
        
        for file in audio_list:
            with Path(str(path) + "/wav_list.config").open("a") as merge_config:
                merge_config.write("file " + f"'{file.name}'\n")
        
        command = f'ffmpeg -f concat -safe 0 -i "{str(path)}/wav_list.config" -c copy "{str(path)+ "/" +file_name}"'
        subprocess.run(command, shell=True)