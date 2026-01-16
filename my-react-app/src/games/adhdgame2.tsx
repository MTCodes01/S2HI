import { useEffect, useRef, useState } from "react";

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
    onAnswer
}: Props) {
    const startTime = useRef<number>(Date.now());
    const [responded, setResponded] = useState(false);

    useEffect(() => {
        startTime.current = Date.now();
        setResponded(false);
    }, [currentItem]);

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
                        responseTime: 3000,
                        mistakeType: "missed_pattern_break"
                    });
                }
            }, 3000);

            return () => clearTimeout(timeout);
        }
    }, [isBreak, responded, onAnswer]);

    return (
        <div className="flex flex-col items-center gap-6">
            <h2 className="text-xl font-semibold">Tap when the pattern breaks</h2>

            <div className="text-5xl">{currentItem}</div>

            <button
                onClick={handleClick}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg"
            >
                Tap
            </button>
        </div>
    );
}
