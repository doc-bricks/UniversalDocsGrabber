"""
Vertragstestsuite für Windows Store Release Readiness in UniversalDocsGrabber.
"""

from scripts.check_store_readiness import check_store_readiness


def test_store_readiness_passes_without_findings():
    """Stellt sicher, dass alle Store-Readiness-Voraussetzungen erfüllt sind."""
    passed, findings = check_store_readiness()
    assert len(findings) == 0, f"Store-Readiness-Befunde aufgetreten: {findings}"
    assert len(passed) >= 10, f"Zu wenige Store-Readiness-Prüfungen: {len(passed)}"
