from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.config import Settings
from app.storage import save_package
from app.toon_image_prompt_generator import generate_image_prompts
from app.toon_models import ToonPackage, ToonRequest
from app.toon_slide_renderer import render_slides
from app.toon_storyboard_generator import OpenAITextProvider, generate_storyboard

logger = logging.getLogger(__name__)

STYLE_OPTIONS = ["괴짜 행정툰", "풍자형", "실무형", "초현실 행정상담", "귀여운 캐릭터형"]


@dataclass
class SessionState:
    idea: str | None = None
    style: str = STYLE_OPTIONS[0]
    panel_count: int = 6
    source_url: str | None = None
    package: ToonPackage | None = None
    rendered_paths: list[Path] = field(default_factory=list)


class ToonBotService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.sessions: dict[int, SessionState] = {}

    def text_provider(self):
        if not self.settings.openai_api_key:
            return None
        return OpenAITextProvider(self.settings.openai_api_key, self.settings.openai_text_model)

    def session(self, user_id: int) -> SessionState:
        return self.sessions.setdefault(user_id, SessionState(panel_count=self.settings.default_panel_count))

    def reset(self, user_id: int) -> None:
        self.sessions.pop(user_id, None)

    def build_request(self, user_id: int) -> ToonRequest:
        state = self.session(user_id)
        if not state.idea:
            raise ValueError("idea is required before generation")
        return ToonRequest(
            user_id=user_id,
            idea=state.idea,
            tone=state.style,
            panel_count=state.panel_count,
            source_url_optional=state.source_url,
        )

    def generate_storyboard_only(self, user_id: int) -> ToonPackage:
        request = self.build_request(user_id)
        logger.info("storyboard_generation_started request_id=%s model=%s", request.request_id, self.settings.openai_text_model)
        package = generate_storyboard(request, self.text_provider())
        self.session(user_id).package = package
        save_package(package, self.settings.output_dir)
        logger.info(
            "storyboard_generation_completed request_id=%s source_needed=%s review_only=%s publish_ready=%s",
            package.request_id,
            package.source_needed,
            package.review_only,
            package.publish_ready,
        )
        return package

    def render_current(self, user_id: int) -> list[Path]:
        package = self.session(user_id).package
        if package is None:
            package = self.generate_storyboard_only(user_id)
        prompts = generate_image_prompts(package)
        package.image_prompt_summaries = prompts
        paths = render_slides(package, self.settings.output_dir)
        self.session(user_id).rendered_paths = paths
        return paths


HELP_TEXT = """사용법:
/newtoon - 새 행정툰 요청 시작
/style - 스타일 선택
/panels - 4~8컷 선택
/source - 공식 출처 URL 또는 메모
/generate - 스토리보드만 생성
/render - 이미지 슬라이드 렌더링
/ping - 실행 상태 확인
/status - 현재 상태
/reset - 세션 초기화

이 봇은 수동 인스타그램 업로드용 파일만 만들며 자동 게시, 승인, 팬아웃을 하지 않습니다.
"""


COMMAND_NAMES = ("start", "help", "status", "newtoon", "style", "panels", "source", "generate", "render", "reset", "ping")
TOKENISH_RE = re.compile(r"(bot)[A-Za-z0-9:_-]+|sk-[A-Za-z0-9_-]{20,}")


def _redact(text: str) -> str:
    return TOKENISH_RE.sub(r"\1<redacted>", text)


def _log_command(command: str, update) -> None:
    chat_id = update.effective_chat.id if update.effective_chat else None
    user_id = update.effective_user.id if update.effective_user else None
    logger.info("telegram command received command=%s chat_id=%s user_id=%s", command, chat_id, user_id)


def create_application(settings: Settings):
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

    service = ToonBotService(settings)

    async def post_init(application) -> None:
        me = await application.bot.get_me()
        logger.info("bot_identity bot_username=%s bot_id=%s", me.username, me.id)
        await application.bot.delete_webhook(drop_pending_updates=False)
        logger.info("telegram webhook cleared for polling drop_pending_updates=False")

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        error = context.error
        logger.error("telegram error class=%s message=%s", error.__class__.__name__, _redact(str(error)))

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("start", update)
        await update.message.reply_text("행정법 테마 인스타툰 패키지를 만드는 검토 전용 봇입니다.\n" + HELP_TEXT)

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("help", update)
        await update.message.reply_text(HELP_TEXT)

    async def newtoon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("newtoon", update)
        service.reset(update.effective_user.id)
        context.user_data["awaiting"] = "idea"
        await update.message.reply_text("아이디어나 주제를 보내주세요.")

    async def style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("style", update)
        await update.message.reply_text("스타일: " + " / ".join(STYLE_OPTIONS))

    async def panels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("panels", update)
        context.user_data["awaiting"] = "panels"
        await update.message.reply_text("컷 수를 4~8 사이 숫자로 보내주세요.")

    async def source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("source", update)
        context.user_data["awaiting"] = "source"
        await update.message.reply_text("공식 출처 URL 또는 메모를 보내주세요. 없으면 source_needed=true로 표시됩니다.")

    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("status", update)
        state = service.session(update.effective_user.id)
        await update.message.reply_text(
            f"idea={bool(state.idea)}, style={state.style}, panels={state.panel_count}, "
            f"storyboard={bool(state.package)}, rendered={len(state.rendered_paths)}"
        )

    async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("reset", update)
        service.reset(update.effective_user.id)
        await update.message.reply_text("세션을 초기화했습니다.")

    async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("generate", update)
        package = service.generate_storyboard_only(update.effective_user.id)
        lines = [package.toon_title, package.logline]
        lines += [f"{p.panel_number}. {p.caption}" for p in package.panels]
        await update.message.reply_text("\n".join(lines))

    async def render(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("render", update)
        paths = service.render_current(update.effective_user.id)
        await update.message.reply_text("렌더 완료: " + ", ".join(path.name for path in paths))

    async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        _log_command("ping", update)
        await update.message.reply_text("pong: Instatoon bot is running")

    async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        state = service.session(update.effective_user.id)
        awaiting = context.user_data.get("awaiting")
        message = update.message.text.strip()
        logger.info("telegram text received awaiting=%s chat_id=%s user_id=%s", awaiting, update.effective_chat.id, update.effective_user.id)
        if awaiting == "panels":
            state.panel_count = max(4, min(8, int(message)))
        elif awaiting == "source":
            state.source_url = message
        elif message in STYLE_OPTIONS:
            state.style = message
        else:
            state.idea = message
        context.user_data["awaiting"] = None
        await update.message.reply_text("저장했습니다. /generate 로 스토리보드를 만들 수 있습니다.")

    logger.info("telegram application building")
    application = Application.builder().token(settings.telegram_toon_bot_token).post_init(post_init).build()
    for command, handler in {
        "start": start,
        "help": help_command,
        "newtoon": newtoon,
        "style": style,
        "panels": panels,
        "source": source,
        "status": status,
        "reset": reset,
        "generate": generate,
        "render": render,
        "ping": ping,
    }.items():
        application.add_handler(CommandHandler(command, handler))
    logger.info("telegram handlers registered commands=%s", ",".join(COMMAND_NAMES))
    application.add_error_handler(error_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    return application
