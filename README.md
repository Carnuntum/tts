# tts - text to speech functions using the coqui TTS package

Some wrapper functions for the coqui tts package to convert a given number of pages from a pdf to audio. 
<br><br>
Requirements: <br>
- python tts package (pip install tts or see documentation for coqui TTS)
- for cuda a feasable gpu
- ffmpeg

For different tts/vocoder models see the documentation for coqui TTS.


Example usage: <br>

```python
import tts_for_pdf

processor = tts_for_pdf.PdfProcessor(pdf_path="/path/to/pdf")

pdf = processor.read_pages(page_range=[0, 150])

tts = tts_for_pdf.ttsProcessor(book=pdf, output_path="/path/where/output/should/be/written/",
                               model_name="tts_models/en/vctk/vits", #multispeaker model
                               speaker_index=273) #select speaker number 273


tts.write_chunks() #split pdf to 20 pages chunks as the tts cli interface cannot handle files at the moment
tts.synthesize_text_chunks() #perform tts
tts.merge_audio_chunks(file_name="output.wav") #combine audio chunks to single .wav file
```
