"""
Configuration des prix des API Claude.
"""

# Prix en USD par million de tokens
CLAUDE_PRICING = {
    "claude-3-5-haiku-20241022": {
        "input": 0.80,  # $0.80 per million input tokens
        "output": 4,  # $4 per million output tokens
    },
    "claude-3-haiku-20240307": {
        "input": 0.25,  # $0.25 per million input tokens
        "output": 1.25,  # $1.25 per million output tokens
    },
}

# Estimation des tokens
TOKEN_ESTIMATION = {
    "chars_per_token": 4,  # Approximation : 4 caractères = 1 token
    "haiku_output_tokens": 150,  # Estimation tokens pour un haïku généré
    "prompt_overhead_tokens": 50,  # Tokens supplémentaires du prompt système
}
