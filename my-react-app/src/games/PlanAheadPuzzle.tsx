import { useState, useEffect, useCallback } from 'react';
import '../styles/PlanAheadPuzzle.css';

type PuzzleResult = {
    correct: boolean;
    moves: number;
    optimalMoves: number;
    responseTime: number;
};

type Props = {
    level: 1 | 2 | 3;
    onAnswer: (result: PuzzleResult) => void;
    ageGroup?: string;
};

export default function PlanAheadPuzzle({ level, onAnswer }: Props) {
    const [grid, setGrid] = useState<number[]>([]);
    const [ballPos, setBallPos] = useState(-1);
    const [goalPos, setGoalPos] = useState(-1);
    const [width, setWidth] = useState(4);
    const [moves, setMoves] = useState(0);
    const [targetMoves, setTargetMoves] = useState(0);
    const [startTime, setStartTime] = useState(Date.now());
    const [isGenerating, setIsGenerating] = useState(true);

    const findShortestPath = (start: number, goal: number, currentGrid: number[], gWidth: number) => {
        const queue: [number, number][] = [[start, 0]];
        const visited = new Set([start]);
        const size = currentGrid.length;

        while (queue.length > 0) {
            const [curr, dist] = queue.shift()!;
            if (curr === goal) return dist;

            const neighbors = [];
            if (curr >= gWidth) neighbors.push(curr - gWidth); // UP
            if (curr < size - gWidth) neighbors.push(curr + gWidth); // DOWN
            if (curr % gWidth !== 0) neighbors.push(curr - 1); // LEFT
            if (curr % gWidth !== gWidth - 1) neighbors.push(curr + 1); // RIGHT

            for (const next of neighbors) {
                if (!visited.has(next) && currentGrid[next] !== 2) {
                    visited.add(next);
                    queue.push([next, dist + 1]);
                }
            }
        }
        return -1;
    };

    const generateLevelData = useCallback(() => {
        const gWidth = level === 1 ? 4 : level === 2 ? 5 : 6;
        const size = gWidth * gWidth;
        let newGrid: number[] = [];
        let start = -1;
        let goal = -1;
        let pathDist = -1;
        let attempts = 0;

        while (pathDist === -1 || pathDist < level * 3) {
            attempts++;
            if (attempts > 50) break; // Safety

            newGrid = new Array(size).fill(0);

            // Random start and goal (usually opposite sides)
            start = Math.floor(Math.random() * gWidth); // Top row
            goal = size - 1 - Math.floor(Math.random() * gWidth); // Bottom row

            newGrid[start] = 1;
            newGrid[goal] = 3;

            // Add obstacles (25% coverage)
            for (let i = 0; i < size; i++) {
                if (i !== start && i !== goal && Math.random() < 0.25) {
                    newGrid[i] = 2;
                }
            }

            pathDist = findShortestPath(start, goal, newGrid, gWidth);
        }

        setWidth(gWidth);
        setGrid(newGrid);
        setBallPos(start);
        setGoalPos(goal);
        setTargetMoves(pathDist);
        setMoves(0);
        setStartTime(Date.now());
        setIsGenerating(false);
    }, [level]);

    useEffect(() => {
        setIsGenerating(true);
        generateLevelData();
    }, [generateLevelData]);

    const moveBall = (direction: 'UP' | 'DOWN' | 'LEFT' | 'RIGHT') => {
        if (isGenerating) return;

        let newPos = ballPos;
        if (direction === 'UP' && ballPos >= width) newPos -= width;
        if (direction === 'DOWN' && ballPos < grid.length - width) newPos += width;
        if (direction === 'LEFT' && ballPos % width !== 0) newPos -= 1;
        if (direction === 'RIGHT' && ballPos % width !== width - 1) newPos += 1;

        if (newPos !== ballPos && grid[newPos] !== 2) {
            const newGrid = [...grid];
            newGrid[ballPos] = 0;
            const reachedGoal = newPos === goalPos;
            newGrid[newPos] = reachedGoal ? 3 : 1; // Keep goal visible if we somehow pass through? No, goal is end.

            setBallPos(newPos);
            setGrid(newGrid);
            setMoves(prev => prev + 1);

            if (reachedGoal) {
                const responseTime = Date.now() - startTime;
                setTimeout(() => {
                    onAnswer({
                        correct: true,
                        moves: moves + 1,
                        optimalMoves: targetMoves,
                        responseTime
                    });
                }, 500);
            }
        }
    };

    if (isGenerating) return <div className="puzzle-container">Generating Puzzle...</div>;

    return (
        <div className="puzzle-container" style={{ '--grid-width': width } as any}>
            <h2 className="puzzle-heading">Reach the Star</h2>
            <p className="puzzle-stats">Moves: {moves} (Target: {targetMoves})</p>

            <div className="puzzle-grid">
                {grid.map((cell, index) => (
                    <div
                        key={index}
                        className={`grid-cell ${cell === 1 ? 'ball' :
                            cell === 2 ? 'wall' :
                                cell === 3 ? 'goal' : ''
                            }`}
                        style={{ width: `${Math.min(60, 240 / width)}px`, height: `${Math.min(60, 240 / width)}px` }}
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
