import React, { useState, useEffect } from 'react';
import "../styles/LandingAnimation.css";
interface LandingAnimationProps {
  onComplete: () => void;
}

const LandingAnimation: React.FC<LandingAnimationProps> = ({ onComplete }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onComplete();
    }, 5500);

    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!isVisible) {
    return null;
  }

  return (
    <div className="landing-container">
      <div className="blue-screen">
        <div className="animation-wrapper">
          {/* Floating particles */}
          <div className="particle particle-1"></div>
          <div className="particle particle-2"></div>
          <div className="particle particle-3"></div>
          <div className="particle particle-4"></div>
          <div className="particle particle-5"></div>
          <div className="particle particle-6"></div>
          
          {/* Main content */}
          <div className="content-wrapper">
            <div className="logo-container">
              <h1 className="landing-text">S2HI</h1>
              <div className="subtitle">Unleash Your Special Powers</div>
            </div>
            
            {/* Custom mascot inline */}
            <div className="landing-mascot-wrapper">
              <svg viewBox="0 0 200 200" className="landing-mascot-svg">
                {/* Glow behind */}
                <circle cx="100" cy="100" r="90" className="landing-mascot-glow" />

                {/* Body */}
                <path d="M60 140 Q100 180 140 140 L140 100 Q100 110 60 100 Z" className="landing-mascot-body" fill="#3b82f6" />

                {/* Head */}
                <rect x="50" y="40" width="100" height="80" rx="30" className="landing-mascot-head" fill="#fff" stroke="#3b82f6" strokeWidth="4" />

                {/* Face Screen */}
                <rect x="60" y="50" width="80" height="60" rx="20" fill="#1e293b" className="landing-mascot-screen" />

                {/* Eyes - Excited */}
                <g className="landing-mascot-eyes">
                  <text x="75" y="80" fontSize="20" fill="#00d4aa">^</text>
                  <text x="105" y="80" fontSize="20" fill="#00d4aa">^</text>
                </g>

                {/* Antenna */}
                <line x1="100" y1="40" x2="100" y2="10" stroke="#3b82f6" strokeWidth="4" />
                <circle cx="100" cy="10" r="8" fill="#ff6b6b" className="landing-mascot-antenna-bulb" />

                {/* Arms */}
                <path d="M50 120 Q30 130 40 150" stroke="#3b82f6" strokeWidth="8" strokeLinecap="round" fill="none" className="landing-mascot-arm-left" />
                <path d="M150 120 Q170 110 160 90" stroke="#3b82f6" strokeWidth="8" strokeLinecap="round" fill="none" className="landing-mascot-arm-right" />
              </svg>
              <div className="landing-mascot-shadow"></div>
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingAnimation;