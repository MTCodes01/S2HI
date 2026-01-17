"""
Gemini AI Question Generation Service

This module provides adaptive question generation using Google's Gemini AI,
following ACMC (Adaptive Computerized Multistage Computer) principles.
"""
import json
import os
from typing import Dict, Any
from google import genai
from google.genai import types

# Initialize Gemini client  
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Game type mapping for each domain/difficulty
GAME_TYPE_MAP = {
    'reading': {'easy': 'LetterFlipFrenzy', 'medium': 'WordChainBuilder', 'hard': 'ReadAloudEcho'},
    'math': {'easy': 'NumberSenseDash', 'medium': 'TimeEstimator', 'hard': 'VisualMathMatch'},
    'attention': {'easy': 'FocusGuard', 'medium': 'TaskSwitchSprint', 'hard': 'PatternWatcher'},
    'writing': {'easy': 'PlanAheadPuzzle', 'medium': 'PlanAheadPuzzle', 'hard': 'PlanAheadPuzzle'}
}


def determine_next_parameters(last_correct, response_time_ms, current_difficulty, domain_counts, session_accuracy, age_group='9-11'):
    """Determine next question parameters using ACMC logic with age-appropriate bounds"""
    difficulty_levels = ['easy', 'medium', 'hard']
    current_idx = difficulty_levels.index(current_difficulty)
    
    # ACMC Adaptive Logic
    if last_correct and response_time_ms < 900:
        next_difficulty_idx = min(2, current_idx + 1)
    elif not last_correct or response_time_ms > 1400:
        next_difficulty_idx = max(0, current_idx - 1)
    else:
        next_difficulty_idx = current_idx
    
    # Age-appropriate difficulty bounds
    if age_group in ['6-8', '6-9']:
        # Young kids: limit to easy and medium only
        next_difficulty_idx = min(1, next_difficulty_idx)  # Max medium
    elif age_group in ['9-11']:
        # Middle age: can handle all levels but prefer medium
        pass  # No restrictions
    elif age_group in ['11-14', '12-14']:
        # Older kids: avoid too easy questions
        next_difficulty_idx = max(0, next_difficulty_idx)  # Min easy, but rare
    
    next_difficulty = difficulty_levels[next_difficulty_idx]
    
    # Domain rotation - Include writing/logic
    domains = ['reading', 'math', 'attention', 'writing']
    min_count = min(domain_counts.values()) if domain_counts else 0
    
    # Prioritize domains with low counts
    least_used = [d for d in domains if domain_counts.get(d, 0) == min_count]
    
    import random
    # 70% chance to pick from least used, 30% total random for variety
    if random.random() < 0.7:
        next_domain = random.choice(least_used)
    else:
        next_domain = random.choice(domains)
    
    return next_domain, next_difficulty


def generate_gemini_question(domain, difficulty, age_group, game_type, last_correct=None, response_time_ms=None, session_accuracy=1.0, last_question_text=None):
    """Generate a question using Gemini AI"""
    # Build context
    context_parts = []
    if last_correct is not None:
        context_parts.append(f"Last answer {'correct' if last_correct else 'incorrect'}")
    if response_time_ms:
        context_parts.append(f"in {response_time_ms}ms")
    context = ", ".join(context_parts) if context_parts else "First question"
    if last_question_text:
        context += f". PREVIOUS QUESTION WAS: '{last_question_text}'. DO NOT REPEAT THIS CONTENT."
    
    # Game-specific instructions
    instructions = {
        'WordChainBuilder': "Generate a 4-6 letter word. Return JSON: { 'targetWord': 'WORD', 'scrambledLetters': ['W', 'R', 'O', 'D'] }",
        'TimeEstimator': "Set targetSeconds: Easy=3-5, Medium=5-7, Hard=7-10.",
        'TaskSwitchSprint': "Generate 8-10 items. Each item: { 'shape': 'circle'|'square', 'color': 'blue'|'orange' }. Also set initialRule: 'COLOR'|'SHAPE'.",
        'NumberSenseDash': "Generate two numbers 'left' and 'right'. Age 6-8: 1-20, Age 9-11: 10-50, Age 12-14: 20-100.",
        'VisualMathMatch': "Create math equation (e.g. '12 + 15') and options array (numbers) with correctValue.",
        'PatternWatcher': "No extra data needed, game generates sequence internally. Just provide age-appropriate encouragement in question_text.",
        'FocusGuard': "Set stimulus to 'green' or 'red'.",
        'PlanAheadPuzzle': "Set level 1-3 based on difficulty.",
        'LetterFlipFrenzy': "Generate a question about similar looking letters (b/d/p/q).",
        'ReadAloudEcho': "Generate a 10-15 word sentence appropriate for age."
    }
    
    instruction = instructions.get(game_type, "Generate appropriate question")
    
    # Age-specific difficulty guidance
    difficulty_guide = {
        '6-8': {
            'easy': 'Very simple, 1-2 step tasks, numbers 1-10, common 3-letter words',
            'medium': 'Simple tasks, numbers up to 20, basic 4-letter words',
            'hard': 'Not used for this age'
        },
        '6-9': {
            'easy': 'Very simple, 1-2 step tasks, numbers 1-10, common 3-letter words',
            'medium': 'Simple tasks, numbers up to 20, basic 4-letter words', 
            'hard': 'Not used for this age'
        },
        '9-11': {
            'easy': 'Straightforward, numbers up to 50, 4-5 letter words',
            'medium': 'Moderate challenge, numbers up to 100, 5-6 letter everyday words',
            'hard': 'Challenging, numbers over 100, 6-7 letter words, multi-step'
        },
        '11-14': {
            'easy': 'Basic level, numbers up to 100, 5-6 letter words',
            'medium': 'Grade-level challenge, larger numbers, 6-8 letter words',
            'hard': 'Advanced level, complex numbers, 8+ letter words, multi-step reasoning'
        },
        '12-14': {
            'easy': 'Basic level, numbers up to 100, 5-6 letter words',
            'medium': 'Grade-level challenge, larger numbers, 6-8 letter words',
            'hard': 'Advanced level, complex numbers, 8+ letter words, multi-step reasoning'
        }
    }
    
    age_guide = difficulty_guide.get(age_group, difficulty_guide['9-11'])
    specific_guide = age_guide.get(difficulty, age_guide.get('medium', ''))
    
    prompt = f"""You are an educational assessment AI. Create a {difficulty.upper()} level {domain} question for {age_group} year-olds.

Game Type: {game_type}
Task: {instruction}
Context: {context}

Difficulty Guidelines for {age_group} at {difficulty} level:
{specific_guide}

REQUIREMENTS:
1. Match the difficulty to the age group precisely
2. Use age-appropriate language and concepts  
3. Make it engaging but not frustrating
4. Vary the content (don't repeat common examples)
5. Return ONLY valid JSON

JSON Format:
{{
  "question_text": "Clear, age-appropriate instruction",
  "options": ["opt1", "opt2", "opt3", "opt4"],
  "correct_option": "correct answer",
  "game_data": {{
    // Game-specific data for {game_type}
  }}
}}

Generate JSON now:"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.9, response_mime_type='application/json')
        )
        
        # Parse JSON response
        question_data = json.loads(response.text)
        question_data.update({'domain': domain, 'difficulty': difficulty, 'game_type': game_type})
        
        print(f"✅ Gemini generated: {question_data.get('question_text', '')[:50]}...")
        return question_data
    except json.JSONDecodeError as e:
        print(f"❌ Gemini returned invalid JSON: {e}")
        print(f"Response text: {response.text[:200] if 'response' in locals() else 'No response'}")
        return generate_fallback_question(domain, difficulty, game_type)
    except Exception as e:
        print(f"❌ Gemini API failed: {type(e).__name__}: {str(e)}")
        return generate_fallback_question(domain, difficulty, game_type)


def generate_fallback_question(domain, difficulty, game_type):
    """Generate varied fallback questions if Gemini fails"""
    import random
    
    # More varied fallback questions
    reading_words = ['CAT', 'DOG', 'SUN', 'MOON', 'TREE', 'BOOK', 'FISH', 'BIRD']
    math_pairs = [(5, 8), (12, 7), (15, 9), (20, 13), (6, 11), (14, 18)]
    colors = ['green', 'red', 'blue', 'yellow']
    
    if domain == 'reading':
        if game_type == 'WordChainBuilder':
            word = random.choice(reading_words)
            letters = list(word)
            random.shuffle(letters)
            return {
                'question_text': f'Unscramble these letters to make a word',
                'options': [word, word[::-1], word[1:] + word[0], word[-1] + word[:-1]],
                'correct_option': word,
                'game_data': {'targetWord': word, 'scrambledLetters': letters},
                'domain': domain,
                'difficulty': difficulty,
                'game_type': game_type
            }
        else:
            letters = random.sample(['b', 'd', 'p', 'q', 'm', 'n', 'w'], 4)
            correct = random.choice(letters)
            return {
                'question_text': f'Which letter is this: {correct.upper()}?',
                'options': letters,
                'correct_option': correct,
                'game_data': {'targetLetter': correct, 'options': letters},
                'domain': domain,
                'difficulty': difficulty,
                'game_type': game_type
            }
    
    elif domain == 'math':
        if game_type == 'TimeEstimator':
            target = random.randint(3, 8)
            return {
                'question_text': f'Estimate {target} seconds!',
                'options': ['Start', 'Stop'],
                'correct_option': 'Stop',
                'game_data': {'targetSeconds': target},
                'domain': domain,
                'difficulty': difficulty,
                'game_type': game_type
            }
        else:
            left, right = random.choice(math_pairs)
            bigger = str(max(left, right))
            return {
                'question_text': f'Which number is bigger: {left} or {right}?',
                'options': [str(left), str(right)],
                'correct_option': bigger,
                'game_data': {'left': left, 'right': right},
                'domain': domain,
                'difficulty': difficulty,
                'game_type': game_type
            }
    
    elif domain == 'attention':
        stimulus = random.choice(colors)
        action = 'GO' if stimulus == 'green' else 'STOP'
        return {
            'question_text': f'Press GO for green, STOP for other colors',
            'options': ['GO', 'STOP'],
            'correct_option': action,
            'game_data': {'stimulus': stimulus},
            'domain': domain,
            'difficulty': difficulty,
            'game_type': game_type
        }
    
    elif domain == 'writing' or domain == 'logic':
        levels = {'easy': 1, 'medium': 2, 'hard': 3}
        level = levels.get(difficulty, 1)
        return {
            'question_text': f'Plan ahead! Solve this Level {level} puzzle.',
            'options': ['Start', 'Reset'],
            'correct_option': 'Start',
            'game_data': {'level': level},
            'domain': domain,
            'difficulty': difficulty,
            'game_type': 'PlanAheadPuzzle'
        }
    
    # Generic fallback
    return {
        'question_text': f'Ready for a {domain} challenge?',
        'options': ['Yes', 'Ready', 'Start', 'Go'],
        'correct_option': 'Yes',
        'game_data': {},
        'domain': domain,
        'difficulty': difficulty,
        'game_type': game_type
    }


def generate_adaptive_question(age_group, last_correct=None, response_time_ms=None, current_domain='reading', current_difficulty='easy', domain_counts=None, session_accuracy=1.0, last_question_text=None, next_domain=None, next_difficulty=None):
    """Main entry point for adaptive question generation"""
    if next_domain and next_difficulty:
        domain, difficulty = next_domain, next_difficulty
    elif last_correct is None:
        domain, difficulty = 'reading', 'easy'
    else:
        domain, difficulty = determine_next_parameters(
            last_correct, response_time_ms or 1000, current_difficulty,
            domain_counts or {}, session_accuracy, age_group
        )
    
    game_type = GAME_TYPE_MAP.get(domain, {}).get(difficulty, 'LetterFlipFrenzy')
    
    return generate_gemini_question(domain, difficulty, age_group, game_type, last_correct, response_time_ms, session_accuracy, last_question_text)
