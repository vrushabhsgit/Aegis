"""Orchestrates question answering from retrieval through audit logging."""

from .models import Answer, Question


def answer_question(question: Question) -> Answer:
    """Answer a question. The retrieval/generation pipeline is a stub for now."""
    return Answer(
        text="The policy question-answering pipeline is not implemented yet.",
        sources=(),
        warning="No policy documents have been searched.",
    )
