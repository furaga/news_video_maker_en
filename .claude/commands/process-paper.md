# /process-paper

Select the most interesting paper from `.cache/pipeline/01_papers.json` and save an English summary to `.cache/pipeline/02_selected.json`.

## Steps

1. Read `.cache/pipeline/01_papers.json`

1a. Load past article/paper titles to prevent duplicate topics:
   - If `.cache/history.json` exists, read it and extract the `title` field from the latest 30 `entries` as `past_titles`
   - If the file does not exist, set `past_titles = []`

2. Score all papers (1–10):
   - **HF Daily Papers listing**: +2 pts bonus (high community attention)
   - Technical novelty and innovation (significantly outperforms prior work, new architecture)
   - Practical usefulness (includes methods, tools, or datasets engineers can actually use)
   - Accessibility (can the key idea be explained in a ~60-second video? not too theory-heavy)
   - **-3 pts** penalty if the topic, field, or method overlaps with a title in `past_titles`

3. Select the highest-scoring paper (tie-break: most `hf_upvotes`, then newest)

4. Process the selected paper in English:
   - `english_title`: rephrase the paper title into a punchy English headline (60 chars max)
   - `english_summary`: detailed English summary of the paper (problem statement, method, results) (200–300 words)
   - `key_points`: 3–5 bullet points for the video script (each max 15 words)
     - Examples: "27× faster inference than baseline", "zero-shot, no fine-tuning required"

5. Research related information with the WebSearch tool (2–3 searches):
   - Search for background, related work, and practical examples for the selected paper's topic
   - Collect supplementary information useful to a global tech audience
   - Summarize the collected information in the `related_research` field (200–300 words in English)

6. Save to `.cache/pipeline/02_selected.json` with the Write tool using the schema below:

```json
{
  "title": "Original paper title (English)",
  "url": "https://arxiv.org/abs/2603.06199",
  "source": "arxiv",
  "image_url": "",
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

- If `01_papers.json` is empty, display an error and stop
- If the JSON cannot be generated correctly, retry up to 2 times
