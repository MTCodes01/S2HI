import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './styles/global.css';
import Assessment from './pages/Assessment';
import Dashboard from './pages/Dashboard';
import LandingAnimation from './pages/LandingAnimation';
import FullAssessment from './pages/FullAssessment';
import { useState } from 'react';

export default function App() {
  const [showLanding, setShowLanding] = useState(true);

  return (
    <BrowserRouter>
      {showLanding && <LandingAnimation onComplete={() => setShowLanding(false)} />}
      <Routes>
        <Route path="/" element={<Assessment />} />
        <Route path="/full-assessment" element={<FullAssessment />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}