// import { useState } from 'react';
import '../styles/ConfidenceSlider.css';

type Props = {
    value: number;
    onChange: (val: number) => void;
};

export default function ConfidenceSlider({ value, onChange }: Props) {
    const getEmoji = (val: number) => {
        if (val < 30) return '😕';
        if (val < 70) return '😐';
        return '🤩';
    };

    const getLabel = (val: number) => {
        if (val < 30) return 'It was hard!';
        if (val < 70) return 'I did okay';
        return 'I crushed it!';
    };

    return (
        <div className="confidence-container">
            <div className="emoji-display">
                {getEmoji(value)}
            </div>

            <p className="confidence-label">{getLabel(value)}</p>

            <input
                type="range"
                min="0"
                max="100"
                value={value}
                onChange={(e) => onChange(Number(e.target.value))}
                className="slider"
            />
        </div>
    );
}
