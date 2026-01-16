import { useEffect, useRef, useState, useCallback } from "react";
import "../styles/PatternWatcher.css";

type PatternResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    expectedPattern?: string[]; // Kept for interface compatibility
    currentItem?: string;       // Kept for interface compatibility
    isBreak?: boolean;          // Kept for compatibility
    onAnswer: (result: PatternResult) => void;
    ageGroup?: string;
};



export default function PatternWatcher({
    onAnswer,
    ageGroup = "9-11"
}: Props) {
    const [currentShape, setCurrentShape] = useState<string>("●");
    const [isGameActive, setIsGameActive] = useState(false);
    const [message, setMessage] = useState("Watch the pattern...");

    // Game state
    const sequenceRef = useRef<string[]>([]);
    const currentIndexRef = useRef(0);
    const breakIndexRef = useRef(0);
    const timeoutRef = useRef<number | null>(null);
    const startTimeRef = useRef<number>(0);
    const hasRespondedRef = useRef(false);

    // Setup difficulty variables based on age
    const speed = ageGroup === '6-8' ? 2000 : (ageGroup === '12-14' ? 1000 : 1500);

    // Generate a sequence
    const startPatternGame = useCallback(() => {
        // Define simple patterns
        const patterns = [
            ["●", "■", "●", "■", "●"], // ABAB...
            ["▲", "▲", "▼", "▼", "▲"], // AABB...
            ["★", "☆", "★", "☆", "★"]
        ];

        const basePattern = patterns[Math.floor(Math.random() * patterns.length)];

        // Determine where the break happens (between index 2 and 4 typically)
        const breakIdx = Math.floor(Math.random() * 2) + 2; // Index 2 or 3

        const sequence = [...basePattern];
        // Insert break
        sequence[breakIdx] = sequence[breakIdx] === "●" ? "■" : "●"; // Simplify break item for now

        // Actually, let's just make a cleaner break logic
        // If pattern is ABAB (0,1,0,1), at index 2 (0) we want a break.
        // It's easier to just generate a flat stream.

        const stream = [];
        const symbolA = ["●", "▲", "★"][Math.floor(Math.random() * 3)];
        const symbolB = ["■", "▼", "☆"][Math.floor(Math.random() * 3)];

        // Create standard ABAB pattern
        for (let i = 0; i < 6; i++) {
            stream.push(i % 2 === 0 ? symbolA : symbolB);
        }

        // Insert Break
        const breakPos = 3 + Math.floor(Math.random() * 2); // 3 or 4
        stream[breakPos] = stream[breakPos - 1]; // Repetition break (A,B,A,A...)

        sequenceRef.current = stream;
        breakIndexRef.current = breakPos;
        currentIndexRef.current = 0;
        hasRespondedRef.current = false;

        setIsGameActive(true);
        nextStep();
    }, []);

    const finishGame = (correct: boolean, avgTime: number, mistake?: string) => {
        setIsGameActive(false);
        if (timeoutRef.current) clearTimeout(timeoutRef.current);

        setMessage(correct ? "Excellent Job!" : "Not quite...");

        // Delay before submitting to let user see result
        setTimeout(() => {
            onAnswer({
                correct,
                responseTime: avgTime,
                mistakeType: mistake
            });
        }, 1000);
    };

    const nextStep = () => {
        if (currentIndexRef.current >= sequenceRef.current.length) {
            // End of sequence without user noticing break (if any) or just finished
            // If we passed the break index without response, it's a miss
            if (!hasRespondedRef.current && currentIndexRef.current > breakIndexRef.current) {
                finishGame(false, 2000, "missed_pattern_break");
            } else {
                // Just finished standard sequence
                finishGame(true, 1500);
            }
            return;
        }

        const item = sequenceRef.current[currentIndexRef.current];
        setCurrentShape(item);

        // Check if we just missed the break
        if (!hasRespondedRef.current && currentIndexRef.current > breakIndexRef.current) {
            finishGame(false, speed, "missed_pattern_break");
            return;
        }

        startTimeRef.current = Date.now();
        currentIndexRef.current += 1;

        timeoutRef.current = window.setTimeout(nextStep, speed);
    };

    const handleReaction = () => {
        if (!isGameActive || hasRespondedRef.current) return;

        hasRespondedRef.current = true;
        const responseTime = Date.now() - startTimeRef.current;

        // Correct if we are AT the break index
        // breakIndexRef is where the item CHANGED from expectation
        // Current item displayed is at currentIndexRef - 1
        const displayedIndex = currentIndexRef.current - 1;

        if (displayedIndex === breakIndexRef.current) {
            finishGame(true, responseTime);
        } else {
            finishGame(false, responseTime, "false_alarm");
        }
    };

    useEffect(() => {
        startPatternGame();
        return () => {
            if (timeoutRef.current) clearTimeout(timeoutRef.current);
        };
    }, [startPatternGame]);

    return (
        <div className="pattern-watcher-container">
            <h2 className="pattern-watcher-heading">Spot the Odd One!</h2>
            <p className="pattern-instruction">Tap the button when the pattern breaks!</p>

            <div className="pattern-display-area">
                <div className={`pattern-item current animate-pop`}>
                    {currentShape}
                </div>
            </div>

            <div className="pattern-controls">
                <button
                    onClick={handleReaction}
                    className="pattern-action-button"
                    disabled={!isGameActive}
                >
                    Different!
                </button>
            </div>

            <div className="status-message">{!isGameActive && message}</div>
        </div>
    );
}
