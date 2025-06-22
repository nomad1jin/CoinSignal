// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Home from './pages/Home';
import AutoTrade from './pages/AutoTrade'; // 추가

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/search" element={<Home />} />
        <Route path="/autotrade" element={<AutoTrade />} /> {/* 새 라우트 */}
      </Routes>
    </Router>
  );
}

export default App;
