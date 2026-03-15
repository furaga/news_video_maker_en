# /run-pipeline

Run all stages sequentially from news/paper fetch through YouTube upload.

## Arguments

- `--mode news|paper`: execution mode (default: `news`)
  - `news`: tech news article mode
  - `paper`: latest research paper mode (arXiv + HF Daily Papers)
- `--dry-run` / `--skip-upload`: run through video generation, skip YouTube upload
- `--from-stage N`: resume from stage N (1=fetch, 2=process, 3=script, 4=video, 5=upload)
- `--run-id ID`: run ID (auto-generated if omitted). Cache paths become `.cache/pipeline/{run_id}/`
- `--publish-at ISO8601`: YouTube scheduled publish time (UTC ISO 8601). e.g., `2026-03-12T23:00:00Z`

## Execution steps

Check arguments, determine the starting stage and mode, then run each stage in sequence.

If `--run-id` is specified, replace `.cache/pipeline/` with `.cache/pipeline/{run_id}/` in all file paths below.

### Stage 1: Fetch

**`--mode news` (default)**, run /fetch-news:
```bash
cd /c/Users/furag/Documents/prog/python/news_video_maker_en && uv run python -m news_video_maker.fetcher.rss
```
After completion, read `.cache/pipeline/{run_id}/01_articles.json`. If the array is empty (`[]`), skip subsequent stages and write "No new articles: only previously processed articles found" to report.md, then stop.

**`--mode paper`**, run /fetch-papers:
```bash
cd /c/Users/furag/Documents/prog/python/news_video_maker_en && uv run python -m news_video_maker.fetcher.paper
```
After completion, read `.cache/pipeline/{run_id}/01_papers.json`. If the array is empty (`[]`), skip subsequent stages and write "No new papers: only previously processed papers found" to report.md, then stop.

(The `PIPELINE_RUN_ID` environment variable is already set; Python automatically writes to the correct directory.)

### Stage 2: Select and generate English summary

If `--from-stage` ≤ 2:

**`--mode news`**: run the same steps as the `/process` command:

1. **Get past titles (duplicate prevention)**:
   - List all `02_selected.json` files in `.cache/pipeline/`:
     ```bash
     ls .cache/pipeline/*/02_selected.json 2>/dev/null
     ```
   - Read the found files (excluding the current `{run_id}`) and collect `title` (English) and `english_title` as `past_titles`
   - If no files found, set `past_titles = []`

2. **Score articles and select the best one**:
   - Read `.cache/pipeline/{run_id}/01_articles.json`
   - Score each article 1–10 using the following **viewership patterns**:

   **Positive factors (tend to drive higher views):**
   - Personal experience / real story format: **+3 pts**
   - Involves money, salary, reward, or prize: **+2 pts**
   - Personally relevant (affects one's own job, phone, or daily services): **+2 pts**
   - Industry drama (notable resignation, protest, conflict, scandal): **+2 pts**
   - Has surprise, irony, or a paradoxical twist: **+1 pt**

   **Negative factors (tend to drive lower views):**
   - Too abstract or generic ("X changed everything"): **-2 pts**
   - Regional or niche company news unfamiliar to a global English audience: **-2 pts**
   - Pure product review / spec announcement with no human drama: **-1 pt**
   - Topic, company, or technology overlaps with a `past_titles` entry: **-10 pts**

   Select the highest-scoring article.

3. **Generate English title, summary, and key points**

4. **Save to `.cache/pipeline/{run_id}/02_selected.json`** with the Write tool

**`--mode paper`**: run the same steps as the `/process-paper` command:

1. **Get past titles (duplicate prevention)**: same as news mode above

2. **Score papers and select the best one**:
   - Read `.cache/pipeline/{run_id}/01_papers.json`
   - Score each paper 1–10 (HF listing +2 pts, technical novelty, practical usefulness, accessibility)
   - Overlap with `past_titles`: **-3 pts** penalty
   - Select highest-scoring paper (tie-break: most `hf_upvotes`, then newest)

3. **Generate English title, summary, and key points**

4. **Save to `.cache/pipeline/{run_id}/02_selected.json`** with the Write tool

### Stage 3: Script generation

If `--from-stage` ≤ 3:
- Read `.cache/pipeline/{run_id}/02_selected.json`

**`--mode news`**: generate the script following the same steps as `/gen-script`.
**`--mode paper`**: generate the script following the same steps as `/gen-script-paper` (section structure optimized for papers).

- Save to `.cache/pipeline/{run_id}/03_script.json` with the Write tool

### Stage 4: Video generation

If `--from-stage` ≤ 4:
```bash
cd /c/Users/furag/Documents/prog/python/news_video_maker_en && uv run python -m news_video_maker.video.composer
```
(The `PIPELINE_RUN_ID` environment variable is already set; Python reads from the correct directory automatically.)

### Stage 4.5: Video validation (technical check + frame extraction)
After stage 4 completes:
```bash
cd /c/Users/furag/Documents/prog/python/news_video_maker_en && uv run python -m news_video_maker.video.validator
```
- If exit code is 1 (`ok: false`): record the error in report.md and stop the pipeline
- On success: `.cache/pipeline/04_validation.json` and `.cache/pipeline/frames/` are created

### Stage 4.6: Video validation (visual check)
Run the `/validate-video` command for Claude Code to visually inspect the frames.
- If visual check fails, record the error in report.md and stop the pipeline

### Stage 5: YouTube upload
If not `--dry-run` and `--from-stage` ≤ 5:

1. **Generate metadata**: run the same steps as `/gen-metadata` and save to `.cache/pipeline/{run_id}/05_metadata.json`

2. **YouTube upload (Python)**:

   If `--publish-at` is specified:
   ```bash
   cd /c/Users/furag/Documents/prog/python/news_video_maker_en && uv run python -m news_video_maker.uploader.youtube --publish-at {publish_at}
   ```
   Otherwise:
   ```bash
   cd /c/Users/furag/Documents/prog/python/news_video_maker_en && uv run python -m news_video_maker.uploader.youtube
   ```

## After completion

After all stages complete, generate `report.md` with the Write tool:

```markdown
# Pipeline Report: YYYY-MM-DD HH:MM

## Run ID
- run_id: {run_id}
- mode: news / paper

## Result: Success / Failure

## Fetched count
- Total: X items (news: article count / paper: paper count)

## Selected content
- Title: ...
- English title: ...
- Source: ... (news: techcrunch etc. / paper: arxiv)
- Score: ...

## Generated video
- Path: output/YYYYMMDD_HHMMSS.mp4
- Duration: XX sec

## YouTube
- URL: https://youtu.be/xxxxx (or "skipped" if --dry-run)
- Privacy: unlisted

## Errors (if any)
- ...
```

## Error handling

- On stage failure, record the error in report.md and stop the pipeline
- Use `--from-stage` to re-run from the failed stage
