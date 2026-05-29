# Instagram Toon Telegram Bot Design

## Purpose

This standalone Telegram bot creates Instagram toon packages that translate absurd
fictional ideas into real-world administrative procedure checkpoints.

Default fictional agency: **이상현상 행정청**
Default department: **괴현상 허가과**
Tagline: **기적, 마법, 몬스터도 절차 앞에서는 민원입니다.**

It is separate from Auto-Sns, Market Analyze, Claude blog generation, and any
cardnews bot. It does not approve, publish, fan out, mutate external approval
state, or post to Instagram.

## Characters

- 백절차: tired but precise main administrative officer.
- 나민원: junior investigator who asks common-sense questions.
- 꼼수요정: trickster who suggests illegal shortcuts and is always corrected.

Episode applicants can include fictional miracle workers, monster trainers,
dragons, ghosts, aliens, wizards, time travelers, and other parody figures.
Use generic/parody phrasing for franchise-like ideas, such as "monster training
center" instead of protected brand names.

## Architecture

- `app/toon_style_bible.py`: core concept, agency, department, tagline, style rules.
- `app/character_registry.py`: recurring character definitions.
- `app/config.py`: environment loading with no raw token logging.
- `app/telegram_bot.py`: Telegram command and session scaffold.
- `app/toon_models.py`: Pydantic request, package, and panel schemas.
- `app/toon_prompt_builder.py`: JSON-only storyboard prompt builder.
- `app/toon_storyboard_generator.py`: fake-first text provider and optional OpenAI adapter.
- `app/toon_image_prompt_generator.py`: clean panel image prompt generation.
- `app/toon_image_generator.py`: disabled-by-default image provider adapter.
- `app/toon_slide_renderer.py`: Pillow-based local slide rendering.
- `app/safety_filter.py`: pre/post generation safety checks.
- `app/storage.py`: local JSON artifact storage under `outputs/<request_id>/`.

## Telegram Commands

- `/start`: explains the bot purpose.
- `/newtoon`: starts a new toon request flow.
- `/style`: lets the user choose 괴짜 행정툰, 풍자형, 실무형, 초현실 행정상담, or 귀여운 캐릭터형.
- `/panels`: chooses 4-8 panels.
- `/source`: accepts an optional official source URL or note.
- `/generate`: generates storyboard only.
- `/render`: renders local placeholder slide images.
- `/help`: usage.
- `/status`: current job state.
- `/reset`: clears the current session.

Buttons or commands for publishing, automatic Instagram upload, approval, or
fanout are intentionally out of scope.

## OpenAI Flow

Text generation is routed through `TextProvider`. Tests use `FakeTextProvider`;
live OpenAI text generation requires explicit future approval and explicit
construction of `OpenAITextProvider`. The prompt requires structured JSON matching
`ToonPackage`.

Image generation is routed through `ImageProvider`, but `ENABLE_IMAGE_GENERATION=false`
by default. This update does not generate images and keeps placeholder rendering
only. Korean dialogue is overlaid locally with Pillow, not embedded in generated
image prompts.

## Manual Instagram Upload Only

The output is a local folder of PNG files and JSON artifacts. The user reviews the
result and manually uploads to Instagram. No Instagram API integration exists.

## Safety Rules

The bot blocks or requires revision for permit/license bypass instructions,
guaranteed approvals, illegal conduct instructions, fabricated legal authority,
hateful or degrading protected-class or religious framing, private personal data,
explicit sexual content, violence/extremism, and political persuasion targeting.

It allows respectful fictional satire, including religious, mythic, historical, or
fictional characters as educational framing. It must not imply that religion,
miracles, money, fame, or influence bypass administrative procedure. If no official
source is provided, `source_needed=true` and a caution is included. Do not claim
historical or legal accuracy without official source support.

## Environment Variables

Required:

- `TELEGRAM_TOON_BOT_TOKEN=`
- `OPENAI_API_KEY=`

Optional:

- `OPENAI_TEXT_MODEL=`
- `OPENAI_IMAGE_MODEL=`
- `OUTPUT_DIR=outputs`
- `DEFAULT_PANEL_COUNT=6`
- `ENABLE_IMAGE_GENERATION=false`
- `MAX_DAILY_GENERATIONS=`
- `ADMIN_USER_IDS=`

## Safe Sample

Input:

> 예수님이 주류 무한 제조 허가를 만들려면 어떻게 해야 할까?

Safe handling:

- Treat the figure as a respectful fictional miracle-worker applicant at 이상현상 행정청.
- 백절차 explains that miracles do not bypass jurisdiction, license category, facility,
  labeling, safety, inspection, tax, or reporting checkpoints.
- 나민원 asks practical questions readers might ask.
- 꼼수요정 may suggest "skip inspection by miracle," but 백절차 immediately corrects it
  as not allowed.
- Include a caution: requirements vary by jurisdiction and facts; official source
  review is needed; no approval outcome is guaranteed.

Example panel outline:

1. The fictional miracle-worker pulls a number ticket at 괴현상 허가과.
2. 백절차 classifies whether the activity is manufacturing, sale, or serving.
3. 나민원 asks why a miracle still needs facility and hygiene checks.
4. 꼼수요정 suggests a shortcut and is corrected.
5. Labels, tax reporting, inspections, and safety records become a checklist.
6. Final caption says official sources must be checked before any real action.

## Local Run

```powershell
pip install -e .[dev]
copy .env.example .env
python -m app.main
```

## Tests

```powershell
pytest
python -m py_compile app\*.py
ruff check .
git diff --check
git diff --cached --check
```

## Future Roadmap

- Add explicit user approval for live OpenAI storyboard dry-runs.
- Add revision loops for individual panels.
- Add ZIP packaging for rendered slides.
- Add optional source attachment parsing.
- Add a future handoff design only if explicitly requested.
