"""
Discord Embed 메시지 빌더
"""
from datetime import datetime

# Embed 색상 코드
COLOR_SUCCESS = 0x2ECC71  # 초록
COLOR_ERROR = 0xE74C3C    # 빨강
COLOR_WARNING = 0xF39C12  # 주황
COLOR_INFO = 0x3498DB     # 파랑
COLOR_CLOSURE = 0x95A5A6  # 회색


class DiscordMessageBuilder:
    """Discord Embed payload 생성기"""

    @classmethod
    def daily_summary(
        cls,
        total_notices: int,
        new_saved: int,
        already_exists: int,
        parse_success: int,
        parse_total: int,
        errors: list[str],
        closures: list[dict],
        duration_seconds: float,
        crawled_notices: list[dict] = None,
        saved_items: list[dict] = None,
    ) -> dict:
        """일일 크롤링 요약 리포트"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        has_errors = bool(errors)
        color = COLOR_WARNING if has_errors else COLOR_SUCCESS
        status = "⚠️ 일부 오류 발생" if has_errors else "✅ 정상 완료"

        fields = [
            {"name": "파싱 성공", "value": f"{parse_success}/{parse_total}건", "inline": True},
            {"name": "중복 스킵", "value": f"{already_exists}건", "inline": True},
            {"name": "소요 시간", "value": f"{duration_seconds:.1f}초", "inline": True},
        ]

        # 크롤링 공지 목록
        if crawled_notices:
            notice_lines = [
                f"• [{n['facility_name']}] {n['title'][:40]}"
                for n in crawled_notices[:10]
            ]
            if len(crawled_notices) > 10:
                notice_lines.append(f"... 외 {len(crawled_notices) - 10}건")
            fields.append({
                "name": f"📋 크롤링 공지 ({total_notices}건)",
                "value": "\n".join(notice_lines),
                "inline": False,
            })
        else:
            fields.append({
                "name": "📋 크롤링 공지",
                "value": f"{total_notices}건",
                "inline": True,
            })

        # 신규 저장 목록
        if saved_items:
            saved_lines = [
                f"• [{s['facility_name']}] {s['valid_month']} — {s['source_notice_title'][:30]}"
                for s in saved_items[:10]
            ]
            if len(saved_items) > 10:
                saved_lines.append(f"... 외 {len(saved_items) - 10}건")
            fields.append({
                "name": f"🆕 신규 저장 ({new_saved}건)",
                "value": "\n".join(saved_lines),
                "inline": False,
            })
        else:
            fields.append({
                "name": "🆕 신규 저장",
                "value": f"{new_saved}건",
                "inline": True,
            })

        if closures:
            closure_lines = [
                f"• {c['facility_name']} ({c['valid_month']})"
                for c in closures
            ]
            fields.append({
                "name": "🚫 휴장 감지",
                "value": "\n".join(closure_lines),
                "inline": False,
            })

        if errors:
            error_lines = [f"• {e}" for e in errors[:5]]
            if len(errors) > 5:
                error_lines.append(f"... 외 {len(errors) - 5}건")
            fields.append({
                "name": f"🔴 에러 ({len(errors)}건)",
                "value": "\n".join(error_lines),
                "inline": False,
            })

        return {
            "embeds": [{
                "title": f"📊 일일 크롤링 리포트 — {now}",
                "description": status,
                "color": color,
                "fields": fields,
            }]
        }

    @classmethod
    def new_schedule_saved(cls, data: dict) -> dict:
        """새 스케줄 데이터 저장 알림"""
        facility_name = data.get("facility_name", "알 수 없음")
        valid_month = data.get("valid_month", "")
        source_url = data.get("source_url", "")
        schedules = data.get("schedules", [])
        title = data.get("source_notice_title", "")

        schedule_parts = []
        for s in schedules:
            day_type = s.get("day_type", "")
            session_count = len(s.get("sessions", []))
            schedule_parts.append(f"{day_type}({session_count}타임)")
        schedule_summary = ", ".join(schedule_parts) if schedule_parts else "없음 (휴장 가능)"

        description = (
            f"**시설:** {facility_name}\n"
            f"**적용월:** {valid_month}\n"
            f"**스케줄:** {schedule_summary}"
        )

        if source_url:
            link_text = title[:50] if title else "원문 보기"
            description += f"\n**공지:** [{link_text}]({source_url})"

        return {
            "embeds": [{
                "title": "🆕 새 스케줄 저장",
                "description": description,
                "color": COLOR_INFO,
            }]
        }

    @classmethod
    def error_alert(cls, stage: str, error_message: str, context: str = "") -> dict:
        """에러/장애 알림"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        description = (
            f"**단계:** {stage}\n"
            f"**시각:** {now}\n"
            f"**에러:** ```{error_message[:500]}```"
        )
        if context:
            description += f"\n**컨텍스트:** {context}"

        return {
            "embeds": [{
                "title": "🚨 파이프라인 에러",
                "description": description,
                "color": COLOR_ERROR,
            }]
        }

    @classmethod
    def pool_closure_detected(
        cls, facility_name: str, valid_month: str, reason: str, source_url: str = ""
    ) -> dict:
        """수영장 휴장 감지 알림"""
        description = (
            f"**시설:** {facility_name}\n"
            f"**기간:** {valid_month}\n"
            f"**사유:** {reason}"
        )
        if source_url:
            description += f"\n[원문 보기]({source_url})"

        return {
            "embeds": [{
                "title": "🚫 수영장 휴장 감지",
                "description": description,
                "color": COLOR_CLOSURE,
            }]
        }
