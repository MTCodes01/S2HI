import { useEffect, useRef } from "react";
import "../styles/NumberSenseDash.css";

type MathResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    left: number;
    right: number;
    onAnswer: (result: MathResult) => void;
    ageGroup?: string;
};

export default function NumberSenseDash({ left, right, onAnswer, ageGroup = "9-11" }: Props) {
    const startTime = useRef<number>(Date.now());

    useEffect(() => {
        startTime.current = Date.now();
    }, [left, right]);

    const handleClick = (choice: number) => {
        const responseTime = Date.now() - startTime.current;
        const correct = choice === Math.max(left, right);

        onAnswer({
            correct,
            responseTime,
            mistakeType: correct ? undefined : "magnitude_error"
        });
    };

    return (
        <div className="number-sense-container">
            <h2 className="number-sense-heading">Which number is larger?</h2>

            <div className="number-sense-options">
                {[left, right].map((num) => (
                    <button
                        key={num}
                        onClick={() => handleClick(num)}
                        className="number-sense-button"
                    >
                        {num}
                    </button>
                ))}
            </div>
        </div>
    );
}
