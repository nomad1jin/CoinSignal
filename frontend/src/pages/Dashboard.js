// src/pages/Dashboard.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [coinList, setCoinList] = useState([]);
  const [loading, setLoading] = useState(true);

  const goToSearch = () => {
    navigate('/search');
  };

  useEffect(() => {
    const fetchTrendingCoins = async () => {
      try {
        const response = await fetch('http://localhost:8000/trending'); // API 주소에 맞게 수정
        const result = await response.json();

        if (result.success) {
          setCoinList(result.data);
        } else {
          console.error('API 실패:', result.message);
        }
      } catch (err) {
        console.error('요청 에러:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendingCoins();
  }, []);

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">코인시그널 - 메인 대시보드</h1>

      <div className="dashboard-layout">
        <div className="dashboard-left">
          {/* 수익률 + 차트 */}
          <section className="section">
            <h2 className="section-title">투자 현황</h2>
            <div className="profit-box">
              <p>기간 수익률</p>
              <p>최근 7일</p>
              <p className="profit-rate">+ 10.02% (97,000원)</p>
            </div>
          </section>

          <section className="section">
            <h2 className="section-title">투자 비중</h2>
            <div className="donut-chart-box">
              여기에 도넛 차트 들어갈 예정
            </div>
          </section>
        </div>

        <div className="dashboard-right">
          <h2 className="section-title">🔥 지금 핫한 코인</h2>
          <ul className="coin-list">
            {loading ? (
              <li>로딩 중...</li>
            ) : coinList.length > 0 ? (
              coinList.map((coin, idx) => (
                <li key={idx}>
                  {coin.coin.toUpperCase()} - Score: {coin.score}
                </li>
              ))
            ) : (
              <li>표시할 코인이 없습니다</li>
            )}
          </ul>

          <button className="novel-style-button" onClick={goToSearch}>
            📌 새로운 코인을 구매하러 가기
          </button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
