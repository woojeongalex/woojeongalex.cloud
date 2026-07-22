"""로그인 이벤트 알림 — 이메일(SMTP) + n8n 웹훅."""
from __future__ import annotations

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx

logger = logging.getLogger(__name__)

_SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
_SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
_SMTP_USER = os.getenv("SMTP_USER", "")
_SMTP_PASS = os.getenv("SMTP_PASS", "")
_REPORT_TO = os.getenv("LOGIN_REPORT_EMAIL", "dnwjdwkd11@gmail.com")
_N8N_WEBHOOK = os.getenv("N8N_LOGIN_WEBHOOK_URL", "")


async def notify_login(
    *,
    user_id: int,
    username: str,
    nickname: str,
    email: str,
    provider: str,
    ip_address: str | None,
    logged_in_at: str,
) -> None:
    payload = {
        "user_id": user_id,
        "username": username,
        "nickname": nickname,
        "email": email,
        "provider": provider,
        "ip_address": ip_address or "-",
        "logged_in_at": logged_in_at,
    }

    await _send_n8n(payload)
    _send_email(payload)


async def _send_n8n(payload: dict) -> None:
    if not _N8N_WEBHOOK:
        logger.debug("[auth][notify] N8N_LOGIN_WEBHOOK_URL 미설정 — 웹훅 스킵")
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.post(_N8N_WEBHOOK, json=payload)
            logger.info("[auth][notify] n8n webhook status=%s", r.status_code)
    except Exception as e:
        logger.warning("[auth][notify] n8n webhook 실패: %s", e)


def _send_email(payload: dict) -> None:
    if not _SMTP_USER or not _SMTP_PASS:
        logger.debug("[auth][notify] SMTP 미설정 — 이메일 스킵")
        return
    try:
        subject = f"[woojeongalex] 로그인 알림 — {payload['nickname']} ({payload['provider']})"
        body = (
            f"로그인 감지\n\n"
            f"  유저 ID   : {payload['user_id']}\n"
            f"  닉네임    : {payload['nickname']}\n"
            f"  username  : {payload['username']}\n"
            f"  이메일    : {payload['email'] or '(없음)'}\n"
            f"  제공자    : {payload['provider']}\n"
            f"  IP        : {payload['ip_address']}\n"
            f"  시각      : {payload['logged_in_at']}\n"
        )
        msg = MIMEMultipart()
        msg["From"] = _SMTP_USER
        msg["To"] = _REPORT_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as s:
            s.ehlo()
            s.starttls()
            s.login(_SMTP_USER, _SMTP_PASS)
            s.sendmail(_SMTP_USER, _REPORT_TO, msg.as_string())
        logger.info("[auth][notify] 이메일 발송 완료 → %s", _REPORT_TO)
    except Exception as e:
        logger.warning("[auth][notify] 이메일 발송 실패: %s", e)
