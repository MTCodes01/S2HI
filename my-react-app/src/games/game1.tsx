import { useEffect, useRef, useState } from "react";

type ReadingResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
};

type Props = {
    question: string;
    options: string[];
    onAnswer: (result: ReadingResult) => void;
};

export default function ReadingGame({ question, options, onAnswer }: Props) {
    const startTime = useRef<number>(Date.now());

    const handleClick = (option: string) => {
        const responseTime = Date.now() - startTime.current;

        // TEMP correctness check (backend will verify later)
        const correct = option === options[0];

        let mistakeType;
        if (!correct) mistakeType = "letter_confusion";

        onAnswer({
            correct,
            responseTime,
            mistakeType
        });
    };

    useEffect(() => {
        startTime.current = Date.now();
    }, [question]);

    return (
        <div className="flex flex-col gap-4">
            <h2 className="text-xl">{question}</h2>
            <div className="grid grid-cols-2 gap-4">
                {options.map(opt => (
                    <button
                        key={opt}
                        onClick={() => handleClick(opt)}
                        className="p-4 border rounded-lg hover:bg-gray-100"
                    >
                        {opt}
                    </button>
                ))}
            </div>
        </div>
    );
}
