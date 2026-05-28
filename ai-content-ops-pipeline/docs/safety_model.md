# Safety Model — AI Content Ops Pipeline

An always-on content engine should never post on its own. Safety here is about
keeping a human at the one irreversible step.

## SAFE MODE (default)

- The posting layer (`src/posting_safety.py`) defaults to `safe_mode=True`.
- In safe mode it **only** updates local files (queue / log / calendar) and, in
  the operator UI's own words, *"never opens a network socket."*
- Real publishing requires **both** `safe_mode=False` **and** a per-platform
  unlock. Skeleton publishers refuse otherwise.

![Posting safety](../assets/posting_safety.png)

## Other guarantees

- **No fabricated claims.** No invented testimonials, case studies, or revenue
  figures anywhere in the system.
- **No spend.** No paid APIs (local LLM + local TTS + FFmpeg).
- **Protected folders.** Raw footage, brand assets, finished videos, and post
  history are archived, never deleted. `pipeline_state.advance` only moves files
  forward.
- **Secrets out of source.** Tokens live in a local `.env` (git-ignored);
  configs ship as `.example.yaml` with names only.

## Honest scale

Personal brand. Manual-posting flow is the default. No audience-scale or revenue
claims are made.
