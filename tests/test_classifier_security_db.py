"""Security and Database classification overrides (Pallavi demo gaps)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.classifier import ClassifierAgent


def test_unauthorized_file_access_promoted_to_security():
    text = (
        "Unauthorized file access\n"
        "User reported being able to view folders they shouldn't access."
    )
    cat = ClassifierAgent._finalize_category("Access Management", text)
    assert cat == "Security"


def test_certificate_expiry_promoted_to_security():
    text = (
        "Certificate expiry warning\n"
        "SSL certificate for internal dev portal expires in 3 days."
    )
    cat = ClassifierAgent._finalize_category("Application", text)
    assert cat == "Security"


def test_slow_etl_import_promoted_to_database():
    text = (
        "Slow data import\n"
        "ETL job for CSV import is taking 4 hours instead of 30 mins."
    )
    cat = ClassifierAgent._finalize_category("Application", text)
    assert cat == "Database"


def test_redis_cluster_promoted_to_database():
    text = "Redis cluster hitting maxmemory limit. Cache eviction causing session drops."
    cat = ClassifierAgent._finalize_category("Application", text)
    assert cat == "Database"


def test_power_bi_gateway_stays_application():
    text = (
        "Power BI data gateway shows offline. Scheduled dataset refresh jobs failing."
    )
    cat = ClassifierAgent._finalize_category("Network", text)
    assert cat == "Application"


def test_security_incident_vpn_termination_is_security():
    text = (
        "Security incident: former employee VPN session still active after termination."
    )
    cat = ClassifierAgent._finalize_category("Network", text)
    assert cat == "Security"


def test_smart_card_reader_is_infrastructure():
    text = "PIV smart card reader not detected on USB ports after Windows update."
    cat = ClassifierAgent._finalize_category("Application", text)
    assert cat == "Infrastructure"


def test_mpls_circuit_is_network_not_hardware():
    text = "MPLS WAN circuit to primary datacenter is completely down."
    cat = ClassifierAgent._finalize_category("Infrastructure", text)
    assert cat == "Network"


def test_ldap_sync_stays_access_management():
    text = "LDAP directory sync to Atlassian Cloud failing. New hires not in Jira."
    cat = ClassifierAgent._finalize_category("Application", text)
    assert cat == "Access Management"
