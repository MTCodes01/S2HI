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
                    ('Which word rhymes with "hat"?', ['cat', 'dog', 'hat', 'mat'], 3),
                    ('Find the word that starts with "s"', ['sun', 'moon', 'cat', 'dog'], 0),
                    ('What letter does "dog" start with?', ['C', 'D', 'B', 'A'], 1),
                    ('Which word rhymes with "big"?', ['pig', 'dog', 'cat', 'hat'], 0),
                    ('Find the word that starts with "b"', ['bat', 'cat', 'dog', 'rat'], 0),
                    ('What letter does "cat" start with?', ['A', 'C', 'B', 'D'], 1),
                    ('Which word rhymes with "ring"?', ['sing', 'dog', 'cat', 'run'], 0),
                    ('Find the word that starts with "m"', ['moon', 'cat', 'dog', 'sun'], 0),
                    ('What letter does "run" start with?', ['R', 'S', 'T', 'D'], 0),
                    ('Which word rhymes with "hop"?', ['stop', 'cat', 'dog', 'hat'], 0),
                    ('Find the word that starts with "d"', ['dog', 'cat', 'bat', 'rat'], 0),
                    ('What letter does "sit" start with?', ['S', 'T', 'B', 'D'], 0),
                ],
                'medium': [
                    ('What is the opposite of "hot"?', ['sad', 'cold', 'small', 'down'], 1),
                    ('Which word means the same as "happy"?', ['sad', 'joyful', 'angry', 'tired'], 1),
                    ('Complete: The dog ___ fast', ['run', 'runs', 'running', 'ran'], 1),
                    ('What is the opposite of "big"?', ['small', 'large', 'huge', 'tiny'], 0),
                    ('Which word means the same as "quick"?', ['fast', 'slow', 'lazy', 'tired'], 0),
                    ('Complete: The cat ___ on the mat', ['sit', 'sits', 'sitting', 'sat'], 1),
                    ('What is the opposite of "dark"?', ['light', 'bright', 'dim', 'night'], 0),
                    ('Which word means the same as "sad"?', ['happy', 'joyful', 'unhappy', 'glad'], 2),
                    ('Complete: I ___ my friend yesterday', ['see', 'sees', 'saw', 'seeing'], 2),
                    ('What is the opposite of "clean"?', ['dirty', 'neat', 'tidy', 'messy'], 0),
                    ('Which word means the same as "kind"?', ['mean', 'nice', 'cruel', 'rude'], 1),
                    ('Complete: She ___ to the store', ['go', 'goes', 'went', 'going'], 1),
                    ('What is the opposite of "young"?', ['old', 'new', 'ancient', 'aged'], 0),
                    ('Which word means the same as "beautiful"?', ['ugly', 'pretty', 'bad', 'wrong'], 1),
                    ('Complete: We ___ playing games', ['are', 'is', 'am', 'be'], 0),
                ],
                'hard': [
                    ('Complete the sentence: She ___ to school yesterday', ['go', 'went', 'goes', 'going'], 1),
                    ('Which word is spelled correctly?', ['recieve', 'receive', 'recive', 'receeve'], 1),
                    ('What is the past tense of "swim"?', ['swam', 'swimmed', 'swum', 'swimming'], 0),
                    ('Which sentence is grammatically correct?', ['She go to school', 'She goes to school', 'She going to school', 'She gone to school'], 1),
                    ('What is the past tense of "run"?', ['ran', 'runned', 'running', 'runs'], 0),
                    ('Which word is spelled correctly?', ['occassion', 'ocasion', 'occasion', 'occassoin'], 2),
                    ('Complete: If I ___ you, I would help', ['were', 'was', 'am', 'is'], 0),
                    ('What is the past tense of "eat"?', ['ate', 'eated', 'eating', 'eats'], 0),
                    ('Which word is spelled correctly?', ['definite', 'definitly', 'definately', 'difinate'], 0),
                    ('Complete: They ___ to the park last week', ['went', 'go', 'goes', 'going'], 0),
                    ('What is the past tense of "do"?', ['did', 'done', 'doing', 'does'], 0),
                    ('Which word is spelled correctly?', ['necessary', 'neccessary', 'necesary', 'neccesary'], 0),
                    ('Complete: The teacher ___ a new lesson today', ['teach', 'teaches', 'teaching', 'taught'], 1),
                    ('What is the past tense of "see"?', ['saw', 'seen', 'seeing', 'sees'], 0),
                    ('Which word is spelled correctly?', ['separate', 'seperate', 'sepearte', 'separete'], 0),
                ]
            },
            'math': {
                'easy': [
                    ('What is {a} + {b}?', None, None),  # Dynamic
                    ('What is {a} - {b}?', None, None),
                    ('Count: ⭐⭐⭐⭐⭐', ['3', '4', '5', '6'], 2),
                    ('What is {a} + {b}?', None, None),
                    ('What is {a} - {b}?', None, None),
                    ('Which is larger: {a} or {b}?', None, None),
                    ('What is {a} + {b}?', None, None),
                    ('What is {a} - {b}?', None, None),
                    ('Count the stars: ⭐⭐⭐', ['2', '3', '4', '5'], 1),
                    ('What is {a} + {b}?', None, None),
                    ('What is {a} - {b}?', None, None),
                    ('How many: ✌️✌️✌️', ['2', '3', '4', '5'], 2),
                    ('What is {a} + {b}?', None, None),
                    ('What is {a} - {b}?', None, None),
                    ('Which is smaller: {a} or {b}?', None, None),
                ],
                'medium': [
                    ('What is {a} × {b}?', None, None),
                    ('What is {a} ÷ {b}?', None, None),
                    ('What comes next: 2, 4, 6, 8, ?', ['9', '10', '11', '12'], 1),
                    ('What is {a} × {b}?', None, None),
                    ('What is {a} ÷ {b}?', None, None),
                    ('Complete: 5, 10, 15, 20, ?', ['25', '24', '22', '21'], 0),
                    ('What is {a} × {b}?', None, None),
                    ('What is {a} ÷ {b}?', None, None),
                    ('Complete: 1, 2, 4, 8, ?', ['16', '12', '10', '9'], 0),
                    ('What is {a} × {b}?', None, None),
                    ('What is {a} ÷ {b}?', None, None),
                    ('Complete: 10, 20, 30, 40, ?', ['50', '45', '35', '55'], 0),
                    ('What is {a} × {b}?', None, None),
                    ('What is {a} ÷ {b}?', None, None),
                    ('Complete: 3, 6, 9, 12, ?', ['15', '14', '13', '16'], 0),
                ],
                'hard': [
                    ('Solve: {a} × {b} + {c}', None, None),
                    ('If 3x = 12, what is x?', ['3', '4', '5', '6'], 1),
                    ('What is 15% of 60?', ['6', '7', '8', '9'], 3),
                    ('Solve: {a} × {b} + {c}', None, None),
                    ('If 2x + 3 = 11, what is x?', ['4', '5', '6', '7'], 0),
                    ('What is 20% of 100?', ['15', '20', '25', '30'], 1),
                    ('Solve: {a} × {b} + {c}', None, None),
                    ('If x - 5 = 10, what is x?', ['10', '15', '20', '25'], 1),
                    ('What is 50% of 80?', ['30', '40', '50', '60'], 1),
                    ('Solve: {a} × {b} + {c}', None, None),
                    ('If 4x = 20, what is x?', ['4', '5', '6', '7'], 1),
                    ('What is 25% of 40?', ['8', '9', '10', '12'], 0),
                    ('Solve: {a} × {b} + {c}', None, None),
                    ('If x + 7 = 15, what is x?', ['6', '7', '8', '9'], 1),
                    ('What is 10% of 50?', ['3', '4', '5', '6'], 2),
                ]
            },
            'attention': {
                'easy': [
                    ('Count the ⭐s: {stars}', None, None),
                    ('Which shape is different? 🔵🔵🔴🔵', ['1st', '2nd', '3rd', '4th'], 2),
                    ('Find the number: A B 3 C D', ['A', 'B', '3', 'C'], 2),
                    ('Count the 🔴s: 🔴🔵🔴🔵🔴', ['2', '3', '4', '5'], 2),
                    ('Which is different? 🔵🔵🔵🟢🔵', ['1st', '2nd', '3rd', '4th'], 3),
                    ('Find the letter: 1 A 2 B 3', ['A', 'B', '1', '3'], 1),
                    ('Count the ⭐s: ⭐🌙⭐🌙⭐', ['2', '3', '4', '5'], 2),
                    ('Which is odd one out? 🔴🔴🟡🔴', ['1st', '2nd', '3rd', '4th'], 2),
                    ('Find the symbol: A # B & C', ['A', '#', 'B', '&'], 1),
                    ('Count the 🌙s: ⭐🌙⭐🌙⭐🌙', ['2', '3', '4', '5'], 3),
                    ('Which shape is missing? 🔵⬜🔵⬜?', ['🔵', '⬜', '🔴', '⬛'], 0),
                    ('Find the number: 5 X 7 Y 9', ['5', 'X', '7', 'Y'], 2),
                    ('Count the ⬜s: ⬜🔵⬜🔵⬜', ['2', '3', '4', '5'], 2),
                    ('Which is different? 🟢🟢🟢🔴🟢', ['1st', '2nd', '3rd', '4th'], 3),
                    ('Find the vowel: B A C D', ['B', 'A', 'C', 'D'], 1),
                ],
                'medium': [
                    ('What comes next: 2, 4, 6, 8, ?', ['9', '10', '11', '12'], 1),
                    ('Pattern: ▲▼▲▼▲?', ['▲', '▼', '●', '■'], 1),
                    ('Which is the odd one out: 2, 4, 5, 8', ['2', '4', '5', '8'], 2),
                    ('What comes next: A, B, A, B, ?', ['A', 'B', 'C', 'D'], 0),
                    ('Pattern: 🔵🔵⬜🔵🔵⬜?', ['🔵', '⬜', '🔴', '⬛'], 0),
                    ('Which is odd: 6, 12, 18, 25', ['6', '12', '18', '25'], 3),
                    ('What comes next: 1, 1, 2, 3, 5, 8, ?', ['10', '11', '13', '15'], 2),
                    ('Pattern: ▲ ▼ ▲ ▼ ?', ['▲', '▼', '●', '■'], 0),
                    ('Which is odd: apple, banana, cat, orange', ['apple', 'banana', 'cat', 'orange'], 2),
                    ('What comes next: Z, Y, X, W, ?', ['V', 'U', 'T', 'S'], 0),
                    ('Pattern: ◆ ◆ ● ◆ ◆ ● ?', ['◆', '●', '■', '▲'], 1),
                    ('Which is odd: 3, 6, 9, 11', ['3', '6', '9', '11'], 3),
                    ('What comes next: 1, 2, 2, 3, 3, 3, ?', ['4', '2', '3', '5'], 0),
                    ('Pattern: → ← → ← ?', ['→', '←', '↑', '↓'], 0),
                    ('Which is odd: red, blue, green, circle', ['red', 'blue', 'green', 'circle'], 3),
                ],
                'hard': [
                    ('Find the pattern: 1, 1, 2, 3, 5, 8, ?', ['10', '11', '13', '15'], 2),
                    ('Complete: A1, B2, C3, D?', ['3', '4', 'E4', 'D4'], 1),
                    ('What number is missing: 2, 4, _, 8, 10', ['5', '6', '7', '8'], 1),
                    ('Find the pattern: 2, 6, 12, 20, ?', ['28', '30', '32', '35'], 0),
                    ('Complete: 1A, 2B, 3C, ?', ['4D', '3D', '4E', '5D'], 0),
                    ('What number is missing: 5, 10, 15, _, 25', ['20', '18', '17', '22'], 0),
                    ('Find the pattern: 1, 4, 9, 16, 25, ?', ['36', '32', '30', '35'], 0),
                    ('Complete: Triangle, Square, Pentagon, ?', ['Hexagon', 'Circle', 'Octagon', 'Star'], 0),
                    ('What number is missing: 1, 1, 2, 3, 5, 8, 13, ?', ['21', '15', '18', '20'], 0),
                    ('Find the pattern: 10, 20, 30, 40, 50, ?', ['60', '55', '65', '70'], 0),
                    ('Complete: Red, Orange, Yellow, Green, ?', ['Blue', 'Purple', 'Pink', 'Brown'], 0),
                    ('What number is missing: 1, 8, 27, 64, ?', ['125', '100', '81', '120'], 0),
                    ('Find the pattern: ▲, ▲▲, ▲▲▲, ▲▲▲▲, ?', ['▲▲▲▲▲', '▲▲', '▲', '▲▲▲'], 0),
                    ('Complete: 1/2, 1/3, 1/4, ?', ['1/5', '1/6', '2/5', '1/8'], 0),
                    ('What comes next: 100, 90, 81, 73, ?', ['66', '64', '62', '70'], 0),
                ]
            },
            'writing': {
                'easy': [
                    ('Complete the sentence: I like to ___', ['running', 'run', 'runs', 'ran'], 1),
                    ('Which is spelled correctly?', ['hous', 'house', 'houz', 'housee'], 1),
                    ('Choose the correct word: She ___ a teacher', ['are', 'am', 'is', 'be'], 2),
                    ('Complete: I ___ happy', ['is', 'am', 'are', 'be'], 1),
                    ('Which is spelled correctly?', ['cat', 'kat', 'catt', 'ca'], 0),
                    ('Choose: He ___ my friend', ['are', 'am', 'is', 'be'], 2),
                    ('Complete: We ___ at school', ['is', 'am', 'are', 'be'], 2),
                    ('Which is spelled correctly?', ['dog', 'dag', 'dogg', 'ddog'], 0),
                    ('Choose: They ___ happy', ['is', 'am', 'are', 'be'], 2),
                    ('Complete: You ___ smart', ['is', 'am', 'are', 'be'], 2),
                    ('Which is spelled correctly?', ['apple', 'aple', 'appel', 'appl'], 0),
                    ('Choose: The teacher ___ here', ['are', 'am', 'is', 'be'], 2),
                    ('Complete: She ___ books', ['like', 'likes', 'liking', 'liked'], 1),
                    ('Which is spelled correctly?', ['window', 'windwo', 'windo', 'winodw'], 0),
                    ('Choose: It ___ sunny', ['are', 'am', 'is', 'be'], 2),
                ],
                'medium': [
                    ('Which sentence is correct?', ['She go to school', 'She goes to school', 'She going to school', 'She gone to school'], 1),
                    ('Complete: The ___ cat sat ___ the mat', ['gray on', 'grey on', 'gray on', 'grey in'], 1),
                    ('Select the correct punctuation:', ['What is your name.', 'What is your name?', 'What is your name!', 'What is your name;'], 1),
                    ('Which sentence is correct?', ['He play football', 'He plays football', 'He playing football', 'He played football'], 1),
                    ('Complete: I ___ yesterday', ['go', 'goes', 'went', 'going'], 2),
                    ('Which is correct grammar?', ['She have a dog', 'She has a dog', 'She having dog', 'She had a dogs'], 1),
                    ('Choose correct form: They ___ at home', ['was', 'were', 'is', 'are'], 1),
                    ('Complete: The ___ child was happy', ['smile', 'smiling', 'smiled', 'smiles'], 1),
                    ('Which sentence is correct?', ['I don\'t know', 'I not know', 'I doesn\'t know', 'I didn\'t knows'], 0),
                    ('Complete: She ___ to the park yesterday', ['go', 'goes', 'went', 'going'], 2),
                    ('Choose correct form: He ___ his homework', ['did', 'does', 'do', 'doing'], 0),
                    ('Which is correct spelling?', ['recieve', 'receive', 'recive', 'receeve'], 1),
                    ('Complete: We ___ finished our work', ['have', 'has', 'is', 'are'], 0),
                    ('Choose correct tense: She ___ to school every day', ['go', 'goes', 'went', 'going'], 1),
                    ('Which sentence is correct?', ['You is smart', 'You are smart', 'You am smart', 'You be smart'], 1),
                ],
                'hard': [
                    ('Which word is a noun?', ['quickly', 'happy', 'jump', 'table'], 3),
                    ('Complete: If she ___ hard, she will succeed', ['studied', 'studies', 'study', 'studying'], 1),
                    ('Which sentence uses the correct tense?', ['They was playing', 'They were playing', 'They are playing', 'All are correct'], 2),
                    ('Choose the correct usage: ___ books are very interesting', ['Their', 'There', 'They\'re', 'Theirs'], 0),
                    ('Which word is an adverb?', ['beautiful', 'quickly', 'happy', 'kind'], 1),
                    ('Complete: By next year, she ___ here for 5 years', ['will work', 'will have worked', 'works', 'has worked'], 1),
                    ('Choose correct form: Neither John ___ Mary is available', ['nor', 'and', 'or', 'but'], 0),
                    ('Which is a compound sentence?', ['She ran fast', 'She ran and fell', 'She ran through the park', 'She was running fast'], 1),
                    ('Complete: ___ done your homework yet?', ['Have you', 'Has you', 'Do you', 'Are you'], 0),
                    ('Choose correct agreement: The team ___ winning their games', ['is', 'are', 'was', 'were'], 0),
                    ('Which word is an adjective?', ['quickly', 'beautiful', 'sadly', 'carefully'], 1),
                    ('Complete: He would have gone if he ___ time', ['have', 'had', 'has', 'having'], 1),
                    ('Choose correct punctuation: ___ coming to the party', ['Whose', 'Who\'s', 'Whos', 'Who is'], 1),
                    ('Which shows parallel structure?', ['Running and to jump', 'Run and jump', 'Running and jumping', 'To run and jump'], 2),
                    ('Complete: The doctor asked what ___ bothering me', ['is', 'was', 'were', 'are'], 1),
                ]
            },
            'logic': {
                'easy': [
                    ('If A=1, B=2, what is C?', ['1', '2', '3', '4'], 2),
                    ('What comes next: 2, 4, 6, ?', ['7', '8', '9', '10'], 1),
                    ('Which does NOT belong: Apple, Banana, Car, Orange', ['Apple', 'Banana', 'Car', 'Orange'], 2),
                    ('If 1=A, 2=B, what is 3?', ['A', 'B', 'C', 'D'], 2),
                    ('What comes next: 5, 10, 15, ?', ['20', '25', '21', '19'], 0),
                    ('Which does NOT belong: Dog, Cat, Bird, Apple', ['Dog', 'Cat', 'Bird', 'Apple'], 3),
                    ('If X=10, Y=20, what is Z?', ['25', '30', '35', '40'], 1),
                    ('What comes next: 1, 3, 5, ?', ['7', '8', '9', '6'], 0),
                    ('Which does NOT belong: Red, Blue, Chair, Green', ['Red', 'Blue', 'Chair', 'Green'], 2),
                    ('If first=1, second=2, what is third?', ['2', '3', '4', '5'], 1),
                    ('What comes next: 10, 20, 30, ?', ['40', '50', '35', '45'], 0),
                    ('Which does NOT belong: Hammer, Nail, Saw, Cloud', ['Hammer', 'Nail', 'Saw', 'Cloud'], 3),
                    ('If Hot=Cold, Big=?, then ?=Small', ['Tiny', 'Large', 'Huge', 'Little'], 1),
                    ('What comes next: 2, 4, 6, 8, ?', ['9', '10', '11', '12'], 1),
                    ('Which does NOT belong: Monday, Tuesday, Blue, Wednesday', ['Monday', 'Tuesday', 'Blue', 'Wednesday'], 2),
                ],
                'medium': [
                    ('If 2X + 3 = 7, what is X?', ['1', '2', '3', '4'], 1),
                    ('Complete the pattern: A1, B2, C3, ?', ['D4', 'D3', 'E4', 'C4'], 0),
                    ('Which is the odd one: 3, 6, 9, 12, 14', ['3', '6', '9', '12', '14'], 4),
                    ('If 3X = 12, what is X?', ['3', '4', '5', '6'], 1),
                    ('Complete: 1, 4, 9, 16, ?', ['25', '20', '24', '26'], 0),
                    ('Which is odd: 2, 4, 6, 8, 9', ['2', '4', '6', '8', '9'], 4),
                    ('If X - 5 = 10, what is X?', ['10', '15', '20', '25'], 1),
                    ('Complete: 2, 3, 5, 8, ?', ['12', '13', '14', '11'], 0),
                    ('Which is odd: Apple, Banana, Car, Orange', ['Apple', 'Banana', 'Car', 'Orange'], 2),
                    ('If 4X = 16, what is X?', ['3', '4', '5', '6'], 1),
                    ('Complete: A, C, E, G, ?', ['I', 'H', 'J', 'K'], 0),
                    ('Which is odd: Red, Circle, Blue, Green', ['Red', 'Circle', 'Blue', 'Green'], 1),
                    ('If X + 7 = 15, what is X?', ['6', '7', '8', '9'], 1),
                    ('Complete: 10, 5, 10, 5, ?', ['10', '5', '0', '15'], 0),
                    ('Which is odd: 1, 2, 3, 4, 7', ['1', '2', '3', '4', '7'], 4),
                ],
                'hard': [
                    ('If X² = 16, what is X?', ['-4', '4', 'Both -4 and 4', 'Cannot be determined'], 2),
                    ('Complete: 1, 4, 9, 16, 25, ?', ['36', '30', '32', '35'], 0),
                    ('Which logic is correct: All cats are animals. Tom is an animal. So Tom is a cat.', ['True', 'False', 'Sometimes true', 'Unknown'], 1),
                    ('If 2X² + 3 = 11, what is X?', ['1', '2', '3', '4'], 1),
                    ('Complete: 1, 1, 2, 3, 5, 8, ?', ['13', '11', '12', '14'], 0),
                    ('Which reasoning is valid: All dogs bark. Fido barks. So Fido is a dog.', ['Valid', 'Invalid', 'Partially valid', 'Unknown'], 1),
                    ('If 3X - 2 = 10, what is X?', ['2', '3', '4', '5'], 2),
                    ('Complete: 2, 6, 12, 20, 30, ?', ['42', '40', '38', '44'], 0),
                    ('Which argument has a logical fallacy?', ['All students study. John studies. Therefore John is a student.', 'All birds fly. Hawks fly. Therefore hawks are birds.', 'All A is B. X is A. Therefore X is B.', 'All ice is cold. This is cold. Therefore this is ice.'], 3),
                    ('If (X+3)² = 25, what is X?', ['2', '-8', '2 or -8', 'Cannot be determined'], 2),
                    ('Complete: 1/2, 1/3, 1/4, 1/5, ?', ['1/6', '1/7', '2/6', '1/8'], 0),
                    ('Which statement is logically consistent?', ['This statement is false.', ['A is B and A is not B.', 'All are false.', 'All are true.'], 2),
                    ('If 5X + 2 = 27, what is X?', ['4', '5', '6', '7'], 0),
                    ('Complete: 1, 3, 6, 10, 15, ?', ['21', '20', '19', '22'], 0),
                    ('Which is a valid conclusion from: Some A are B. Some B are C.', ['Some A are C.', 'All A are C.', 'No A are C.', 'Cannot be determined.'], 3),
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
        domain_map = {0: 'reading', 1: 'math', 2: 'attention', 3: 'writing', 4: 'logic'}
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
