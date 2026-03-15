# /gen-script

Generate a 30–60 second English narration video script from the processed article in `.cache/pipeline/02_selected.json` and save it to `.cache/pipeline/03_script.json`.

## Steps

1. Read `.cache/pipeline/02_selected.json`

2. Generate a script with the following structure:

   | Section | Purpose | Target duration |
   |---|---|---|
   | `hook` | Grab attention — viewer must want to keep watching (required techniques below) | 3–4 sec (~8–12 words) |
   | `main_1` | News overview and background | 7–10 sec (~18–25 words) |
   | `main_2` | Details and technical content | 7–10 sec (~18–25 words) |
   | `main_3` | Related information and industry impact | 7–10 sec (~18–25 words) |
   | `main_4` | Additional context or future outlook (optional) | 7–10 sec (~18–25 words) |
   | `outro` | Wrap-up (do NOT include a subscribe call-to-action — the CTA section adds that automatically) | 4–5 sec (~10–13 words) |

   **Important**:
   - Multiple sections create card-switch animations that keep the video visually dynamic.
   - If `related_research` exists in `02_selected.json`, actively use it in `main_3` or `main_4`.

### Hook techniques (required)

The hook `narration_text` must follow one of these 4 patterns. **Plain declarative sentences like "Company X announced Y" are forbidden.**

| Pattern | Characteristic | English example |
|---|---|---|
| **Numbers** | Lead with a concrete statistic to convey scale instantly | "With just 2 GPUs, one developer took the number one spot on the global leaderboard." |
| **Reversal** | Wrap up an unexpected outcome in one sentence | "The US military's own hacking tool was actually being used by Russian spies." |
| **Urgency** | Build tension through time, speed, or loss | "Overnight, millions of developers worldwide lost access to a service they depend on every day." |
| **Loop** | Open with the most surprising fact, close with a question | "A solo developer beat every major AI lab — with $200 in cloud credits. Here's how." |

**Curiosity gap:** End the hook with a sentence that makes the viewer think "Why?" or "What happened next?":
- Question: "But why did this happen?"
- Paradox: "And the reason is not what you'd expect."
- Scale: "And that's just the beginning."
- Negation: "But this story is about much more than just that."

(Phrases like "More details coming up" or "Stay tuned" do not fit short-form video — forbidden.)

### Section bridges (recommended)

Add a bridge sentence at the end of `main_1` through `main_3` to reduce swipe-away temptation:

- "But what exactly was the data being used for?"
- "And the most surprising part is still ahead."
- "So how bad was the actual damage?"

3. Estimate duration from word count (~2.5 words/sec, ~130 wpm English natural speech) and adjust to total 25–60 seconds:
   - Over 60 sec → shorten each `main_*` section and regenerate (once)
   - Under 25 sec → add more detail to each `main_*` section and regenerate (once)

4. Save to `.cache/pipeline/03_script.json` with the Write tool (**all fields are required; do not omit `image_url`, `bg_prompt`, or `annotations`**):

```json
{
  "title": "Video title (60 chars max, **keyword** markup OK)",
  "source_url": "https://...",
  "image_url": "https://... (copied from 02_selected.json; empty string if missing)",
  "total_duration_sec": 45.0,
  "sections": [
    {
      "type": "hook",
      "narration_text": "English narration with **keyword** markup for visual highlighting",
      "subtitle_text": "Key point only (15 words max)",
      "bg_prompt": "Stable Diffusion prompt in English (see guidelines below)",
      "annotations": {},
      "estimated_duration_sec": 4.0
    },
    {
      "type": "main_1",
      "narration_text": "...",
      "subtitle_text": "...",
      "bg_prompt": "...",
      "annotations": {"LLM": "large language model"},
      "estimated_duration_sec": 9.0
    },
    {
      "type": "main_2",
      "narration_text": "...",
      "subtitle_text": "...",
      "bg_prompt": "...",
      "annotations": {},
      "estimated_duration_sec": 9.0
    },
    {
      "type": "main_3",
      "narration_text": "...",
      "subtitle_text": "...",
      "bg_prompt": "...",
      "annotations": {},
      "estimated_duration_sec": 9.0
    },
    {
      "type": "outro",
      "narration_text": "Closing narration (no subscribe call-to-action)",
      "subtitle_text": "...",
      "bg_prompt": "...",
      "annotations": {},
      "estimated_duration_sec": 5.0
    }
  ]
}
```

### annotations guidelines

Add brief English explanations for technical terms and acronyms in `annotations`.

**Rules:**
- Key must match a term wrapped in `**keyword**` markup in `narration_text`
- Value is a short English description (aim for 5 words or fewer)
- Only for acronyms and technical jargon a general viewer may not know
- Not needed for widely known terms (Google, YouTube, AI, etc.)
- For repeated terms, only annotate on first occurrence (use `{}` for subsequent sections)

### bg_prompt guidelines

Generate a **Stable Diffusion prompt in English** that visually represents the section's narration content.

**Rules:**
- Describe concrete objects, places, and artifacts in English (e.g., `PS5 DualSense controller on wooden desk, glowing circuit board`)
- Specify lighting and angle (e.g., `soft ambient lighting, close-up, eye-level shot`)
- Always append `photorealistic, 8k, cinematic, no text, no people`
- Convert abstract concepts to visual objects:
  - "security vulnerability" → `digital padlock with crack, glowing circuit board`
  - "hacking" → `computer screen with code, dark room with monitors`
  - "bounty" → `dollar bills, bank check, money`

## Title guidelines

Generate a hook-style title optimized for YouTube Shorts.

**Format examples (60 chars max):**
- `**OpenAI** Just Changed Everything` — company + impact
- `The AI That Beat Every Human at This` — intrigue
- `Engineers Are Losing Jobs to **This Tool**` — personal stakes
- `**Google** Quietly Did Something Huge` — insider feel

**Avoid:**
- Descriptive titles ("Company X announced a new feature for Y")
- Titles over 60 characters (displayed at the top of the YouTube Shorts screen)

**Title keyword markup:**
- Use `**keyword**` in the `title` field to highlight 1–2 words (shown in yellow on screen)
- Prioritize company names or product names
- The `**...**` markup is for on-screen display only — stripped automatically on YouTube upload

## Quality standards

- Natural spoken English (contractions are fine: "it's", "they've", "don't")
- Short sentences, active voice
- Spell out acronyms on first use where helpful (e.g., "large language model, or LLM")
- `subtitle_text` is the key point from `narration_text` only (15 words max)
- `narration_text` serves as both the TTS input and the subtitle display text — include `**keyword**` markup directly in it
