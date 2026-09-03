"""ReturnSentinel AI Audit Explanation Module.

Provides asynchronous, LLM-generated plain-English explanations of risk predictions
and policy decisions using Google Gemini.
"""

from audit.audit_generator import (
    build_audit_prompt,
    generate_audit_explanation,
    generate_and_persist_audit,
)

__all__ = [
    "build_audit_prompt",
    "generate_audit_explanation",
    "generate_and_persist_audit",
]
