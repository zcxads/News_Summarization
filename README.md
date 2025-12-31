# AI Daily News Summary

인공지능(AI) 관련 최신 뉴스를 자동으로 수집하고, Google Gemini LLM을 사용하여 핵심 내용을 요약해 주는 서비스입니다.

## 주요 기능
- **뉴스 크롤링**: 국내외 주요 AI 뉴스 사이트에서 최신 기사를 자동으로 수집합니다.
- **AI 요약**: Gemini 3 Flash 모델을 활용하여 기사 내용을 전문적이고 간결하게 한글로 요약합니다.
- **스케줄링**: 2시간 간격으로 새로운 뉴스를 체크하고 요약본을 업데이트합니다.
- **반응형 웹 UI**: 모던하고 세련된 다크 모드 기반의 인터페이스를 제공합니다.

## 기술 스택
### Backend
- **Python / FastAPI**: 빠르고 현대적인 고성능 웹 프레임워크
- **SQLite**: 가벼운 로컬 데이터베이스
- **Google Generative AI (Gemini)**: 뉴스 요약을 위한 LLM
- **BeautifulSoup4**: 웹 크롤링
- **APScheduler**: 백그라운드 작업 스캐줄링

### Frontend
- **React**: 사용자 인터페이스 구축
- **Vite**: 초고속 프런트엔드 빌드 도구
- **Vanilla CSS**: 세련된 글래스모피즘(Glassmorphism) 디자인

## 시작하기

### 1. 환경 설정
프로젝트 루트 폴더에 `.env` 파일을 생성하고 아래 내용을 입력합니다.
```env
GEMINI_API_KEY=your_gemini_api_key
```

### 2. 로컬 실행
**백엔드 실행 (API 및 스케줄러)**
```bash
pip install -r requirements.txt
python main.py
```

**프론트엔드 실행**
```bash
npm install
npm run dev:client
```

## 배포 (Deployment)
본 프로젝트는 **Render**와 **Docker**를 통한 자동 배포에 최적화되어 있습니다.
- `Dockerfile`: 멀티 스테이지 빌드를 지원합니다.
- `render.yaml`: Render Blueprint를 지원합니다.
