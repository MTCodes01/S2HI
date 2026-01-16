import { useEffect, useRef } from "react";

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
};

export default function VisualMathMatch({
    equation,
    correctValue,
    options,
    onAnswer
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
        <div className="flex flex-col gap-6 items-center">
            <h2 className="text-xl font-semibold">
                Match the equation to the blocks
            </h2>

            <div className="text-2xl">{equation}</div>

            <div className="flex gap-6">
                {options.map((value) => (
                    <button
                        key={value}
                        onClick={() => handleClick(value)}
                        className="p-4 border rounded-lg hover:bg-gray-100"
                    >
                        {"●".repeat(value)}
                    </button>
                ))}
            </div>
        </div>
    );
}
