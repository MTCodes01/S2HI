import { useEffect, useRef } from "react";
import "../styles/VisualMathMatch.css";

type VisualMathResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    equation: string;        // e.g. "3 + 2"
    correctValue: number;    // e.g. 5
    options: number[];       // e.g. [4,5,6]
    onAnswer: (result: VisualMathResult) => void;
    ageGroup?: string;
};

export default function VisualMathMatch({
    equation,
    correctValue,
    options,
    onAnswer,
    ageGroup = "9-11"
}: Props) {
    const startTime = useRef<number>(Date.now());

    useEffect(() => {
        startTime.current = Date.now();
    }, [equation]);

    const handleClick = (choice: number) => {
        const responseTime = Date.now() - startTime.current;
        const correct = choice === correctValue;

        onAnswer({
            correct,
            responseTime,
            mistakeType: correct ? undefined : "visual_quantity_mismatch"
        });
    };

    return (
        <div className="visual-math-container">
            <h2 className="visual-math-heading">
                Match the equation to the blocks
            </h2>

            <div className="visual-math-equation">{equation}</div>

            <div className="visual-math-options">
                {options.map((value) => (
                    <button
                        key={value}
                        onClick={() => handleClick(value)}
                        className="visual-math-option"
                    >
                        <div className="visual-math-block">{"●".repeat(value)}</div>
                    </button>
                ))}
            </div>
        </div>
    );
}
