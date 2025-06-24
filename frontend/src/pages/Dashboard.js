// src/pages/Dashboard.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Dashboard.css';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const COLORS = ['#FF8042', '#0088FE', '#00C49F', '#FFBB28', '#FF6384'];

function Dashboard() {
  const navigate = useNavigate();
  const [coinList, setCoinList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [allocation, setAllocation] = useState([]);
  const [returnRate, setReturnRate] = useState(0);
  const [returnKrw, setReturnKrw] = useState(0);
  const [totalValue, setTotalValue] = useState(0);

  const goToSearch = () => {
    navigate('/autotrade');
  };

  useEffect(() => {
    const fetchTrendingCoins = async () => {
      try {
        const response = await fetch('http://localhost:8000/trending');
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

    const fetchAllocation = async () => {
      try {
        const response = await fetch('http://localhost:8000/allocation');
        const result = await response.json();

        if (result.success) {
          setAllocation(result.data.allocation);
          setTotalValue(result.data.total_value);
        }
      } catch (err) {
        console.error('할당 정보 에러:', err);
      }
    };

    const fetchPerformance = async () => {
      try {
        const response = await fetch('http://localhost:8000/performance');
        const result = await response.json();

        if (result.success) {
          setReturnRate(result.data.return_rate);
          setReturnKrw(result.data.return_krw);
        }
      } catch (err) {
        console.error('수익률 정보 에러:', err);
      }
    };

    fetchTrendingCoins();
    fetchAllocation();
    fetchPerformance();
  }, []);

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">코인시그널 - 메인 대시보드</h1>

      <div className="dashboard-layout">
        <div className="dashboard-left">
          {/* 수익률 */}
          <section className="section">
            <h2 className="section-title">투자 현황</h2>
            <div className="profit-box">
              <p>기간 수익률</p>
              <p>최근 7일</p>
              <p className={returnRate >= 0 ? 'profit-rate plus' : 'profit-rate minus'}>
                {returnRate >= 0 ? '+' : ''}{(returnRate * 100).toFixed(2)}% ({returnKrw.toLocaleString()}원)
              </p>
            </div>
          </section>

          {/* 도넛 차트 */}
          <section className="section">
            <h2 className="section-title">투자 비중</h2>
            <div className="donut-chart-box">
              {allocation.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={allocation}
                        dataKey="percent"
                        nameKey="coin"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {allocation.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                  <p className="total-value-text">총 투자금: {totalValue.toLocaleString()}원</p>
                </>
              ) : (
                <p>도넛 차트 데이터를 불러오는 중...</p>
              )}
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