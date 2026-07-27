# AI 오답 mate (Frontend + Local Proxy)

간단한 로컬 프론트엔드와 Flask 프록시(시뮬레이션 모드 포함)입니다.

빠른 시작:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY = ''  # 비워두면 시뮬레이션 모드
python server.py
python -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```

보안:
- `.env`에 API 키를 보관하고 `.gitignore`에 포함시켜 커밋하지 마세요.
- 이미 공개한 키는 즉시 폐기(revoke)하세요.

파일 목록:
- `index.html`, `styles.css`, `app.js` — 프론트엔드
- `server.py` — 로컬 프록시
