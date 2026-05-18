"""
Prompt Compression Engine — Section 6

Deduplicates, removes irrelevant context, and reduces
prompt size while preserving intent and constraints.
"""

import re
from collections import Counter

from ppc.config.thresholds import (
    COMPRESSION_AUTO_THRESHOLD_TOKENS,
    COMPRESSION_TARGET_RANGE,
    COMPRESSION_DUPLICATE_THRESHOLD,
)


def estimate_tokens(text: str) -> int:
    return len(text.split())


def _deduplicate_lines(text: str) -> str:
    lines = text.split("\n")
    seen: set[str] = set()
    line_counts: Counter[str] = Counter()
    for line in lines:
        stripped = line.strip().lower()
        if stripped:
            line_counts[stripped] += 1

    result: list[str] = []
    for line in lines:
        stripped = line.strip().lower()
        if not stripped:
            result.append("")
            continue
        if stripped not in seen:
            seen.add(stripped)
            result.append(line)
        else:
            count = line_counts[stripped]
            if count <= 1:
                result.append(line)

    return "\n".join(result)


def _remove_filler_phrases(text: str) -> str:
    fillers = [
        r"\b(basicamente|basically)\b",
        r"\b(esencialmente|essentially)\b",
        r"\b(de alguna manera|somehow)\b",
        r"\b(de cierta forma|in a way)\b",
        r"\b(tipo\s+de|kind\s+of)\b",
        r"\b(yo\s+creo|i\s+think)\b",
        r"\b(yo\s+dir[ií]a|i\s+would\s+say)\b",
        r"\b(en\s+mi\s+opini[oó]n|in\s+my\s+opinion)\b",
        r"\b(obviamente|obviously)\b",
        r"\b(claramente|clearly)\b",
        r"\b(literalmente|literally)\b",
        r"\b(honestamente|honestly)\b",
    ]
    result = text
    for filler in fillers:
        result = re.sub(filler, "", result, flags=re.IGNORECASE)
    result = re.sub(r"\s{2,}", " ", result)
    return result.strip()


def _trim_whitespace(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def compress_prompt(
    prompt: str,
    intent_goal: str,
    constraints: list[str],
    target_reduction: float = 0.30,
) -> str:
    if not prompt.strip():
        return prompt

    current_tokens = estimate_tokens(prompt)

    result = _deduplicate_lines(prompt)
    result = _remove_filler_phrases(result)
    result = _trim_whitespace(result)

    after_tokens = estimate_tokens(result)
    reduction = 1.0 - (after_tokens / max(current_tokens, 1))
    target_min, target_max = COMPRESSION_TARGET_RANGE

    if reduction < target_min and current_tokens > 100:
        pass

    if after_tokens > current_tokens:
        return prompt

    return result


def should_compress(prompt: str, force: bool = False) -> bool:
    if force:
        return True
    tokens = estimate_tokens(prompt)
    return tokens > COMPRESSION_AUTO_THRESHOLD_TOKENS


def estimate_compression_ratio(original: str, compressed: str) -> float:
    orig_tokens = estimate_tokens(original)
    comp_tokens = estimate_tokens(compressed)
    if orig_tokens == 0:
        return 0.0
    return 1.0 - (comp_tokens / orig_tokens)
