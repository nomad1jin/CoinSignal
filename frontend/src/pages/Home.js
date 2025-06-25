// src/pages/Home.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // ✅ navigate 추가
import '../styles/Home.css';

function Home() {
  const [coin, setCoin] = useState('');
  const navigate = useNavigate(); // ✅ 페이지 이동을 위한 훅

  const handleSubmit = (e) => {
    e.preventDefault();
    if (coin.trim()) {
      console.log(`입력한 코인: ${coin}`);
      // ✅ 자동매매 페이지로 이동하면서 쿼리 전달
      navigate(`/autotrade?coin=${encodeURIComponent(coin)}`);
    } else {
      alert('코인 이름을 입력해주세요.');
    }
  };

  return (
    <div className="home-wrapper">
      <div className="home-card">
        <h1 className="home-title">🔍 구매를 원하는 코인을 검색하세요</h1>

        <form className="home-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={coin}
            onChange={(e) => setCoin(e.target.value)}
            placeholder="예: Bitcoin, Ethereum..."
            className="home-input"
          />
          <button type="submit" className="home-button">검색</button>
        </form>
      </div>
    </div>
  );
}

export default Home;