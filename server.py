"""
Lightweight Flask proxy for local use with a Gemini-compatible endpoint.

SECURITY:
- Do NOT commit your API key to source control.
- Export your key locally and run the server; the server will send the key in Authorization header.
- I will NOT and CANNOT use the key you pasted. Run this locally.

Usage:
$ set GEMINI_API_KEY=your_key_here    (PowerShell: $env:GEMINI_API_KEY = 'KEY')
$ set GEMINI_URL=https://your-gemini-endpoint.example/v1/generate  # optional
$ python server.py

By default, if GEMINI_API_KEY is not set, the server returns a safe simulated response for testing.
"""
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GEMINI_URL = os.environ.get('GEMINI_URL')  # set to provider endpoint if known
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    # collect incoming form data
    subject = request.form.get('subject')
    correct = request.form.get('correct')
    mine = request.form.get('mine')
    my_solution = request.form.get('mySolution')
    question = request.form.get('question')

    # file handling: keep simple, do not store; forward as bytes if provider supports multipart
    problem_file = request.files.get('problemFile')
    solution_file = request.files.get('solutionFile')

    # Build a prompt suitable for your model/provider
    prompt_text = (
        f"과목: {subject}\n정답: {correct}\n내 답: {mine}\n"
        f"내 풀이: {my_solution}\n질문: {question}\n"
        "위 정보를 바탕으로 오답 원인과 개선 포인트를 요약해줘. 단계별로 권장 학습 방법도 제시해줘."
    )

    # If no API key configured, return a simulated response for local testing
    if not GEMINI_API_KEY or not GEMINI_URL:
        demo = {
            'subject': subject or '미지정',
            'summary': '(시뮬레이션) 계산 실수 또는 중요한 단계 누락으로 보입니다.',
            'recommendations': [
                '각 단계에서 근거를 적고 검산하는 습관을 들이세요.',
                '유사 문제 3개를 풀이해 개념을 강화하세요.'
            ]
        }
        return jsonify({'ok': True, 'demo': True, 'analysis': demo})

    # Prepare request for upstream provider
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'prompt': prompt_text,
        'max_output_tokens': 800,
        'temperature': 0.2
    }

    try:
        resp = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        return jsonify({'ok': True, 'demo': False, 'provider': resp.json()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502

if __name__ == '__main__':
    # Run locally
    app.run(host='127.0.0.1', port=5000, debug=True)
