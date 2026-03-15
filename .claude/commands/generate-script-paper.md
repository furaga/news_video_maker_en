# /gen-script-paper

Generate a 30–60 second English narration video script from the processed paper in `.cache/pipeline/02_selected.json` and save it to `.cache/pipeline/03_script.json`.

## Steps

1. Read `.cache/pipeline/02_selected.json`

2. Generate a script with the following structure:

   | Section | Purpose | Target duration |
   |---|---|---|
   | `hook` | Grab attention — viewer must want to keep watching (required techniques below) | 3–4 sec (~8–12 words) |
   | `main_1` | Research question and existing problem (why this research matters) | 7–10 sec (~18–25 words) |
   | `main_2` | Proposed method (what they did and how — the core idea) | 7–10 sec (~18–25 words) |
   | `main_3` | Experimental results and performance numbers (e.g., "27× faster than prior work") | 7–10 sec (~18–25 words) |
   | `main_4` | Practical impact and future outlook (optional) | 7–10 sec (~18–25 words) |
   | `outro` | Wrap-up (do NOT include a subscribe call-to-action — the CTA section adds that automatically) | 4–5 sec (~10–13 words) |

   **Important**:
   - Multiple sections create card-switch animations that keep the video visually dynamic.
   - If `related_research` exists in `02_selected.json`, actively use it in `main_3` or `main_4`.

### Hook techniques (required)

The hook `narration_text` must follow one of these 4 patterns. **Plain declarative sentences like "Researchers proposed a new method" are forbidden.**

| Pattern | Characteristic | English example |
|---|---|---|
| **Numbers** | Lead with a concrete improvement metric | "With just 2 GPUs, one researcher took the top spot on the global AI leaderboard." |
| **Reversal** | Wrap up a counterintuitive result in one sentence | "They improved model accuracy by 17% — without changing a single weight." |
| **Urgency** | Highlight a critical limitation of current methods | "Today's AI has a fatal blind spot that nobody's been able to fix — until now." |
| **Loop** | Open with the most surprising result, close with a question | "A solo developer beat every major lab with $200 in compute. Here's the trick." |

**Curiosity gap:** End the hook with a sentence that makes the viewer think "How?" or "Why?":
- Question: "So how did they pull it off?"
- Paradox: "And the approach is completely unlike anything tried before."
- Scale: "And the most surprising part is still ahead."

(Phrases like "More details coming up" do not fit short-form video — forbidden.)

### Section bridges (recommended)

Add a bridge sentence at the end of `main_1` through `main_3`:

- "So what exactly is the core idea behind this?"
- "And the most surprising part is still ahead."
- "Let's look at the actual numbers."

3. Estimate duration from word count (~2.5 words/sec, ~130 wpm English natural speech) and adjust to total 25–60 seconds:
   - Over 60 sec → shorten each `main_*` section and regenerate (once)
   - Under 25 sec → add more detail to each `main_*` section and regenerate (once)

4. Save to `.cache/pipeline/03_script.json` with the Write tool (**all fields are required; do not omit `image_url`, `bg_prompt`, or `annotations`**):

```json
{
  "title": "Video title (60 chars max, **keyword** markup OK)",
  "source_url": "https://arxiv.org/abs/...",
  "image_url": "",
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
- Not needed for widely known terms (AI, Google, GPU, etc.)
- For repeated terms, only annotate on first occurrence (use `{}` for subsequent sections)

### bg_prompt guidelines

Generate a **Stable Diffusion prompt in English** that visually represents the section's content.

**Rules:**
- Describe concrete objects, places, and artifacts in English
- Specify lighting and angle
- Always append `photorealistic, 8k, cinematic, no text, no people`
- Convert abstract concepts to visual objects:
  - "faster inference" → `fast flowing data streams, server rack with glowing blue lights`
  - "improved accuracy" → `target with bullseye, precision instruments, measurement tools`
  - "training / learning" → `computer screen showing training curves, neural network diagram`
  - "robot control" → `robotic arm on laboratory table, mechanical joints, sensors`
  - "natural language processing" → `text floating in digital space, word clouds, code on screen`

## Title guidelines

Generate a hook-style title optimized for YouTube Shorts papers content.

**Format examples (60 chars max):**
- `**LLM** Inference Just Got 27× Faster` — numerical impact
- `**Image Generation** Finally Beats Human Quality` — achievement
- `**Robots** Can Now Build Their Own Tools` — surprise
- `**RL-Free** Autonomous Flight Is Here` — method innovation

**Avoid:**
- Direct translations of the paper title (too technical, too long)
- Descriptive titles ("Team X proposes a new method for Y")
- Titles over 60 characters

**Title keyword markup:**
- Use `**keyword**` in the `title` field to highlight 1–2 words (shown in yellow on screen)
- Prioritize the core technical area or method name
- The `**...**` markup is for on-screen display only — stripped automatically on YouTube upload

## Quality standards

- Natural spoken English (contractions are fine: "it's", "they've", "don't")
- Short sentences, active voice
- Spell out acronyms on first use where helpful (e.g., "large language model, or LLM")
- `subtitle_text` is the key point from `narration_text` only (15 words max)
- `narration_text` serves as both the TTS input and the subtitle display text — include `**keyword**` markup directly in it
