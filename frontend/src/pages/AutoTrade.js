// ✅ AutoTrade.js
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/AutoTrade.css';
import axios from 'axios';

function AutoTrade() {
  const location = useLocation();
  const navigate = useNavigate();
  const query = new URLSearchParams(location.search);
  const coinName = query.get('coin') || '해당 코인';

  const [started, setStarted] = useState(false);
  const [visibleSteps, setVisibleSteps] = useState([]);
  const [invest, setInvest] = useState('');
  const [lossCut, setLossCut] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [coinCount, setCoinCount] = useState('');

  const statusSteps = [
    {
      title: '🔍 트렌드 분석 결과',
      content: `${coinName}의 검색량은 전날에 비해 35% 증가하였습니다.`,
    },
    {
      title: '🔥 급등한 코인의 데이터 크롤링',
      content: 'Twitter 게시물 1,000개 수집 / Reddit 게시물 1,000개 수집 완료',
    },
    {
      title: '📊 감정 분석 중',
      content: `SNS 분석 결과, ${coinName}에 대한 감정은 "긍정"으로 나타났습니다.`,
    },
    {
      title: '📉 손절/익절 감시 중',
      content: '지정하신 손절 / 익절 기준으로 자동 모니터링이 시작됩니다.',
    },
    {
      title: '⏳ 자동매매 시스템 실행 중',
      content: `${coinName}에 대한 매수를 진행하고 있습니다.`,
    },
  ];

  const handleStart = async () => {
    try {
      await axios.post('http://localhost:8000/user/info', {
        max_daily_invest: Number(invest),
        loss_cut: -Math.abs(Number(lossCut)) / 100,
        take_profit: Math.abs(Number(takeProfit)) / 100,
        max_coin_count: Number(coinCount),
      });

      await axios.post('http://localhost:8000/autotrade/start');

      setStarted(true);
      statusSteps.forEach((_, i) => {
        setTimeout(() => {
          setVisibleSteps((prev) => [...prev, i]);
        }, i * 1200);
      });
    } catch (error) {
      console.error('자동매매 시작 실패:', error);
    }
  };

  const goToDashboard = () => {
    navigate('/');
  };

  return (
    <div className="auto-container">
      {!started ? (
        <div className="auto-box">
          <h2>💸 일일 투자 금액</h2>
          <div className="input-group">
            <input
              placeholder="예: 100000"
              value={invest}
              onChange={(e) => setInvest(e.target.value)}
            />
            <span>원</span>
          </div>

          <h2>🛑 손절 (%)</h2>
          <div className="input-group">
            <input
              placeholder="예: 3"
              value={lossCut}
              onChange={(e) => setLossCut(e.target.value)}
            />
            <span>%</span>
          </div>

          <h2>📈 익절 (%)</h2>
          <div className="input-group">
            <input
              placeholder="예: 5"
              value={takeProfit}
              onChange={(e) => setTakeProfit(e.target.value)}
            />
            <span>%</span>
          </div>

          <h2>🪙 코인 구매 수</h2>
          <div className="input-group">
            <input
              placeholder="예: 5"
              value={coinCount}
              onChange={(e) => setCoinCount(e.target.value)}
            />
            <span>개</span>
          </div>

          <button className="start-button" onClick={handleStart}>
            🚀 자동매매 시작
          </button>
        </div>
      ) : (
        <div className="status-box">
          {statusSteps.map((step, i) =>
            visibleSteps.includes(i) ? (
              <div className="status-item" key={i}>
                <strong>{step.title}</strong>
                <p className="status-content">{step.content}</p>
                {i === statusSteps.length - 1 && (
                  <button className="go-dashboard-btn" onClick={goToDashboard}>
                    📂 보유 자산 보러가기
                  </button>
                )}
              </div>
            ) : null
          )}
        </div>
      )}
    </div>
  );
}

export default AutoTrade;