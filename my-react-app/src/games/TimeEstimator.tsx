import { useState, useRef } from 'react';
import '../styles/TimeEstimator.css';

type TimeResult = {
    accuracy: number; // 0 to 1 (1 is perfect)
    estimatedTime: number;
    targetTime: number;
    deviation: number;
};

type Props = {
    targetSeconds: number;
    onAnswer: (result: TimeResult) => void;
};

export default function TimeEstimator({ targetSeconds, onAnswer }: Props) {
    const [isHolding, setIsHolding] = useState(false);
    const [feedback, setFeedback] = useState<string | null>(null);
    const startTime = useRef<number>(0);
    const timerRef = useRef<NodeJS.Timeout | null>(null);

    const handleMouseDown = () => {
        if (feedback) return; // Prevent interaction during feedback
        setIsHolding(true);
        startTime.current = Date.now();

        // Add visual pulse animation via class
    };

    const handleMouseUp = () => {
        if (!isHolding) return;
        setIsHolding(false);

        const endTime = Date.now();
        const durationMs = endTime - startTime.current;
        const durationSec = durationMs / 1000;
        const targetMs = targetSeconds * 1000;

        const deviation = Math.abs(durationMs - targetMs);
        const percentError = deviation / targetMs;
        const accuracy = Math.max(0, 1 - percentError); // 1 = perfect, 0 = way off

        setFeedback(`${durationSec.toFixed(2)}s`);

        setTimeout(() => {
            onAnswer({
                accuracy,
                estimatedTime: durationMs,
                targetTime: targetMs,
                deviation
            });
        }, 1500);
    };

    return (
        <div className="time-estimator-container">
            <h2 className="time-heading">Time Wizard</h2>
            <p className="time-instruction">
                Press and hold the button for exactly <strong>{targetSeconds} seconds</strong>.
            </p>

            <div className={`timer-circle ${isHolding ? 'pulsing' : ''}`}>
                <button
                    className="hold-button"
                    onMouseDown={handleMouseDown}
                    onMouseUp={handleMouseUp}
                    onTouchStart={handleMouseDown}
                    onTouchEnd={handleMouseUp}
                    disabled={!!feedback}
                >
                    {feedback ? feedback : (isHolding ? "Hold..." : "Press & Hold")}
                </button>
            </div>

            <div className="visual-cue">
                {/* Optional visual cue line or just whitespace */}
            </div>
        </div>
    );
}
