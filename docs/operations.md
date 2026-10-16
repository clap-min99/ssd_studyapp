# 운영 및 트러블슈팅

[README로 돌아가기](../README.md)

배포 절차와 과거 장애 기록이다. 기록의 버전·환경은 현재와 다를 수 있으므로 실제 설정 파일과 함께 확인한다.

OpenAI API 키와 모델 전환 설정: [OpenAI 설정 문서](openai.md).

## 배포 (Google Cloud Run)

```bash
gcloud run deploy ssd-studyapp-api \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --max-instances=2 \
  --set-env-vars DJANGO_DEBUG=False,DJANGO_ADMIN_URL=<임의 문자열>/,DJANGO_ALLOWED_HOSTS=<서비스 URL>,CORS_EXTRA_ORIGINS=<Vercel 도메인> \
  --set-secrets DJANGO_SECRET_KEY=django-secret-key:latest,DATABASE_URL=database-url:latest,OPENAI_API_KEY=openai-api-key:latest
```

민감한 값(`DJANGO_SECRET_KEY`, `DATABASE_URL`, `OPENAI_API_KEY`)은 평문 대신
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

## 데이터 로딩 최적화 배포

- 백엔드를 먼저 배포한 뒤 프론트엔드를 배포한다. 프론트엔드는 `compact=1`로 목록을 요청하고, 카드를 열 때 새 `/api/content/{kind}/{id}/` API에서 원문·저장된 해설을 가져온다.
- `compact=1`을 생략하면 기존 응답을 유지한다. DB 마이그레이션은 필요하지 않다.
- 목록의 제목·본문은 유지하므로 기존 개념 전체 검색과 북마크 필터는 그대로 동작한다. 페이지 분할은 아직 적용하지 않았다.
- JSON 응답은 클라이언트가 지원하면 gzip으로 압축한다.
- 태그·레슨·타임라인·개념 목록·카드 상세는 브라우저 메모리에서 최대 60초 재사용한다. 새로고침하면 캐시가 비워진다. 계정별 캐시를 분리하고 로그아웃·AI 해설 생성 시 초기화한다.
- 복습 상태·용어 숙련도·북마크·메모에는 완료 응답 캐시를 적용하지 않는다.
- 운영 Cloud Run 인스턴스 수, worker/thread, DB 연결 재사용 설정은 변경하지 않았다. 실제 서버 응답 시간은 배포 후 별도로 재측정한다.

검증: 임시 SQLite DB에서 `python manage.py test digest.test_content_performance digest.test_query_performance digest.test_review_sessions digest.test_bookmarks`, 프론트엔드에서 `npm test`, `npm run build`.

## 복습 기능 DB 적용

복습 목표와 이어하기 기능은 `0016_review_sessions` 마이그레이션으로 추가된 테이블 사용.
새 코드로 서비스를 실행하기 전에 대상 DB에 다음 명령 적용 필요.

```bash
python manage.py migrate
```

기존 용어·복습 기록은 유지. 현재 Cloud Run 컨테이너 시작 명령에는 마이그레이션이 포함되지 않으므로
배포 전 대상 DB에 별도 적용 필요.

## 개념 북마크 DB 적용

개념 북마크는 `0017_conceptbookmark` 마이그레이션으로 추가되는 계정별 저장 테이블을 사용한다.
새 백엔드 배포 전에 대상 DB에 `python manage.py migrate`를 실행한다.
Cloud Run 컨테이너 시작 시 자동 적용되지 않는다. 프론트엔드는 마이그레이션과 백엔드 배포 후 배포한다.
기존 개념과 용어 데이터는 유지되며, 계정 또는 개념을 삭제하면 해당 북마크도 삭제된다.

## Gmail 인증 복구

로컬은 `fetcher/credentials.json`과 `fetcher/token.json`을 사용하고,
GitHub Actions는 Secrets에서 인증 정보를 복원한다. 두 환경의 인증 정보는 다를 수 있다.

`deleted_client` 오류는 토큰에 연결된 OAuth 클라이언트가 삭제됐다는 뜻이다.
유효한 데스크톱 앱 OAuth 클라이언트 JSON으로 `fetcher/credentials.json`을 교체하고,
기존 `fetcher/token.json`을 다른 이름으로 옮긴 뒤 수집 명령을 실행해 다시 인증한다.
Actions에도 같은 인증을 적용하려면 `GMAIL_CREDENTIALS_JSON`과 `GMAIL_TOKEN_JSON`을 갱신한다.

토큰 만료나 철회 오류는 실행 로그와 OAuth 앱의 게시 상태를 확인하고 재인증한다.

## 기존 장애 대응 기록

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
| Gmail 토큰 7일마다 만료 | OAuth 동의 화면이 "테스트" 상태 | "프로덕션"으로 게시 (README의 자동화 설명 참고) |
| 스트릭 배지가 갱신 안 됨 | `StreakBadge`가 앱 마운트 시 한 번만 fetch, 복습 완료 이벤트를 못 받음 | `refreshKey` prop + 복습 제출 시 콜백으로 재조회 트리거 |
| 레슨의 SVG 그림 일부가 사라짐 | 레슨 본문 markdown 안에서 `<svg>...</svg>` 블록 중간에 빈 줄이 있으면, 마크다운 파서가 그 지점에서 HTML 블록을 끊어버려 이후 태그들이 `<svg>` 밖으로 떨어져 나가 렌더링 안 됨 | SVG 블록 내부에 빈 줄 절대 넣지 않기 |
| "6만~10만 회" 같은 숫자 범위 표기가 취소선으로 보임 | GFM 마크다운이 단일 `~`도 취소선(strikethrough) 문법으로 해석 | 범위 표기의 `~`는 `\~`로 이스케이프 |
| "**용어(영문)**이/가/은/는" 형태의 볼드가 안 먹고 별표가 그대로 보임 | CommonMark의 강조 닫힘 규칙상, 닫는 `**` 바로 앞이 괄호 등 구두점이면서 바로 뒤에 공백/구두점 없이 문자(조사)가 오면 우측-플랭킹 조건을 못 만족해 닫힘으로 인정 안 됨 | `)**조사` 패턴 뒤에 공백 하나 추가 (`)** 조사`) — 새 레슨 콘텐츠 작성 후 `\)\*\*[가-힣]` 정규식으로 항상 검사 |
