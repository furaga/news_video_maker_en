# 仕様書: コンテンツ処理（Content Processor）

## 目的

Select the most interesting article from the fetched list and generate an English summary. Handled by Claude Code (LLM).

## 対応コマンド

`.claude/commands/process-article.md` → `/process`

## 担当

Claude Code（LLM処理）

---

## 入力

**ファイル**: `.cache/pipeline/01_articles.json`（`specs/01_news_fetcher.md` の出力）

---

## 出力

**ファイル**: `.cache/pipeline/02_selected.json`

**Schema** (`ProcessedArticle`):

```json
{
  "title": "Original English title",
  "url": "https://...",
  "source": "techcrunch",
  "english_title": "Punchy English headline (60 chars max)",
  "english_summary": "Detailed English summary (200–300 words)",
  "interest_score": 8.5,
  "key_points": [
    "Point 1 (1 sentence, 15 words max)",
    "Point 2",
    "Point 3"
  ],
  "related_research": "Related background information from WebSearch (200–300 words)"
}
```

---

## Data model

Defined as a model under `src/news_video_maker/processor/` (to be added on implementation):

```python
from dataclasses import dataclass

@dataclass
class ProcessedArticle:
    title: str
    url: str
    source: str
    english_title: str
    english_summary: str
    interest_score: float
    key_points: list[str]
    related_research: str  # Background information from WebSearch
```

---

## 振る舞い

### ステップ0: 過去採用タイトルの取得

`.cache/history.json` が存在する場合に Read ツールで読み込み、`entries` の `title` フィールドを最新 30 件取得する（新しい順）。ファイルがなければ空リストとして扱う。

### Step 1: Score articles

Load all article titles and summaries (first 300 chars) from `01_articles.json`. Claude scores each 1–10:

**Scoring criteria (global English-speaking tech audience):**
- Technically interesting (new technology, innovative approach, etc.)
- Relevant to a global English-speaking tech audience
- Important update to a tool or service engineers use daily
- Substantive content, not purely sensational
- Overlap with past titles from Step 0: **-3 pts** penalty

### Step 2: Select the highest-scoring article

Pick the one with the highest score. Prefer newer articles on tie.

### Step 3: Generate English summary

Using the selected article's `summary_text` (or first 2000 chars of `full_text` if available):

1. **`english_title`**: rephrase the original title into a punchy English headline (60 chars max)
2. **`english_summary`**: detailed English summary (200–300 words)
   - Include technical background and significance
   - Use technical terms as-is; clarify with brief parenthetical if needed
3. **`key_points`**: 3–5 bullet points for the video script (each max 15 words)

### Step 4: Research related information

Use the `WebSearch` tool to search 2–3 times for information related to the selected article:

- Goal: provide supplementary depth beyond the article itself
- Examples: similar cases, competing technologies, industry background, expert commentary, future outlook
- Summarize the collected information in English in `related_research` (200–300 words)

---

## エラー処理

- `01_articles.json` が空の場合はエラーを raise してパイプラインを停止する
- スコアリング結果が JSON として正しく解釈できない場合は再度試みる（最大2回）
- 要約生成に失敗した場合は次点の記事を試みる

---

## コマンド実装ノート（`.claude/commands/process-article.md`）

Claude Code コマンドとして実装するため、コマンドファイル内で:

1. `Read` ツールで `.cache/pipeline/01_articles.json` を読み込む
2. Claude 自身がスコアリングと選定を判断する
3. `WebSearch` ツールで関連情報を2〜3回調査する
4. `Write` ツールで `.cache/pipeline/02_selected.json` を保存する

Python ツールへの依存はなし（Claude が直接 JSON を生成する）。

---

## テスト方針

このステージは Claude Code（LLM）が処理するため、ユニットテストではなくコマンド実行による E2E テストで確認する:

- 正常系: `01_articles.json` から `02_selected.json` が生成されること
- 出力が JSON スキーマに準拠していること
- `key_points` が 3〜5 件であること
- `interest_score` が 1.0〜10.0 の範囲であること
- `related_research` フィールドが存在し、空でないこと
