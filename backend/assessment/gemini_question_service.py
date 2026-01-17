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
    if age_group == '6-8':
        # Young kids: limit to easy and medium only
        next_difficulty_idx = min(1, next_difficulty_idx)  # Max medium
    elif age_group == '9-11':
        # Middle age: can handle all levels but prefer medium
        pass  # No restrictions
    elif age_group in ['12-14', '14+']:
        # Older kids and teens: avoid too easy questions, prefer medium-hard
        next_difficulty_idx = max(0, next_difficulty_idx)  # Min easy, but rare
    
    next_difficulty = difficulty_levels[next_difficulty_idx]
    
    # Domain rotation - Strictly pick least used
    domains = ['reading', 'math', 'attention', 'writing']
    counts = [domain_counts.get(d, 0) for d in domains]
    min_val = min(counts)
    
    # Get all domains that have the minimum count
    least_used = [d for d in domains if domain_counts.get(d, 0) == min_val]
    
    import random
    # Strictly pick from least used to ensure perfect balance
    next_domain = random.choice(least_used)
    
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
    
    # Game-specific instructions with age-appropriate scaling
    age_params = {
        '6-8': {'num_range': '1-10', 'time_range': '2-4', 'word_len': '3-4'},
        '9-11': {'num_range': '10-50', 'time_range': '3-6', 'word_len': '4-6'},
        '12-14': {'num_range': '20-100', 'time_range': '4-8', 'word_len': '5-7'},
        '14+': {'num_range': '50-200', 'time_range': '5-10', 'word_len': '6-9'}
    }
    params = age_params.get(age_group, age_params['9-11'])
    
    instructions = {
        'WordChainBuilder': f"Generate a {params['word_len']} letter word appropriate for age {age_group}. CRITICAL: scrambledLetters must contain EVERY letter from targetWord (if a letter appears twice in the word, it must appear twice in the array). Return JSON: {{ 'targetWord': 'WORD', 'scrambledLetters': ['W', 'O', 'R', 'D'] }} where scrambledLetters is the exact letters of targetWord in random order.",
        'TimeEstimator': f"Set targetSeconds based on difficulty: Easy={params['time_range'].split('-')[0]}, Medium={int(params['time_range'].split('-')[0]) + 2}, Hard={params['time_range'].split('-')[1]}.",
        'TaskSwitchSprint': "Generate 8-10 items. Each item: { 'shape': 'circle'|'square', 'color': 'blue'|'orange' }. Also set initialRule: 'COLOR'|'SHAPE'.",
        'NumberSenseDash': f"Generate two numbers 'left' and 'right' for comparison. Use range {params['num_range']} for this age group.",
        'VisualMathMatch': f"Create a math equation appropriate for age {age_group} (e.g. '15 + 7' or '3 x 4') and a list of 4 numeric 'options' with the 'correctValue'. Use numbers in range {params['num_range']}.",
        'PatternWatcher': "No extra data needed, game generates sequence internally. Just provide age-appropriate encouragement in question_text.",
        'FocusGuard': "Set stimulus to 'green' or 'red'.",
        'PlanAheadPuzzle': f"This is a GRID-BASED pathfinding puzzle game. Set level 1-3 based on difficulty and gridSize: 3 for age 6-8, 4 for 9-11, 5 for 12-14, 6 for 14+. The question_text should be simple like 'Reach the Star!' or 'Navigate to the goal!'. This is NOT an essay or written planning task - it's a visual puzzle where users move a ball through a grid.",
        'LetterFlipFrenzy': f"""Generate a reading comprehension question with exactly 4 word options appropriate for age {age_group}.
        
CRITICAL INSTRUCTION - FOLLOW THIS PROCESS EXACTLY:
1. FIRST: Generate 4 age-appropriate words (use {params['word_len']} letter words)
2. SECOND: Analyze these words for common properties (letters, positions, patterns)
3. THIRD: Create a question that AT LEAST ONE word can correctly answer
4. FOURTH: Set correct_option to the word that answers the question

Valid question patterns (choose ONE that matches your words):
- "Which word contains the letter 'X' as the second/third/fourth letter?" (verify one word has letter X at that position)
- "Which word starts with the letter 'X'?" (verify one word starts with X)
- "Which word ends with the letter 'X'?" (verify one word ends with X)
- "Which word has exactly N letters?" (verify one word has N letters)
- "Which word contains the letter 'X'?" (verify one word contains X anywhere)

VALIDATION CHECKLIST before returning:
✓ Did I generate exactly 4 words?
✓ Is there at least one word that correctly answers my question?
✓ Is correct_option set to a word that answers the question?
✓ Are all words age-appropriate ({params['word_len']} letters for {age_group})?

Example for age 6-8:
Words: ["edge", "moon", "star", "lake"]
Question: "Which word contains the letter 'd' as the second letter?"
Correct: "edge" (e-d-g-e, second letter is 'd')""",
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
        '9-11': {
            'easy': 'Straightforward, numbers up to 50, 4-5 letter words',
            'medium': 'Moderate challenge, numbers up to 100, 5-6 letter everyday words',
            'hard': 'Challenging, numbers over 100, 6-7 letter words, multi-step'
        },
        '12-14': {
            'easy': 'Basic level, numbers up to 100, 5-6 letter words',
            'medium': 'Grade-level challenge, larger numbers, 6-8 letter words',
            'hard': 'Advanced level, complex numbers, 8+ letter words, multi-step reasoning'
        },
        '14+': {
            'easy': 'Standard level, numbers up to 200, 6-7 letter words',
            'medium': 'Advanced challenge, large numbers, 7-9 letter complex words',
            'hard': 'Expert level, very large numbers, 9+ letter words, multi-step abstract reasoning'
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
        return generate_fallback_question(domain, difficulty, game_type, age_group)
    except Exception as e:
        print(f"❌ Gemini API failed: {type(e).__name__}: {str(e)}")
        return generate_fallback_question(domain, difficulty, game_type, age_group)


def generate_fallback_question(domain, difficulty, game_type, age_group='9-11'):
    """Generate varied fallback questions if Gemini fails"""
    import random
    
    # Age-appropriate word lists
    words_by_age = {
        '6-8': ['CAT', 'DOG', 'SUN', 'BED', 'HAT', 'CUP', 'BAT', 'PIG'],
        '9-11': ['MOON', 'TREE', 'BOOK', 'FISH', 'BIRD', 'STAR', 'BLUE', 'RAIN'],
        '12-14': ['PLANET', 'FOREST', 'GARDEN', 'RHYTHM', 'KNIGHT', 'ISLAND'],
        '14+': ['SYMPHONY', 'ASTRONOMY', 'TECHNIQUE', 'ATMOSPHERE', 'ARCHITECT']
    }
    
    # Age-appropriate number ranges
    num_ranges = {
        '6-8': (1, 10),
        '9-11': (10, 50),
        '12-14': (20, 100),
        '14+': (50, 200)
    }
    
    # Age-appropriate time targets
    time_ranges = {
        '6-8': (2, 4),
        '9-11': (3, 6),
        '12-14': (4, 8),
        '14+': (5, 10)
    }
    
    reading_words = words_by_age.get(age_group, words_by_age['9-11'])
    num_min, num_max = num_ranges.get(age_group, (10, 50))
    time_min, time_max = time_ranges.get(age_group, (3, 6))
    
    # Generate random number pairs appropriate for age
    math_pairs = [(random.randint(num_min, num_max), random.randint(num_min, num_max)) for _ in range(5)]
    
    # Generate age-appropriate math equations
    if age_group == '6-8':
        math_eqs = [(f'{a} + {b}', a+b) for a, b in [(random.randint(1, 5), random.randint(1, 5)) for _ in range(3)]]
    elif age_group == '14+':
        math_eqs = [
            (f'{a} × {b}', a*b) for a, b in [(random.randint(10, 20), random.randint(2, 9)) for _ in range(2)]
        ] + [(f'{a} + {b}', a+b) for a, b in [(random.randint(50, 100), random.randint(20, 80)) for _ in range(2)]]
    else:
        math_eqs = [
            (f'{a} + {b}', a+b) for a, b in [(random.randint(5, 20), random.randint(5, 20)) for _ in range(2)]
        ] + [(f'{a} × {b}', a*b) for a, b in [(random.randint(2, 10), random.randint(2, 5)) for _ in range(2)]]
    
    colors = ['green', 'red', 'blue', 'yellow']
    
    if domain == 'reading':
        if game_type == 'WordChainBuilder':
            word = random.choice(reading_words)
            # Ensure ALL letters from word are included
            letters = list(word)
            scrambled = letters.copy()
            random.shuffle(scrambled)
            return {
                'question_text': f'Unscramble these letters to make a word',
                'options': [word, word[::-1], word[1:] + word[0], word[-1] + word[:-1]],
                'correct_option': word,
                'game_data': {'targetWord': word, 'scrambledLetters': scrambled},
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
            target = random.randint(time_min, time_max)
            return {
                'question_text': f'Estimate {target} seconds!',
                'options': ['Start', 'Stop'],
                'correct_option': 'Stop',
                'game_data': {'targetSeconds': target},
                'domain': domain,
                'difficulty': difficulty,
                'game_type': game_type
            }
        elif game_type == 'VisualMathMatch' or difficulty == 'hard':
            eq, ans = random.choice(math_eqs)
            opts = [str(ans), str(ans+random.randint(1,5)), str(abs(ans-random.randint(1,5))), str(ans+random.randint(6,10))]
            random.shuffle(opts)
            return {
                'question_text': f'Solve: {eq}',
                'options': opts,
                'correct_option': str(ans),
                'game_data': {
                    'equation': eq,
                    'correctValue': ans,
                    'options': [int(o) for o in opts]
                },
                'domain': domain,
                'difficulty': difficulty,
                'game_type': 'VisualMathMatch'
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
                'game_type': 'NumberSenseDash'
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
        
        # Age-based grid size
        grid_sizes = {
            '6-8': 3,
            '9-11': 4,
            '12-14': 5,
            '14+': 6
        }
        grid_size = grid_sizes.get(age_group, 4)
        
        return {
            'question_text': f'Plan ahead! Solve this Level {level} puzzle.',
            'options': ['Start', 'Reset'],
            'correct_option': 'Start',
            'game_data': {'level': level, 'gridSize': grid_size},
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
