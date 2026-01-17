
import sys
import os
import random

# Add project root to path
sys.path.append(os.getcwd())

from assessment.question_generator_model import QuestionGeneratorModel

gen = QuestionGeneratorModel()

print("--- MATH ---")
for i in range(15):
    q = gen.generate_question('math', 'hard')
    print(f"{q['question_text']} | {q['options']}")

print("\n--- ATTN ---")
for i in range(5):
    q = gen.generate_question('attention', 'medium')
    print(f"{q['question_text']} | {q['options']}")
