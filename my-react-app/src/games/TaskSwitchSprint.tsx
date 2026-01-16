import { useState, useEffect, useRef } from 'react';
import '../styles/TaskSwitchSprint.css';

type TaskResult = {
    correct: boolean;
    responseTime: number;
    mistakeType?: string;
    switchCost?: number; // Time difference between switch trials and repeat trials
};

type Item = {
    shape: 'circle' | 'square';
    color: 'blue' | 'orange';
};

type Rule = 'COLOR' | 'SHAPE';

type Props = {
    initialRule: Rule; // Use Rule type here
    items: Item[]; // Sequence of items to show
    onAnswer: (result: TaskResult) => void;
    ageGroup?: string;
};

export default function TaskSwitchSprint({ initialRule, items, onAnswer, ageGroup = "9-11" }: Props) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [currentRule, setCurrentRule] = useState<Rule>(initialRule);
    const [showFeedback, setShowFeedback] = useState<'correct' | 'wrong' | null>(null);
    const startTime = useRef<number>(Date.now());
    const [ruleChanged, setRuleChanged] = useState(false);

    // switch rule logic
    useEffect(() => {
        // Easier for younger kids: Switch less often
        const switchFrequency = ageGroup === '6-8' ? 5 : 3;

        if (currentIndex > 0 && currentIndex % switchFrequency === 0) {
            setCurrentRule(prev => prev === 'COLOR' ? 'SHAPE' : 'COLOR');
            setRuleChanged(true);
            setTimeout(() => setRuleChanged(false), 1000);
        }
        startTime.current = Date.now();
    }, [currentIndex, ageGroup]);

    const handleResponse = (choice: 'left' | 'right') => {
        const item = items[currentIndex];

        // Logic: Left button = Blue/Circle, Right button = Orange/Square
        // This is a simplified mapping for the game
        const targetProperty = currentRule === 'COLOR' ? item.color : item.shape;

        const isLeftCorrect = (currentRule === 'COLOR' && item.color === 'blue') ||
            (currentRule === 'SHAPE' && item.shape === 'circle');

        const correct = (choice === 'left' && isLeftCorrect) ||
            (choice === 'right' && !isLeftCorrect);

        const responseTime = Date.now() - startTime.current;

        setShowFeedback(correct ? 'correct' : 'wrong');

        setTimeout(() => {
            setShowFeedback(null);

            if (currentIndex < items.length - 1) {
                setCurrentIndex(prev => prev + 1);
            } else {
                // End of round
                onAnswer({
                    correct,
                    responseTime,
                    mistakeType: correct ? undefined : "switching_error"
                });
            }
        }, 500);
    };

    const currentItem = items[currentIndex];

    return (
        <div className={`task-switch-container ${currentRule.toLowerCase()}-mode`}>
            <div className={`rule-banner ${ruleChanged ? 'pulse-rule' : ''}`}>
                Match by: <strong>{currentRule}</strong>
            </div>

            <div className={`stimulus-display ${showFeedback || ''}`}>
                <div className={`game-shape ${currentItem.shape} ${currentItem.color}`}></div>
            </div>

            <div className="response-buttons">
                <button className="task-btn left" onClick={() => handleResponse('left')}>
                    <span className="btn-icon">🔵 / ●</span>
                    <span className="btn-label">Blue / Circle</span>
                </button>
                <div className="divider">OR</div>
                <button className="task-btn right" onClick={() => handleResponse('right')}>
                    <span className="btn-icon">🔶 / ■</span>
                    <span className="btn-label">Orange / Square</span>
                </button>
            </div>
        </div>
    );
}
