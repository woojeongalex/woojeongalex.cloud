from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import urllib.parse
from base64 import urlsafe_b64decode, urlsafe_b64encode

import requests as http_requests
from fastapi import APIRouter, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse

oauth_router = APIRouter(prefix="/auth", tags=["oauth"])

_GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
_GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
_SESSION_SECRET = os.getenv("SESSION_SECRET", secrets.token_hex(32))
_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "https://api-backend.woojeongalex.cloud/auth/google/callback",
)

_LOGIN_HTML = """\
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Woojeongalex API — 로그인</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0a0a0a;
      color: #fff;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .card {
      background: #111;
      border: 1px solid #222;
      border-radius: 1.5rem;
      padding: 2.5rem;
      width: 100%;
      max-width: 360px;
      text-align: center;
    }
    .badge {
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #6b7280;
      margin-bottom: 1.25rem;
    }
    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }
    p  { font-size: 0.875rem; color: #9ca3af; margin-bottom: 2rem; line-height: 1.6; }
    .btn-google {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      width: 100%;
      padding: 0.875rem 1.25rem;
      background: #fff;
      color: #000;
      font-size: 0.875rem;
      font-weight: 600;
      border: none;
      border-radius: 0.75rem;
      cursor: pointer;
      text-decoration: none;
      transition: opacity 0.15s;
    }
    .btn-google:hover { opacity: 0.9; }
    .docs-link {
      display: block;
      margin-top: 1.25rem;
      font-size: 0.8rem;
      color: #4b5563;
      text-decoration: none;
    }
    .docs-link:hover { color: #9ca3af; }
  </style>
</head>
<body>
  <div class="card">
    <span class="badge">Developer Access</span>
    <h1>API 로그인</h1>
    <p>Google 계정으로 로그인하면<br />Swagger 문서에 접근할 수 있습니다.</p>
    <a href="/auth/google" class="btn-google">
      <svg width="18" height="18" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
      Google로 계속하기
    </a>
    <a href="/docs" class="docs-link">← Swagger 문서로 바로 가기</a>
  </div>
</body>
</html>
"""


def _make_session_token(email: str, name: str) -> str:
    payload = (
        urlsafe_b64encode(json.dumps({"email": email, "name": name}).encode())
        .rstrip(b"=")
        .decode()
    )
    sig = hmac.new(
        _SESSION_SECRET.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}.{sig}"


def _verify_session_token(token: str) -> dict | None:
    if "." not in token:
        return None
    payload, _, sig = token.rpartition(".")
    expected = hmac.new(
        _SESSION_SECRET.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        padded = payload + "=" * (-len(payload) % 4)
        return json.loads(urlsafe_b64decode(padded).decode())
    except Exception:
        return None


@oauth_router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dev_login_page():
    return HTMLResponse(_LOGIN_HTML)


@oauth_router.get("/google")
def google_login():
    if not _GOOGLE_CLIENT_ID:
        return HTMLResponse(
            "<p style='font-family:sans-serif;padding:2rem'>"
            "GOOGLE_CLIENT_ID가 설정되지 않았습니다. backend/.env를 확인하세요.</p>",
            status_code=503,
        )
    params = urllib.parse.urlencode(
        {
            "client_id": _GOOGLE_CLIENT_ID,
            "redirect_uri": _REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
        }
    )
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@oauth_router.get("/google/callback")
def google_callback(code: str, state: str | None = None):
    token_resp = http_requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": _GOOGLE_CLIENT_ID,
            "client_secret": _GOOGLE_CLIENT_SECRET,
            "redirect_uri": _REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    access_token = token_resp.json().get("access_token", "")

    user_resp = http_requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    user_resp.raise_for_status()
    user = user_resp.json()

    session_token = _make_session_token(
        email=user.get("email", ""),
        name=user.get("name", ""),
    )
    response = RedirectResponse("/docs", status_code=302)
    response.set_cookie(
        "dev_session",
        session_token,
        httponly=True,
        samesite="lax",
        max_age=86400 * 7,
    )
    return response


@oauth_router.get("/me")
def get_me(dev_session: str | None = Cookie(default=None)):
    if not dev_session:
        return {"authenticated": False}
    data = _verify_session_token(dev_session)
    if not data:
        return {"authenticated": False}
    return {"authenticated": True, **data}
