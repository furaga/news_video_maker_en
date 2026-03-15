# 仕様書: 台本生成（Script Generator）

## 目的

Generate a 30–60 second English narration video script from a processed article. Handled by Claude Code (LLM).

## 対応コマンド

`.claude/commands/generate-script.md` → `/gen-script`

## 担当

Claude Code（LLM処理）

---

## 入力

**ファイル**: `.cache/pipeline/02_selected.json`（`specs/02_content_processor.md` の出力）

---

## 出力

**ファイル**: `.cache/pipeline/03_script.json`

**Schema** (`VideoScript`):

```json
{
  "title": "Video title (YouTube upload title, 60 chars max)",
  "source_url": "https://...",
  "total_duration_sec": 45.0,
  "sections": [
    {
      "type": "hook",
      "narration_text": "English narration (also used as subtitle display text, with **keyword** markup)",
      "subtitle_text": "Short key point for display (15 words max)",
      "estimated_duration_sec": 4.0
    },
    {
      "type": "main_1",
      "narration_text": "...",
      "subtitle_text": "...",
      "estimated_duration_sec": 9.0
    },
    {
      "type": "main_2",
      "narration_text": "...",
      "subtitle_text": "...",
      "estimated_duration_sec": 9.0
    },
    {
      "type": "main_3",
      "narration_text": "...",
      "subtitle_text": "...",
      "estimated_duration_sec": 9.0
    },
    {
      "type": "outro",
      "narration_text": "...",
      "subtitle_text": "...",
      "estimated_duration_sec": 5.0
    }
  ]
}
```

---

## データモデル

`src/news_video_maker/script/models.py`（実装時に追加）:

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ScriptSection:
    type: Literal["hook", "main_1", "main_2", "main_3", "main_4", "outro"]
    narration_text: str
    subtitle_text: str
    estimated_duration_sec: float

@dataclass
class VideoScript:
    title: str
    source_url: str
    total_duration_sec: float
    sections: list[ScriptSection]
```

---

## 振る舞い

### 台本の構成

| セクション | 目的 | 目標尺 |
|---|---|---|
| `hook` | 視聴者の興味を引く導入 | 4〜5秒 |
| `main_1` | ニュースの概要・背景 | 7〜10秒 |
| `main_2` | 詳細・技術的内容 | 7〜10秒 |
| `main_3` | 関連情報・業界への影響 | 7〜10秒 |
| `main_4` | 補足・今後の展望（任意） | 7〜10秒 |
| `outro` | まとめ・締め | 4〜5秒 |

各セクションが切り替わるたびにカードアニメーションが発生するため、セクションを細かく分けることで画面に動きが生まれる。`02_selected.json` の `related_research` フィールドがある場合は `main_3` 以降で活用する。

### Duration estimation

Based on English natural speech rate (~130 wpm):
- **Standard rate**: ~2.5 words/sec
- Example: 35 sec → ~87 words

### Script quality standards

- Natural spoken English (contractions OK: "it's", "they've", "don't")
- Short sentences, active voice
- Spell out acronyms on first use where helpful (e.g., "large language model, or LLM")
- `narration_text` is used as both the TTS input and the subtitle display text — `**keyword**` markup is included directly
- `subtitle_text` keeps the key point from `narration_text` (15 words max)

### YouTube title generation

- 60 chars max
- Hook-style, not descriptive

---

## エラー処理

- `total_duration_sec` が 60 秒を超える場合は各 `main_*` セクションを短縮して再生成する（1回まで）
- `total_duration_sec` が 25 秒未満の場合は各 `main_*` セクションに情報を補足して再生成する（1回まで）

---

## コマンド実装ノート（`.claude/commands/generate-script.md`）

1. `Read` ツールで `.cache/pipeline/02_selected.json` を読み込む
2. Claude 自身が台本を生成する
3. 文字数カウントで尺を推定し、必要に応じて調整する
4. `Write` ツールで `.cache/pipeline/03_script.json` を保存する

---

## テスト方針

コマンド実行による E2E テストで確認:

- 正常系: `02_selected.json` から `03_script.json` が生成されること
- `sections` に `hook`, `main_1`, `main_2`, `main_3`, `outro` が含まれること（合計5件以上）
- `total_duration_sec` が 25〜60 の範囲であること
- `subtitle_text` が各セクションで 25 文字以内であること（概ね）
- `related_research` がある場合は `main_3` 以降に内容が反映されていること
