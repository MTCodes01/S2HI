import React from 'react';
import '../styles/mascot.css';

interface MascotProps {
    expression?: 'happy' | 'thinking' | 'excited' | 'waiting';
    size?: 'small' | 'medium' | 'large';
}

const Mascot: React.FC<MascotProps> = ({ expression = 'happy', size = 'medium' }) => {
    return (
        <div className={`mascot-container ${size} ${expression}`}>
            <svg viewBox="0 0 200 200" className="mascot-svg">
                {/* Glow behind */}
                <circle cx="100" cy="100" r="90" className="mascot-glow" />

                {/* Body */}
                <path d="M60 140 Q100 180 140 140 L140 100 Q100 110 60 100 Z" className="mascot-body" fill="#3b82f6" />

                {/* Head */}
                <rect x="50" y="40" width="100" height="80" rx="30" className="mascot-head" fill="#fff" stroke="#3b82f6" strokeWidth="4" />

                {/* Face Screen */}
                <rect x="60" y="50" width="80" height="60" rx="20" fill="#1e293b" className="mascot-screen" />

                {/* Eyes */}
                <g className="mascot-eyes">
                    {expression === 'happy' && (
                        <>
                            <path d="M75 75 Q85 65 95 75" stroke="#00d4aa" strokeWidth="4" fill="none" strokeLinecap="round" />
                            <path d="M105 75 Q115 65 125 75" stroke="#00d4aa" strokeWidth="4" fill="none" strokeLinecap="round" />
                        </>
                    )}
                    {expression === 'waiting' && (
                        <>
                            <circle cx="85" cy="75" r="5" fill="#00d4aa" className="eye-blink" />
                            <circle cx="115" cy="75" r="5" fill="#00d4aa" className="eye-blink" />
                        </>
                    )}
                    {expression === 'excited' && (
                        <>
                            <text x="75" y="80" fontSize="20" fill="#00d4aa">^</text>
                            <text x="105" y="80" fontSize="20" fill="#00d4aa">^</text>
                        </>
                    )}
                </g>

                {/* Antenna */}
                <line x1="100" y1="40" x2="100" y2="10" stroke="#3b82f6" strokeWidth="4" />
                <circle cx="100" cy="10" r="8" fill="#ff6b6b" className="mascot-antenna-bulb" />

                {/* Arms */}
                <path d="M50 120 Q30 130 40 150" stroke="#3b82f6" strokeWidth="8" strokeLinecap="round" fill="none" className="mascot-arm-left" />
                <path d="M150 120 Q170 110 160 90" stroke="#3b82f6" strokeWidth="8" strokeLinecap="round" fill="none" className="mascot-arm-right" />
            </svg>
            <div className="mascot-shadow"></div>
        </div>
    );
};

export default Mascot;
