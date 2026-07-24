# AI Wrong Answer Analysis API

## 프로젝트 소개
이 프로젝트는 학생이 문제, 정답, 답안, 풀이, 질문을 입력하면 생성형 AI가 오답을 분석해 주는 Flask 기반 백엔드 API 서버입니다.

## 백엔드 역할
- 서버 상태 확인 API 제공
- 일반 오답 분석 API 제공
- 재분석 API 제공
- 요청 데이터 검증 및 이미지 검증 수행
- OpenAI API를 호출해 구조화된 분석 결과를 반환
- CORS, 요청 크기 제한, API 키 관리 등을 처리

## 폴더 구조
```text
backend/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ extensions.py
│  ├─ routes/
│  │  ├─ analysis.py
│  │  └─ health.py
│  ├─ schemas/
│  │  ├─ requests.py
│  │  ├─ responses.py
│  │  └─ errors.py
│  ├─ services/
│  │  ├─ analysis_service.py
│  │  ├─ ai_service.py
│  │  ├─ image_service.py
│  │  └─ prompt_service.py
│  ├─ validators/
│  │  ├─ input_validator.py
│  │  └─ file_validator.py
│  ├─ prompts/
│  │  ├─ common.py
│  │  └─ subjects.py
│  ├─ errors/
│  │  ├─ exceptions.py
│  │  └─ handlers.py
│  └─ utils/
│     ├─ identifiers.py
│     └─ logging_utils.py
├─ tests/
├─ run.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
└─ README.md
```

## Python 가상환경 생성
PowerShell:
```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 라이브러리 설치
```powershell
pip install -r requirements.txt
```

## 환경 변수 설정
1. `.env.example`를 복사해 `.env`를 생성합니다.
2. OpenAI API 키를 입력합니다.

```powershell
Copy-Item .env.example .env
```

## 개발 서버 실행
```powershell
python run.py
```

## API 목록
- GET /api/health
- POST /api/analyze
- POST /api/reanalyze

## 일반 분석 요청 필드
- subject: 국어, 수학, 영어
- unit: 선택
- questionType: 객관식, 단답형, 서술형
- questionText: 선택, 최대 8000자
- correctAnswer: 필수
- studentAnswer: 필수
- studentSolution: 선택
- studentQuestion: 선택
- questionImage: 선택
- solutionImage: 선택

## 재분석 요청 필드
- reanalysisType: easy, detailed, alternative, reconsider, newQuestion
- previousAnalysis: 이전 분석 결과 JSON 문자열
- newStudentQuestion: 새 질문 (newQuestion용)

## 성공 응답 예시
```json
{
  "success": true,
  "analysisId": "uuid",
  "analysis": {
    "studentQuestion": "왜 틀렸나요?",
    "questionAnswer": "답은 3입니다.",
    "errorType": "계산 오류",
    "correctParts": ["개념은 맞습니다."],
    "firstError": "처음 계산이 틀렸습니다.",
    "correctSolution": ["1단계", "2단계"],
    "comparison": [{"step": 1, "studentStep": "2", "correctStep": "3", "status": "차이 있음", "questionRelated": true}],
    "reviewContent": ["계산 순서를 확인하세요."],
    "caution": "주의하세요."
  },
  "meta": {
    "subject": "수학",
    "reanalyzed": false
  }
}
```

## 오류 응답 예시
```json
{
  "success": false,
  "error": {
    "errorCode": "MISSING_FIELD",
    "message": "정답을 입력해주세요.",
    "retryable": false,
    "details": {}
  }
}
```

## 이미지 제한
- 허용 형식: JPG, JPEG, PNG, WEBP
- 최대 파일 크기: 5MB
- 최대 이미지 길이: 2000px

## CORS 설정
- ALLOWED_ORIGINS 환경 변수로 허용 출처를 관리합니다.

## 테스트 실행
```powershell
pytest -q
```

## 프론트엔드 연동 방법
- 프론트엔드에서 multipart/form-data로 요청합니다.
- 응답은 JSON으로 받습니다.
- 브라우저 저장소는 프론트엔드 측에서 관리합니다.

## GitHub에 올리면 안 되는 파일
- .env
- API 키가 포함된 파일

## 운영 환경 주의사항
- 디버그 모드 사용 금지
- 환경 변수로 민감 정보를 관리
- 로그와 오류에 민감 정보를 포함하지 않기
