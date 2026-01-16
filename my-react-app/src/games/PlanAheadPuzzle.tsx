import { useState } from 'react';
import '../styles/PlanAheadPuzzle.css';

type PuzzleResult = {
    correct: boolean;
    moves: number;
    optimalMoves: number;
    responseTime: number;
};

type Props = {
    level: 1 | 2 | 3; // Difficulty
    onAnswer: (result: PuzzleResult) => void;
};

export default function PlanAheadPuzzle({ level, onAnswer }: Props) {
    // Simplified: Use a 3-cup logic puzzle (move ball from A to C)
    // For demo purposes, this is a simplified grid path puzzle
    // "Get the ball to the star in minimum moves"

    // 0 = empty, 1 = ball, 2 = obstacle, 3 = goal
    const [grid, setGrid] = useState<number[]>([
        1, 0, 0,
        0, 2, 0,
        0, 0, 3
    ]);
    const [ballPos, setBallPos] = useState(0);
    const [moves, setMoves] = useState(0);
    const [startTime] = useState(Date.now());

    const width = 3;

    const moveBall = (direction: 'UP' | 'DOWN' | 'LEFT' | 'RIGHT') => {
        let newPos = ballPos;

        if (direction === 'UP' && ballPos >= width) newPos -= width;
        if (direction === 'DOWN' && ballPos < 6) newPos += width;
        if (direction === 'LEFT' && ballPos % width !== 0) newPos -= 1;
        if (direction === 'RIGHT' && ballPos % width !== 2) newPos += 1;

        if (newPos !== ballPos && grid[newPos] !== 2) {
            // Valid move
            const newGrid = [...grid];
            newGrid[ballPos] = 0;
            newGrid[newPos] = 1;

            setBallPos(newPos);
            setGrid(newGrid);
            setMoves(prev => prev + 1);

            // Check win
            if (newPos === 8) { // Goal position
                const responseTime = Date.now() - startTime;
                setTimeout(() => {
                    onAnswer({
                        correct: true,
                        moves: moves + 1,
                        optimalMoves: 4,
                        responseTime
                    });
                }, 500);
            }
        }
    };

    return (
        <div className="puzzle-container">
            <h2 className="puzzle-heading">Reach the Star</h2>
            <p className="puzzle-stats">Moves: {moves} (Target: 4)</p>

            <div className="puzzle-grid">
                {grid.map((cell, index) => (
                    <div
                        key={index}
                        className={`grid-cell ${cell === 1 ? 'ball' :
                                cell === 2 ? 'wall' :
                                    cell === 3 ? 'goal' : ''
                            }`}
                    >
                        {cell === 1 && '⚽'}
                        {cell === 2 && '🧱'}
                        {cell === 3 && '⭐'}
                    </div>
                ))}
            </div>

            <div className="puzzle-controls">
                <div className="d-pad">
                    <button className="d-btn up" onClick={() => moveBall('UP')}>▲</button>
                    <div className="d-row">
                        <button className="d-btn left" onClick={() => moveBall('LEFT')}>◀</button>
                        <button className="d-btn right" onClick={() => moveBall('RIGHT')}>▶</button>
                    </div>
                    <button className="d-btn down" onClick={() => moveBall('DOWN')}>▼</button>
                </div>
            </div>
        </div>
    );
}
