import { useState, useEffect, useRef } from 'react';
import '../styles/WordChainBuilder.css';

type WordChainResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
    moves: number;
};

type Props = {
    targetWord: string;
    scrambledLetters: string[];
    onAnswer: (result: WordChainResult) => void;
    ageGroup?: string;
};

export default function WordChainBuilder({ targetWord, scrambledLetters, onAnswer, ageGroup = "9-11" }: Props) {
    const [currentChain, setCurrentChain] = useState<string[]>([]);
    const [availableLetters, setAvailableLetters] = useState<string[]>(scrambledLetters);
    const [moves, setMoves] = useState(0);
    const startTime = useRef<number>(Date.now());

    useEffect(() => {
        setAvailableLetters(scrambledLetters);
        setCurrentChain([]);
        setMoves(0);
        startTime.current = Date.now();
    }, [scrambledLetters]);

    const handleLetterSelect = (letter: string, index: number) => {
        const newChain = [...currentChain, letter];
        const newAvailable = [...availableLetters];
        newAvailable.splice(index, 1);

        setCurrentChain(newChain);
        setAvailableLetters(newAvailable);
        setMoves(prev => prev + 1);

        // Auto-check if word is complete based on target length
        if (newChain.length === targetWord.length) {
            checkResult(newChain.join(''));
        }
    };

    const handleUndo = () => {
        if (currentChain.length === 0) return;

        const lastLetter = currentChain[currentChain.length - 1];
        const newChain = currentChain.slice(0, -1);
        const newAvailable = [...availableLetters, lastLetter];

        setCurrentChain(newChain);
        setAvailableLetters(newAvailable);
        setMoves(prev => prev + 1);
    };

    const checkResult = (formedWord: string) => {
        const responseTime = Date.now() - startTime.current;
        const correct = formedWord.toLowerCase() === targetWord.toLowerCase();

        // Slight delay to show the full word before submitting
        setTimeout(() => {
            onAnswer({
                correct,
                responseTime,
                moves,
                mistakeType: correct ? undefined : "sequencing_error"
            });
        }, 500);
    };

    return (
        <div className="word-chain-container">
            <h2 className="word-chain-heading">Unscramble the Word</h2>

            <div className="chain-display-area">
                {currentChain.map((letter, i) => (
                    <div key={i} className="chain-slot filled">
                        {letter}
                    </div>
                ))}
                {/* Empty slots placeholders */}
                {Array.from({ length: targetWord.length - currentChain.length }).map((_, i) => (
                    <div key={`empty-${i}`} className="chain-slot empty" />
                ))}
            </div>

            <div className="letter-bank">
                {availableLetters.map((letter, i) => (
                    <button
                        key={`${letter}-${i}`}
                        className="letter-tile"
                        onClick={() => handleLetterSelect(letter, i)}
                    >
                        {letter}
                    </button>
                ))}
            </div>

            <div className="controls">
                <button
                    className="undo-btn"
                    onClick={handleUndo}
                    disabled={currentChain.length === 0}
                >
                    ⎌ Undo
                </button>
            </div>
        </div>
    );
}
