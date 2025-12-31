import React, { useState, useEffect } from 'react';

const App = () => {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/news')
            .then(res => res.json())
            .then(data => {
                setNews(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const krNews = news.filter(n => n.source === 'aitimes.kr');
    const comNews = news.filter(n => n.source === 'aitimes.com');

    return (
        <div className="container">
            <header className="header">
                <h1>AI DAILY NEWS SUMMARY</h1>
                <p className="subtitle">인공지능 소식을 매일 2시간 간격으로 요약하여 제공합니다.</p>
                <div className="glow-bar"></div>
            </header>

            <main className="content">
                <section className="site-section">
                    <h2 className="site-title">인공지능신문</h2>
                    <div className="news-grid">
                        {loading ? (
                            <div className="loader">데이터를 불러오는 중...</div>
                        ) : (
                            krNews.map(item => <NewsCard key={item.id} item={item} />)
                        )}
                    </div>
                </section>

                <section className="site-section">
                    <h2 className="site-title">AI타임즈</h2>
                    <div className="news-grid">
                        {loading ? (
                            <div className="loader">데이터를 불러오는 중...</div>
                        ) : (
                            comNews.map(item => <NewsCard key={item.id} item={item} />)
                        )}
                    </div>
                </section>
            </main>

            <footer className="footer">
                <p>© 2025 AI Daily Summary. Powered by Gemini LLM.</p>
            </footer>
        </div>
    );
};

const NewsCard = ({ item }) => {
    return (
        <div className="card">
            <div className="card-glass"></div>
            <div className="card-content">
                <span className="date">{item.published_at}</span>
                <h3 className="title">{item.title}</h3>
                <div className="summary" dangerouslySetInnerHTML={{ __html: item.summary?.replace(/\n/g, '<br/>') || '요약 생성 중...' }}></div>
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="link">원문 보기</a>
            </div>
        </div>
    );
};

export default App;
