import { useState } from 'react';
import '../styles/ConfidenceSlider.css';

type Props = {
    onConfirm: (confidence: number) => void;
};

export default function ConfidenceSlider({ onConfirm }: Props) {
    const [value, setValue] = useState(50);

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
            <h3>How do you feel you did?</h3>

            <div className="emoji-display">
                {getEmoji(value)}
            </div>

            <p className="confidence-label">{getLabel(value)}</p>

            <input
                type="range"
                min="0"
                max="100"
                value={value}
                onChange={(e) => setValue(Number(e.target.value))}
                className="slider"
            />

            <button
                className="confirm-btn"
                onClick={() => onConfirm(value)}
            >
                Confirm
            </button>
        </div>
    );
}
