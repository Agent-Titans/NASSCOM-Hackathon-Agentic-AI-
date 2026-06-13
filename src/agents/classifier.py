"""
Classifier agent — Gemini-first for category (LLD), RAG fallback, keyword last.

RAG similar tickets inform resolution steps and Supervisor scoring but never
skip the Gemini classify call when the API is available.
"""
from __future__ import annotations

from typing import Optional

from src.agents.keyword_index import score_categories
from src.config.settings import get_settings
from src.clients.gemini_client import GeminiClient
from src.models.schemas import ClassificationResult, SanitizedText, SimilarTicketMatch

# Background "security policy" context must not alone justify Security category.
_SECURITY_INCIDENT_MARKERS = (
    "security incident",
    "siem",
    "dlp flagged",
    "dlp alert",
    "breach",
    "phishing",
    "malware",
    "ransomware",
    "ransom note",
    "compromised",
    "unauthorized access",
    "unauthorized rdp",
    "unauthorized login",
    "successful login from",
    "foreign ip",
    "unknown ip",
    "secret in log",
    "password in plain text",
    "pipeline log printed",
    "credential leak",
    "leaked password",
    "suspicious email",
    "secret access key",
    "api key",
    "accidentally pushed",
    "public github",
    "public repository",
    "exposed credential",
    "leaked secret",
    "purge the git",
    "git commit history",
    "unauthorized file access",
    "shouldn't access",
    "should not access",
    "inappropriate access",
    "privilege escalation",
    "ssl certificate",
    "certificate expiry",
    "certificate expires",
    "cert expiry",
    "tls certificate",
    "certificate authority",
)
_INFRA_CORE_MARKERS = (
    "docker",
    "hypervisor",
    "virtualization",
    "bios",
    "hvci",
    "virtual machine",
    "hardware-assisted",
)
_APP_CORE_MARKERS = ("compilation", "runtime error", "exception", "stack trace")
_NETWORK_OPS_MARKERS = (
    "whitelist",
    "white list",
    "allow my ip",
    "firewall",
    "vpn",
    "error 807",
    "cannot connect to vpn",
    "vpn client",
    "start my vpn",
    "vpn will not",
    "load balancer",
    "loadbalancer",
    "lb node",
    "reverse proxy",
    "gateway timeout",
    "504 gateway",
    "502 bad gateway",
    "traffic spike",
    "packet loss",
    "zscaler",
    "nginx",
    "f5",
    "mpls",
    "sd-wan",
    "bgp",
    "wan circuit",
    "ipsec",
    "dnssec",
    "dns resolution",
    "multicast storm",
    "802.1x",
    "nac quarantine",
    "globalprotect",
)
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
    "keyboard",
    "trackpad",
    "docking station",
    "headset",
    "microphone",
    "presentation remote",
    "presentation clicker",
    "usb receiver",
    "smart card",
    "piv card",
    "yubikey",
    "monitor arm",
    "monitor stand",
    "projector",
    "tape library",
    "robot arm",
    "label printer",
    "zebra printer",
    "webcam",
    "usb hub",
    "usb-c hub",
)
_APP_PLATFORM_MARKERS = (
    "tableau",
    "power bi",
    "onenote",
    "outlook",
    "microsoft teams",
    "teams live",
    "excel",
    "google chrome",
    "chrome extension",
    "sharepoint",
    "confluence",
    "jira board",
    "slack workflow",
    "webex",
    "zoom",
    "figma",
    "sap gui",
    "sap fiori",
    "visual studio code",
    "vs code",
    "acrobat",
    "splunk forwarder",
    "intune compliance",
    "notepad++",
    "autocad",
)
_APP_JOB_MARKERS = (
    "sync error",
    "not syncing",
    "refresh failed",
    "extract refresh",
    "dataset refresh",
    "gateway connection",
    "crashes opening",
    "crashes every",
    "macro file",
    "webhook",
    "live event",
    "extension",
    "screen share",
)
_DB_ENGINE_MARKERS = (
    "redis",
    "mongodb",
    "mongo atlas",
    "cassandra",
    "dynamodb",
    "elasticsearch",
    "snowflake",
    "influxdb",
    "postgres",
    "postgresql",
    "mysql",
    "sql server",
    "oracle rac",
    "connection pool exhausted",
    "always on",
    "streaming replica",
    "sentinel failover",
    "tempdb",
    "replication stopped",
    "failover loop",
)
_STORAGE_PLATFORM_MARKERS = (
    "netapp",
    "nfs mount",
    "stale file handle",
    "veeam",
    "san lun",
    "snapshot full",
    "snapshot reserve",
    "isilon",
    "backup chain",
    "backup exec",
    "vol_",
)
_ACCESS_PROVISIONING_MARKERS = (
    "ldap sync",
    "okta group",
    "password reset",
    "new hire",
    "new intern",
    "account creation",
    "offboarding",
    "shared mailbox",
    "break-glass",
    "service account password rotation",
    "conditional access",
    "contributor access",
    "license assignment",
    "contractor needs",
    "jira board access",
    "mailbox delegation",
)
_DB_INCIDENT_MARKERS = (
    "deadlock",
    "query timeout",
    "sql error",
    "replica lag",
    "schema migration",
    "database migration",
    "tablespace",
    "oracle error",
    "postgres error",
    "etl job",
    "etl ",
    "csv import",
    "data import",
    "bulk-copy",
    "bulk copy",
    "bcp",
    "import script",
    "slow import",
    "transaction log",
)

_VALID_CATEGORIES = frozenset(
    {
        "Infrastructure",
        "Application",
        "Security",
        "Database",
        "Storage",
        "Network",
        "Access Management",
    }
)


class ClassifierAgent:
    def __init__(self, gemini: GeminiClient | None = None) -> None:
        self.gemini = gemini or GeminiClient()

    @staticmethod
    def build_classification_text(
        sanitized: SanitizedText,
        *,
        title: str | None = None,
    ) -> str:
        """Full incident context for Gemini + reconcile (title carries strong signals)."""
        body = (sanitized.text or "").strip()
        head = (title or "").strip()
        if head and body:
            return f"{head}\n{body}"
        return head or body

    def classify(
        self,
        sanitized: SanitizedText,
        similar: Optional[SimilarTicketMatch] = None,
        *,
        title: str | None = None,
    ) -> ClassificationResult:
        classify_text = self.build_classification_text(sanitized, title=title)
        if sanitized.blocked or not classify_text:
            return ClassificationResult(
                use_case_category="Security",
                subcategory="policy",
                confidence_hint="low",
                source="gemini_unavailable",
            )

        parsed = self.gemini.classify_ticket(classify_text)
        if parsed:
            cat = parsed.get("use_case_category", "Application")
            if cat not in _VALID_CATEGORIES:
                cat = "Application"
            cat = self._finalize_category(cat, classify_text)
            hint = parsed.get("confidence_hint", "medium")
            if hint not in ("low", "medium", "high"):
                hint = "medium"
            if (
                similar
                and similar.similarity_score >= get_settings().rag_sim_medium
                and similar.classification.use_case_category != cat
            ):
                hint = "low"
            return ClassificationResult(
                use_case_category=cat,
                subcategory=parsed.get("subcategory"),
                confidence_hint=hint,
                source="gemini",
            )

        if (
            similar
            and similar.similarity_score >= get_settings().rag_sim_medium
        ):
            cat = self._finalize_category(
                similar.classification.use_case_category, classify_text
            )
            return ClassificationResult(
                use_case_category=cat,
                subcategory=similar.classification.subcategory or "similar_ticket",
                confidence_hint=similar.classification.confidence_hint,
                source="rag",
            )

        return self._keyword_fallback(classify_text)

    @staticmethod
    def _finalize_category(category: str, text: str) -> str:
        """Promote true security incidents, then apply failure-owner reconcile rules."""
        lower = text.lower()
        if any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            return "Security"
        category = ClassifierAgent._reconcile_access_provisioning_priority(
            category, text
        )
        category = ClassifierAgent._reconcile_app_platform_priority(category, text)
        category = ClassifierAgent._reconcile_db_engine_priority(category, text)
        category = ClassifierAgent._reconcile_storage_platform_priority(category, text)
        category = ClassifierAgent._reconcile_hardware_priority(category, text)
        category = ClassifierAgent._reconcile_network_ops_priority(category, text)
        category = ClassifierAgent._reconcile_database_ops_priority(category, text)
        return ClassifierAgent._reconcile_security_false_positive(category, text)

    @staticmethod
    def _reconcile_access_provisioning_priority(category: str, text: str) -> str:
        """Identity provisioning beats app/DB when no active security incident."""
        lower = text.lower()
        if any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            return category
        if not any(marker in lower for marker in _ACCESS_PROVISIONING_MARKERS):
            return category
        if category in ("Application", "Database", "Network"):
            return "Access Management"
        return category

    @staticmethod
    def _reconcile_app_platform_priority(category: str, text: str) -> str:
        """Named app/client failures → Application over DB, Access, or Network."""
        lower = text.lower()
        if not any(marker in lower for marker in _APP_PLATFORM_MARKERS):
            return category
        if any(marker in lower for marker in _ACCESS_PROVISIONING_MARKERS):
            return category
        if any(marker in lower for marker in _DB_ENGINE_MARKERS):
            if not any(marker in lower for marker in _APP_JOB_MARKERS):
                return category
        if category in (
            "Database",
            "Storage",
            "Access Management",
            "Network",
            "Infrastructure",
        ):
            return "Application"
        return category

    @staticmethod
    def _reconcile_db_engine_priority(category: str, text: str) -> str:
        """Database/cache engine outages → Database over Application or Network."""
        lower = text.lower()
        if not any(marker in lower for marker in _DB_ENGINE_MARKERS):
            return category
        if any(marker in lower for marker in _APP_PLATFORM_MARKERS) and any(
            marker in lower for marker in _APP_JOB_MARKERS
        ):
            return category
        if category in ("Application", "Network"):
            return "Database"
        return category

    @staticmethod
    def _reconcile_storage_platform_priority(category: str, text: str) -> str:
        """NAS/backup/SAN platform issues → Storage (physical tape library → hardware)."""
        lower = text.lower()
        if "tape library" in lower or (
            "robot arm" in lower and "jammed" in lower
        ):
            return "Infrastructure"
        if "san lun" in lower and category == "Database":
            return "Storage"
        if not any(marker in lower for marker in _STORAGE_PLATFORM_MARKERS):
            return category
        if category in ("Application", "Database"):
            return "Storage"
        return category

    @staticmethod
    def _reconcile_hardware_priority(category: str, text: str) -> str:
        """Charger/battery/peripheral issues are Infrastructure, not Network."""
        lower = text.lower()
        if not any(marker in lower for marker in _HARDWARE_MARKERS):
            return category
        if any(marker in lower for marker in _NETWORK_OPS_MARKERS):
            return category
        if category in ("Network", "Application", "Database"):
            return "Infrastructure"
        if any(marker in lower for marker in _APP_PLATFORM_MARKERS):
            return category
        return category

    @staticmethod
    def _reconcile_network_ops_priority(category: str, text: str) -> str:
        """
        Firewall/VPN/IP whitelist requests are Network ops even when SQL is mentioned.
        """
        lower = text.lower()
        if not any(marker in lower for marker in _NETWORK_OPS_MARKERS):
            return category
        if any(marker in lower for marker in _DB_INCIDENT_MARKERS):
            return category
        if category in ("Database", "Security", "Application", "Infrastructure"):
            return "Network"
        return category

    @staticmethod
    def _reconcile_database_ops_priority(category: str, text: str) -> str:
        """ETL/import/SQL engine failures are Database even when described as jobs or scripts."""
        lower = text.lower()
        if not any(marker in lower for marker in _DB_INCIDENT_MARKERS):
            return category
        if any(marker in lower for marker in _NETWORK_OPS_MARKERS):
            return category
        if any(marker in lower for marker in _STORAGE_PLATFORM_MARKERS) or "san lun" in lower:
            return category
        if category in ("Application", "Storage"):
            return "Database"
        return category

    @staticmethod
    def _reconcile_security_false_positive(category: str, text: str) -> str:
        """
        Post-Gemini safety net: downgrade contextual Security false-positives.

        Example: Docker/hypervisor failure mentioning 'security policy updates'
        must stay Infrastructure/Application, not Security (Hand 3 kill switch).
        """
        if category != "Security":
            return category
        lower = text.lower()
        if any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            return category
        if any(marker in lower for marker in _INFRA_CORE_MARKERS):
            return "Infrastructure"
        if any(marker in lower for marker in _APP_CORE_MARKERS):
            return "Application"
        return category

    @staticmethod
    def _keyword_fallback(text: str) -> ClassificationResult:
        ranked = score_categories(text)
        cat = ranked[0][0] if ranked else "Application"
        if cat not in _VALID_CATEGORIES:
            cat = "Application"
        score = ranked[0][1] if ranked else 0.0
        cat = ClassifierAgent._finalize_category(cat, text)
        hint = "high" if cat == "Security" else ("medium" if score >= 0.5 else "low")
        return ClassificationResult(
            use_case_category=cat,
            subcategory="keyword",
            confidence_hint=hint,
            source="keyword",
        )
