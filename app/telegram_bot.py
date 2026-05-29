from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.config import Settings
from app.storage import save_package
from app.toon_image_prompt_generator import generate_image_prompts
from app.toon_models import ToonPackage, ToonRequest
from app.toon_slide_renderer import render_slides
from app.toon_storyboard_generator import generate_storyboard

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
        package = generate_storyboard(request)
        self.session(user_id).package = package
        save_package(package, self.settings.output_dir)
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
/status - 현재 상태
/reset - 세션 초기화

이 봇은 수동 인스타그램 업로드용 파일만 만들며 자동 게시, 승인, 팬아웃을 하지 않습니다.
"""


def create_application(settings: Settings):
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

    service = ToonBotService(settings)

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("행정법 테마 인스타툰 패키지를 만드는 검토 전용 봇입니다.\n" + HELP_TEXT)

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(HELP_TEXT)

    async def newtoon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        service.reset(update.effective_user.id)
        context.user_data["awaiting"] = "idea"
        await update.message.reply_text("아이디어나 주제를 보내주세요.")

    async def style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("스타일: " + " / ".join(STYLE_OPTIONS))

    async def panels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data["awaiting"] = "panels"
        await update.message.reply_text("컷 수를 4~8 사이 숫자로 보내주세요.")

    async def source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data["awaiting"] = "source"
        await update.message.reply_text("공식 출처 URL 또는 메모를 보내주세요. 없으면 source_needed=true로 표시됩니다.")

    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        state = service.session(update.effective_user.id)
        await update.message.reply_text(
            f"idea={bool(state.idea)}, style={state.style}, panels={state.panel_count}, "
            f"storyboard={bool(state.package)}, rendered={len(state.rendered_paths)}"
        )

    async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        service.reset(update.effective_user.id)
        await update.message.reply_text("세션을 초기화했습니다.")

    async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        package = service.generate_storyboard_only(update.effective_user.id)
        lines = [package.toon_title, package.logline]
        lines += [f"{p.panel_number}. {p.caption}" for p in package.panels]
        await update.message.reply_text("\n".join(lines))

    async def render(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        paths = service.render_current(update.effective_user.id)
        await update.message.reply_text("렌더 완료: " + ", ".join(path.name for path in paths))

    async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        state = service.session(update.effective_user.id)
        awaiting = context.user_data.get("awaiting")
        message = update.message.text.strip()
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

    application = Application.builder().token(settings.telegram_toon_bot_token).build()
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
    }.items():
        application.add_handler(CommandHandler(command, handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    return application
