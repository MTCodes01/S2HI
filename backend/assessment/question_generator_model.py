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
            },
            'writing': {
                'easy': [
                    ('Complete the sentence: I like to ___', ['running', 'run', 'runs', 'ran'], 1),
                    ('Which is spelled correctly?', ['hous', 'house', 'houz', 'housee'], 1),
                    ('Choose the correct word: She ___ a teacher', ['are', 'am', 'is', 'be'], 2),
                ],
                'medium': [
                    ('Which sentence is correct?', ['She go to school', 'She goes to school', 'She going to school', 'She gone to school'], 1),
                    ('Complete: The ___ cat sat ___ the mat', ['gray on', 'grey on', 'gray on', 'grey in'], 1),
                    ('Select the correct punctuation:', ['What is your name.', 'What is your name?', 'What is your name!', 'What is your name;'], 1),
                ],
                'hard': [
                    ('Which word is a noun?', ['quickly', 'happy', 'jump', 'table'], 3),
                    ('Complete: If she ___ hard, she will succeed', ['studied', 'studies', 'study', 'studying'], 1),
                    ('Which sentence uses the correct tense?', ['They was playing', 'They were playing', 'They are playing', 'All are correct'], 2),
                ]
            },
            'logic': {
                'easy': [
                    ('If A=1, B=2, what is C?', ['1', '2', '3', '4'], 2),
                    ('What comes next: 2, 4, 6, ?', ['7', '8', '9', '10'], 1),
                    ('Which does NOT belong: Apple, Banana, Car, Orange', ['Apple', 'Banana', 'Car', 'Orange'], 2),
                ],
                'medium': [
                    ('If 2X + 3 = 7, what is X?', ['1', '2', '3', '4'], 1),
                    ('Complete the pattern: A1, B2, C3, ?', ['D4', 'D3', 'E4', 'C4'], 0),
                    ('Which is the odd one: 3, 6, 9, 12, 14', ['3', '6', '9', '12', '14'], 4),
                ],
                'hard': [
                    ('If X² = 16, what is X?', ['-4', '4', 'Both -4 and 4', 'Cannot be determined'], 2),
                    ('Complete: 1, 4, 9, 16, 25, ?', ['36', '30', '32', '35'], 0),
                    ('Which logic is correct: All cats are animals. Tom is an animal. So Tom is a cat.', ['True', 'False', 'Sometimes true', 'Unknown'], 1),
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
            # Fallback - if domain not found, use reading
            if domain not in self.templates:
                domain = 'reading'
            if difficulty not in self.templates[domain]:
                difficulty = 'easy'
            templates = self.templates.get(domain, {}).get(difficulty, self.templates['reading']['easy'])

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

        return {
            'domain': domain,
            'difficulty': difficulty,
            'question_text': question_text,
            'options': options,
            'correct_option': options[correct_idx]
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
