# /gen-metadata

Generate YouTube upload metadata (description and tags).

## Steps

Read with the Read tool:
- `.cache/pipeline/02_selected.json`
- `.cache/pipeline/03_script.json`

Based on the content, generate the following.

**Tags (`tags`)** — 15–20 items, each 30 chars max:
- Article-specific tags: company names, product names, and technology names from the article (English only)
- Topic tags: searchable terms for the article category (e.g., `security`, `AI development`, `machine learning`)
- Fixed tags: `tech news`, `AI`, `ShortNews`, `Shorts`, `technology`, `{source}`

**Description (`description`)**:
Generate using the following format (tags are all elements of the `tags` array prefixed with `#`):

```
Source: {source_url}

---
Daily AI and tech news in 60 seconds.

#TechNews #Technology #AI #ShortNews #Shorts #{article-specific-tag-1} #{article-specific-tag-2} ...
```

- The `Source:` line must always come first
- Hashtag line: start with `#TechNews #Technology #AI #ShortNews #Shorts`, then append article-specific tags
- Do not include article summaries or bullet points

Save with the Write tool to `.cache/pipeline/05_metadata.json`:

```json
{
  "description": "generated description",
  "tags": ["tag1", "tag2", "..."],
  "generated_at": "YYYY-MM-DDTHH:MM:SS"
}
```

If JSON cannot be generated correctly, retry once.

After generation, display the description and tags for review.

---

## Poster comment generation

After saving metadata, generate a poster comment.

### Steps

1. Fetch the article via WebFetch from `source_url` and extract detailed information
2. Search for supplementary information with WebSearch (related events, background, numbers, people)
3. Generate the poster comment from the collected information

### Comment style

- Write in clear, informative English
- Supplement with details, background, numbers, and people that didn't make it into the video
- Add context from web research for a multi-angle perspective
- Target length: 150–300 words (2–3 paragraphs)
- No questions, clickbait, or emojis — calm, factual tone

### Save

Append to `.cache/youtube_comments.md` (in project root `.cache/`) using the format below. Create the file if it does not exist.

```markdown
## {Video title (no ** markup)}
URL: https://youtu.be/{video_id}
Generated: YYYY-MM-DD

{Comment body}

---
```

- If `{video_id}` is not yet known (before upload), write `URL: (not yet uploaded)`. The `/upload` command will replace this with the actual URL after upload.
- Before appending, read `.cache/youtube_comments.md` with the Read tool and skip if the same title or URL already exists (duplicate prevention).

## Prerequisites

- `.cache/pipeline/02_selected.json` must exist
- `.cache/pipeline/03_script.json` must exist
