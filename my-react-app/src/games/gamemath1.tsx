import { useEffect, useRef, useState } from "react";

type MathResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    left: number;
    right: number;
    onAnswer: (result: MathResult) => void;
};

export default function NumberSenseDash({ left, right, onAnswer }: Props) {
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
        <div className="flex flex-col items-center gap-6">
            <h2 className="text-xl font-semibold">Which number is larger?</h2>

            <div className="flex gap-8">
                {[left, right].map((num) => (
                    <button
                        key={num}
                        onClick={() => handleClick(num)}
                        className="text-3xl p-8 border rounded-xl hover:bg-gray-100"
                    >
                        {num}
                    </button>
                ))}
            </div>
        </div>
    );
}
