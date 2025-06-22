// src/pages/AutoTrade.js
import React, { useState } from 'react';
import axios from 'axios';
import '../styles/AutoTrade.css';

function AutoTrade() {
  const [dailyInvest, setDailyInvest] = useState('');
  const [lossCut, setLossCut] = useState('');
  const [takeProfit, setTakeProfit] = useState('');

  const handleStart = async () => {
    if (!dailyInvest || !lossCut || !takeProfit) {
      alert('모든 값을 입력해주세요.');
      return;
    }

    try {
      const res = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/user-setting`, {
        max_daily_invest: parseInt(dailyInvest),
        loss_cut: parseFloat(-Math.abs(lossCut) / 100),  // 음수로 보냄
        take_profit: parseFloat(takeProfit / 100),
      });

      if (res.data?.success) {
        alert('자동매매 설정이 완료되었습니다.');
        // 여기서 자동매매 실행 or 상태 화면 이동 등 처리
      } else {
        alert(res.data?.message || '설정에 실패했습니다.');
      }
    } catch (err) {
      console.error(err);
      alert('서버 오류가 발생했습니다.');
    }
  };

  return (
    <div className="auto-container">
      <h1 className="auto-title">🤖 자동매매 설정</h1>
      <div className="auto-box">
        <div className="auto-form-group">
          <label>💸 일일 투자 금액</label>
          <input
            type="number"
            placeholder="예: 100000원"
            value={dailyInvest}
            onChange={(e) => setDailyInvest(e.target.value)}
          />
        </div>

        <div className="auto-form-group">
          <label>🛑 손절 (%)</label>
          <input
            type="number"
            placeholder="예: 3"
            value={lossCut}
            onChange={(e) => setLossCut(e.target.value)}
          />
        </div>

        <div className="auto-form-group">
          <label>📈 익절 (%)</label>
          <input
            type="number"
            placeholder="예: 5"
            value={takeProfit}
            onChange={(e) => setTakeProfit(e.target.value)}
          />
        </div>

        <button className="start-button" onClick={handleStart}>
          자동매매 시작
        </button>
      </div>
    </div>
  );
}

export default AutoTrade;
