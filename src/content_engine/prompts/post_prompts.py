"""Prompt templates for social media post generation.

Each prompt returns a system message and user message for the LLM.
Platform adaptation is handled separately in platform_adapter.py.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptPair:
    system: str
    user: str


# ---------------------------------------------------------------------------
# Base system context
# ---------------------------------------------------------------------------

SYSTEM_BASE = """\
You are a social media content writer for {brand_name}, a health optimization platform \
that provides evidence-based supplement and wellness information.

Tone: {tone_description}
Language: {language}
Target audience: Health-conscious adults interested in biohacking, supplements, and wellness.

Rules:
- Never make medical claims or promise cures
- Always frame as educational/informational
- Include disclaimers when discussing health effects
- Be engaging and approachable, not academic
- Use short paragraphs for readability
- Do NOT use markdown formatting (no **, no ##, no bullet points with *)
"""

TONE_DESCRIPTIONS = {
    "scientific_casual": (
        "Scientific yet accessible. Reference research when relevant but keep language "
        "conversational. Think 'smart friend who reads PubMed' not 'textbook professor'. "
        "Use analogies and practical examples."
    ),
    "accessible_preventive": (
        "Warm and approachable. Focus on practical wellness tips. "
        "Avoid jargon, use simple language. Think 'friendly health coach'."
    ),
}


# ---------------------------------------------------------------------------
# Post type prompts
# ---------------------------------------------------------------------------

def supplement_spotlight(
    supplement_name: str,
    supplement_info: str,
    brand_name: str = "BioMaxing",
    tone: str = "scientific_casual",
    language: str = "English",
) -> PromptPair:
    """Generate a post spotlighting a specific supplement."""
    return PromptPair(
        system=SYSTEM_BASE.format(
            brand_name=brand_name,
            tone_description=TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS["scientific_casual"]),
            language=language,
        ),
        user=f"""\
Write a Telegram channel post about {supplement_name}.

Source information:
{supplement_info}

Requirements:
- Start with an attention-grabbing hook (question, surprising fact, or common misconception)
- Explain what it does and the key evidence in 2-3 short paragraphs
- Include practical takeaway (who might benefit, typical dosage range)
- End with a disclaimer: "This is educational content, not medical advice. Consult a healthcare professional."
- Total length: 150-250 words
- Do NOT use any markdown. Use plain text only. Use emoji sparingly (1-3 max).
- Do NOT include hashtags (those will be added separately)
""",
    )


def educational_tip(
    topic: str,
    details: str = "",
    brand_name: str = "BioMaxing",
    tone: str = "scientific_casual",
    language: str = "English",
) -> PromptPair:
    """Generate an educational wellness tip post."""
    return PromptPair(
        system=SYSTEM_BASE.format(
            brand_name=brand_name,
            tone_description=TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS["scientific_casual"]),
            language=language,
        ),
        user=f"""\
Write a Telegram channel post with a practical wellness/biohacking tip about: {topic}

{"Additional context: " + details if details else ""}

Requirements:
- Start with a hook that makes the reader curious
- Give one clear, actionable tip with brief explanation of why it works
- If relevant, mention how supplements or practices can support this
- Keep it concise: 100-180 words
- End with a disclaimer if health claims are made
- Do NOT use any markdown. Plain text only. Emoji sparingly (1-3 max).
- Do NOT include hashtags
""",
    )


def myth_busting(
    myth: str,
    reality: str = "",
    brand_name: str = "BioMaxing",
    tone: str = "scientific_casual",
    language: str = "English",
) -> PromptPair:
    """Generate a myth-busting post."""
    return PromptPair(
        system=SYSTEM_BASE.format(
            brand_name=brand_name,
            tone_description=TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS["scientific_casual"]),
            language=language,
        ),
        user=f"""\
Write a Telegram channel post that busts this common health/supplement myth:

Myth: {myth}
{"Reality: " + reality if reality else ""}

Requirements:
- Start by stating the myth clearly (frame it as something people commonly believe)
- Explain why it's wrong or misleading, referencing evidence
- Give the more accurate picture
- 120-200 words
- Engaging, slightly provocative tone — challenge assumptions
- End with disclaimer if needed
- Do NOT use any markdown. Plain text only. Emoji sparingly.
- Do NOT include hashtags
""",
    )


def research_highlight(
    finding: str,
    source_info: str = "",
    brand_name: str = "BioMaxing",
    tone: str = "scientific_casual",
    language: str = "English",
) -> PromptPair:
    """Generate a post about an interesting research finding."""
    return PromptPair(
        system=SYSTEM_BASE.format(
            brand_name=brand_name,
            tone_description=TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS["scientific_casual"]),
            language=language,
        ),
        user=f"""\
Write a Telegram channel post about this research finding:

{finding}
{"Source: " + source_info if source_info else ""}

Requirements:
- Open with why this matters to the reader
- Summarize the finding in simple terms (what they studied, what they found)
- Note any limitations or caveats
- Practical implications: what does this mean for someone optimizing their health?
- 150-250 words
- End with disclaimer
- Do NOT use any markdown. Plain text only. Emoji sparingly.
- Do NOT include hashtags
""",
    )


def free_topic(
    topic: str,
    instructions: str = "",
    brand_name: str = "BioMaxing",
    tone: str = "scientific_casual",
    language: str = "English",
) -> PromptPair:
    """Generate a post on any topic with custom instructions."""
    return PromptPair(
        system=SYSTEM_BASE.format(
            brand_name=brand_name,
            tone_description=TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS["scientific_casual"]),
            language=language,
        ),
        user=f"""\
Write a Telegram channel post about: {topic}

{instructions if instructions else "Write an engaging, informative post. 150-250 words."}

General rules:
- Do NOT use any markdown formatting
- Plain text only, emoji sparingly (1-3 max)
- Do NOT include hashtags (added separately)
- Include disclaimer if health claims are made
""",
    )


# ---------------------------------------------------------------------------
# Prompt registry
# ---------------------------------------------------------------------------

PROMPT_TYPES = {
    "supplement_spotlight": supplement_spotlight,
    "educational_tip": educational_tip,
    "myth_busting": myth_busting,
    "research_highlight": research_highlight,
    "free_topic": free_topic,
}
