from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToonCharacter:
    name: str
    role: str
    description: str
    prompt_description: str


BAEK_JEOLCHA = ToonCharacter(
    name="백절차",
    role="main explainer",
    description="A tired but precise administrative officer at 괴현상 허가과.",
    prompt_description=(
        "Baek Jeolcha, tired but precise Korean administrative officer, modern office attire, "
        "calm expression, checklist clipboard"
    ),
)

NA_MINWON = ToonCharacter(
    name="나민원",
    role="junior investigator",
    description="A junior investigator who asks common-sense questions for readers.",
    prompt_description=(
        "Na Minwon, junior investigator, curious expression, field notebook, practical posture"
    ),
)

KOMSU_YOJEONG = ToonCharacter(
    name="꼼수요정",
    role="safety foil",
    description="A trickster who suggests illegal shortcuts and is always corrected.",
    prompt_description=(
        "Komsu fairy, tiny trickster safety foil, mischievous but non-threatening, "
        "always corrected by officials"
    ),
)

DEFAULT_CHARACTERS: tuple[ToonCharacter, ...] = (
    BAEK_JEOLCHA,
    NA_MINWON,
    KOMSU_YOJEONG,
)


def character_registry_text() -> str:
    return "\n".join(
        f"- {character.name} ({character.role}): {character.description}"
        for character in DEFAULT_CHARACTERS
    )


def character_prompt_text() -> str:
    return "; ".join(character.prompt_description for character in DEFAULT_CHARACTERS)
