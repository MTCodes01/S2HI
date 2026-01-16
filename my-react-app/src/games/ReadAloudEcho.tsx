import { useEffect, useRef, useState } from "react";
import "../styles/ReadAloudEcho.css";

type ReadingEchoResult = {
    accuracy: number;
    responseTime: number;
    mistakes: number;
};

type Props = {
    sentence: string;
    onAnswer: (result: ReadingEchoResult) => void;
    ageGroup?: string;
};

export default function ReadAloudEcho({ sentence, onAnswer, ageGroup = "9-11" }: Props) {
    const [input, setInput] = useState("");
    const startTime = useRef<number>(Date.now());

    useEffect(() => {
        startTime.current = Date.now();
        setInput("");
    }, [sentence]);

    const calculateAccuracy = () => {
        const target = sentence.trim().toLowerCase();
        const typed = input.trim().toLowerCase();

        let correctChars = 0;
        for (let i = 0; i < Math.min(target.length, typed.length); i++) {
            if (target[i] === typed[i]) correctChars++;
        }

        return correctChars / target.length;
    };

    const handleSubmit = () => {
        const responseTime = Date.now() - startTime.current;
        const accuracy = calculateAccuracy();
        const mistakes = sentence.length - Math.round(accuracy * sentence.length);

        onAnswer({
            accuracy,
            responseTime,
            mistakes
        });
    };

    return (
        <div className="read-echo-container">
            <h2 className="read-echo-heading">Read & Type the Sentence</h2>
            <p className="read-echo-sentence">{sentence}</p>

            <textarea
                className="read-echo-input"
                rows={3}
                placeholder="Type what you read..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />

            <button
                onClick={handleSubmit}
                className="read-echo-submit"
            >
                Submit
            </button>
        </div>
    );
}
