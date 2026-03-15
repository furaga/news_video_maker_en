# /gen-video

Generate a video from the script in `.cache/pipeline/03_script.json` and save it to `output/`.

## Steps

Execute with the Bash tool:

```bash
cd /c/Users/furag/Documents/prog/python/news_video_maker_en && uv run python -m news_video_maker.video.composer
```

After execution, report the path of the generated video.

## Prerequisites

- Internet connection required (edge-tts calls Microsoft's TTS API)
- `.cache/pipeline/03_script.json` must exist

## Error handling

- TTS failure: display the error log and stop (intermediate files are preserved)
- moviepy rendering failure: display the error log and stop (intermediate files are preserved)
