# SSD Digest App

SSD/NAND 컨트롤러 펌웨어 및 자동차 SW 취업을 목표로, 매일 수집한 뉴스 다이제스트 메일을
자동으로 수집·정리해서 쌓아주는 개인 학습 인프라.

메일을 열어 읽고, 용어를 찾아보고, 손으로 정리하던 반복 작업을 자동화해서
정리보다는 개념 이해에 시간을 쓸 수 있게 만드는 것을 목표로 함.

## 앱 기능

매일 아침 도착하는 "SSD/자동차 SW 펌웨어 데일리 브리핑" 메일을 자동으로 가져와
기사 요약·인사이트·새로운 용어·학습 콘텐츠로 구조화, 웹에서 언제든 확인할 수 있게 보여줌.

- **오늘 피드** — 가장 최근 다이제스트를 한 화면에. 카테고리(SSD/자동차) → 태그(FTL, NAND,
  PCIe, AUTOSAR 등) 알약 버튼으로 좁혀서, 지나간 기사도 주제별로 다시 찾아볼 수 있음
- **타임라인** — 날짜별로 쌓인 기록을 훑어보기
- **용어 사전** — 지금까지 나온 모든 용어를 검색 가능한 형태로 누적. "용어/개념" 토글로
  플래시카드식 용어 설명과, 기사 없는 날 오는 미니 아티클(개념 설명)을 구분해서 봄.
  개념도 태그로 카테고리 필터링 가능
- **복습** — 간격 반복(spaced repetition) 알고리즘 기반. 서술형(Gemini 첨삭) / 객관식
  (다른 용어 뜻풀이를 오답 보기로 활용) 두 모드 지원. 맞으면 간격이 늘어나고, 틀리면 다음 날
  다시 봄
- **스트릭** — 연속 복습일수를 상단바에 표시
- **로그인** — 토큰 인증, 회원가입 화면 없이 admin에서 계정 직접 생성 (아는 사람만 쓰는
  개인용 도구)

## 전체 구조

```
[매일 05:00 KST 뉴스 다이제스트 메일 발송]
                ↓
[GitHub Actions: 05:00~06:45 KST 15분 간격 재시도]
                ↓
[Gmail API로 메일 수집] → [Gemini API로 구조화(JSON), 503 자동 재시도 포함]
                ↓
[Django + Supabase(PostgreSQL)에 저장]
                ↓
[React 프론트엔드(Vercel)가 Django API(Cloud Run)를 통해 표시, 로그인 필요]
```

메일 형식이 매일 조금씩 달라지므로, 정규식 대신 LLM 기반 파싱을 택함
(`fetcher/parser.py`는 정규식 버전 참고용, `fetcher/gemini_parser.py`가 실제 사용 중인 버전).

## 기술 스택

| 영역 | 기술 |
|---|---|
| 메일 수집 | Gmail API (OAuth 2.0, Desktop 클라이언트) |
| 파싱 | Gemini API (`gemini-3.6-flash`), 503 등 일시적 오류는 20초 간격 자동 재시도 |
| 백엔드 | Django + Django REST Framework |
| DB | PostgreSQL (Supabase, Transaction Pooler 주소 — Direct Connection은 IPv6 전용이라 대부분 네트워크에서 막힘) |
| 인증 | DRF TokenAuthentication |
| 자동화 | GitHub Actions (스케줄 cron) |
| 프론트엔드 | React (Vite ^5.4.11 고정) + React Router, 순수 CSS |
| 배포 | Google Cloud Run(백엔드, asia-south1) + Vercel(프론트엔드) |
| CI/CD | Cloud Build 트리거 — `master` push 시 자동 빌드+배포 |

## 폴더 구조

```
ssd_studyapp/
├── manage.py
├── requirements.txt
├── Dockerfile                  # Cloud Run 배포용
├── .dockerignore
├── cloudbuild.yaml             # Cloud Build 트리거가 사용 (build→push→deploy 3단계)
├── .env                        # 로컬 전용, git 제외
├── .gitignore
│
├── config/
│   ├── settings.py             # DB 분기, CORS, DJANGO_ADMIN_URL(숨김 처리), 보안 설정
│   └── urls.py
│
├── digest/
│   ├── models.py                # DailyDigest / Article / LearningItem / Term /
│   │                             # Tag / ReviewRecord / Insight / Question / DailyActivity
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── management/commands/
│       ├── fetch_digest.py      # 매일 실행되는 핵심 커맨드 (--force, --dry-run 지원)
│       ├── seed_tags.py         # 태그 12종 초기 데이터
│       └── backfill_tags.py     # 기존 기사에 소급으로 태그 채우는 1회성 커맨드
│
├── fetcher/                     # Django와 독립적인 수집/파싱 모듈
│   ├── gmail_client.py
│   ├── gemini_parser.py         # 구조화 + 태그 분류 + 답변 첨삭, 전부 여기
│   ├── credentials.json         # git 제외
│   └── token.json               # git 제외, 최초 인증 후 자동 생성
│
├── .github/workflows/fetch_digest.yml
│
└── frontend/
    ├── src/
    │   ├── api/client.js        # api / reviewApi, CATEGORY_LABEL/BADGE_CLASS
    │   ├── components/          # Modal, TermDetail, DigestNotes, StreakBadge
    │   ├── pages/
    │   │   ├── TodayFeed.jsx    # 오늘 피드 + 카테고리/태그 브라우저
    │   │   ├── Timeline.jsx
    │   │   ├── DigestDetail.jsx / DigestView.jsx
    │   │   ├── Glossary.jsx     # 용어/개념 토글 + 카테고리 필터
    │   │   ├── Review.jsx       # 서술형/객관식 복습
    │   │   ├── Privacy.jsx      # OAuth 프로덕션 게시용 최소 개인정보처리방침
    │   │   └── Login.jsx
    │   ├── App.jsx / App.css
    └── vercel.json
```

## 로컬에서 실행하기

```bash
# 백엔드
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_tags
python manage.py fetch_digest      # 최초 실행 시 브라우저 인증 필요 (credentials.json 필요)
python manage.py runserver

# 프론트엔드
cd frontend
npm install
npm run dev
```

**매일 쓰는 명령어**
```bash
python manage.py fetch_digest              # 최신 다이제스트 가져와서 저장
python manage.py fetch_digest --dry-run    # 저장 없이 결과만 미리보기
python manage.py fetch_digest --force      # 같은 날짜 데이터 덮어쓰기
```

로컬 `.env`의 `DATABASE_URL`이 Supabase 프로덕션 주소와 동일하므로, 로컬에서 실행한
결과가 곧바로 실제 서비스에 반영됨 (별도의 로컬 전용 DB 없음).

## 배포 (Google Cloud Run)

```bash
gcloud run deploy ssd-studyapp-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --max-instances=2 \
  --set-env-vars DJANGO_DEBUG=False,DJANGO_ADMIN_URL=<임의 문자열>/,DJANGO_ALLOWED_HOSTS=<서비스 URL>,CORS_EXTRA_ORIGINS=<Vercel 도메인> \
  --set-secrets DJANGO_SECRET_KEY=django-secret-key:latest,DATABASE_URL=database-url:latest,GEMINI_API_KEY=gemini-api-key:latest
```

민감한 값(`DJANGO_SECRET_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`)은 평문 대신
Secret Manager에 저장해서 참조. 필요한 IAM 권한 (프로젝트 번호는 예시):
```bash
gcloud projects add-iam-policy-binding <project-id> \
  --member="serviceAccount:<project-number>-compute@developer.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"
gcloud projects add-iam-policy-binding <project-id> \
  --member="serviceAccount:<project-number>-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding <project-id> \
  --member="serviceAccount:<project-number>-compute@developer.gserviceaccount.com" \
  --role="roles/run.admin"
gcloud iam service-accounts add-iam-policy-binding \
  <project-number>-compute@developer.gserviceaccount.com \
  --member="serviceAccount:<project-number>-compute@developer.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

**CI/CD**: Cloud Build 트리거가 `master` 브랜치 push마다 `cloudbuild.yaml`을 읽어
빌드→Artifact Registry push→Cloud Run 배포까지 자동 수행. 이후로는 로컬에서
`git push`만 하면 몇 분 뒤 자동 반영됨 (Cloud Shell에서 수동 `gcloud run deploy` 불필요).

**리전**: DB(Supabase, 뭄바이/`ap-south-1`)와 Cloud Run 리전을 맞춰서(`asia-south1`)
API 응답마다 발생하는 서버↔DB 왕복 지연을 없앰 — 처음엔 서울(`asia-northeast3`)로
배포했다가, 요청 하나당 DB 쿼리가 여러 번 나가는 구조라 지연이 누적돼 체감 속도가
크게 느렸던 것을 이 방식으로 해결함.

**무료 한도**: Cloud Run Always Free(월 요청 200만 건 등)는 GCP 90일/약 $300 체험
크레딧과 별개로 계속 적용됨. 체험판 만료 전 "일반 계정으로 전환"해도 무료 한도 안에서는
과금되지 않음 — 다만 전환을 안 해두면 만료일에 서비스가 자동으로 멈추니 미리 해두는 게 안전함.

## 자동화 (GitHub Actions)

`.github/workflows/fetch_digest.yml`이 다이제스트 발송 시각(05:00 KST)에 맞춰
05:00~06:45 KST 사이 15분 간격으로 재시도. 이미 저장된 날짜는 자동으로 건너뛰므로
여러 번 실행돼도 중복 저장 걱정 없음. PC가 꺼져 있어도 동작함.

**필요한 GitHub Secrets**: `GMAIL_CREDENTIALS_JSON`, `GMAIL_TOKEN_JSON`, `GEMINI_API_KEY`,
`DATABASE_URL`, `DJANGO_SECRET_KEY`

**⚠️ Gmail OAuth 앱을 반드시 "프로덕션"으로 게시해둘 것**: OAuth 동의 화면이
"테스트" 상태면 리프레시 토큰이 발급 후 **7일 뒤 무조건 만료**됨 (사용 빈도 무관).
`console.cloud.google.com/apis/credentials/consent`에서 게시 상태를 프로덕션으로
바꾸면 이 문제가 사라짐. 토큰이 만료되면 로컬에서 `fetcher/token.json` 삭제 후
`python manage.py fetch_digest` 재실행 → 브라우저 재인증 → 새 `token.json`을
`GMAIL_TOKEN_JSON` 시크릿에 갱신.

## 트러블슈팅 로그

| 문제 | 원인 | 해결 |
|---|---|---|
| Vite 8.x 빌드 실패 (Windows) | rolldown 네이티브 바이너리 이슈 | `vite ^5.4.11`로 고정 |
| Supabase Direct Connection 연결 안 됨 | IPv6 전용 | Transaction Pooler 주소로 전환 |
| Gemini 모델명 만료 | `gemini-2.5-flash` deprecated | `gemini-3.6-flash`로 교체 |
| Gemini 503 자주 발생 | 일시적 과부하 | 클라이언트에 `HttpRetryOptions`(20초 간격, 4회) 추가 |
| Gemini가 null 반환 시 DB 에러 | TextField는 NULL 비허용 | `_none_to_empty()`로 방어 |
| Cloud Run 컨테이너 시작 실패 | Dockerfile이 `$PORT` 대신 포트 8000 하드코딩 | `CMD exec gunicorn ... --bind 0.0.0.0:$PORT`로 수정 |
| `gcloud run deploy` 소스 업로드 권한 오류 | 최신 GCP 프로젝트는 기본 서비스 계정에 자동 권한 미부여 | `roles/cloudbuild.builds.builder` 부여 |
| 배포 시 시크릿 접근 거부 | 서비스 계정에 Secret Manager 권한 없음 | `roles/secretmanager.secretAccessor` 부여 |
| 재배포할 때마다 400 Bad Request | `--set-env-vars`가 기존 `DJANGO_ALLOWED_HOSTS` 덮어씀 | 재배포 시 항상 `DJANGO_ALLOWED_HOSTS` 포함해서 지정 |
| Cloud Build 트리거는 성공하는데 실제 배포 안 됨 | Dockerfile 자동감지 트리거는 빌드만 하고 배포 안 함 | `cloudbuild.yaml`로 build→push→deploy 3단계 명시 |
| Cloud Build "logging bucket" 오류 | 서비스 계정 지정 시 로그 저장 위치 명시 필요 | `cloudbuild.yaml`에 `options: logging: CLOUD_LOGGING_ONLY` 추가 |
| 새 다이제스트에 기사가 하나도 저장 안 됨 | 태그 기능 추가 중 들여쓰기 실수로 기사 저장 루프가 `if not created:` 블록 안에 갇힘 | 루프를 블록 밖으로 이동 |
| Gmail 토큰 7일마다 만료 | OAuth 동의 화면이 "테스트" 상태 | "프로덕션"으로 게시 (위 자동화 섹션 참고) |
| 스트릭 배지가 갱신 안 됨 | `StreakBadge`가 앱 마운트 시 한 번만 fetch, 복습 완료 이벤트를 못 받음 | `refreshKey` prop + 복습 제출 시 콜백으로 재조회 트리거 |

## 앞으로 할 것

- [ ] PWA 오프라인 지원
- [ ] 질문/인사이트 전체 모아보기 화면 (API는 이미 있음, 프론트 화면만 없음)
- [ ] 용어 숙련도 통계/대시보드