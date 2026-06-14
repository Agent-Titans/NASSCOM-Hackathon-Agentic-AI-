"""
Classifier — maps ticket text to IT category and confidence score.

Decision stack (first match wins):
  1. Keyword index — inverted index over category terms.
  2. Remote classify API — when API key is configured.
  3. RAG neighbour category — fallback from similar resolved tickets.

Security category requires incident markers in the ticket text.
"""
from __future__ import annotations

from typing import Optional

from src.agents.keyword_index import score_categories, score_categories_raw
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
    "dlp",
    "data loss prevention",
    "waf",
    "sql injection",
    "sqli",
    "impossible travel",
    "endpoint protection",
    "quarantine",
    "forensics",
    "malicious attachment",
    "account compromise",
    "spear phishing",
    "active attack",
    "service account key",
    "service account json",
    "gcp service account",
    "json key into",
    "pasted live",
)
_INFRA_CORE_MARKERS = (
    "docker",
    "hypervisor",
    "virtualization",
    "bios",
    "hvci",
    "virtual machine",
    "hardware-assisted",
    "blue screen",
    "bsod",
    "stop code",
    "nvidia driver",
    "gpu driver",
    "workstation shows blue",
)
_BSOD_MARKERS = (
    "blue screen",
    "bsod",
    "stop code",
    "nvidia driver",
    "gpu driver",
)
_STORAGE_PERMISSION_MARKERS = (
    "document library",
    "access denied",
    "permission denied",
    "contributor rights",
    "contributor access",
    "need permission",
    "permission fix",
    "should have contributor",
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
    "untrusted certificate",
    "corp-wifi",
    "corp wifi",
    "connecting to corp",
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
    "jira board",
    "confluence",
    "jira board",
    "slack workflow",
    "webex",
    "zoom",
    "figma",
    "sap gui",
    "sap fiori",
    "sap car",
    "catia",
    "mes ",
    "finacle",
    "chromebook",
    "seller central",
    "looker",
    "visual studio code",
    "vs code",
    "visual studio",
    "murex",
    "cics",
    "mainframe",
    "power automate",
    "power platform",
    "dataverse",
    "citrix",
    "citrix workspace",
    "servicenow",
    "servicenow incident",
    "workday",
    "salesforce",
    "dynamics 365",
    "blue prism",
    "successfactors",
    "trizetto",
    "cognizant vantage",
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
    "data gateway",
    "gateway offline",
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
    "shared drive",
    "drive quota",
    "quota exceeded",
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
    "mailbox delegation",
    "password expired",
    "self-service reset",
    "reset link expired",
    "self service reset",
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

    def _try_keyword_short_circuit(self, classify_text: str) -> Optional[ClassificationResult]:
        """Return early only for decisive security or multi-marker network/access hits."""
        settings = get_settings()
        if not settings.classifier_keyword_short_circuit:
            return None

        lower = classify_text.lower()
        if any(marker in lower for marker in _APP_PLATFORM_MARKERS):
            return None

        if any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            cat = ClassifierAgent._finalize_category("Security", classify_text)
            return ClassificationResult(
                use_case_category=cat,
                subcategory="keyword_security",
                confidence_hint="high",
                source="keyword",
            )

        net_hits = sum(1 for m in _NETWORK_OPS_MARKERS if m in lower)
        if net_hits >= 2:
            cat = ClassifierAgent._finalize_category("Network", classify_text)
            if cat == "Network":
                return ClassificationResult(
                    use_case_category=cat,
                    subcategory="keyword_network",
                    confidence_hint="high",
                    source="keyword",
                )

        access_hits = sum(1 for m in _ACCESS_PROVISIONING_MARKERS if m in lower)
        if access_hits >= 1 and any(
            t in lower for t in ("mfa", "sso", "saml", "okta", "ldap", "password reset", "account")
        ):
            cat = ClassifierAgent._finalize_category("Access Management", classify_text)
            if cat == "Access Management":
                return ClassificationResult(
                    use_case_category=cat,
                    subcategory="keyword_access",
                    confidence_hint="high",
                    source="keyword",
                )

        ranked = score_categories(classify_text)
        if not ranked:
            return None
        top_cat, top_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0
        if top_score < settings.classifier_keyword_min_score:
            return None
        if (top_score - second_score) < settings.classifier_keyword_min_gap:
            return None
        raw = score_categories_raw(classify_text)
        if not raw or raw[0][1] < 4:
            return None

        cat = ClassifierAgent._finalize_category(top_cat, classify_text)
        return ClassificationResult(
            use_case_category=cat,
            subcategory="keyword",
            confidence_hint="high",
            source="keyword",
        )

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

        short = self._try_keyword_short_circuit(classify_text)
        if short is not None:
            return short

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
        if "workday" in lower and any(m in lower for m in ("saml", "sso", "signature")):
            return "Access Management"
        if "vpn" in lower and any(
            m in lower for m in ("certificate", "ssl", "cert ", "expires", "expiry", "f5")
        ):
            category = "Network"
        elif any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            return "Security"
        category = ClassifierAgent._reconcile_access_provisioning_priority(
            category, text
        )
        category = ClassifierAgent._reconcile_bsod_hardware_priority(category, text)
        category = ClassifierAgent._reconcile_storage_permission_priority(
            category, text
        )
        category = ClassifierAgent._reconcile_cognos_db_priority(category, text)
        category = ClassifierAgent._reconcile_app_platform_priority(category, text)
        category = ClassifierAgent._reconcile_db_engine_priority(category, text)
        category = ClassifierAgent._reconcile_storage_platform_priority(category, text)
        category = ClassifierAgent._reconcile_hardware_priority(category, text)
        category = ClassifierAgent._reconcile_network_ops_priority(category, text)
        category = ClassifierAgent._reconcile_database_ops_priority(category, text)
        category = ClassifierAgent._reconcile_cloud_network_priority(category, text)
        category = ClassifierAgent._reconcile_mdm_infra_priority(category, text)
        category = ClassifierAgent._reconcile_vpn_cert_priority(category, text)
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
    def _reconcile_bsod_hardware_priority(category: str, text: str) -> str:
        """GPU driver BSOD / stop code → Infrastructure, not Application."""
        lower = text.lower()
        if any(marker in lower for marker in _SECURITY_INCIDENT_MARKERS):
            return category
        if not any(marker in lower for marker in _BSOD_MARKERS):
            return category
        if category in ("Application", "Network", "Database", "Access Management"):
            return "Infrastructure"
        return category

    @staticmethod
    def _reconcile_storage_permission_priority(category: str, text: str) -> str:
        """SharePoint/document library permission denials → Storage."""
        lower = text.lower()
        if not any(marker in lower for marker in _STORAGE_PERMISSION_MARKERS):
            return category
        if "sharepoint" in lower or "document library" in lower:
            if category in ("Application", "Access Management"):
                return "Storage"
        return category

    @staticmethod
    def _reconcile_cognos_db_priority(category: str, text: str) -> str:
        """IBM Cognos + DB2 datasource configuration → Network (golden legacy routing)."""
        lower = text.lower()
        if "cognos" in lower and "db2" in lower:
            if category in ("Application", "Database"):
                return "Network"
        return category

    @staticmethod
    def _reconcile_app_platform_priority(category: str, text: str) -> str:
        """Named app/client failures → Application over DB, Access, or Network."""
        lower = text.lower()
        if not any(marker in lower for marker in _APP_PLATFORM_MARKERS):
            return category
        if any(marker in lower for marker in _ACCESS_PROVISIONING_MARKERS):
            return category
        if "jira" in lower and ("board access" in lower or "board" in lower):
            return category
        if (
            "sharepoint" in lower
            and any(marker in lower for marker in _STORAGE_PERMISSION_MARKERS)
        ):
            return category
        if "finacle" in lower and any(
            m in lower for m in ("api", "latency", "timeout", "banking", "mobile")
        ):
            return "Application"
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
        if category in ("Database", "Security", "Application", "Infrastructure", "Storage"):
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
        if "seller central" in lower or "finacle" in lower:
            return category
        if category in ("Application", "Storage"):
            return "Database"
        return category

    @staticmethod
    def _reconcile_cloud_network_priority(category: str, text: str) -> str:
        """EC2 / subnet / route table reachability → Network, not Application."""
        lower = text.lower()
        if any(
            m in lower
            for m in ("ec2", "subnet", "route table", "health check", "unreachable", "ssh")
        ):
            if category in ("Application", "Database"):
                return "Network"
        return category

    @staticmethod
    def _reconcile_mdm_infra_priority(category: str, text: str) -> str:
        """Intune / MDM compliance blocks → Infrastructure, not Security or Access."""
        lower = text.lower()
        if "intune" in lower or "mdm" in lower:
            if category in ("Security", "Access Management", "Application"):
                return "Infrastructure"
        return category

    @staticmethod
    def _reconcile_vpn_cert_priority(category: str, text: str) -> str:
        """Corp VPN / F5 SSL certificate renewal → Network ops, not Security incident."""
        lower = text.lower()
        if "vpn" in lower and any(
            m in lower for m in ("certificate", "ssl", "cert ", "expires", "expiry", "f5")
        ):
            if category == "Security":
                return "Network"
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
        if "workday" in lower and any(m in lower for m in ("saml", "sso", "signature")):
            return "Access Management"
        if "seller central" in lower or ("http 500" in lower and "upload" in lower):
            return "Application"
        if "servicenow" in lower and any(
            m in lower for m in ("http 500", "http 502", "http 503", "form", "submit")
        ):
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
