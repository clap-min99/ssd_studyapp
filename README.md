# SSD Digest App

**SSD·자동차 SW 뉴스와 디지털 설계·컴퓨터 구조 기초를 개념 학습과 복습으로 연결하는 개인 학습 앱.**

SSD/NAND 컨트롤러 펌웨어 및 자동차 SW 취업 준비를 위한 개인 학습 인프라.
메일을 읽고, 용어를 찾아보고, 내용을 따로 정리하는 반복 작업을 줄여
개념 이해와 반복 학습에 시간을 쓰는 것이 목표.

[전체 파이프라인](#전체-파이프라인) · [주요 기능](#주요-기능) · [로컬 실행](#로컬-실행) · [패치 노트](CHANGELOG.md) · [운영 문서](docs/operations.md)

## 학습 흐름

매일의 기사와 기초 개념을 같은 태그로 연결해, 새로운 소식을 기존 학습 맥락에서 이해하도록 구성.

1. **기사 읽기**: 최신 피드에서 기사 요약과 인사이트 확인. 날짜를 누르면 달력에서 과거 콘텐츠 탐색.
2. **기초 개념 학습**: 용어 사전과 챕터 레슨에서 모르는 개념 확인. 컴퓨터 구조 기초부터 SSD·자동차 분야로 학습 확장.
3. **실제 사례 연결**: 챕터의 관련 기사·용어를 통해 개념의 활용 사례 탐색.
4. **이해도 확인과 복습**: 서술형·객관식 문제 풀이 후 일정 간격으로 반복 학습.

## 전체 파이프라인

### 콘텐츠 수집과 저장

- **입력 데이터**: 외부에서 발송되어 Gmail에 도착한 「SSD/자동차 SW 펌웨어 데일리 브리핑」 메일.
- **프로젝트 범위**: 메일 수집 → 구조화·저장 → 학습 화면 제공.
- **외부 처리 범위**: 뉴스 검색과 원본 메일 작성·발송.

```mermaid
flowchart TD
    Mail[외부 다이제스트 메일 → Gmail] --> Gmail[Gmail API: 대상 메일 조회]
    Actions[GitHub Actions: 정기 실행 또는 날짜 지정] --> Gmail
    Gmail --> OpenAI[OpenAI: 기사·학습 콘텐츠·용어 구조화 및 태그 분류]
    OpenAI --> Save[Django: 원문·구조화 데이터 저장]
    Save --> DB[(Supabase PostgreSQL)]
    Save --> Explain[OpenAI: 심화 해설 생성]
    Explain --> DB
```

- **저장 순서**: 파싱 결과 검증 → DB 저장 → 심화 해설 생성.
- **항목 검증**: 원문의 독립된 기사·학습 항목을 각각 카드로 추출하고 원문 순서 유지. 항목 누락·합침과 요약 분량·문체를 검사하며, 재시도 후에도 검증에 실패하면 DB 저장 전에 중단.
- **해설 생성 실패 시**: 저장된 다이제스트 유지, 앱에서 해설 생성 재시도 가능.
- **중복 처리**: 이미 저장된 날짜는 기본적으로 건너뛰기.

### 웹에서 학습과 복습

```mermaid
flowchart LR
    Web[React · Vercel] --> API[Django REST API · Cloud Run]
    API --> DB[(Supabase PostgreSQL)]
    Web --> Learn[피드 · 날짜별 달력 · 용어 · 챕터/레슨]
    Web --> Review[서술형·객관식 복습]
    Review --> API
    API --> AI[OpenAI: 서술형 답변 첨삭]
```

일별 콘텐츠와 미리 작성한 커리큘럼을 태그로 연결.
레슨은 시드 데이터로 관리하고, 복습 결과에 따라 다음 복습 간격 조정.

## 주요 기능

| 기능 | 할 수 있는 일 |
|---|---|
| 오늘 피드 | 최신 기사·학습 콘텐츠를 읽고 카테고리와 태그로 탐색 |
| 날짜별 달력 | 피드 날짜를 눌러 과거 기사·학습 콘텐츠·용어 확인. 콘텐츠가 있는 날짜만 선택 가능 |
| 챕터·레슨 | 선행 개념 순서에 따라 학습하고 관련 기사·용어 확인 |
| 컴퓨터 구조 기초 | H&H RISC-V판 1–3장 기반 43개 레슨. 도식·단계별 예제·확인 문제·펼쳐보는 해설 제공 |
| 용어 사전·개념 모음 | 누적 용어와 개념 콘텐츠 검색, 분야·태그별 탐색, 개념 카드에서 원문·AI 심화 해설 확인 |
| 개념 북마크 | 로그인 후 개념을 계정별로 저장·해제하고 저장한 개념만 모아보기. 검색·태그 필터와 함께 사용 가능 |
| 복습 | 하루 목표·주제·날짜별 출제, 취약 용어 학습, 서버에 진도를 저장해 이어하기 |
| 스트릭 | 연속 복습일수 확인 |
| 회원가입·로그인 | 아이디·비밀번호로 가입 후 바로 로그인, 계정별 복습·질문·인사이트 관리 |
| 계정 삭제 | 상단 아이디 → 계정 관리에서 현재 비밀번호 확인 후 회원 탈퇴. 개인 기록 삭제, 공용 콘텐츠 유지 |

커리큘럼은 세 트랙으로 구성.

- **컴퓨터 구조 기초**: 디지털 설계의 출발점 → 조합논리 설계 → 순차논리 설계. Harris & Harris의 《Digital Design and Computer Architecture, RISC-V Edition》 흐름에 맞춰 1장 12개·2장 14개·3장 17개 레슨 구성. 이후 장은 순차 확장 예정.
- **SSD/NAND**: NAND → 호스트 인터페이스 → FTL → 컨트롤러 → 신뢰성 → 차세대.
- **자동차 SW**: 차량 전자 구조 → 차량 통신 → AUTOSAR & SDV → 기능안전·보안 → ADAS/응용 SW.

기초 레슨에는 직접 만든 SVG 도식과 참고한 책의 절·페이지를 표시.
확인 문제는 스스로 풀고 해설을 펼쳐보는 방식이며, 레슨 완료·점수는 자동 저장하지 않음.
앱 로고와 시작 화면을 제공하며, 챕터·용어 사전·복습 화면의 제목 스타일을 통일.

### 날짜별 콘텐츠 탐색

피드 날짜 클릭 → 달력에서 날짜 선택 → 해당 날짜의 기사·학습 콘텐츠·용어 확인.
콘텐츠가 없는 날짜는 선택할 수 없고, 월 이동도 콘텐츠가 있는 월 사이에서만 가능.
날짜별 화면의 ‘최신으로’ 링크로 최신 피드에 복귀.

용어는 처음 등장한 날짜뿐 아니라 다시 등장한 날짜에도 표시하고 중복 제거.
비어 있는 다이제스트는 달력·최신 피드에서 제외.
하단 타임라인 메뉴는 제거했으며, 기존 `/timeline` 주소는 링크 호환을 위해 유지.

## 카드 요약과 상세 보기

- **메인 카드**: 기사 요약은 최대 300자, 학습 요약은 최대 350자로 핵심과 맥락을 설명. 요약과 인사이트는 설명체 존댓말로 통일하고 제목 앞 항목 번호는 제거.
- **상세 보기**: 기사·개념 카드에서 해당 항목의 메일 원문과 AI 심화 해설 확인. 해설에는 배경지식·펌웨어 관점·더 공부할 거리 포함.
- **기존 콘텐츠**: 새 요약 규칙은 새 수집부터 적용. 기존 날짜 재생성 방법과 북마크 삭제 주의사항은 아래 자동화 안내 참고.

## 복습 방식

1. **하루 학습량 설정**: 기본 10개, 5·10·20개 중 선택. 계정별 목표 저장.
2. **출제 범위 선택**: 전체 또는 SSD/자동차 분야·주제·다이제스트 날짜로 제한.
3. **출제 순서**: 복습일이 오래 지난 용어 우선, 남은 자리에 새 용어 배정. 새 용어는 하루 최대 3개.
4. **문제 풀이**: 서술형·AI 첨삭 또는 객관식 선택. 객관식 오답은 같은 주제 우선, 중복·빈 보기 제외.
5. **진도 저장**: 답변 저장 성공 시 완료 처리. 화면 재진입 시 같은 날의 마지막 문제 목록에서 이어하기.
6. **목표 완료**: 완료 화면에서 추가 5개 학습 가능. 새 용어 한도와 당일 완료 용어 제외 규칙은 유지.

취약 용어 모드는 복습 예정일과 관계없이 ‘몰랐음·애매함’으로 기록된 용어만 출제.
주제별 학습도 하루 목표에 합산. 날짜가 바뀌면 새 복습 목록으로 시작하며 기존 복습 기록은 유지.
새 용어 한도나 출제 범위 때문에 가능한 문제가 적으면 목표보다 적은 분량으로 종료.
저장 전 작성 중인 답변은 이어하기 대상에서 제외.

## 주요 설계 결정

- **LLM 기반 구조화**: 가변적인 메일 형식에 대응하기 위해 기사·학습 콘텐츠·용어를 LLM으로 추출하고 원문 보관.
  파싱 구현 위치: `fetcher/openai_parser.py`.
- **태그 기반 학습 연결**: 기사와 용어를 주제로 묶고, 학습 순서가 있는 태그를 챕터로 확장해 뉴스와 커리큘럼 연결.
- **사전 작성 레슨**: 검토한 콘텐츠를 시드로 관리하고, Markdown과 인라인 SVG로 설명과 도식 제공.
- **데이터 로딩 최적화**: 목록에서 원문·해설을 제외하고 상세를 열 때 조회. 챕터는 탭별로 필요한 데이터를 불러오고 반복 DB 조회를 줄이며 JSON 응답에 gzip 압축 적용.
- **브라우저 메모리 캐시**: 태그·레슨·날짜 목록·개념 목록·카드 상세를 계정별로 최대 60초 재사용. 로그아웃·AI 해설 생성 시 초기화하며, 복습 상태·숙련도·북마크·메모에는 완료 응답 캐시 미적용.
- **PC와 독립적인 수집**: GitHub Actions에서 정기 수집 실행. API는 Cloud Run, 프론트엔드는 Vercel에서 제공.

모델 구조: [커리큘럼 문서](docs/curriculum.md).
기초 트랙의 장별 범위·작성 형식·용어·그림·검수 기준: [기초 학습 작성 규칙](docs/foundations.md).

## 기술 스택

| 영역 | 사용 기술 |
|---|---|
| 프론트엔드 | React, Vite, React Router, CSS, marked |
| 백엔드·인증 | Django, Django REST Framework, TokenAuthentication |
| 데이터베이스 | Supabase PostgreSQL, 로컬 SQLite 지원 |
| 메일·AI | Gmail API(OAuth 2.0), OpenAI API |
| 수집 자동화 | GitHub Actions |
| 배포 | Vercel, Google Cloud Run, Artifact Registry, Cloud Build |

패키지 버전: [requirements.txt](requirements.txt), [frontend/package.json](frontend/package.json).
백엔드 배포: `master` push → 연결된 Cloud Build 트리거 실행 →
`cloudbuild.yaml`에 정의된 빌드 → 이미지 업로드 → Cloud Run 배포.

## 로컬 실행

실행 환경: Actions와 동일한 **Python 3.12**, 프론트엔드용 Node.js 및 npm.

### 1. 환경 설정

프로젝트 루트에 `.env` 생성. 아래는 로컬 SQLite 사용 예시.

```dotenv
DJANGO_SECRET_KEY=local-development-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,testserver
DATABASE_URL=sqlite:///db.sqlite3
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-5.4-mini
```

- **DB 설정**: `DATABASE_URL` 생략 시 SQLite 사용. Supabase 주소 설정 시 로컬 명령도 해당 DB에 반영되므로 개발용 DB와 서비스 DB 구분 필요.
- **Gmail 인증**: 데스크톱 앱 OAuth 클라이언트 JSON을 `fetcher/credentials.json`에 저장.
  최초 수집 시 브라우저 인증 후 `fetcher/token.json` 자동 생성.

### 2. 백엔드 실행

가상환경 생성·활성화 후 프로젝트 루트에서 실행.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_tags
python manage.py seed_lessons
python manage.py seed_lesson_pages
python manage.py seed_foundations
python manage.py createsuperuser
python manage.py runserver
```

앱 로그인 화면의 **회원가입**으로 일반 계정 생성 가능. `createsuperuser`는 관리자 계정 생성용.
메일 수집은 별도로 `python manage.py fetch_digest` 실행.
`seed_foundations`는 컴퓨터 구조 기초 3개 챕터·43개 레슨을 생성·갱신.
본문 수정 후 재실행하면 기존 레슨 ID를 유지하며 파일 내용으로 갱신하므로 DB에서 수동 편집한 본문은 덮어씀.

기존 환경을 업데이트할 때도 `python manage.py migrate` 실행 필요.
복습 목표·이어하기는 `0016_review_sessions`, 개념 북마크는 `0017_conceptbookmark` 사용.
컴퓨터 구조 기초 분류는 `0018_tag_foundations_category` 사용. 이미 적용된 환경에서 레슨 내용만 갱신하려면 `seed_foundations` 재실행.
Cloud Run 시작 시 자동 적용되지 않으므로 대상 DB 마이그레이션 → 백엔드 → 프론트엔드 순서로 배포.
날짜별 달력 변경 자체에는 추가 마이그레이션·시드가 필요 없으며, 새 날짜 API를 위해 백엔드와 프론트엔드를 함께 배포.

### 3. 프론트엔드 실행

별도 터미널에서 실행.

```bash
cd frontend
npm install
npm run dev
```

- **기본 API 경로**: `/api`. Vite가 로컬 백엔드 `http://127.0.0.1:8000`으로 전달합니다.
- **다른 백엔드 연결**: 로컬은 `frontend/vite.config.js`의 프록시 대상, 운영은 `frontend/vercel.json`의 `/api/:path(.*)` rewrite 대상을 변경합니다. `VITE_API_BASE`는 사용하지 않습니다.
- **로그인 유지**: HttpOnly 쿠키 기반 서버 세션으로 최대 30일 유지합니다. 백엔드 → 프런트엔드 순서로 배포하고, 최초 전환 후에는 한 번 다시 로그인합니다. 세부 설정은 [운영 문서](docs/operations.md#로그인-유지-변경-배포)를 참고하세요.

## AI 모델 설정

기본 모델: `gpt-5.4-mini`. 루트 `.env`의 `OPENAI_API_KEY`와 `OPENAI_MODEL`로 설정.
메일 구조화·심화 해설·서술형 첨삭·태그 분류에 공통 적용.
기능별 모델을 따로 설정할 수 있으며, 기존 DB와 Gmail 인증은 그대로 사용.

로컬·GitHub Actions·Cloud Run의 키 등록과 모델 설정: [OpenAI 설정 문서](docs/openai.md).

## 자동화와 누락 날짜 복구

- **정기 실행**: [수집 워크플로](.github/workflows/fetch_digest.yml)에서 KST 05:00~06:45 사이 15분 간격 실행.
- **기본 수집 대상**: 최근 메일 중 최신 다이제스트.
- **일시적 오류 대응**: OpenAI SDK에서 일시적 연결·서버·요청 제한 오류를 최대 2회 재시도.

**누락 날짜 복구는 날짜를 직접 지정하는 방식.** 과거 누락분의 일괄 자동 복구는 미지원.

1. **수동 실행 열기**: 날짜 지정 기능이 반영된 브랜치에서 GitHub **Actions → Fetch Daily Digest → Run workflow** 선택.
2. **대상 날짜 입력**: `date`에 `2026-10-13`처럼 메일 제목의 날짜 입력 후 실행.
3. **복구 결과 확인**: 실행 로그와 앱의 날짜별 달력 확인. 다른 날짜는 각각 별도 실행. 날짜 목록은 최대 60초 캐시되므로 새 날짜가 바로 표시되지 않으면 잠시 후 달력을 다시 열어 확인.

이미 저장된 날짜를 새 파싱 규칙으로 다시 만들려면 `date` 입력 후 **force** 체크.
해당 날짜의 기존 기사·학습 카드를 교체하고 AI 해설도 다시 생성하므로 API 사용료 발생.
카드 ID가 교체되면서 해당 개념의 북마크도 삭제되므로 북마크 보존이 필요하면 사용하지 않기.
`force`의 기본값은 꺼짐이며, 정기 실행은 기존처럼 저장된 날짜를 건너뛰기.

`date`를 비우면 최신 메일 수집. 아래 명령으로 로컬 실행도 가능.

```bash
python manage.py fetch_digest                     # 최신 메일 수집
python manage.py fetch_digest --date 2026-10-13   # 특정 날짜 복구
python manage.py fetch_digest --dry-run           # DB 저장 없이 파싱 결과 확인
python manage.py fetch_digest --force             # 선택된 날짜의 기존 콘텐츠 교체
```

- **중복 저장 방지**: 이미 저장된 날짜는 기본적으로 건너뛰며, 누락 날짜 복구에는 `--force` 불필요.
- **미리보기 범위**: `--dry-run`은 DB 저장만 생략하며 Gmail 및 OpenAI API 호출 포함.

Actions 실행에 필요한 GitHub Secrets. 로컬 인증 파일과 별도 관리.

| Secret | 용도 |
|---|---|
| `GMAIL_CREDENTIALS_JSON` | Gmail OAuth 클라이언트 JSON |
| `GMAIL_TOKEN_JSON` | Gmail 접근 토큰 및 갱신 정보 |
| `OPENAI_API_KEY` | 구조화·해설 생성 API 인증 |
| `DATABASE_URL` | 저장 대상 DB 연결 |
| `DJANGO_SECRET_KEY` | Django 실행 설정 |

배포 절차와 기존 장애 대응 기록: [운영 문서](docs/operations.md).

## 코드 둘러보기

```text
ssd_studyapp/
├── config/                  # Django 설정·URL
├── digest/                  # 데이터 모델·REST API·관리 명령
│   ├── content/foundations/ # H&H 기초 레슨 Markdown·인라인 SVG
│   └── management/commands/ # 수집 및 커리큘럼 시드
├── fetcher/                 # Gmail 수집·OpenAI 파싱·원문 순서 처리
├── frontend/src/            # React 화면·컴포넌트·API 클라이언트
├── .github/workflows/       # 수집 자동화
├── cloudbuild.yaml          # 백엔드 빌드·배포
└── docs/                    # 운영·커리큘럼 상세 문서
```

## 앞으로 할 것

- [ ] 컴퓨터 구조 기초 3장 이후 레슨 확장
- [ ] 채용공고 메뉴·목록 추가
- [ ] PWA 오프라인 지원
- [ ] 질문·인사이트 전체 모아보기 화면
- [ ] 용어 숙련도 통계·대시보드
- [ ] 콘텐츠가 쌓인 자동차 트랙 일반 태그를 챕터로 확장
- [ ] 챕터·레슨 완료 체크 및 학습 진행률
