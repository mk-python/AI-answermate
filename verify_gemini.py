import json
import os
import urllib.request

key = os.getenv('GOOGLE_API_KEY', '')
models = [
    'gemini-flash-latest',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-flash-lite-latest',
]
for model in models:
    body = {
        'contents': [
            {
                'type': 'text',
                'text': '안녕하세요. 이 모델은 작동하나요?'
            }
        ],
        'temperature': 0.2,
    }
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}',
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print('MODEL', model, 'STATUS', resp.status)
            print(resp.read().decode('utf-8'))
    except Exception as e:
        print('MODEL', model, 'ERROR', type(e).__name__, e)
        if hasattr(e, 'read'):
            try:
                print(e.read().decode('utf-8', errors='ignore'))
            except Exception:
                pass
        print('-' * 80)
