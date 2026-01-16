import { useEffect, useRef } from "react";
import "../styles/LetterFlipFrenzy.css";

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
        <div className="reading-game-container">
            <h2 className="reading-question">{question}</h2>
            <div className="reading-options-grid">
                {options.map(opt => (
                    <button
                        key={opt}
                        onClick={() => handleClick(opt)}
                        className="reading-option-button"
                    >
                        {opt}
                    </button>
                ))}
            </div>
        </div>
    );
}
