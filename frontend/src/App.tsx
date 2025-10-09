import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Destinations from './pages/Destinations';
import Recommendations from './pages/Recommendations';
import ChatAI from './pages/ChatAI';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-base-200">
        <div className="navbar bg-primary text-primary-content">
          <div className="flex-1">
            <Link to="/" className="btn btn-ghost text-xl">✈️ Travel App</Link>
          </div>
          <div className="flex-none">
            <ul className="menu menu-horizontal px-1">
              <li><Link to="/" className="btn btn-ghost">Destinations</Link></li>
              <li><Link to="/reco" className="btn btn-ghost">Recommandations</Link></li>
              <li><Link to="/chat" className="btn btn-ghost">Chat IA</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="container mx-auto p-4">
          <Routes>
            <Route path="/" element={<Destinations />} />
            <Route path="/reco" element={<Recommendations />} />
            <Route path="/chat" element={<ChatAI />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}