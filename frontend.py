import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import error, parse, request

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI 오답 mate</title>
  <style>
    :root {
      --bg: #f5f7ff;
      --card: #ffffff;
      --primary: #4f46e5;
      --primary-soft: #eef2ff;
      --accent: #06b6d4;
      --text: #1f2937;
      --muted: #6b7280;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Pretendard', 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, var(--bg), #eef2ff);
      color: var(--text);
    }
    a { color: inherit; text-decoration: none; }
    .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
    header {
      display: flex; justify-content: space-between; align-items: center; gap: 16px;
      padding: 20px 0 28px;
    }
    .brand { font-size: 1.6rem; font-weight: 800; color: var(--primary); }
    .pill { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; background: var(--primary-soft); border-radius: 999px; color: var(--primary); font-weight: 700; }
    .hero {
      display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 24px; align-items: center;
      background: var(--card); border-radius: 28px; padding: 32px; box-shadow: 0 16px 40px rgba(79,70,229,.1);
    }
    .hero h1 { font-size: 2.2rem; margin: 0 0 12px; }
    .hero p { color: var(--muted); line-height: 1.7; }
    .hero-actions { display: flex; gap: 12px; margin-top: 20px; flex-wrap: wrap; }
    .btn {
      border: 0; border-radius: 999px; padding: 12px 18px; cursor: pointer; font-weight: 700;
      transition: transform .15s ease;
    }
    .btn:hover { transform: translateY(-2px); }
    .btn-primary { background: var(--primary); color: white; }
    .btn-secondary { background: #f3f4f6; color: var(--text); }
    .card { background: var(--card); border-radius: 24px; padding: 24px; box-shadow: 0 10px 30px rgba(15,23,42,.06); }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px; }
    .section-title { font-size: 1.2rem; font-weight: 800; margin: 0 0 16px; }
    .steps { display: grid; gap: 12px; }
    .step { padding: 14px; border-radius: 16px; background: #f9fafb; color: var(--muted); }
    .step strong { color: var(--text); }
    form { display: grid; gap: 14px; }
    label { display: grid; gap: 6px; font-weight: 700; }
    input, textarea, select {
      width: 100%; padding: 12px 14px; border: 1px solid #d1d5db; border-radius: 12px; font-size: 1rem; background: #fff;
    }
    textarea { min-height: 96px; resize: vertical; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .preview { margin-top: 8px; max-height: 180px; overflow: hidden; border-radius: 16px; border: 1px dashed #cbd5e1; }
    .preview img { width: 100%; height: auto; display: block; }
    .result-box {
      border: 1px solid #e5e7eb; border-radius: 20px; padding: 20px; background: linear-gradient(145deg, #f8fbff, #ffffff);
      margin-top: 16px;
    }
    .result-box h3 { margin-top: 0; }
    .tag { display: inline-block; padding: 6px 10px; border-radius: 999px; background: var(--primary-soft); color: var(--primary); font-size: .9rem; font-weight: 700; margin: 4px 6px 6px 0; }
    .muted { color: var(--muted); }
    .list { display: grid; gap: 10px; }
    .record-item { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 14px; background: #f9fafb; }
    .record-item button { border: 0; background: none; cursor: pointer; font-size: 1rem; }
    .hidden { display: none; }
    .warning { color: var(--danger); font-weight: 700; }
    @media (max-width: 900px) {
      .hero, .grid, .row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">AI 오답 mate</div>
      <div class="pill">학생 맞춤 오답 분석</div>
    </header>

    <section class="hero">
      <div>
        <h1>오답을 분석해서, 다음 시험을 더 잘 보게 돕습니다.</h1>
        <p>문제·정답·학생 답·풀이를 입력하면 AI가 왜 틀렸는지, 어떤 개념이 부족했는지, 다음에 어떻게 공부해야 하는지 정리해줍니다. 최근 기록과 즐겨찾기까지 브라우저에 저장됩니다.</p>
        <div class="hero-actions">
          <button class="btn btn-primary" onclick="document.getElementById('analysis').scrollIntoView({behavior:'smooth'})">오답 분석 시작</button>
          <button class="btn btn-secondary" onclick="showDemo()">데모 보기</button>
        </div>
      </div>
      <div class="card">
        <h3 class="section-title">이용 방법</h3>
        <div class="steps">
          <div class="step"><strong>1.</strong> 과목과 문제 정보를 입력합니다.</div>
          <div class="step"><strong>2.</strong> 정답, 학생 답, 풀이를 적습니다.</div>
          <div class="step"><strong>3.</strong> AI 분석 결과와 공부 방향을 확인합니다.</div>
        </div>
      </div>
    </section>

    <div class="grid">
      <section class="card">
        <h3 class="section-title">최근 분석 기록</h3>
        <div id="recentRecords" class="list"></div>
      </section>

      <section class="card">
        <h3 class="section-title">즐겨찾기</h3>
        <div id="favoriteRecords" class="list"></div>
      </section>
    </div>

    <section id="analysis" class="card" style="margin-top:24px;">
      <h3 class="section-title">오답 분석</h3>
      <form id="analysisForm">
        <div class="row">
          <label>과목
            <select name="subject">
              <option value="국어">국어</option>
              <option value="수학">수학</option>
              <option value="영어">영어</option>
            </select>
          </label>
          <label>단원
            <input name="unit" placeholder="예: 2단원 함수" />
          </label>
        </div>
        <div class="row">
          <label>문제 유형
            <select name="problemType">
              <option value="객관식">객관식</option>
              <option value="단답형">단답형</option>
              <option value="서술형">서술형</option>
            </select>
          </label>
          <label>문제 내용
            <textarea name="problemContent" placeholder="문제 내용을 입력하세요."></textarea>
          </label>
        </div>
        <label>문제 이미지 업로드
          <input type="file" id="problemImage" accept="image/*" />
          <div id="problemPreview" class="preview hidden"></div>
        </label>
        <div class="row">
          <label>정답
            <input name="correctAnswer" placeholder="정답을 입력하세요." />
          </label>
          <label>학생 답
            <input name="studentAnswer" placeholder="학생이 적은 답을 입력하세요." />
          </label>
        </div>
        <label>학생 풀이
          <textarea name="studentSolution" placeholder="학생의 풀이 과정을 적어주세요."></textarea>
        </label>
        <label>풀이 이미지 업로드
          <input type="file" id="solutionImage" accept="image/*" />
          <div id="solutionPreview" class="preview hidden"></div>
        </label>
        <label>학생 질문
          <textarea name="studentQuestion" placeholder="학생이 궁금해하는 점을 적어주세요."></textarea>
        </label>
        <button class="btn btn-primary" type="submit">분석 요청</button>
      </form>

      <div id="resultArea" class="hidden" style="margin-top:20px;"></div>
    </section>
  </div>

  <script>
    const STORAGE_KEY = 'ai-mate-records';
    const FAVORITE_KEY = 'ai-mate-favorites';

    const form = document.getElementById('analysisForm');
    const resultArea = document.getElementById('resultArea');
    const recentRecords = document.getElementById('recentRecords');
    const favoriteRecords = document.getElementById('favoriteRecords');

    function loadRecords() {
      try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch { return []; }
    }
    function saveRecords(records) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
    }
    function loadFavorites() {
      try { return JSON.parse(localStorage.getItem(FAVORITE_KEY) || '[]'); } catch { return []; }
    }
    function saveFavorites(favorites) {
      localStorage.setItem(FAVORITE_KEY, JSON.stringify(favorites));
    }

    let favorites = loadFavorites();
    let records = loadRecords();

    function renderRecords() {
      const recent = records.slice(0, 5);
      const fav = records.filter(item => favorites.includes(item.id));

      recentRecords.innerHTML = recent.length ? recent.map(item => `
        <div class="record-item">
          <div>
            <strong>${item.subject}</strong><br />
            <span class="muted">${item.unit || '단원 미입력'} · ${item.problemType || '문제유형 미입력'}</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <button onclick="toggleFavorite('${item.id}')">${favorites.includes(item.id) ? '⭐' : '☆'}</button>
            <button onclick="showRecord('${item.id}')">보기</button>
          </div>
        </div>
      `).join('') : '<div class="muted">아직 저장된 기록이 없습니다.</div>';

      favoriteRecords.innerHTML = fav.length ? fav.map(item => `
        <div class="record-item">
          <div>
            <strong>${item.subject}</strong><br />
            <span class="muted">${item.unit || '단원 미입력'}</span>
          </div>
          <button onclick="toggleFavorite('${item.id}')">⭐</button>
        </div>
      `).join('') : '<div class="muted">즐겨찾기 항목이 없습니다.</div>';
    }

    function toggleFavorite(id) {
      favorites = favorites.includes(id) ? favorites.filter(item => item !== id) : [...favorites, id];
      saveFavorites(favorites);
      renderRecords();
    }

    function showRecord(id) {
      const item = records.find(record => record.id === id);
      if (!item) return;
      renderResult(item.analysis, item);
      window.scrollTo({ top: document.getElementById('analysis').offsetTop, behavior: 'smooth' });
    }

    document.getElementById('problemImage').addEventListener('change', async function (event) {
      const preview = document.getElementById('problemPreview');
      const file = event.target.files[0];
      if (!file) { preview.classList.add('hidden'); preview.innerHTML = ''; return; }
      const dataUrl = await readFileAsDataUrl(file);
      preview.innerHTML = `<img src="${dataUrl}" alt="문제 이미지" />`;
      preview.classList.remove('hidden');
    });

    document.getElementById('solutionImage').addEventListener('change', async function (event) {
      const preview = document.getElementById('solutionPreview');
      const file = event.target.files[0];
      if (!file) { preview.classList.add('hidden'); preview.innerHTML = ''; return; }
      const dataUrl = await readFileAsDataUrl(file);
      preview.innerHTML = `<img src="${dataUrl}" alt="풀이 이미지" />`;
      preview.classList.remove('hidden');
    });

    function readFileAsDataUrl(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      const formData = new FormData(form);
      const payload = {
        subject: formData.get('subject') || '국어',
        unit: formData.get('unit') || '',
        problemType: formData.get('problemType') || '객관식',
        problemContent: formData.get('problemContent') || '',
        correctAnswer: formData.get('correctAnswer') || '',
        studentAnswer: formData.get('studentAnswer') || '',
        studentSolution: formData.get('studentSolution') || '',
        studentQuestion: formData.get('studentQuestion') || '',
        problemImage: document.getElementById('problemPreview').querySelector('img')?.getAttribute('src') || '',
        solutionImage: document.getElementById('solutionPreview').querySelector('img')?.getAttribute('src') || ''
      };

      resultArea.innerHTML = '<div class="result-box"><p class="muted">분석 중입니다. 잠시만 기다려주세요.</p></div>';
      resultArea.classList.remove('hidden');

      try {
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || '분석 요청에 실패했습니다.');
        renderResult(data, payload);
        const record = {
          id: `${Date.now()}`,
          subject: payload.subject,
          unit: payload.unit,
          problemType: payload.problemType,
          analysis: data
        };
        records = [record, ...records].slice(0, 10);
        saveRecords(records);
        renderRecords();
      } catch (error) {
        resultArea.innerHTML = `<div class="result-box"><p class="warning">분석 요청 중 문제가 발생했습니다.</p><p class="muted">${error.message}</p></div>`;
      }
    });

    function renderResult(data, payload) {
      const sections = [
        { label: '핵심 원인', value: data.cause || '분석 결과가 없습니다.' },
        { label: ' 놓친 개념', value: data.concept || '분석 결과가 없습니다.' },
        { label: '오답 분석', value: data.analysis || '분석 결과가 없습니다.' },
        { label: '학습 방향', value: data.plan || '분석 결과가 없습니다.' },
        { label: '풀이 비교', value: data.comparison || '분석 결과가 없습니다.' }
      ];

      resultArea.innerHTML = `
        <div class="result-box">
          <h3>분석 결과</h3>
          <p class="muted">${payload.subject} · ${payload.unit || '단원 미입력'} · ${payload.problemType}</p>
          <div>
            <span class="tag">정답: ${payload.correctAnswer || '미입력'}</span>
            <span class="tag">학생 답: ${payload.studentAnswer || '미입력'}</span>
          </div>
          ${sections.map(section => `
            <div style="margin-top:14px;">
              <strong>${section.label}</strong>
              <p style="margin:8px 0 0; line-height:1.7;">${section.value}</p>
            </div>
          `).join('')}
          ${data.mock ? '<p class="warning" style="margin-top:14px;">현재는 데모 응답으로 표시 중입니다. Google Gemini API 연결이 되면 더 정교한 분석으로 바뀝니다.</p>' : ''}
        </div>
      `;
      resultArea.classList.remove('hidden');
    }

    function showDemo() {
      document.querySelector('select[name="subject"]').value = '수학';
      document.querySelector('input[name="unit"]').value = '2단원 함수';
      document.querySelector('textarea[name="problemContent"]').value = '함수 f(x)=2x+3의 그래프가 x축과 만나는 지점을 구하시오.';
      document.querySelector('input[name="correctAnswer"]').value = 'x=-1.5';
      document.querySelector('input[name="studentAnswer"]').value = 'x=-1';
      document.querySelector('textarea[name="studentSolution"]').value = '2x+3=0을 풀어 x=-1.5라고 생각했지만 계산 실수로 -1로 썼습니다.';
      document.querySelector('textarea[name="studentQuestion"]').value = '방정식 풀이 과정에서 실수는 어떻게 줄일 수 있나요?';
      document.getElementById('analysis').scrollIntoView({ behavior: 'smooth' });
    }

    renderRecords();
    window.toggleFavorite = toggleFavorite;
    window.showRecord = showRecord;
  </script>
</body>
</html>
"""


class AIAnalysisHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = parse.urlparse(self.path).path
        if path in ('/', '/index.html'):
            self._send_text(200, HTML_PAGE, 'text/html; charset=utf-8')
        elif path == '/api/health':
            self._send_json(200, {'status': 'ok', 'service': 'AI 오답 mate'})
        else:
            self._send_text(404, 'Not Found', 'text/plain; charset=utf-8')

    def do_POST(self):
        path = parse.urlparse(self.path).path
        if path != '/api/analyze':
            self._send_text(404, 'Not Found', 'text/plain; charset=utf-8')
            return

        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'
        try:
            payload = json.loads(body or '{}')
        except json.JSONDecodeError:
            self._send_json(400, {'error': '잘못된 JSON 형식입니다.'})
            return

        try:
            result = self._analyze(payload)
            self._send_json(200, result)
        except Exception as exc:
            self._send_json(500, {'error': str(exc)})

    def _analyze(self, payload):
        api_key = os.getenv('GOOGLE_API_KEY') or GOOGLE_API_KEY
        if not api_key:
            raise RuntimeError('Google API 키가 설정되지 않았거나 사용할 수 없습니다.')
        return self._call_gemini_api(payload, api_key)

    def _call_gemini_api(self, payload, api_key):
        prompt = f"""
당신은 학생의 오답을 분석해주는 교육 코치입니다.
과목: {payload.get('subject', '국어')}
단원: {payload.get('unit', '')}
문제 유형: {payload.get('problemType', '')}
문제 내용: {payload.get('problemContent', '')}
정답: {payload.get('correctAnswer', '')}
학생 답: {payload.get('studentAnswer', '')}
학생 풀이: {payload.get('studentSolution', '')}
학생 질문: {payload.get('studentQuestion', '')}

다음 형식으로 5개 항목을 한국어로 답변하세요.
1. 핵심 원인
2. 놓친 개념
3. 오답 분석
4. 학습 방향
5. 풀이 비교
"""
        models = [
            'gemini-flash-latest',
            'gemini-2.5-flash',
            'gemini-2.5-flash-lite',
            'gemini-pro-latest'
        ]
        last_error = None
        for model in models:
            try:
                return self._call_gemini_model(payload, api_key, model, prompt)
            except RuntimeError as exc:
                last_error = exc
                if '404' in str(exc) or 'Requested entity was not found' in str(exc):
                    continue
                raise
        raise RuntimeError(f'지원되는 Gemini 모델을 찾을 수 없습니다. 마지막 오류: {last_error}')

    def _call_gemini_model(self, payload, api_key, model, prompt):
        body = {
            'contents': [
                {
                    'type': 'text',
                    'text': prompt
                }
            ],
            'temperature': 0.7,
            'maxOutputTokens': 700
        }
        data = json.dumps(body).encode('utf-8')
        req = request.Request(
            f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        try:
            with request.urlopen(req, timeout=60) as resp:
                response = json.loads(resp.read().decode('utf-8'))
        except error.HTTPError as http_err:
            message = http_err.read().decode('utf-8', errors='ignore')
            raise RuntimeError(f'Gemini API HTTPError {http_err.code}: {message}')
        except error.URLError as url_err:
            raise RuntimeError(f'Gemini API 연결 실패: {url_err.reason}')

        if 'candidates' in response and response['candidates']:
            candidate = response['candidates'][0]
            if 'content' in candidate and candidate['content']:
                msg = ''.join(part.get('text', '') for part in candidate['content'] if part.get('type') == 'text')
            elif 'output' in candidate and candidate['output']:
                msg = ''.join(part.get('text', '') for part in candidate['output'] if part.get('type') == 'text')
            elif 'content' in candidate and isinstance(candidate['content'], list):
                msg = ''.join(item.get('text', '') for item in candidate['content'] if isinstance(item, dict) and item.get('type') == 'output_text')
            else:
                msg = ''
        elif 'output' in response and response['output']:
            msg = ''.join(part.get('text', '') for part in response['output'] if part.get('type') == 'text')
        else:
            msg = ''

        if not msg:
            raise RuntimeError('Gemini API 응답에서 텍스트를 파싱할 수 없습니다.')

        return {
            'mock': False,
            'cause': msg.split('1. 핵심 원인')[1].split('2. 놓친 개념')[0].strip() if '1. 핵심 원인' in msg else msg,
            'concept': msg.split('2. 놓친 개념')[1].split('3. 오답 분석')[0].strip() if '2. 놓친 개념' in msg else '',
            'analysis': msg.split('3. 오답 분석')[1].split('4. 학습 방향')[0].strip() if '3. 오답 분석' in msg else '',
            'plan': msg.split('4. 학습 방향')[1].split('5. 풀이 비교')[0].strip() if '4. 학습 방향' in msg else '',
            'comparison': msg.split('5. 풀이 비교')[1].strip() if '5. 풀이 비교' in msg else '',
            'subject': payload.get('subject', '국어')
        }

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status, content, content_type):
        body = content.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def run_server(port=8000):
    server = ThreadingHTTPServer(('0.0.0.0', port), AIAnalysisHandler)
    print(f'AI 오답 mate 서버가 http://localhost:{port} 에서 실행 중입니다.')
    print('Google Gemini API 키를 사용합니다. 환경 변수 GOOGLE_API_KEY를 바꾸려면: $env:GOOGLE_API_KEY="your-key"')
    server.serve_forever()


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    run_server(port)
