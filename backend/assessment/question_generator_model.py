"""
Question Generator Model Class

This module contains the QuestionGeneratorModel class that can be
imported by both the training script and Django views.
"""

import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier


class QuestionGeneratorModel:
    """
    Model that predicts next question domain/difficulty and generates questions.
    """
    
    def __init__(self):
        self.domain_classifier = None
        self.difficulty_classifier = None
        
        # Game type mapping: domain -> difficulty -> game_type
        self.game_types = {
            'reading': {
                'easy': 'LetterFlipFrenzy',
                'medium': 'WordChainBuilder',
                'hard': 'ReadAloudEcho'
            },
            'math': {
                'easy': 'NumberSenseDash',
                'medium': 'TimeEstimator',
                'hard': 'VisualMathMatch'
            },
            'attention': {
                'easy': 'FocusGuard',
                'medium': 'TaskSwitchSprint',
                'hard': 'PatternWatcher'
            },
            'writing': {
                'easy': 'PlanAheadPuzzle',
                'medium': 'PlanAheadPuzzle',
                'hard': 'PlanAheadPuzzle'
            }
        }
        
        # Question templates by domain and difficulty
        self.templates = {
            'reading': {
                'easy': [
                    ('Find the word that starts with "{letter}"', ['bat', 'car', 'ant', 'cat'], 2),
                    ('Which word rhymes with "cat"?', ['dog', 'bat', 'car', 'sun'], 1),
                    ('What letter does "apple" start with?', ['B', 'A', 'C', 'D'], 1),
                ],
                'medium': [
                    ('What is the opposite of "hot"?', ['sad', 'cold', 'small', 'down'], 1),
                    ('Which word means the same as "happy"?', ['sad', 'joyful', 'angry', 'tired'], 1),
                    ('Complete: The dog ___ fast', ['run', 'runs', 'running', 'ran'], 1),
                ],
                'hard': [
                    ('Complete the sentence: She ___ to school yesterday', ['go', 'went', 'goes', 'going'], 1),
                    ('Which word is spelled correctly?', ['recieve', 'receive', 'recive', 'receeve'], 1),
                    ('What is the past tense of "swim"?', ['swam', 'swimmed', 'swum', 'swimming'], 0),
                ]
            },
            'math': {
                'easy': [
                    ('What is {a} + {b}?', None, None),  # Dynamic
                    ('What is {a} - {b}?', None, None),
                    ('Count: ⭐⭐⭐⭐⭐', ['3', '4', '5', '6'], 2),
                ],
                'medium': [
                    ('What is {a} × {b}?', None, None),
                    ('What is {a} ÷ {b}?', None, None),
                    ('What comes next: 2, 4, 6, 8, ?', ['9', '10', '11', '12'], 1),
                ],
                'hard': [
                    ('Solve: {a} × {b} + {c}', None, None),
                    ('If 3x = 12, what is x?', ['3', '4', '5', '6'], 1),
                    ('What is 15% of 60?', ['6', '7', '8', '9'], 3),
                ]
            },
            'attention': {
                'easy': [
                    ('Count the ⭐s: {stars}', None, None),
                    ('Which shape is different? 🔵🔵🔴🔵', ['1st', '2nd', '3rd', '4th'], 2),
                    ('Find the number: A B 3 C D', ['A', 'B', '3', 'C'], 2),
                ],
                'medium': [
                    ('What comes next: 2, 4, 6, 8, ?', ['9', '10', '11', '12'], 1),
                    ('Pattern: ▲▼▲▼▲?', ['▲', '▼', '●', '■'], 1),
                    ('Which is the odd one out: 2, 4, 5, 8', ['2', '4', '5', '8'], 2),
                ],
                'hard': [
                    ('Find the pattern: 1, 1, 2, 3, 5, 8, ?', ['10', '11', '13', '15'], 2),
                    ('Complete: A1, B2, C3, D?', ['3', '4', 'E4', 'D4'], 1),
                    ('What number is missing: 2, 4, _, 8, 10', ['5', '6', '7', '8'], 1),
                ]
            }
        }
    
    def fit(self, X, y):
        """
        Train the model.
        
        Args:
            X: Features [cur_domain, cur_diff, correct, time_ms]
            y: Targets [target_domain, target_diff]
        """
        # Split y into domain and difficulty
        y_domain = y[:, 0]
        y_difficulty = y[:, 1]
        
        # Train domain classifier
        self.domain_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.domain_classifier.fit(X, y_domain)
        
        # Train difficulty classifier
        self.difficulty_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.difficulty_classifier.fit(X, y_difficulty)
        
        return self
    
    def predict(self, X):
        """
        Predict next domain and difficulty.
        
        Args:
            X: Features array of shape (n_samples, 4)
        
        Returns:
            Array of shape (n_samples, 2) with [domain, difficulty]
        """
        domain_pred = self.domain_classifier.predict(X)
        difficulty_pred = self.difficulty_classifier.predict(X)
        
        # Combine predictions
        result = np.column_stack([domain_pred, difficulty_pred])
        return result
    
    def generate_question(self, domain, difficulty):
        """
        Generate a question for the given domain and difficulty.
        
        Args:
            domain: 'reading', 'math', or 'attention'
            difficulty: 'easy', 'medium', or 'hard'
        
        Returns:
            Dictionary with question_text, options, correct_option
        """
        # Map numeric to string if needed
        domain_map = {0: 'reading', 1: 'math', 2: 'attention'}
        diff_map = {0: 'easy', 1: 'medium', 2: 'hard'}
        
        if isinstance(domain, (int, np.integer)):
            domain = domain_map.get(domain, 'reading')
        if isinstance(difficulty, (int, np.integer)):
            difficulty = diff_map.get(difficulty, 'medium')
        
        # Get templates for this domain/difficulty
        templates = self.templates.get(domain, {}).get(difficulty, [])
        if not templates:
            # Fallback
            templates = self.templates['reading']['easy']
        
        # Choose random template
        template = random.choice(templates)
        question_text, options, correct_idx = template
        
        # Generate dynamic content for math questions
        if domain == 'math' and options is None:
            if 'What is' in question_text and '+' in question_text:
                a, b = random.randint(1, 10), random.randint(1, 10)
                answer = a + b
                question_text = f"What is {a} + {b}?"
                options = self._generate_options(answer)
                correct_idx = options.index(str(answer))
            elif '×' in question_text:
                a, b = random.randint(2, 9), random.randint(2, 9)
                answer = a * b
                question_text = f"What is {a} × {b}?"
                options = self._generate_options(answer)
                correct_idx = options.index(str(answer))
            elif '-' in question_text:
                a = random.randint(5, 15)
                b = random.randint(1, a-1)
                answer = a - b
                question_text = f"What is {a} - {b}?"
                options = self._generate_options(answer)
                correct_idx = options.index(str(answer))
            elif '÷' in question_text:
                b = random.randint(2, 5)
                answer = random.randint(2, 10)
                a = answer * b
                question_text = f"What is {a} ÷ {b}?"
                options = self._generate_options(answer)
                correct_idx = options.index(str(answer))
            elif 'Solve:' in question_text:
                a, b, c = random.randint(2, 5), random.randint(2, 5), random.randint(1, 10)
                answer = a * b + c
                question_text = f"Solve: {a} × {b} + {c}"
                options = self._generate_options(answer)
                correct_idx = options.index(str(answer))
        
        # Generate dynamic content for attention questions
        if domain == 'attention' and 'Count the ⭐s' in question_text:
            count = random.randint(5, 12)
            stars = ''.join(['⭐' if random.random() > 0.3 else '🔵' for _ in range(count + 5)])
            actual_count = stars.count('⭐')
            question_text = f"Count the ⭐s: {stars}"
            options = self._generate_options(actual_count)
            correct_idx = options.index(str(actual_count))
        
        # Handle letter substitution for reading
        if '{letter}' in question_text:
            letter = random.choice(['A', 'B', 'C', 'D'])
            question_text = question_text.format(letter=letter)
            # Update options to match
            words = {'A': 'ant', 'B': 'bat', 'C': 'cat', 'D': 'dog'}
            correct_word = words[letter]
            options = random.sample([w for w in words.values() if w != correct_word], 3)
            options.insert(random.randint(0, 3), correct_word)
            correct_idx = options.index(correct_word)
        
        # Determine game type
        game_type = self.game_types.get(domain, {}).get(difficulty, 'LetterFlipFrenzy')
        
        # Generate game-specific data
        game_data = self._generate_game_data(game_type, domain, difficulty, question_text, options, correct_idx)
        
        return {
            'domain': domain,
            'difficulty': difficulty,
            'question_text': question_text,
            'options': options,
            'correct_option': options[correct_idx],
            'game_type': game_type,
            'game_data': game_data
        }
    
    def _generate_options(self, correct_answer):
        """Generate 4 options including the correct answer."""
        options = [str(correct_answer)]
        
        # Generate 3 wrong options
        for _ in range(3):
            wrong = correct_answer + random.choice([-3, -2, -1, 1, 2, 3])
            if wrong > 0 and str(wrong) not in options:
                options.append(str(wrong))
        
        # Fill remaining if needed
        while len(options) < 4:
            wrong = correct_answer + random.randint(-5, 5)
            if wrong > 0 and str(wrong) not in options:
                options.append(str(wrong))
        
        # Shuffle
        random.shuffle(options)
        return options[:4]
    
    def _generate_game_data(self, game_type, domain, difficulty, question_text, options, correct_idx):
        """Generate game-specific data for interactive games."""
        game_data = {}
        
        if game_type == 'WordChainBuilder':
            # Generate target word and scrambled letters
            target_word = options[correct_idx] if options else 'READ'
            scrambled = list(target_word.upper())
            random.shuffle(scrambled)
            game_data = {
                'targetWord': target_word,
                'scrambledLetters': scrambled
            }
        
        elif game_type == 'TimeEstimator':
            # Time estimation challenge
            if difficulty == 'easy':
                target_seconds = random.choice([3, 4, 5])
            elif difficulty == 'medium':
                target_seconds = random.choice([5, 6, 7])
            else:
                target_seconds = random.choice([7, 8, 10])
            
            game_data = {
                'targetSeconds': target_seconds
            }
        
        elif game_type == 'TaskSwitchSprint':
            # Generate sequence of shapes and colors
            shapes = ['circle', 'square']
            colors = ['blue', 'orange']
            num_items = 4 if difficulty == 'easy' else 6 if difficulty == 'medium' else 8
            
            items = []
            for _ in range(num_items):
                items.append({
                    'shape': random.choice(shapes),
                    'color': random.choice(colors)
                })
            
            game_data = {
                'initialRule': random.choice(['COLOR', 'SHAPE']),
                'items': items
            }
        
        elif game_type == 'PlanAheadPuzzle':
            # Puzzle level based on difficulty
            level = 1 if difficulty == 'easy' else 2 if difficulty == 'medium' else 3
            game_data = {
                'level': level
            }
        
        elif game_type == 'FocusGuard':
            # Go/No-Go task
            game_data = {
                'stimulus': random.choice(['green', 'red'])
            }
        
        elif game_type == 'NumberSenseDash':
            # Number comparison
            left = random.randint(1, 20) if difficulty == 'easy' else random.randint(10, 50)
            right = random.randint(1, 20) if difficulty == 'easy' else random.randint(10, 50)
            game_data = {
                'left': left,
                'right': right
            }
        
        elif game_type == 'VisualMathMatch':
            # Visual equation matching
            if options and len(options) > 0:
                correct_value = int(options[correct_idx]) if options[correct_idx].isdigit() else 5
            else:
                correct_value = random.randint(1, 10)
            
            game_data = {
                'equation': question_text,
                'correctValue': correct_value,
                'options': [int(o) if o.isdigit() else 0 for o in options] if options else [correct_value]
            }
        
        elif game_type == 'PatternWatcher':
            # Pattern recognition
            patterns = [['A', 'B', 'A', 'B'], ['1', '2', '1', '2'], ['X', 'Y', 'X', 'Y']]
            pattern = random.choice(patterns)
            game_data = {
                'expectedPattern': pattern,
                'currentItem': pattern[0] if random.random() > 0.2 else 'C',
                'isBreak': random.random() < 0.3
            }
        
        elif game_type == 'ReadAloudEcho':
            # Reading aloud - use question_text as the sentence
            game_data = {
                'sentence': question_text
            }
        
        elif game_type == 'LetterFlipFrenzy':
            # Letter recognition with similar letters
            game_data = {
                'question': question_text,
                'options': options if options else ['b', 'd', 'p', 'q']
            }
        
        return game_data
