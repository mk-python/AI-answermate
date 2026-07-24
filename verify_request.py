import json
import urllib.request
import urllib.error

payload = {
    'subject': '수학',
    'unit': '2단원 함수',
    'problemType': '객관식',
    'problemContent': '함수 f(x)=2x+3의 그래프가 x축과 만나는 지점을 구하시오.',
    'correctAnswer': 'x=-1.5',
    'studentAnswer': 'x=-1',
    'studentSolution': '2x+3=0을 풀어 x=-1.5라고 생각했지만 계산 실수로 -1로 썼습니다.',
    'studentQuestion': '방정식 풀이 과정에서 실수는 어떻게 줄일 수 있나요?'
}
req = urllib.request.Request(
    'http://localhost:8000/api/analyze',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
try:
    with urllib.request.urlopen(req, timeout=90) as r:
        print('STATUS', r.status)
        print(r.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode('utf-8', errors='ignore'))
except urllib.error.URLError as e:
    print('URL', e.reason)
