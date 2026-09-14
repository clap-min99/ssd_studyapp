# SSD Digest App

SSD/NAND 컨트롤러 펌웨어 및 자동차 SW 취업을 목표로, 매일 수집한 뉴스 다이제스트 메일을
자동으로 수집·정리해서 쌓아주는 개인 학습 인프라

메일을 열어 읽고, 용어를 찾아보고, 손으로 정리하던 반복 작업을 자동화해서
정리보다는 개념 이해에 시간을 쓸 수 있게 만드는 것을 목표로 함.

## 앱 기능

매일 아침 도착하는 "SSD/자동차 SW 펌웨어 데일리 브리핑" 메일을 자동으로 가져와
기사 요약·인사이트·새로운 용어·학습 콘텐츠로 구조화, 웹에서 언제든 확인할 수 있게 보여줌

- **오늘 피드** — 가장 최근 다이제스트를 한 화면에
- **타임라인** — 날짜별로 쌓인 기록을 훑어보기
- **용어 사전** — 지금까지 나온 모든 용어를 검색 가능한 형태로 누적

## 전체 구조

```
[매일 07:00 KST 뉴스 다이제스트 메일 발송]
                ↓
[GitHub Actions: 매일 07:15 KST 자동 실행]
                ↓
[Gmail API로 메일 수집] → [Gemini API로 구조화(JSON)]
                ↓
[Django + Supabase(PostgreSQL)에 저장]
                ↓
[React 프론트엔드(Vercel)가 Django API(Render)를 통해 표시]
```

메일 형식이 매일 조금씩 달라지므로, 정규식 대신 **LLM 기반 파싱**을 택함.
(`fetcher/parser.py`는 정규식 버전, `fetcher/gemini_parser.py`가 실제 사용 중인 버전)

## 기술 스택

| 영역 | 기술 |
|---|---|
| 메일 수집 | Gmail API (OAuth 2.0) |
| 파싱 | Gemini API (`gemini-3.6-flash`) |
| 백엔드 | Django + Django REST Framework |
| DB | PostgreSQL (Supabase, 무료 티어) |
| 자동화 | GitHub Actions (스케줄 cron) |
| 프론트엔드 | React (Vite) + React Router |
| 배포 | Render(백엔드) + Vercel(프론트엔드) |

## 폴더 구조

```
ssd_digest_app/
├── manage.py
├── requirements.txt
├── build.sh                    # Render 배포 시 자동 실행 (설치/collectstatic/migrate)
├── Procfile                    # Render 실행 명령어 (gunicorn)
├── .env                        # 로컬 전용, git에는 안 올라감
├── .gitignore
│
├── config/                     # Django 프로젝트 설정
│   ├── settings.py             # DB 분기(로컬 sqlite ↔ Supabase), CORS, WhiteNoise
│   └── urls.py
│
├── digest/                     # Django 앱
│   ├── models.py               # DailyDigest, Article, LearningItem, Term
│   ├── serializers.py          # DRF 시리얼라이저
│   ├── views.py                # /api/digests/, /api/terms/
│   ├── admin.py
│   └── management/commands/
│       └── fetch_digest.py     # 매일 실행되는 핵심 커맨드
│
├── fetcher/                    # Django와 독립적인 수집/파싱 모듈
│   ├── gmail_client.py         # Gmail API 인증 + 메일 조회
│   ├── gemini_parser.py        # Gemini로 구조화 (현재 사용 중)
│   ├── llm_parser.py           # Claude API 버전 (참고용, 미사용)
│   ├── parser.py               # 정규식 버전 (참고용, 미사용 — 형식 변동에 취약해서 폐기)
│   ├── run_pipeline.py         # Django 없이 단독 테스트용
│   ├── credentials.json        # Google Cloud OAuth 클라이언트 (git 제외)
│   └── token.json              # 최초 인증 후 자동 생성 (git 제외)
│
├── .github/workflows/
│   └── fetch_digest.yml        # 매일 07:15 KST 자동 실행
│
└── frontend/                   # React (Vite)
    ├── src/
    │   ├── api/client.js       # Django API 호출
    │   ├── pages/
    │   │   ├── TodayFeed.jsx
    │   │   ├── Timeline.jsx
    │   │   ├── DigestDetail.jsx
    │   │   └── Glossary.jsx
    │   ├── App.jsx              # 라우팅 + 하단 네비게이션
    │   └── App.css
    └── vercel.json               # SPA 라우팅(새로고침 404 방지)
```

## 로컬에서 실행하기

### 1. 백엔드 (Django)

```bash
pip install -r requirements.txt
```

`.env` 파일 생성:

```
GEMINI_API_KEY=발급받은-키
DATABASE_URL=postgresql://postgres.xxx:비밀번호@xxx.pooler.supabase.com:6543/postgres
```

Google Cloud Console에서 받은 `credentials.json`을 `fetcher/`에 위치시킨 뒤:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py fetch_digest      # 최초 실행 시 브라우저 인증 필요
python manage.py runserver
```

### 2. 프론트엔드 (React)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

`http://localhost:5173` 접속.

## 매일 쓰는 명령어

```bash
python manage.py fetch_digest              # 최신 다이제스트 가져와서 저장
python manage.py fetch_digest --dry-run    # 저장 없이 결과만 미리보기
python manage.py fetch_digest --force      # 같은 날짜 데이터 덮어쓰기
```

## 자동화 (GitHub Actions)

`.github/workflows/fetch_digest.yml`이 매일 07:15 KST(UTC 22:15)에 자동으로
`fetch_digest`를 실행합니다. PC가 꺼져 있어도 동작합니다.

**필요한 GitHub Secrets**

| 이름 | 설명 |
|---|---|
| `GMAIL_CREDENTIALS_JSON` | `fetcher/credentials.json` 내용 전체 |
| `GMAIL_TOKEN_JSON` | `fetcher/token.json` 내용 전체 (로컬에서 인증 완료 후) |
| `GEMINI_API_KEY` | Gemini API 키 |
| `DATABASE_URL` | Supabase 연결 문자열 (pooler 주소 권장) |
| `DJANGO_SECRET_KEY` | 임의의 랜덤 문자열 |

Actions 탭에서 "Fetch Daily Digest" 워크플로우를 수동 실행(`Run workflow`)할 수도 있습니다.

## 배포

- **백엔드**: Render (Free tier) — `build.sh`가 빌드 시 자동으로 마이그레이션까지 수행
  - 환경변수: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `CORS_EXTRA_ORIGINS`(프론트엔드 도메인)
- **프론트엔드**: Vercel — Root Directory를 `frontend`로 지정
  - 환경변수: `VITE_API_BASE=https://백엔드주소.onrender.com/api`

> Render 무료 티어는 15분간 요청이 없으면 슬립 모드로 전환되고, 다음 요청 시 깨어나는 데
> 30초~1분 정도 걸릴 수 있습니다.

## 앞으로 할 것

- [ ] 참고 디자인 반영해서 UI 스타일 개선
- [ ] PWA 설정 (아이폰 홈 화면 추가, 오프라인 지원)
- [ ] 주간 복습 기능을 앱 안에 통합 (지금은 대화로 진행)
- [ ] 용어 숙련도(`familiarity`) 갱신 UI 추가