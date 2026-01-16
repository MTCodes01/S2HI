from django.core.management.base import BaseCommand
from assessment.models import Question

class Command(BaseCommand):
    help = 'Seeds the database with real assessment questions and game content'

    def handle(self, *args, **options):
        questions = [
            # --- READING (LetterFlipFrenzy, WordChainBuilder, ReadAloudEcho) ---
            # EASY: LetterFlipFrenzy
            {'id': 'R_E_01', 'domain': 'reading', 'difficulty': 'easy', 'text': 'Which letter is "b"?', 'options': ['b', 'd', 'p', 'q'], 'correct': 'b'},
            {'id': 'R_E_02', 'domain': 'reading', 'difficulty': 'easy', 'text': 'Find the letter "p"', 'options': ['q', 'p', 'd', 'b'], 'correct': 'p'},
            {'id': 'R_E_03', 'domain': 'reading', 'difficulty': 'easy', 'text': 'Select "m"', 'options': ['w', 'v', 'n', 'm'], 'correct': 'm'},
            
            # MEDIUM: WordChainBuilder (Jumbled Letters)
            {'id': 'R_M_01', 'domain': 'reading', 'difficulty': 'medium', 'text': 'Spell the word for "The feline pet"', 'options': ['A', 'C', 'T'], 'correct': 'CAT'},
            {'id': 'R_M_02', 'domain': 'reading', 'difficulty': 'medium', 'text': 'Spell the word for "Something you read"', 'options': ['O', 'K', 'O', 'B'], 'correct': 'BOOK'},
            {'id': 'R_M_03', 'domain': 'reading', 'difficulty': 'medium', 'text': 'Spell the word for "The glowing orb in the sky"', 'options': ['N', 'U', 'S'], 'correct': 'SUN'},
            
            # HARD: ReadAloudEcho
            {'id': 'R_H_01', 'domain': 'reading', 'difficulty': 'hard', 'text': 'The quick brown fox jumps over the lazy dog.', 'options': [], 'correct': 'The quick brown fox jumps over the lazy dog.'},
            {'id': 'R_H_02', 'domain': 'reading', 'difficulty': 'hard', 'text': 'She sells seashells by the seashore.', 'options': [], 'correct': 'She sells seashells by the seashore.'},
            
            # --- MATH (NumberSenseDash, TimeEstimator, VisualMathMatch) ---
            # EASY: NumberSenseDash
            {'id': 'M_E_01', 'domain': 'math', 'difficulty': 'easy', 'text': 'Which is larger?', 'options': ['5', '12'], 'correct': '12'},
            {'id': 'M_E_02', 'domain': 'math', 'difficulty': 'easy', 'text': 'Which is smaller?', 'options': ['18', '7'], 'correct': '7'},
            
            # MEDIUM: TimeEstimator
            {'id': 'M_M_01', 'domain': 'math', 'difficulty': 'medium', 'text': 'Stop the clock at 5 seconds!', 'options': ['5'], 'correct': '5'},
            {'id': 'M_M_02', 'domain': 'math', 'difficulty': 'medium', 'text': 'Stop the clock at 3 seconds!', 'options': ['3'], 'correct': '3'},
            
            # HARD: VisualMathMatch (Simplified for now)
            {'id': 'M_H_01', 'domain': 'math', 'difficulty': 'hard', 'text': 'What is 5 + 3?', 'options': ['7', '8', '9'], 'correct': '8'},
            {'id': 'M_H_02', 'domain': 'math', 'difficulty': 'hard', 'text': 'What is 10 - 4?', 'options': ['6', '5', '7'], 'correct': '6'},
            
            # --- ATTENTION (FocusGuard, TaskSwitchSprint, PatternWatcher) ---
            # EASY: FocusGuard
            {'id': 'A_E_01', 'domain': 'attention', 'difficulty': 'easy', 'text': 'Tap on Green, Wait on Red', 'options': ['green', 'red'], 'correct': 'green'},
            
            # MEDIUM: TaskSwitchSprint
            {'id': 'A_M_01', 'domain': 'attention', 'difficulty': 'medium', 'text': 'Follow the changing rules!', 'options': ['COLOR', 'SHAPE'], 'correct': 'COLOR'},
            
            # HARD: PatternWatcher (Refactored to be self-contained)
            {'id': 'A_H_01', 'domain': 'attention', 'difficulty': 'hard', 'text': 'Spot the odd one in the pattern!', 'options': [], 'correct': 'pattern_break'},

            # --- WRITING / LOGIC (PlanAheadPuzzle) ---
            {'id': 'W_M_01', 'domain': 'writing', 'difficulty': 'medium', 'text': 'Unblock the path to the exit!', 'options': [], 'correct': 'exit_reached'},
            {'id': 'W_H_01', 'domain': 'writing', 'difficulty': 'hard', 'text': 'Solve the sequence puzzle!', 'options': [], 'correct': 'solved'},
        ]

        # Clear existing non-essential questions (optional, but good for cleanup)
        # Question.objects.all().delete()

        created_count = 0
        for q in questions:
            obj, created = Question.objects.update_or_create(
                question_id=q['id'],
                defaults={
                    'domain': q['domain'],
                    'difficulty': q['difficulty'],
                    'question_text': q['text'],
                    'options': q['options'],
                    'correct_option': q['correct']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(questions)} questions ({created_count} new)'))
