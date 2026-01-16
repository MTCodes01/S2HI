import { useEffect, useRef, useState } from "react";

type ReadingEchoResult = {
    accuracy: number;
    responseTime: number;
    mistakes: number;
};

type Props = {
    sentence: string;
    onAnswer: (result: ReadingEchoResult) => void;
};

export default function ReadAloudEcho({ sentence, onAnswer }: Props) {
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
        <div className="flex flex-col gap-4">
            <h2 className="text-lg font-semibold">Read & Type the Sentence</h2>
            <p className="text-xl bg-gray-100 p-4 rounded">{sentence}</p>

            <textarea
                className="border rounded p-3"
                rows={3}
                placeholder="Type what you read..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />

            <button
                onClick={handleSubmit}
                className="bg-blue-600 text-white p-3 rounded hover:bg-blue-700"
            >
                Submit
            </button>
        </div>
    );
}
