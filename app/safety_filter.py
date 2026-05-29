from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    requires_revision: bool = False


BLOCK_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(bypass|evade|avoid|skip|몰래|우회|회피).{0,24}(permit|license|approval|허가|면허|승인)", "permit_bypass"),
    (r"(guarantee|guaranteed|확정|보장).{0,24}(approval|permit|license|승인|허가|면허)", "guaranteed_result"),
    (r"(fake|forge|fabricate|위조|가짜).{0,24}(document|certificate|permit|문서|증명|허가)", "illegal_document"),
    (r"(hate|inferior|vermin|멸시|열등|박멸).{0,24}(christian|muslim|jew|buddhist|religious|기독교|무슬림|유대|불교|종교)", "protected_or_religious_hate"),
    (r"(address|phone|주민등록|전화번호|주소).{0,20}(dox|expose|공개|털어)", "private_data"),
    (r"(explicit sexual|pornographic|노골적 성|포르노)", "explicit_sexual"),
    (r"(bomb|terror|extremist|테러|폭탄|극단주의)", "violence_extremism"),
    (r"(target|microtarget|persuade).{0,30}(voters|religious group|유권자|종교집단)", "political_persuasion_targeting"),
)

REVISION_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(statute|case|precedent|law|판례|조문|법령).{0,18}(invent|make up|지어내|창작)", "fabricated_source"),
)


def check_text_safety(text: str) -> SafetyResult:
    normalized = re.sub(r"\s+", " ", text.lower())
    blocked = [reason for pattern, reason in BLOCK_PATTERNS if re.search(pattern, normalized)]
    revisions = [reason for pattern, reason in REVISION_PATTERNS if re.search(pattern, normalized)]
    if blocked:
        return SafetyResult(allowed=False, reasons=blocked, requires_revision=True)
    if revisions:
        return SafetyResult(allowed=False, reasons=revisions, requires_revision=True)
    return SafetyResult(allowed=True)


def assert_safe_or_raise(text: str) -> None:
    result = check_text_safety(text)
    if not result.allowed:
        raise ValueError(f"Unsafe toon request: {', '.join(result.reasons)}")
