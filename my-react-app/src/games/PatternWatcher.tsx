import { useEffect, useRef, useState } from "react";
import "../styles/PatternWatcher.css";

type PatternResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    expectedPattern: string[];
    currentItem: string;
    isBreak: boolean;
    onAnswer: (result: PatternResult) => void;
};

export default function PatternWatcher({
    expectedPattern,
    currentItem,
    isBreak,
    onAnswer,
    ageGroup = "9-11" // Default prop
}: Props & { ageGroup?: string }) {
    const startTime = useRef<number>(Date.now());
    const [responded, setResponded] = useState(false);

    // Track previous item for visual comparison
    const prevItemRef = useRef<string | null>(null);
    useEffect(() => {
        return () => { prevItemRef.current = currentItem; };
    }, [currentItem]);

    useEffect(() => {
        startTime.current = Date.now();
        setResponded(false);
    }, [currentItem]);

    // Adjust timeout based on age
    const getTimeoutDuration = () => {
        if (ageGroup === '6-8') return 5000; // Slower for younger
        if (ageGroup === '12-14') return 2000; // Faster for older
        return 3000; // Default
    };

    const handleClick = () => {
        if (responded) return;
        setResponded(true);

        const responseTime = Date.now() - startTime.current;

        onAnswer({
            correct: isBreak,
            responseTime,
            mistakeType: isBreak ? undefined : "false_alarm"
        });
    };

    // Missed break detection
    useEffect(() => {
        if (isBreak) {
            const timeout = setTimeout(() => {
                if (!responded) {
                    onAnswer({
                        correct: false,
                        responseTime: getTimeoutDuration(),
                        mistakeType: "missed_pattern_break"
                    });
                }
            }, getTimeoutDuration());

            return () => clearTimeout(timeout);
        }
    }, [isBreak, responded, onAnswer, ageGroup]);

    return (
        <div className="pattern-watcher-container">
            <h2 className="pattern-watcher-heading">Tap when the pattern changes!</h2>

            <div className="pattern-comparison">
                {/* Visual Hint: Show previous item faintly */}
                <div className="pattern-item previous">
                    <span className="label">Previous</span>
                    <div className="content">{prevItemRef.current || "?"}</div>
                </div>

                <div className="pattern-arrow">➡</div>

                <div className={`pattern-item current ${isBreak ? "highlight-break" : ""}`}>
                    <span className="label">Current</span>
                    <div className="content">{currentItem}</div>
                </div>
            </div>

            <button
                onClick={handleClick}
                className={`pattern-action-button ${responded ? 'clicked' : ''}`}
                disabled={responded}
            >
                {responded ? (isBreak ? "Good Catch!" : "Oops!") : "Different!"}
            </button>
        </div>
    );
}
