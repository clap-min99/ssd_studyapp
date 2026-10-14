# OpenAI API 설정

[README로 돌아가기](../README.md)

메일 구조화, 기사·학습 콘텐츠 심화 해설, 서술형 복습 첨삭, 기존 데이터의 태그·원문 채우기를
OpenAI Responses API로 처리. 기존 DB 데이터와 Gmail OAuth 인증은 그대로 사용.

## 로컬 설정

1. 가상환경에서 `python -m pip install -r requirements.txt` 실행.
2. 프로젝트 루트의 기존 `.env`에 아래 두 항목 추가. 다른 Django·DB 설정은 유지.
3. 실행 중인 백엔드 재시작.

```dotenv
OPENAI_API_KEY=발급받은_API_키
OPENAI_MODEL=gpt-5.4-mini
```

설정 예시: [`.env.example`](../.env.example). 실제 키는 `.env`에만 저장하고 커밋에서 제외.
`GEMINI_API_KEY`는 더 이상 사용하지 않으므로 삭제 가능.

기본 모델은 `gpt-5.4-mini`. 모델 변경 시 해당 프로젝트의 모델 접근 권한과 Responses API·
Structured Outputs 지원 여부 확인 필요. 모델의 사용 가능 여부는 계정에 따라 달라질 수 있음.

## 기능별 모델 설정 (선택)

| 환경변수 | 담당 기능 |
|---|---|
| `OPENAI_MODEL` | 모든 기능의 기본 모델 |
| `OPENAI_PARSE_MODEL` | 메일 구조화·원문 추출 |
| `OPENAI_EXPLAIN_MODEL` | 기사·학습 콘텐츠 심화 해설 |
| `OPENAI_REVIEW_MODEL` | 서술형 복습 첨삭 |
| `OPENAI_TAG_MODEL` | 기존 기사·용어 태그 분류 |

적용 순서: 기능별 설정 → `OPENAI_MODEL` → 코드 기본값 `gpt-5.4-mini`.
처음에는 기본 모델 하나로 시작하고, 결과와 비용을 확인한 뒤 기능별로 조정 가능.
공백이나 빈 값으로 둔 기능별 설정은 기본 모델 사용.

## GitHub Actions 설정

저장소 **Settings → Secrets and variables → Actions**에서 설정.

- **Secrets**: `OPENAI_API_KEY`에 실제 키 저장.
- **Variables**: `OPENAI_MODEL`에 `gpt-5.4-mini` 입력. 생략 시에도 같은 모델 사용.
- 기능별 모델 변경이 필요하면 위 표의 기능별 환경변수 이름으로 Variables 추가.
- Gmail 인증과 DB 연결에 사용하는 기존 Secrets는 유지.

수동 실행: **Actions → Fetch Daily Digest → Run workflow**.
누락 날짜 복구 시 `date`에 `2026-10-13` 입력.
이미 저장된 날짜의 카드도 다시 만들려면 **force** 체크 후 실행.
선택한 날짜의 기사·학습 카드 교체 및 해설 재생성으로 API 사용료 발생.

## Cloud Run 설정

현재 [Cloud Build 설정](../cloudbuild.yaml)은 아래 구성을 사용.

1. 서비스가 사용하는 GCP 프로젝트의 Secret Manager에 **`openai-api-key`** Secret 생성 후 실제 키 저장.
2. Cloud Run 실행 서비스 계정에 해당 Secret 읽기 권한 부여.
3. Cloud Build 트리거의 사용자 정의 치환 변수 **`_OPENAI_MODEL`**에 `gpt-5.4-mini` 설정.
   생략 시 `cloudbuild.yaml`의 기본값 적용.
4. 새 코드 배포 후 Cloud Run의 `OPENAI_API_KEY` Secret 참조와 `OPENAI_MODEL` 환경변수 확인.

기능별 모델은 `_OPENAI_PARSE_MODEL`, `_OPENAI_EXPLAIN_MODEL`, `_OPENAI_REVIEW_MODEL`,
`_OPENAI_TAG_MODEL` 치환 변수로 변경 가능. 기본은 모두 빈 값.
Cloud Run 콘솔에서만 변경한 모델 설정은 다음 Cloud Build 배포 시 치환 변수 값으로 다시 적용되므로
지속할 설정은 Cloud Build 트리거에도 반영 필요.

로컬 `.env`, GitHub Actions, Cloud Run 설정은 서로 독립적이므로 각 실행 환경에 별도 등록 필요.
프론트엔드에는 API 키 설정 불필요.

## 확인 및 오류 대응

```bash
# Gmail 조회와 OpenAI 구조화 실행. DB 저장은 생략하지만 API 사용료 발생.
python manage.py fetch_digest --date 2026-10-13 --dry-run

# 결과 확인 후 실제 저장 및 심화 해설 생성
python manage.py fetch_digest --date 2026-10-13
```

`--dry-run`은 수집·구조화 확인용이며 심화 해설·첨삭·태그 백필은 별도 호출.
로컬 Gmail OAuth 오류는 OpenAI 키와 별개이므로 [운영 문서](operations.md)의 Gmail 인증 복구 참고.

- **키 누락·인증 오류**: 실행 환경의 `OPENAI_API_KEY` 확인.
- **모델 접근 오류**: 모델명과 해당 API 프로젝트의 접근 권한 확인.
- **429 오류**: API 결제 잔액·사용 한도·요청 속도 확인. 잔액 부족은 대기만으로 해결되지 않음.
- **일시적 API 오류**: SDK의 최대 2회 재시도 후 실패 시 같은 날짜로 다시 실행.
- **응답 거절·미완료·형식 오류**: DB 저장 전 실패 처리. 기존 날짜는 `--force` 없이 유지.
- **해설 생성 실패**: 다이제스트 저장은 유지하며 앱에서 재생성 가능.

공식 안내: [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini),
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
