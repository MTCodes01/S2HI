import { useEffect, useRef, useState } from "react";
import "../styles/PatternWatcher.css";

type PatternResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    onAnswer: (result: PatternResult) => void;
};

export default function PatternWatcher({
    onAnswer,
    ageGroup = "9-11"
}: Props & { ageGroup?: string }) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [trials, setTrials] = useState<{ item: string; isBreak: boolean }[]>([]);
    const [responses, setResponses] = useState<{ correct: boolean; responseTime: number }[]>([]);
    const [respondedThisTrial, setRespondedThisTrial] = useState(false);
    const startTime = useRef<number>(Date.now());
    const isGameOver = useRef(false);

    // Timing based on age
    const duration = ageGroup === '6-8' ? 2500 : ageGroup === '12-14' ? 1200 : 1800;

    // Initialize sequence
    useEffect(() => {
        const pattern = ["A", "B"];
        const sequence: { item: string; isBreak: boolean }[] = [];
        const totalItems = 12;

        for (let i = 0; i < totalItems; i++) {
            const shouldBeBreak = i > 2 && Math.random() < 0.25;
            if (shouldBeBreak) {
                sequence.push({ item: "X", isBreak: true });
            } else {
                sequence.push({ item: pattern[i % 2], isBreak: false });
            }
        }
        setTrials(sequence);
        startTime.current = Date.now();
    }, []);

    // Automatic progression
    useEffect(() => {
        if (trials.length === 0 || isGameOver.current) return;

        const timer = setTimeout(() => {
            // Process missed break if not responded
            if (trials[currentIndex].isBreak && !respondedThisTrial) {
                setResponses(prev => [...prev, { correct: false, responseTime: duration }]);
            } else if (!trials[currentIndex].isBreak && !respondedThisTrial) {
                // Correctly ignored a non-break
                setResponses(prev => [...prev, { correct: true, responseTime: duration }]);
            }

            if (currentIndex < trials.length - 1) {
                setCurrentIndex(prev => prev + 1);
                setRespondedThisTrial(false);
                startTime.current = Date.now();
            } else {
                handleGameOver();
            }
        }, duration);

        return () => clearTimeout(timer);
    }, [currentIndex, trials, respondedThisTrial]);

    const handleGameOver = () => {
        if (isGameOver.current) return;
        isGameOver.current = true;

        const finalAccuracy = responses.filter(r => r.correct).length / (responses.length || 1);
        const avgTime = responses.reduce((acc, r) => acc + r.responseTime, 0) / (responses.length || 1);

        onAnswer({
            correct: finalAccuracy > 0.7,
            responseTime: Math.round(avgTime),
            mistakeType: finalAccuracy < 0.7 ? "sequence_error" : undefined
        });
    };

    const handleClick = () => {
        if (respondedThisTrial || isGameOver.current) return;
        setRespondedThisTrial(true);

        const responseTime = Date.now() - startTime.current;
        const correct = trials[currentIndex].isBreak;

        setResponses(prev => [...prev, { correct, responseTime }]);
    };

    if (trials.length === 0) return <div className="pattern-watcher-container">Loading...</div>;

    const currentTrial = trials[currentIndex];
    const prevTrial = currentIndex > 0 ? trials[currentIndex - 1] : null;

    return (
        <div className="pattern-watcher-container">
            <h2 className="pattern-watcher-heading">Tap when the pattern changes!</h2>
            <div className="game-progress">Item {currentIndex + 1} of {trials.length}</div>

            <div className="pattern-display-area">
                <div className="pattern-cards">
                    <div className="pattern-card previous">
                        <span className="card-label">PREVIOUS</span>
                        <div className="card-content">{prevTrial ? prevTrial.item : "?"}</div>
                    </div>

                    <div className="pattern-connector">➡</div>

                    <div className={`pattern-card current ${respondedThisTrial ? 'responded' : ''}`}>
                        <span className="card-label">CURRENT</span>
                        <div className="card-content">{currentTrial.item}</div>
                    </div>
                </div>
            </div>

            <div className="pattern-controls">
                <button
                    onClick={handleClick}
                    className={`pattern-btn-large ${respondedThisTrial ? 'disabled' : ''}`}
                    disabled={respondedThisTrial}
                >
                    DIFFERENT!
                </button>
            </div>

            <div className="game-hint">
                <p>Pattern is usually A ➡ B ➡ A ➡ B...</p>
                <p>Tap <strong>DIFFERENT!</strong> if you see something else (like X)!</p>
            </div>
        </div>
    );
}
