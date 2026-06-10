"""Topic + title overlap checks so weak RAG hits do not drive wrong resolutions."""
from __future__ import annotations

from src.models.schemas import ClassificationResult, ResolutionResult, SimilarTicketMatch
from src.services.semantic_similarity import stemmed_jaccard

_HARDWARE_MARKERS = (
    "charger",
    "power adapter",
    "power cable",
    "power brick",
    "battery",
    "not charging",
    "won't charge",
    "wont charge",
    "doesn't charge",
    "doesnt charge",
    "replace laptop",
    "broken screen",
    "cracked screen",
    "keyboard",
    "trackpad",
    "touchpad",
    "docking station",
    "dock station",
    "monitor cable",
    "display port",
    "hdmi port",
    "usb port broken",
)

_NETWORK_MARKERS = (
    "vpn",
    "wi-fi",
    "wifi",
    "wireless",
    "dns",
    "firewall",
    "internet",
    "network diagnostic",
    "rejoin wi-fi",
    "no internet",
    "cannot connect to vpn",
    "unable to connect to vpn",
)

_PLATFORM_MARKERS = (
    "airflow",
    "scheduler",
    "dag run",
    "task log",
    "job log",
    "worker log",
    "audit log",
    "kubernetes",
    "kubectl",
)

_ACCESS_MARKERS = (
    "password reset",
    "forgot password",
    "mfa",
    "authenticator",
    "locked out",
    "account locked",
)

_CATEGORY_TOPICS: dict[str, frozenset[str]] = {
    "Network": frozenset({"network"}),
    "Infrastructure": frozenset({"hardware"}),
    "Access Management": frozenset({"access"}),
}

_CONFLICTING_TOPIC_PAIRS = (
    (frozenset({"hardware"}), frozenset({"network"})),
    (frozenset({"hardware"}), frozenset({"access"})),
    (frozenset({"network"}), frozenset({"access"})),
)


def topic_buckets(text: str) -> set[str]:
    """Coarse topic labels detected in free text."""
    lower = text.lower()
    buckets: set[str] = set()
    if any(marker in lower for marker in _HARDWARE_MARKERS):
        buckets.add("hardware")
    if any(marker in lower for marker in _NETWORK_MARKERS):
        buckets.add("network")
    if any(marker in lower for marker in _ACCESS_MARKERS):
        buckets.add("access")
    if any(marker in lower for marker in _PLATFORM_MARKERS):
        buckets.add("platform")
    return buckets


def _topics_conflict(query_topics: set[str], match_topics: set[str]) -> bool:
    if not query_topics or not match_topics:
        return False
    if query_topics & match_topics:
        return False
    for left, right in _CONFLICTING_TOPIC_PAIRS:
        if (query_topics & left and match_topics & right) or (
            query_topics & right and match_topics & left
        ):
            return True
    return False


def _is_user_ticket(similar: SimilarTicketMatch) -> bool:
    ticket_id = similar.ticket_id.lower()
    return not (
        ticket_id.startswith("kb-")
        or ticket_id.startswith("rag-")
        or ticket_id.startswith("ent-")
    )


def is_rag_relevant(query_text: str, similar: SimilarTicketMatch) -> tuple[bool, str]:
    """
    Return (relevant, reason).

    Rejects matches where the prior ticket topic/title does not align with the query
    (e.g. VPN playbook for a laptop charger request).
    """
    query = query_text.strip()
    if not query:
        return True, "no_query"

    match_text = similar.title.strip()
    query_topics = topic_buckets(query)
    match_topics = topic_buckets(match_text)
    category_topics = _CATEGORY_TOPICS.get(
        similar.classification.use_case_category, frozenset()
    )
    match_topics |= set(category_topics)

    if _topics_conflict(query_topics, match_topics):
        return False, "topic_mismatch"

    title_overlap = stemmed_jaccard(query, match_text)
    min_overlap = 0.10
    if _is_user_ticket(similar):
        min_overlap = 0.12

    if title_overlap < min_overlap and not (query_topics & match_topics):
        return False, "low_title_overlap"

    return True, "relevant"


def is_reference_relevant(
    query_text: str,
    *,
    ticket_id: str,
    title: str,
    score: float,
    source: str,
    category: str = "Application",
) -> bool:
    """Whether a citation link should be shown for this ticket query."""
    similar = SimilarTicketMatch(
        ticket_id=ticket_id,
        title=title,
        similarity_score=score,
        classification=ClassificationResult(use_case_category=category, source="rag"),
        resolution=ResolutionResult(),
        department_queue="",
        source=source,
    )
    return is_rag_relevant(query_text, similar)[0]
