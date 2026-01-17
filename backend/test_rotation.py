
import sys
import os
from unittest.mock import MagicMock

# Mock google.genai before importing service
mock_genai = MagicMock()
sys.modules['google.genai'] = mock_genai

# Add project root to path
sys.path.append(os.getcwd())

from backend.assessment.gemini_question_service import determine_next_parameters

def simulate_rotation(iterations=100):
    counts = {'reading': 0, 'math': 0, 'attention': 0, 'writing': 0}
    current_diff = 'easy'
    
    for i in range(iterations):
        # Always assume correct answer for simple rotation check
        domain, diff = determine_next_parameters(
            True, 500, current_diff, counts, 1.0, '9-11'
        )
        counts[domain] += 1
        current_diff = diff
    
    print(f"Results after {iterations} iterations:")
    for domain, count in counts.items():
        print(f"  {domain}: {count} ({count/iterations*100:.1f}%)")

if __name__ == "__main__":
    simulate_rotation(100)
    print("-" * 20)
    simulate_rotation(100)
