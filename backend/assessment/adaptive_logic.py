"""
Adaptive question delivery logic.
Rule-based fallback when ML-based AQA is not ready.
"""
from .models import Question, UserResponse


def get_next_difficulty(current_difficulty: str, correct: bool, response_time_ms: int) -> str:
    """
    Determine the next difficulty level based on performance.
    
    Rules:
    - Wrong answer or slow (>2000ms) → easier difficulty
    - Right answer and fast (<1500ms) → harder difficulty
    - Otherwise → same difficulty
    """
    difficulty_levels = ['easy', 'medium', 'hard']
    current_index = difficulty_levels.index(current_difficulty) if current_difficulty in difficulty_levels else 1
    
    # Wrong or slow → easier
    if not correct or response_time_ms > 2000:
        new_index = max(0, current_index - 1)
    # Right and fast → harder
    elif correct and response_time_ms < 1500:
        new_index = min(2, current_index + 1)
    else:
        new_index = current_index
    
    return difficulty_levels[new_index]


def get_next_domain(session_id: str, current_domain: str = None) -> str:
    """
    Rotate through domains for balanced assessment.
    """
    domains = ['reading', 'writing', 'math', 'attention']
    
    # Get responses for this session to determine domain rotation
    responses = UserResponse.objects.filter(session_id=session_id).order_by('-answered_at')
    
    if not responses.exists():
        return 'reading'  # Start with reading
    
    # Count responses per domain
    domain_counts = {}
    for domain in domains:
        domain_counts[domain] = responses.filter(domain=domain).count()
    
    # Return the domain with fewest responses
    min_count = min(domain_counts.values())
    for domain in domains:
        if domain_counts[domain] == min_count:
            return domain
    
    return 'reading'


def get_adaptive_question(
    session_id: str,
    last_question_id: str = None,
    correct: bool = None,
    response_time_ms: int = None
) -> Question:
    """
    Get the next adaptive question based on user performance.
    Tries ML model first, falls back to rule-based logic.
    
    Args:
        session_id: Current session ID
        last_question_id: ID of the last question answered
        correct: Whether the last answer was correct
        response_time_ms: Response time in milliseconds
    
    Returns:
        Next Question object or None if no questions available
    """
    # Get answered question IDs for this session
    answered_ids = UserResponse.objects.filter(
        session_id=session_id
    ).values_list('question_id', flat=True)
    
    # Try ML model first
    try:
        from .ml_utils import get_next_question_ml
        next_domain, next_difficulty = get_next_question_ml(
            session_id,
            last_question_id,
            correct,
            response_time_ms
        )
    except Exception as e:
        # Fallback to rule-based logic
        print(f"⚠️  ML question generation failed, using rule-based: {e}")
        
        # Determine difficulty for next question
        if last_question_id and correct is not None and response_time_ms is not None:
            try:
                last_question = Question.objects.get(question_id=last_question_id)
                next_difficulty = get_next_difficulty(
                    last_question.difficulty,
                    correct,
                    response_time_ms
                )
            except Question.DoesNotExist:
                next_difficulty = 'medium'
        else:
            # First question - start with easy
            next_difficulty = 'easy'
        
        # Get next domain
        next_domain = get_next_domain(session_id, None)
    
    # Try to find a question matching criteria
    question = Question.objects.filter(
        domain=next_domain,
        difficulty=next_difficulty
    ).exclude(question_id__in=answered_ids).first()
    
    # Fallback: try any difficulty in the domain
    if not question:
        question = Question.objects.filter(
            domain=next_domain
        ).exclude(question_id__in=answered_ids).first()
    
    # Fallback: try any domain with target difficulty
    if not question:
        question = Question.objects.filter(
            difficulty=next_difficulty
        ).exclude(question_id__in=answered_ids).first()
    
    # Final fallback: any unanswered question
    if not question:
        question = Question.objects.exclude(question_id__in=answered_ids).first()
    
    return question
