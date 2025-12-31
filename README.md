# AI Daily News Summarizer

인공지능 소식을 매일 자동으로 수집하고, Gemini LLM을 통해 요약하여 제공하는 풀스택 웹 애플리케이션입니다.

## 1. 문제 정의 (Problem Definition)

수많은 AI 관련 뉴스가 쏟아지는 현대 사회에서, 모든 기사를 직접 찾아 읽는 것은 많은 시간과 노력이 소요됩니다. 
- **정보 과잉**: 어떤 뉴스가 중요한지 판단하기 어렵습니다.
- **언어 장벽**: 주요 소식이 해외 매체에서 먼저 나올 경우 접근성이 떨어집니다. (본 프로젝트는 국내 주요 AI 매체를 우선적으로 다룹니다.)
- **시간 소모**: 매번 사이트를 방문하여 업데이트를 확인해야 하는 번거로움이 있습니다.

**해결책**: 2시간 간격으로 주요 언론사의 AI 기사를 크롤링하고, 강력한 Gemini AI를 사용하여 핵심 요약을 생성함으로써 사용자가 단 몇 초 만에 최신 트렌드를 파악할 수 있도록 돕습니다.

## 2. 주요 기능 (Key Features)

- **자동 크롤링**: 인공지능신문, AI타임즈 등 국내 주요 AI 전문 매체의 최신 기사를 2시간마다 수집합니다.
- **AI 요약**: Google Gemini Flash 모델을 사용하여 기사 본문을 제목 + 3개 핵심 포인트로 자동 요약합니다.
- **데이터 보존**: 자정 이후에도 이전 데이터가 삭제되지 않도록 보호하며, 당일 뉴스가 올라오기 전까지는 전날의 콘텐츠를 지속적으로 제공합니다.
- **반응형 인터페이스**: 현대적이고 깔끔한 UI를 통해 모바일과 데스크톱 어디서든 편리하게 소식을 확인할 수 있습니다.

## 3. 프로젝트 구조 (Project Structure)

```text
news_summarization/
├── backend/                # 백엔드 핵심 로직 (Python Package)
│   ├── crawler.py          # 뉴스 크롤러 로직
│   ├── summarizer.py       # Gemini API 활용 요약 엔진
│   ├── database.py         # PostgreSQL DB 인터페이스
│   ├── tasks.py            # 백그라운드 스케줄러 및 작업
│   ├── check_db.py         # DB 상태 확인 도구
│   └── __init__.py         # 패키지 초기화 파일
├── frontend/               # 프론트엔드 (React + Vite)
│   ├── src/                # 소스 코드
│   ├── index.html          # HTML 엔트리
│   ├── vite.config.js      # Vite 설정
│   └── package.json        # 프론트엔드 의존성
├── main.py                 # 서비스 통합 및 API 진입점 (Root)
├── requirements.txt        # 전체 백엔드 의존성 (Root)
├── Dockerfile              # 컨테이너화 설정
├── render.yaml             # Render.com 배포 설정 (PostgreSQL 포함)
└── README.md               # 프로젝트 문서 (현재 파일)
```

## 4. 시작하기 (Getting Started)

### 사전 준비
- Python 3.10+
- Node.js 20+
- Google Gemini API Key
- PostgreSQL (로컬 개발 시)

### 환경 설정
`.env` 파일을 root 폴더에 생성하세요.
```env
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/news_db
```

### 서버 실행 (Backend)
```bash
pip install -r requirements.txt
python main.py
```

### 클라이언트 실행 (Frontend)
```bash
cd frontend
npm install
npm run dev
```

## 5. 배포 (Deployment)

본 프로젝트는 Docker를 통해 간편하게 배포할 수 있습니다.
### Docker Compose (추천)
Docker Compose를 사용하면 환경 변수와 볼륨 설정이 자동으로 적용되어 더 간편합니다.
```bash
# 실행
docker-compose up -d

# 중지
docker-compose down
```

### Docker CLI
```bash
docker build -t ai-news-summarizer .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key ai-news-summarizer
```

## 6. 라이선스
ISC License
