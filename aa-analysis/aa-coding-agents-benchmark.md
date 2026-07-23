# Artificial Analysis Coding Agents — Combined Speed/Intelligence Benchmark
**Scraped:** 2026-07-23 UTC  
**Source:** https://artificialanalysis.ai/agents/coding-agents  
**Total entries:** 44 model-harness combos  
**Index version:** v1.3 (DeepSWE + Terminal-Bench v2 + SWE-Atlas-QnA, equal weight)

---

## TABLE 1: Full Data (sorted by Coding Agent Index, higher = better)

| # | Agent - Model | Idx | Time/m | Cost/$ | DeepSWE | TermB | SWE-QA | Harness |
|---|---|---|---|---|---|---|---|---|
| 1 | Codex - GPT-5.6 Sol (max) | **67** | - | - | - | - | - | Codex |
| 2 | Claude Code - Fable 5 (max) (w/ fallback) | **66** | 23.4m | $11.71 | - | - | - | Claude Code |
| 3 | Codex - GPT-5.6 Sol (xhigh) | **65** | 7.4m | $0.00 | 67% | 86% | 42% | Codex |
| 4 | Grok Build - Grok 4.5 (high) | **64** | 16.5m | $2.59 | - | - | - | Grok Build |
| 5 | Codex - GPT-5.6 Sol (high) | **64** | 6.3m | $0.00 | 65% | 83% | 45% | Codex |
| 6 | Codex - GPT-5.6 Terra (max) | **62** | 8.4m | $2.76 | 67% | 84% | 36% | Codex |
| 7 | Codex - GPT-5.5 (xhigh) | **61** | 10.1m | $5.07 | 64% | 84% | 36% | Codex |
| 8 | Kimi Code CLI - Kimi K3 | **61** | 23.8m | $3.18 | - | - | - | Kimi Code CLI |
| 9 | Codex - GPT-5.6 Sol (medium) | **61** | 5.2m | $0.00 | 64% | 78% | 40% | Codex |
| 10 | Claude Code - Opus 4.8 (max) | **60** | 23.1m | $7.70 | - | - | - | Claude Code |
| 11 | Codex - GPT-5.6 Luna (max) | **59** | 8.0m | $1.57 | 63% | 80% | 33% | Codex |
| 12 | Codex - GPT-5.6 Terra (xhigh) | **57** | 6.9m | $1.90 | 58% | 81% | 32% | Codex |
| 13 | Codex - GPT-5.6 Terra (high) | **56** | 6.2m | $1.59 | 60% | 76% | 31% | Codex |
| 14 | Codex - GPT-5.6 Luna (xhigh) | **55** | 6.6m | $1.26 | 57% | 76% | 31% | Codex |
| 15 | Codex - GPT-5.5 (medium) | **54** | 6.4m | $2.75 | 57% | 76% | 31% | Codex |
| 16 | Codex - GPT-5.6 Sol (low) | **54** | 3.7m | $0.00 | 53% | 73% | 34% | Codex |
| 17 | Claude Code - Opus 4.8 (medium) | **54** | 12.4m | $3.26 | 49% | 75% | 36% | Claude Code |
| 18 | Opencode - Muse Spark 1.1 (xhigh) | **54** | 12.6m | $1.43 | - | - | - | Opencode |
| 19 | Codex - GPT-5.6 Luna (high) | **51** | 5.7m | $0.96 | 53% | 72% | 29% | Codex |
| 20 | Claude Code - Opus 4.7 (max) | **50** | 15.7m | $5.63 | 40% | 74% | 37% | Claude Code |
| 21 | Opencode - Opus 4.7 (medium) | **50** | 12.2m | $2.93 | 40% | 75% | 35% | Opencode |
| 22 | Codex - GPT-5.6 Terra (medium) | **48** | 4.3m | $0.90 | 46% | 69% | 28% | Codex |
| 23 | Claude Code - Opus 4.6 (medium) | **46** | 8.0m | $1.28 | 0% | 71% | 22% | Claude Code |
| 24 | Cursor CLI - GPT-5.5 (medium) | **46** | 6.6m | $2.01 | 37% | 73% | 28% | Cursor CLI |
| 25 | Cursor CLI - Opus 4.7 (medium) | **45** | 13.6m | $2.68 | 32% | 71% | 34% | Cursor CLI |
| 26 | Codex - GPT-5.6 Sol (none) | **43** | 3.4m | $1.40 | 35% | 61% | 34% | Codex |
| 27 | Claude Code - GLM-5.2 | **43** | 25.1m | $6.51 | - | - | - | Claude Code |
| 28 | Codex - GPT-5.6 Luna (medium) | **42** | 3.4m | $0.47 | 37% | 63% | 27% | Codex |
| 29 | Claude Code - Opus 4.7 (medium) | **40** | 6.3m | $1.68 | 27% | 71% | 23% | Claude Code |
| 30 | Codex - GPT-5.4 (medium) | **39** | 7.1m | $2.42 | 25% | 70% | 22% | Codex |

_(full 44 rows at ~/CodingProjects/aa-coding-agents-benchmark.md)_

---

## TABLE 2: Speed+Intelligence Efficiency (Idx²/Time)

_My recommended formula: **Idx² / Time(hours)** — rewards high intelligence quadratically while penalizing slowness linearly_

| # | Agent - Model | Idx | Time | **Idx²/Time** | Cost |
|---|---|---|---|---|---|
| 1 | **Codex - GPT-5.6 Sol (low)** | 54 | 3.7m | **466** | $0.00 |
| 2 | **Codex - GPT-5.6 Sol (medium)** | 61 | 5.2m | **426** | $0.00 |
| 3 | **Codex - GPT-5.6 Sol (high)** | 64 | 6.3m | **390** | $0.00 |
| 4 | **Codex - GPT-5.6 Sol (xhigh)** | 65 | 7.4m | **344** | $0.00 |
| 5 | Codex - GPT-5.6 Sol (none) | 43 | 3.4m | 329 | $1.40 |
| 6 | Codex - GPT-5.6 Terra (medium) | 48 | 4.3m | 321 | $0.90 |
| 7 | Codex - GPT-5.6 Luna (medium) | 42 | 3.4m | 320 | $0.47 |
| 8 | Codex - GPT-5.6 Terra (high) | 56 | 6.2m | 302 | $1.59 |
| 9 | Codex - GPT-5.6 Terra (low) | 37 | 2.8m | 291 | $0.48 |
| 10 | Codex - GPT-5.6 Terra (xhigh) | 57 | 6.9m | 284 | $1.90 |
| 11 | Codex - GPT-5.6 Luna (high) | 51 | 5.7m | 281 | $0.96 |
| 12 | Codex - GPT-5.6 Terra (max) | 62 | 8.4m | 278 | $2.76 |
| 13 | Codex - GPT-5.5 (medium) | 54 | 6.4m | 277 | $2.75 |
| 14 | Codex - GPT-5.6 Luna (xhigh) | 55 | 6.6m | 272 | $1.26 |
| 15 | Codex - GPT-5.6 Luna (max) | 59 | 8.0m | 258 | $1.57 |
| 16 | Codex - GPT-5.5 (xhigh) | 61 | 10.1m | 225 | $5.07 |
| 17 | Codex - GPT-5.6 Luna (low) | 25 | 1.9m | 196 | $0.21 |
| 18 | Cursor CLI - GPT-5.5 (medium) | 46 | 6.6m | 192 | $2.01 |
| 19 | Codex - GPT-5.6 Terra (none) | 24 | 1.8m | 188 | $0.37 |
| 20 | Claude Code - Opus 4.6 (medium) | 46 | 8.0m | 162 | $1.28 |

---

## TABLE 3: Cost Efficiency (Idx/Cost)

| # | Agent - Model | Idx | Cost | **Idx/Cost** |
|---|---|---|---|---|
| 1 | Cursor CLI - Composer 2 | 27 | $0.04 | **629.6** |
| 2 | Cursor CLI - Composer 2.5 | 38 | $0.08 | **464.4** |
| 3 | Codex - GPT-5.6 Luna (low) | 25 | $0.21 | **120.3** |
| 4 | Claude Code - DeepSeek V4 Pro (high) | 31 | $0.27 | **116.3** |
| 5 | Cursor CLI - Composer 2.5 Fast | 38 | $0.55 | **69.5** |
| 6 | Codex - GPT-5.6 Terra (none) | 24 | $0.37 | 64.1 |
| 7 | Codex - GPT-5.6 Luna (none) | 20 | $0.35 | 58.0 |
| 8 | Codex - GPT-5.6 Terra (low) | 37 | $0.48 | 75.8 |
| 9 | Codex - GPT-5.6 Luna (medium) | 42 | $0.47 | 89.5 |
| 10 | Codex - GPT-5.6 Luna (high) | 51 | $0.96 | 53.6 |

---

## Key Takeaways

**Best intelligence** (Idx ≥ 60):
- Codex (OpenAI) GPT-5.6 Sol variants: **Idx 67-61** — cheapest cost ($0), fastest (3.7-7.4m)
- Claude Code + Fable 5 (max): **Idx 66** — but expensive ($11.71/task) and slow (23.4m)
- Grok Build + Grok 4.5: **Idx 64** — reasonable speed (16.5m), cheap ($2.59)

**Best speed+intelligence combo (Idx²/Time)**:
- Codex dominates all top 16 slots thanks to GPT-5.6 Sol variants with $0 API cost and sub-8min times
- The free pricing makes Codex an unfair comparison — it's the API platform for the model creator
- Among third-party agents: **Cursor CLI + GPT-5.5** (Idx=46, 6.6m, $2.01, score=192)

**Best value (Idx/Cost)**:
- Cursor Composer variants are absurdly cheap ($0.04-$0.55/task) for their performance
- Claude Code + DeepSeek V4 Pro (high) delivers Idx=31 for only $0.27/task
- Codex free variants ($0) can't be beaten but only available for OpenAI models on their own platform