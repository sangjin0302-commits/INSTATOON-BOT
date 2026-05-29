from __future__ import annotations

DEFAULT_FICTIONAL_AGENCY = "이상현상 행정청"
DEFAULT_DEPARTMENT = "괴현상 허가과"
TAGLINE = "기적, 마법, 몬스터도 절차 앞에서는 민원입니다."

CORE_CONCEPT = (
    "Translate absurd fictional ideas into real-world administrative procedure checkpoints "
    "through modern fictional/parody administrative-law framing."
)

STYLE_RULES: tuple[str, ...] = (
    "Use fictional/parody framing.",
    "Treat religious, mythic, historical, and fictional figures respectfully.",
    "Prefer generic/parody phrasing for copyrighted franchises.",
    "Do not claim historical or legal accuracy without official source.",
    "Do not invent statutes, cases, precedents, adjudications, or official sources.",
    "If no official source is provided, set source_needed=true.",
    "Do not provide illegal evasion instructions.",
    "Do not guarantee permits, licenses, approvals, or outcomes.",
    "Korean dialogue must be overlaid locally with Pillow, not embedded in generated images.",
    "Do not generate images unless explicitly enabled later.",
)

GENERIC_APPLICANT_EXAMPLES: tuple[str, ...] = (
    "fictional miracle worker",
    "monster trainer",
    "dragon keeper",
    "ghost landlord",
    "alien vendor",
    "wizard researcher",
    "time traveler",
)


def style_bible_text() -> str:
    examples = ", ".join(GENERIC_APPLICANT_EXAMPLES)
    rules = "\n".join(f"- {rule}" for rule in STYLE_RULES)
    return "\n".join(
        [
            f"Default fictional agency: {DEFAULT_FICTIONAL_AGENCY}",
            f"Default department: {DEFAULT_DEPARTMENT}",
            f"Tagline: {TAGLINE}",
            f"Core concept: {CORE_CONCEPT}",
            f"Allowed episode applicants: {examples}.",
            "Rules:",
            rules,
        ]
    )
