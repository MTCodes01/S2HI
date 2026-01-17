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
    correctAnswer?: string; // The specific word to fill in the blank
    ageGroup?: string;
};

export default function ReadAloudEcho({ sentence, onAnswer, correctAnswer }: Props) {
    const [input, setInput] = useState("");
    const startTime = useRef<number>(Date.now());

    useEffect(() => {
        startTime.current = Date.now();
        setInput("");
    }, [sentence]);

    const isFillInBlank = sentence.includes("___");

    const calculateAccuracy = () => {
        const typed = input.trim().toLowerCase();
        if (!typed) return 0;

        // If it's a fill-in-the-blank question
        if (isFillInBlank && correctAnswer) {
            const targetWord = correctAnswer.trim().toLowerCase();
            const fullSentence = sentence.replace("___", targetWord).trim().toLowerCase();

            // 1. User typed just the correct word
            if (typed === targetWord) return 1.0;

            // 2. User typed the whole reconstructed sentence
            if (typed === fullSentence) return 1.0;

            // 3. Check if the typed word is contained in the full sentence (partial match)
            if (fullSentence.includes(typed) && typed.length > 2) {
                // Return a high accuracy if they typed most of it correctly
                return 0.8;
            }
        }

        // Standard strict character matching fallback
        const target = sentence.trim().toLowerCase();
        let correctChars = 0;
        for (let i = 0; i < Math.min(target.length, typed.length); i++) {
            if (target[i] === typed[i]) correctChars++;
        }

        return correctChars / target.length;
    };

    const handleSubmit = () => {
        const responseTime = Date.now() - startTime.current;
        const accuracy = calculateAccuracy();
        const mistakes = accuracy === 1.0 ? 0 : (accuracy < 0.5 ? 2 : 1);

        onAnswer({
            accuracy,
            responseTime,
            mistakes
        });
    };

    return (
        <div className="read-echo-container">
            <h2 className="read-echo-heading">
                {isFillInBlank ? "Complete the Sentence" : "Read & Type the Sentence"}
            </h2>
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
