import { useEffect, useRef, useState } from "react";
import "../styles/FocusGuard.css";

type AttentionResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    stimulus: "green" | "red";
    onAnswer: (result: AttentionResult) => void;
};

export default function FocusGuard({ stimulus, onAnswer }: Props) {
    const startTime = useRef<number>(Date.now());
    const [clicked, setClicked] = useState(false);

    useEffect(() => {
        startTime.current = Date.now();
        setClicked(false);
    }, [stimulus]);

    const handleClick = () => {
        if (clicked) return;
        setClicked(true);

        const responseTime = Date.now() - startTime.current;

        const correct =
            (stimulus === "green") ||
            (stimulus === "red" && false);

        onAnswer({
            correct,
            responseTime,
            mistakeType: correct ? undefined : "impulsive_click"
        });
    };

    // Auto-timeout logic
    useEffect(() => {
        const timeoutDuration = 2000; // 2 seconds to decide

        const timeout = setTimeout(() => {
            if (!clicked) {
                // If time runs out and they DIDN'T click:
                if (stimulus === "red") {
                    // Correct! They ignored the red.
                    onAnswer({
                        correct: true,
                        responseTime: timeoutDuration,
                        mistakeType: undefined
                    });
                } else {
                    // Incorrect. They missed the green.
                    onAnswer({
                        correct: false,
                        responseTime: timeoutDuration,
                        mistakeType: "missed_target"
                    });
                }
            }
        }, timeoutDuration);

        return () => clearTimeout(timeout);
    }, [stimulus, clicked, onAnswer]);

    return (
        <div className="focus-guard-container">
            <h2 className="focus-guard-heading">
                {stimulus === "green" ? "Tap GREEN!" : "Don't Tap!"}
            </h2>

            <button
                onClick={handleClick}
                className={`focus-target-button ${stimulus === "green" ? "green" : "red"} ${clicked ? "clicked" : ""}`}
            />
        </div>
    );
}
