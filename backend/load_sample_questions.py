"""
Management command to load sample questions into the database.
Run with: python manage.py load_sample_questions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ld_screening.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from assessment.models import Question


SAMPLE_QUESTIONS = [
    # Reading - Easy
    {
        'question_id': 'R_01',
        'domain': 'reading',
        'difficulty': 'easy',
        'question_text': 'Which letter is this? b',
        'options': ['b', 'd', 'p', 'q'],
        'correct_option': 'b'
    },
    {
        'question_id': 'R_02',
        'domain': 'reading',
        'difficulty': 'easy',
        'question_text': 'Which letter is this? d',
        'options': ['b', 'd', 'p', 'q'],
        'correct_option': 'd'
    },
    # Reading - Medium
    {
        'question_id': 'R_03',
        'domain': 'reading',
        'difficulty': 'medium',
        'question_text': 'Which word rhymes with "cat"?',
        'options': ['dog', 'bat', 'sun', 'cup'],
        'correct_option': 'bat'
    },
    {
        'question_id': 'R_04',
        'domain': 'reading',
        'difficulty': 'medium',
        'question_text': 'What is the opposite of "hot"?',
        'options': ['warm', 'cold', 'big', 'fast'],
        'correct_option': 'cold'
    },
    # Reading - Hard
    {
        'question_id': 'R_05',
        'domain': 'reading',
        'difficulty': 'hard',
        'question_text': 'Which word is spelled correctly?',
        'options': ['recieve', 'receive', 'receve', 'receeve'],
        'correct_option': 'receive'
    },
    {
        'question_id': 'R_06',
        'domain': 'reading',
        'difficulty': 'hard',
        'question_text': 'Find the word with silent letters:',
        'options': ['jump', 'knight', 'stand', 'help'],
        'correct_option': 'knight'
    },
    
    # Math - Easy
    {
        'question_id': 'M_01',
        'domain': 'math',
        'difficulty': 'easy',
        'question_text': 'What is 3 + 2?',
        'options': ['4', '5', '6', '7'],
        'correct_option': '5'
    },
    {
        'question_id': 'M_02',
        'domain': 'math',
        'difficulty': 'easy',
        'question_text': 'What is 7 - 3?',
        'options': ['3', '4', '5', '10'],
        'correct_option': '4'
    },
    # Math - Medium
    {
        'question_id': 'M_03',
        'domain': 'math',
        'difficulty': 'medium',
        'question_text': 'What is 6 × 4?',
        'options': ['20', '24', '28', '30'],
        'correct_option': '24'
    },
    {
        'question_id': 'M_04',
        'domain': 'math',
        'difficulty': 'medium',
        'question_text': 'What is 36 ÷ 6?',
        'options': ['4', '5', '6', '7'],
        'correct_option': '6'
    },
    # Math - Hard
    {
        'question_id': 'M_05',
        'domain': 'math',
        'difficulty': 'hard',
        'question_text': 'What is 12 × 11?',
        'options': ['121', '122', '132', '144'],
        'correct_option': '132'
    },
    {
        'question_id': 'M_06',
        'domain': 'math',
        'difficulty': 'hard',
        'question_text': 'What is 144 ÷ 12?',
        'options': ['10', '11', '12', '13'],
        'correct_option': '12'
    },
    
    # Writing - Easy
    {
        'question_id': 'W_01',
        'domain': 'writing',
        'difficulty': 'easy',
        'question_text': 'Which letter comes after "A"?',
        'options': ['B', 'C', 'D', 'E'],
        'correct_option': 'B'
    },
    {
        'question_id': 'W_02',
        'domain': 'writing',
        'difficulty': 'easy',
        'question_text': 'Complete the word: _at (animal that says meow)',
        'options': ['b', 'c', 'd', 'r'],
        'correct_option': 'c'
    },
    # Writing - Medium
    {
        'question_id': 'W_03',
        'domain': 'writing',
        'difficulty': 'medium',
        'question_text': 'Which sentence has correct punctuation?',
        'options': [
            'where are you going',
            'Where are you going?',
            'where are you going?',
            'Where are you going'
        ],
        'correct_option': 'Where are you going?'
    },
    {
        'question_id': 'W_04',
        'domain': 'writing',
        'difficulty': 'medium',
        'question_text': 'Choose the correct plural:',
        'options': ['childs', 'childes', 'children', 'childrens'],
        'correct_option': 'children'
    },
    # Writing - Hard
    {
        'question_id': 'W_05',
        'domain': 'writing',
        'difficulty': 'hard',
        'question_text': 'Which word correctly completes: "They ___ to the park."',
        'options': ['gone', 'went', 'goed', 'going'],
        'correct_option': 'went'
    },
    {
        'question_id': 'W_06',
        'domain': 'writing',
        'difficulty': 'hard',
        'question_text': 'Select the correctly spelled word:',
        'options': ['seperate', 'separate', 'seperete', 'separete'],
        'correct_option': 'separate'
    },
    
    # Attention - Easy
    {
        'question_id': 'A_01',
        'domain': 'attention',
        'difficulty': 'easy',
        'question_text': 'Count the red circles: 🔴🔵🔴🔵🔴',
        'options': ['2', '3', '4', '5'],
        'correct_option': '3'
    },
    {
        'question_id': 'A_02',
        'domain': 'attention',
        'difficulty': 'easy',
        'question_text': 'Which shape is different? ⬜⬜⬛⬜',
        'options': ['First', 'Second', 'Third', 'Fourth'],
        'correct_option': 'Third'
    },
    # Attention - Medium
    {
        'question_id': 'A_03',
        'domain': 'attention',
        'difficulty': 'medium',
        'question_text': 'What number comes next: 2, 4, 6, 8, ?',
        'options': ['9', '10', '11', '12'],
        'correct_option': '10'
    },
    {
        'question_id': 'A_04',
        'domain': 'attention',
        'difficulty': 'medium',
        'question_text': 'Find the odd one out:',
        'options': ['Apple', 'Banana', 'Carrot', 'Orange'],
        'correct_option': 'Carrot'
    },
    # Attention - Hard
    {
        'question_id': 'A_05',
        'domain': 'attention',
        'difficulty': 'hard',
        'question_text': 'What comes next: 1, 1, 2, 3, 5, 8, ?',
        'options': ['10', '11', '13', '15'],
        'correct_option': '13'
    },
    {
        'question_id': 'A_06',
        'domain': 'attention',
        'difficulty': 'hard',
        'question_text': 'Find the pattern: A1, B2, C3, D4, ?',
        'options': ['E4', 'E5', 'F5', 'D5'],
        'correct_option': 'E5'
    },
]


def load_questions():
    """Load sample questions into the database."""
    created_count = 0
    updated_count = 0
    
    for q_data in SAMPLE_QUESTIONS:
        question, created = Question.objects.update_or_create(
            question_id=q_data['question_id'],
            defaults={
                'domain': q_data['domain'],
                'difficulty': q_data['difficulty'],
                'question_text': q_data['question_text'],
                'options': q_data['options'],
                'correct_option': q_data['correct_option']
            }
        )
        
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    print(f"Loaded questions: {created_count} created, {updated_count} updated")
    print(f"Total questions in database: {Question.objects.count()}")


if __name__ == '__main__':
    load_questions()
