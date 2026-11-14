# Prompt versions (M3)

Each version is a file in this folder. The cache key of every LLM call contains the prompt version, so a new version never reuses
answers of an older one. Versions are never edited after they have been used; a change means a new file.

| version | date | change | pilot result |
|---|---|---|---|
| extract_v1 | 2026-10-19 | first version (quote-exact spans, numbers only from the span, fixed condition conversions, gravity class by words) | not run yet |
| verify_v1 | 2026-10-19 | first version of the separate support-check prompt (supported / partial / unsupported) | not run yet |
