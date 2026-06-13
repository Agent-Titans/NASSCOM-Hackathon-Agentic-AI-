"""Tests for outbound notification email routing."""
from src.config.notification_emails import (
    ASSIGNEE_NOTIFICATION_EMAIL,
    REQUESTER_NOTIFICATION_EMAIL,
    SECOPS_NOTIFICATION_EMAIL,
    assignee_notification_email,
    extract_contact_email,
    requester_notification_email,
)


def test_requester_maps_to_demo_inbox():
    assert requester_notification_email("pallavi@user") == REQUESTER_NOTIFICATION_EMAIL


def test_requester_uses_contact_email_from_description():
    desc = "VPN broken\n\nContact email: real.person@company.com"
    assert requester_notification_email("pallavi@user", desc) == "real.person@company.com"


def test_assignee_maps_to_agent_inbox():
    assert assignee_notification_email("subbu@employee", "Software") == ASSIGNEE_NOTIFICATION_EMAIL


def test_secops_assignee_maps_to_secops_inbox():
    assert assignee_notification_email("narsimha@employee", "SecOps") == SECOPS_NOTIFICATION_EMAIL


def test_extract_contact_email():
    assert extract_contact_email("Issue\n\nContact email: a@b.co") == "a@b.co"
