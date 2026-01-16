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

    // Auto-timeout for "missed green"
    useEffect(() => {
        if (stimulus === "green") {
            const timeout = setTimeout(() => {
                if (!clicked) {
                    onAnswer({
                        correct: false,
                        responseTime: 3000,
                        mistakeType: "missed_target"
                    });
                }
            }, 3000);

            return () => clearTimeout(timeout);
        }
    }, [stimulus, clicked, onAnswer]);

    return (
        <div className="focus-guard-container">
            <h2 className="focus-guard-heading">Tap GREEN. Ignore RED.</h2>

            <button
                onClick={handleClick}
                className={`focus-target-button ${stimulus === "green" ? "green" : "red"} ${clicked ? "clicked" : ""}`}
            />
        </div>
    );
}
