"""Guardrail security exceptions — halt pipeline before downstream LLM agents."""


class SecurityGuardrailException(Exception):
    """
    Raised when ticket text fails injection / override checks.

    The orchestrator must catch this and force Hand 3 without calling
    Classifier, Router, or Resolver (LLD: unsafe content → human queue).
    """

    def __init__(self, reason: str, *, layer: str = "regex") -> None:
        self.reason = reason
        self.layer = layer
        super().__init__(reason)
