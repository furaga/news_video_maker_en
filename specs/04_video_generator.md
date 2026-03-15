# 仕様書: 動画生成（Video Generator）

## 目的

Generate MP4 video from the script: synthesize audio with edge-tts, generate background images, and compose with moviepy.

## 対応コマンド

`.claude/commands/generate-video.md` → `/gen-video`

## 担当

Python (edge-tts + moviepy + Pillow)
Commands invoke Python scripts in `src/news_video_maker/video/` via the Bash tool.

---

## 入力

**ファイル**: `.cache/pipeline/03_script.json`（`specs/03_script_generator.md` の出力）

---

## 出力

- **動画ファイル**: `output/<YYYYMMDD>_<HHMMSS>.mp4`
- **パスファイル**: `.cache/pipeline/04_video_path.txt`（動画ファイルの絶対パス）

---

## 動画仕様

| 項目 | 値 |
|---|---|
| 解像度 | 1080 × 1920 px（9:16 縦型、YouTube Shorts 対応） |
| フレームレート | 30 fps |
| 映像コーデック | H.264 |
| 音声コーデック | AAC |
| コンテナ | MP4 |

---

## 振る舞い

### Step 1: Audio synthesis (edge-tts)

Handled by `src/news_video_maker/video/tts.py`.

Synthesize `narration_text` for each section using the edge-tts Microsoft Neural TTS API:

1. Call `edge_tts.Communicate(text, voice).save(output_path)` asynchronously
2. Save the generated MP3 to `.cache/audio/<section_index>.mp3`

The TTS voice is configurable via `TTS_VOICE` in `config.py` (default: `en-US-ChristopherNeural`).
Internet connection required.

### ステップ2: 背景画像生成

`src/news_video_maker/video/background.py` と `src/news_video_maker/video/visuals.py` が担当。

背景画像の優先順位（`composer.py` で制御）:

1. `image_url` が指定されている場合: 記事画像をダウンロードして base64 化
2. `image_url` 未指定または取得失敗の場合: **Stable Diffusion（SD 1.5）でAI生成**
   - モデル: `runwayml/stable-diffusion-v1-5`（Hugging Face diffusers、ローカル・無料）
   - 生成サイズ: 576×1024（9:16）→ PIL で 1080×1920 にリサイズ
   - キャッシュ: `.cache/images/bg_generated.png`
   - 初回実行時のみモデルダウンロード（~4GB）
   - `diffusers` 未インストールの場合はスキップして次のフォールバックへ
3. AI生成も失敗した場合: 暗い青 CSS グラデーション（既存動作）

#### Ken Burns 効果

`visuals.py` の Playwright レンダリング時に `.bg` 要素のズームを時間経過で変化させる:

- 動画開始時: `transform: scale(1.06)`
- 動画終了時: `transform: scale(1.14)`
- 計算式: `scale = 1.06 + 0.08 * (globalTime / totalDuration)`
- `globalTime` = 動画全体での絶対時刻（セクション開始時刻 + セクション内経過時刻）
- テキスト: `subtitle_text` を中央寄せで表示
  - フォント: システムの日本語フォント（`C:/Windows/Fonts/meiryo.ttc` または `YuGothic`）
  - フォントサイズ: 72px
  - 色: 白
- ソース表記: 右下に「Source: {source}」を小さく表示（32px、グレー）
- 生成した PNG を `.cache/images/<section_index>.png` に保存

### ステップ3: 動画合成（moviepy）

`src/news_video_maker/video/composer.py` が担当。

1. 各セクションの WAV の実際の長さを取得
2. PNG 画像から `ImageClip` を作成（duration = WAV の長さ）
3. `AudioFileClip` で WAV を読み込む
4. 各セクションのクリップを `CompositeVideoClip` で合成
5. セクションを `concatenate_videoclips` で結合
6. `write_videofile()` で MP4 出力
   - `codec="libx264"`, `audio_codec="aac"`, `fps=30`

### Subtitle timing calculation

Subtitle chunk timing is determined as follows (not purely character count):

1. Split `narration_text` at English sentence boundaries (`.!?`)
2. Synthesize each sentence individually with edge-tts and measure actual audio length
3. Distribute section total duration proportionally to sentence audio lengths
4. Sub-chunks within a sentence are distributed by character count ratio

Individual sentence MP3s are cached in `.cache/audio/sentences/`.

---

## Module structure

### `src/news_video_maker/video/tts.py`

```python
# edge-tts English TTS client
# Input: text, output path
# Output: MP3 file path
def synthesize(text: str, output_path: Path, voice: str = TTS_VOICE) -> Path: ...
```

### `src/news_video_maker/video/visuals.py`

```python
# Pillow テキストカード生成
# 入力: subtitle_text, source_name, image_url（省略可）
# 出力: PNG ファイルパス
def generate_text_card(subtitle_text: str, source: str, output_path: Path, image_url: str | None = None) -> Path: ...
```

### `src/news_video_maker/video/composer.py`

```python
# moviepy 動画合成
# 入力: VideoScript（JSON から復元）
# 出力: MP4 ファイルパス
def compose_video(script: VideoScript, output_path: Path) -> Path: ...
```

---

## Error handling

- **edge-tts failure**: display detailed error message and stop; confirm internet connectivity
- **Pillow font not found**: fall back to `ImageFont.load_default()` with a warning
- **moviepy rendering failure**: display error log and stop; preserve intermediate files (MP3/PNG)

---

## Intermediate files

The following cache files are **not deleted** on success (kept for debugging and reuse):

```
.cache/
  audio/
    00_hook.mp3
    01_main.mp3
    02_outro.mp3
  images/
    00_hook.png
    01_main.png
    02_outro.png
```

---

## Implementation notes

- edge-tts outputs MP3 (not WAV); moviepy loads MP3 via ffmpeg with no issues
- For moviepy v2 API differences, use `use context7` to check the latest API
- `output/` directory is created automatically if it doesn't exist

---

## Test policy

- `tests/video/test_composer.py`
- Mock the edge-tts `synthesize()` call
- At least one synthesis test using a short silent audio file
- Confirm the generated MP4 file exists
