# /process

Select the most interesting article from `.cache/pipeline/01_articles.json` and save an English summary to `.cache/pipeline/02_selected.json`.

## Steps

1. Read `.cache/pipeline/01_articles.json`

1a. Load past article titles to prevent duplicate topics:
   - If `.cache/history.json` exists, read it and extract the `title` field from the latest 30 `entries` as `past_titles`
   - If the file does not exist, set `past_titles = []`

2. Score all articles (1–10):
   - Technically interesting (new technology, innovative approach, etc.)
   - Relevant to a global English-speaking tech audience
   - Important update to a tool or service engineers use daily
   - Substantive content (not purely sensational)
   - Has a surprising or unexpected angle (famous company failures, record-breaking numbers, dramatic reversals, scandals) (+1–2 pts)
   - Interesting even to non-engineers (+1 pt)
   - **-3 pts** penalty if the topic, company, or technology overlaps with a title in `past_titles`
   - Plain version/feature announcements with no emotional impact (-1 pt)
   - Abstract articles lacking numbers, proper nouns, or concrete examples (-1 pt)

3. Select the highest-scoring article (prefer newer on tie)

4. Carry over the `image_url` field from `01_articles.json` unchanged

5. Process the selected article in English:
   - `english_title`: rephrase the original title into a punchy English headline (60 chars max)
   - `english_summary`: detailed English summary of the article (200–300 words)
   - `key_points`: 3–5 bullet points in English for the video script (each max 15 words)

6. Research related information with the WebSearch tool (2–3 searches):
   - Search for background information and related technology relevant to the article topic
   - Collect supplementary information useful to a global tech audience
   - Examples: similar cases, industry impact, technical details, expert opinions
   - Summarize the collected information in the `related_research` field (200–300 words in English)

7. Save to `.cache/pipeline/02_selected.json` with the Write tool using the schema below:

```json
{
  "title": "Original English title",
  "url": "https://...",
  "source": "techcrunch",
  "image_url": "https://... (copied from 01_articles.json; empty string if missing)",
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

## Error handling

- If `01_articles.json` is empty, display an error and stop
- If the JSON cannot be generated correctly, retry up to 2 times
