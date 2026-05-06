# **한조각(One-Piece)**

## 📖 프로젝트 소개

> 개인의 취향에 맞는 향테리어를 추천하는 서비스

<br>

---

## 🗓️ 프로젝트 기간
- 2026년 4월 2일 - 2026년 5월 8일
<br>

---

## 🧰 사용 스택



<br>

---

# 👥 팀 동료


| 프로필                                                         | GitHub                                 | 이름  |
|-------------------------------------------------------------|----------------------------------------|-----|
| <img src="https://github.com/PJG8806.png" width="80"/> | [@PJG8806](https://github.com/PJG8806) | 박진규 |
| <img src="https://github.com/HHJina.png" width="80"/> | [@HHJina](https://github.com/HHJina)   | 황현진 |
| <img src="https://github.com/gyugyu99.png" width="80"/>     | [@gyu](https://github.com/gyugyu99)    | 이규빈 |
| <img src="https://github.com/tkdqh57.png" width="80"/>      | [@sangbo](https://github.com/tkdqh57)  | 심상보 |




<br>

## 🔗 Social Sharing & OG Crawler (공유 및 소셜 크롤러)

<details>
<summary><b>상세 내용 보기 (클릭)</b></summary>

### 🔑 주요 기능 (Key Features)
* **동적 공유 이미지 생성 (Dynamic Image Generation)**
    * 결과 반영 HTML 템플릿 실시간 렌더링 및 **Playwright** 기반 고해상도 PNG 캡처
* **소셜 미디어 최적화 (OG Tag Management)**
    * 고유 `share_id`를 부여하고 **Open Graph** 메타데이터 최적화
    * 카카오톡, 페이스북 등 채널별 고품질 미리보기 카드 이미지 제공
* **효율적인 리소스 서빙**
    * 생성 이미지를 S3에 자동 업로드하고 **CloudFront CDN**을 통해 지연 없는 로딩 구현

### 🛠 기술 스택 (Technical Stack)
* **Browser Automation:** Playwright (Python)
* **Template Engine:** Django Templates
* **Infrastructure:** Amazon S3 & AWS CloudFront

### 🚀 개발 중점 사항 (Development Focus)
* **보안 업로드**: AWS Presigned URL 및 CloudFront 연동으로 이미지 보안 노출 차단
* **자원 절약**: S3 Handler 내 중복 체크 로직으로 동일 결과에 대한 이미지 생성 방지
</details>

---

## 👤 User & Authentication (유저 및 인증)
<details>
<summary><b>상세 내용 보기 (클릭)</b></summary>

### 🔑 주요 기능 (Key Features)
* **다중 소셜 로그인 지원 (Multi-Channel Social Login)**
    * **Google, Kakao, Naver** API 연동을 통한 간편 로그인 제공
    * OAuth 2.0 프로토콜 기반의 안전한 데이터 연동
* **휴대폰 번호 기반 보안 인증 (SMS Authentication)**
    * **Solapi(Coolsms)** 활용 실시간 인증 번호 발송 시스템
    * 6자리 숫자 코드 방식을 통한 사용자 편의성 및 보안 강화
* **S3 기반 프로필 이미지 시스템 (Profile Management)**
    * **Amazon S3** 및 **Presigned URL** 방식을 통한 서버 부하 최소화 및 보안 업로드 구현

### 🛠 기술 스택 (Technical Stack)
* **Backend:** Python Django (REST Framework)
* **Infrastructure:** Docker, Docker-Compose
* **Storage:** Amazon S3
* **Testing:** Django TestCase & setUpTestData

### 🚀 개발 중점 사항 (Development Focus)
* `TestCase`와 `setUpTestData`를 활용한 고성능 백엔드 테스트 환경 구축
* Docker 기반의 일관된 개발 및 운영 환경 유지
</details>
<br>

---

## 🧪 Scent & AI Analysis (향수 추천 및 AI 분석)

<details>
<summary><b>상세 내용 보기 (클릭)</b></summary>

### 🔑 주요 기능 (Key Features)
* **하이브리드 데이터 스코어링 (Hybrid Scoring System)**
    * 설문 답변을 5가지 지표(Freshness, Warmth, Softness, Depth, Sweetness)로 수치화
    * **유클리드 거리** 알고리즘을 활용해 1만 건의 DB 중 최적의 향수 선별
* **Gemini AI 기반 개인화 큐레이션**
    * 유저 선호도를 결합한 프롬프트를 통해 맞춤형 추천 사유 자동 생성
    * **Gemini Flash** 기반의 카테고리별 맞춤형 향수 시각화 이미지 생성
* **서비스 안정성 및 결함 허용 (Fault Tolerance)**
    * **3-Step Retry**: API 에러 시 5초 간격으로 최대 3회 재귀적 재시도 수행
    * **Graceful Degradation**: 호출 실패 시에도 추천 리스트를 우선 반환하여 연속성 유지

### 🛠 기술 스택 (Technical Stack)
* **AI Engine:** Google Gemini Pro & Gemini 2.5 Flash
* **Cache:** Redis (지표 맵핑 데이터 및 DB 캐싱)
* **Storage:** Amazon S3 & AWS CloudFront

### 🚀 개발 중점 사항 (Development Focus)
* **성능 최적화**: DB 쿼리 최적화를 통해 응답 시간을 **1.2s에서 0.1s로 91% 단축**
* **캐싱 전략**: 빈번한 데이터 조회를 Redis에 캐싱하여 DB 부하 최소화
</details>

---

## 🤖 Chatbot (AI 향기 추천 챗봇)

<details>
<summary><b>상세 내용 보기 (클릭)</b></summary>

### 🔑 주요 기능 (Key Features)
* **대화형 개인화 추천 시스템 (Conversational Recommendation)**
    * 자연스러운 대화를 통해 공간, 분위기, 강도, 시간대를 분석하여 최적의 향수 추천
    * **LLM + Rule-based 이중 파싱** 구조를 통해 한국어 자연어 처리의 안정성 확보
    * 정보 부족 시 베스트셀러 기반의 **Fallback 추천**으로 대화 끊김 방지
* **Redis 기반 지능형 세션 관리 (Session Management)**
    * **Redis TTL(20분)** 기반 세션 관리로 멀티 프로세스 환경에서도 안정적인 동시성 유지
    * 대화 히스토리, Context, 추천 이력을 통합 관리하여 맥락 있는 대화 제공
* **AI 응답 안정성 및 보안 (Reliability & Security)**
    * **모델 Fallback 전략**: 메인 모델 실패 시 `gemini-2.0-flash-lite`로 자동 전환
    * **이중 검증 시스템**: 프롬프트 제어와 백엔드 로직을 결합해 중복 추천을 원천 차단
    * **보안 필터링**: `korcen` 라이브러리를 통한 욕설 감지 및 프롬프트 인젝션 방어

### 🛠 기술 스택 (Technical Stack)
* **AI Engine:** Google Gemini 2.5 Flash
* **Backend:** Python Django (REST Framework)
* **Session & Cache:** Redis
* **Validation:** korcen (Korean Censorship Library)

### 🚀 개발 중점 사항 (Development Focus)
* **신뢰성 향상**: LLM 단독 의존에서 탈피, **Rule-based 매핑 테이블을 병행**하여 분석 정확도 개선
* **데이터 유연성**: 하드코딩된 데이터를 **DB 직접 조회 방식**으로 리팩토링하여 데이터 확장성 확보
* **아키텍처 고도화**: 메모리 기반 세션을 **Redis**로 전환하여 서버 재시작 및 멀티 프로세스 환경에 대응
</details>

---

## 🖼️ AI Image Analysis & Integrated Curation (이미지 분석 및 통합 큐레이션)

<details>
<summary><b>상세 내용 보기 (클릭)</b></summary>

### 🔑 주요 기능 (Key Features)
* **멀티모달 AI 분석 및 장애 방어 (AI Integration & Resilience)**
    * **Google Gemini API**를 활용하여 이미지의 무드 및 향기 메타데이터 정밀 추출
    * 외부 API 지연(504 Timeout) 대비 **재시도(Retry) 로직** 및 **Fallback 방어선**(DB 기반 인기 향수 제공) 구축
* **이미지 메타데이터 전처리 파이프라인**
    * **OpenCV & ColorThief**를 활용한 지배 색상(Hex), 명도, 채도, 대비 분석 및 수치화
    * **S3 Presigned URL** 방식을 도입하여 대용량 이미지 처리 시 서버 부하 최소화 및 보안 강화
* **자체 매칭 알고리즘 및 통합 API (BFF Pattern)**
    * **다이스 계수(Dice Coefficient)** 알고리즘 기반 키워드 매칭 및 가중치(Weight) 적용 추천 로직 구현
    * 이미지·설문·챗봇 데이터를 단일 엔드포인트로 묶어주는 **BFF(Backend For Frontend) 패턴** 설계

### 🛠️ 기술 스택 (Technical Stack)
* **Backend:** Python, Django (REST Framework)
* **Data / AI:** Google Gemini API, OpenCV, Numpy, ColorThief
* **Infrastructure:** AWS S3, Docker, Nginx, Gunicorn

### 🚀 개발 중점 사항 (Development Focus)
* **시스템 가용성 최적화**: Gunicorn 동시성 튜닝(Thread/Worker 설정)을 통해 외부 API 대기 시간으로 인한 서버 연쇄 장애 방지
* **데이터 무결성 보장**: 복수 테이블 데이터 동시 Insert 시 `transaction.atomic()`을 적용하여 원자성 확보
* **인터페이스 추상화**: 다형성(Polymorphism)을 활용해 출처가 다른 데이터를 단일 규격(DTO)으로 추상화하여 프론트엔드 렌더링 효율 극대화
</details>

---

## 📂 프로젝트 구조

<details>
<summary><b>주요 디렉토리 구조 보기 (클릭)</b></summary>

```bash

.
├── apps/                   # 서비스 핵심 로직 앱 모음
│   ├── analysis/           # 데이터 분석 및 통계 관련 로직
│   ├── chatbot/            # AI 챗봇 및 실시간 응답(SSE) 처리
│   ├── core/               # 공통 유틸리티 및 베이스 모델
│   ├── question/           # 질문/답변 게시판 및 카테고리 관리
│   ├── scent/              # (프로젝트 고유 기능) 향료/데이터 관련 로직
│   └── users/              # 유저 인증, 소셜 로그인 및 프로필 관리
├── config/                 # Django 프로젝트 설정 (settings, asgi/wsgi)
├── deployments/            # 배포 관련 설정 (Docker, Nginx 등)
├── envs/                   # 환경 변수 설정 파일 관리 (.env)
├── scripts/                # 자동화 및 실행 스크립트 (makefile 연동)
├── static/ & templates/    # 정적 파일 및 HTML 템플릿
├── makefile                # 프로젝트 운영 명령축약 (docker_up 등)
├── pyproject.toml & uv.lock # Python 패키지 및 의존성 관리 (uv 사용)
└── manage.py               # Django 실행 엔드포인트

```
</details>

<br>

---
<br>

# 📘 프로젝트 규칙 (Project Rules)

## 🌿 Git Workflow & Convention

### 1.⏳ Git Flow

기본적으로 다음과 같은 브랜치들을 사용합니다.
```
- main/: 제품의 배포 가능한 최종 상태를 저장하는 브랜치
- develop/: 개발 중인 기능을 통합하는 브랜치
- feature/: 새로운 기능 개발을 위한 브랜치
- fix/: 버그를 수정하는 브랜치
- refactor: 리팩토링을 위한 브랜치
- hotfix/: 운영 중인 서비스의 긴급 수정 사항을 처리하는 브랜치
```    
- 기본 브랜치: `main`, `develop`
- `main`, `develop` 직접 push **금지**
- 모든 PR은 최소 **1인 이상 승인 필수**

<br>

### 2. ✏️ Git Commit Convention

 - **🧱 기본 구조** : ` <type>(#이슈번호): <작업 요약> `
 - **✅ 예시** :
   - `✨feat(#10): 시험 모델 추가`
   - `🐛fix(#32): 마이그레이션 오류 수정`
   - `♻️refactor(#78): 시험 조회 로직 리팩터링`
   - `📝docs(#51): README 구조 업데이트`
     
<details>
<summary><strong> 📐 Commit Template </strong></summary><br>

```

### 아래 1번 문항부터 주석 문구가 빈줄에 주석을 지우고 문항에 대한 내용을 작성하고 커밋을 완료해주세요.

# 1. 아래 형식에 맞춰 커밋 메시지 타이틀을 작성하세요:
# <이모지> <타입>: <간결한 커밋 메시지 요약>
#
# 예시:
# ✨ feat: 사용자 로그인 기능 추가
# 🐛 fix: 댓글 생성 시 발생하는 NullPointerException 수정
# 💡 chore: 불필요한 로그 제거 및 변수명 수정
# 🎨 style: black, isort 코드 포매터 실행
# 📝 docs: README에 프로젝트 설명 추가
# 🚚 build: Dockerfile 수정하여 실행 오류 해결
# ✅ test: 게시글 API 단위 테스트 추가
# ♻️ refactor: 중복 코드 제거 및 함수 분리
# 🚑 hotfix: 프로덕션 장애 수정 - 잘못된 URL 패턴 수정

# 2. 변경 또는 추가사항을 아래에 간략하게 작성하세요 ( 필수 )
#
# 본문 내용은 어떻게 변경했는지 보다 무엇을 변경했는지 또는 왜 변경했는지를 설명합니다.

# 3. 이슈가 있다면 아래에 연결하세요 ( 선택 )
#
# 예시
# 관련 이슈: #123

```
</details>

 -   **🔖 Commit Type 정의 → gitmoji**
   
<div align=center> 
  
| 깃모지 |    타입    | 설명                           |
| :-: | :------: | :--------------------------- |
|  ✨  |   feat   | 새로운 기능 추가                    |
|  🐛 |    fix   | 버그 수정                        |
|  💡 |   chore  | 기능 추가 없이 코드 수정 (오타, 주석 등)    |
|  🎨 |   style  | 코드 포매팅 수정                    |
|  📝 |   docs   | 문서 수정 (README 등)             |
|  🚚 |   build  | 빌드 관련 파일 수정                  |
|  ✅  |   test   | 테스트 코드 추가/변경 (프로덕션 코드 변경 없음) |
|  ♻️ | refactor | 리팩터링 (기능 변화 없음)              |
|  🚑 |  hotfix  | 긴급 수정                        |

</div>
  
  
## 🧑🏻‍💻 Code Convention

**1. 🧠 네이밍 규칙**
- **파일명**:  snake_case
- **클래스명**:  PascalCase
- **함수명**:  snake_case
-  **상수**:  UPPER_SNAKE_CASE

<br>

**2. 📍 URL 매핑 규칙**
- `Trailing Slash`는 추가하지 않는다

<br>

**3. ✨ Code Formatting**
- ruff
- mypy
- 위 두 가지를 사용하여 코드 포매팅과 타입 어노테이션을 준수한다.
<br>

**4. 🧪 Test Code**
- Django 내부에 포함된 `TestClient`를 활용하여 테스트코드를 작성한다.
<br>

**5. 🏷️ Swagger 문서**
- Swagger 문서 자동화를 위한 라이브러리로 `drf-spectacular`를 사용한다.
- `extend_schema` 데코레이터를 사용하여 스키마를 구성하고 각 API 별 태깅, API 요약, 구체적인 설명, 파라미터 등을 지정한다.
  - Tag는 해당 API가 해당되는 요구사항 정의서의 카테고리 명을 사용
  - Summary에 해당 API의 요약 설명을 기재
  - Description에 해당 API의 구체적인 동작 설명

<br>

---


## :clipboard: Documents

> [ 🧚 요구사항 정의서 ](https://docs.google.com/spreadsheets/d/1_Lbf-QrA5HzuDRuJK7IijTsXtF867ecWdxJiwiTHop8/edit?usp=sharing)
> 
> [ 🪄 API 명세서 ](https://docs.google.com/spreadsheets/d/1Fh0TjI_4rdC4Q8X6oWCMxx8ioiVlwLabtmGF4nXFPmU/edit?gid=1498506670#gid=1498506670)
>
> [ 🔦 테이블 명세서 ](https://docs.google.com/spreadsheets/d/1xoPda8LjmjpIXA5qnQA7MF6EoyDfh7YNI2l_-0WV0hY/edit?gid=0#gid=0)
>