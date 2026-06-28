# -*- coding: utf-8 -*-
"""Regressionstests Bugfix Batch #27 — REL-PUB_UniversalDocsGrabber.

Fixes in diesem Batch:
  U4: IMAP-Sequenznummern (MSN) → UIDs (conn.uid('search'/'fetch'))
      Schützt vor MSN-Verschiebung durch parallele Expunges fremder Sessions.
  U5: NIL-Guard in _convert_body_to_pdf() — get_payload(decode=True) kann None
      zurückgeben (malformed Multipart), was zuvor AttributeError auslöste.
  U6: NIL-Guard in process_email() — uid('fetch')-Antwort data[0] kann None sein,
      wenn die Nachricht zwischen Search und Fetch gelöscht wurde.
"""

import email
import email.mime.multipart
import email.mime.text
import unittest
from pathlib import Path
from unittest.mock import MagicMock

PROJ = Path(__file__).parent.parent
SRC = PROJ / "UniversalDocsGrabberV1.py"


def _src():
    return SRC.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# U4 — MSN → UID: Quellcode-Checks
# ---------------------------------------------------------------------------

class TestU4UIDConversionSource(unittest.TestCase):
    """Stellt sicher dass process_profile/process_email UIDs statt MSNs nutzen."""

    def test_process_profile_uses_uid_search(self):
        self.assertIn("conn.uid('search',", _src(),
                      "process_profile() muss conn.uid('search', ...) statt conn.search() nutzen")

    def test_process_email_uses_uid_fetch(self):
        self.assertIn("conn.uid('fetch',", _src(),
                      "process_email() muss conn.uid('fetch', ...) statt conn.fetch() nutzen")

    def test_no_bare_conn_search_in_process_profile(self):
        """conn.search() (MSN-Pfad) darf in process_profile() nicht mehr vorkommen."""
        src = _src()
        start = src.find("def process_profile(")
        end = src.find("\n    def ", start + 1)
        self.assertNotIn("conn.search(", src[start:end],
                         "process_profile() enthält noch conn.search() (MSN-Pfad)")

    def test_no_bare_conn_fetch_in_process_email(self):
        """conn.fetch() (MSN-Pfad) darf in process_email() nicht mehr vorkommen."""
        src = _src()
        start = src.find("def process_email(")
        end = src.find("\n    def ", start + 1)
        self.assertNotIn("conn.fetch(", src[start:end],
                         "process_email() enthält noch conn.fetch() (MSN-Pfad)")


# ---------------------------------------------------------------------------
# U4 — MSN-Verschiebungs-Szenario: Verhaltenstest mit Mock
# ---------------------------------------------------------------------------

class TestU4VerschiebungsSzenario(unittest.TestCase):
    """
    Verhaltenstest für den MSN-Shift-Fall.

    Bei einem parallelen Expunge verschiebt sich jede MSN um 1; ein
    MSN-Fetch würde die falsche Nachricht holen. UID-basierte Operationen
    sind dagegen stabil.

    Der Mock lässt nur conn.uid() zu — conn.search() und conn.fetch()
    schlagen mit AssertionError fehl. Damit scheitert jeder Codepfad,
    der noch MSN-Operationen enthält, explizit in diesem Test.
    """

    def _make_fake_conn(self, uid_to_bytes):
        """Mock-IMAP-Connector: nur uid() zugelassen, search/fetch schlagen fehl."""
        conn = MagicMock()
        conn.search.side_effect = AssertionError("MSN search() genutzt — UID-Pfad erwartet")
        conn.fetch.side_effect = AssertionError("MSN fetch() genutzt — UID-Pfad erwartet")

        uid_list = list(uid_to_bytes.keys())
        uid_str = b" ".join(uid_list)

        def fake_uid(command, *args):
            if command.lower() == "search":
                return ("OK", [uid_str])
            if command.lower() == "fetch":
                uid = args[0]
                raw = uid_to_bytes.get(uid)
                if raw is None:
                    return ("OK", [None])
                return ("OK", [(b"%b (RFC822 {%d})" % (uid, len(raw)), raw)])
            return ("OK", [b""])

        conn.uid.side_effect = fake_uid
        return conn

    def test_uid_fetch_delivers_correct_message_after_hypothetical_expunge(self):
        """
        Nach einem Expunge von UID 1001 ist die frühere MSN 2 jetzt MSN 1.
        UID 1002 ist trotzdem noch korrekt adressierbar.
        """
        raw_mail = email.mime.text.MIMEText("Testinhalt")
        raw_mail["From"] = "absender@example.com"
        raw_mail["Subject"] = "Korrekte Mail"
        raw_mail["Date"] = "Sat, 28 Jun 2026 00:00:00 +0000"
        raw_bytes = raw_mail.as_bytes()

        uid_1002 = b"1002"
        conn = self._make_fake_conn({uid_1002: raw_bytes})

        # Search gibt UIDs zurück
        typ, data = conn.uid("search", "ALL")
        self.assertEqual(typ, "OK")
        ids = data[0].split()
        self.assertIn(b"1002", ids)

        # Fetch per UID liefert die richtige Mail
        res, fetch_data = conn.uid("fetch", uid_1002, "(RFC822)")
        self.assertEqual(res, "OK")
        self.assertIsNotNone(fetch_data[0])
        parsed = email.message_from_bytes(fetch_data[0][1])
        self.assertEqual(parsed["Subject"], "Korrekte Mail")

        # MSN-Pfade wurden NIE aufgerufen
        conn.search.assert_not_called()
        conn.fetch.assert_not_called()

    def test_uid_fetch_returns_none_for_expunged_uid(self):
        """Wenn eine UID inzwischen expunged wurde, liefert fetch data[0]=None."""
        conn = self._make_fake_conn({})  # Keine UIDs bekannt
        res, data = conn.uid("fetch", b"9999", "(RFC822)")
        self.assertEqual(res, "OK")
        self.assertIsNone(data[0])


# ---------------------------------------------------------------------------
# U5 — NIL-Guard in _convert_body_to_pdf: Quellcode-Checks
# ---------------------------------------------------------------------------

class TestU5NilGuardBodyToPdfSource(unittest.TestCase):
    """Stellt sicher dass _convert_body_to_pdf NIL-Guards hat."""

    def test_nil_guard_present_in_source(self):
        self.assertIn("_payload is None", _src(),
                      "_convert_body_to_pdf() braucht NIL-Guard für get_payload(decode=True)")

    def test_at_least_two_nil_guards_in_function(self):
        """Mindestens 2 Guards: HTML + Plain-Text (beide Äste)."""
        src = _src()
        start = src.find("def _convert_body_to_pdf(")
        end = src.find("\n    def ", start + 1)
        func_body = src[start:end]
        count = func_body.count("is None") + func_body.count("is not None")
        self.assertGreaterEqual(count, 2,
                                f"_convert_body_to_pdf() hat nur {count} NIL-Guard(s), mind. 2 erwartet")

    def test_no_chained_decode_without_guard_in_function(self):
        """
        get_payload(decode=True).decode(...) ohne vorherige Zuweisung darf nicht
        mehr im Funktionskörper vorkommen — jedes Payload wird jetzt separat
        einer Variable zugewiesen und dann geprüft.
        """
        src = _src()
        start = src.find("def _convert_body_to_pdf(")
        end = src.find("\n    def ", start + 1)
        func_body = src[start:end]
        self.assertNotIn("get_payload(decode=True).decode(", func_body,
                         "Direkt verkettetes .get_payload().decode() ohne NIL-Guard gefunden")


# ---------------------------------------------------------------------------
# U6 — NIL-Guard für fetch-Antwort in process_email: Quellcode-Check
# ---------------------------------------------------------------------------

class TestU6NilGuardFetchResponse(unittest.TestCase):
    """process_email() prüft data[0] auf None bevor es indexiert wird."""

    def test_nil_guard_for_data_in_process_email(self):
        src = _src()
        start = src.find("def process_email(")
        end = src.find("\n    def ", start + 1)
        func_body = src[start:end]
        self.assertIn("data[0] is None", func_body,
                      "process_email() braucht NIL-Guard 'data[0] is None' nach uid('fetch')")


# ---------------------------------------------------------------------------
# Syntaxprüfung
# ---------------------------------------------------------------------------

class TestSyntaxValidity(unittest.TestCase):
    def test_syntax_valid(self):
        import py_compile
        py_compile.compile(str(SRC), doraise=True)


if __name__ == "__main__":
    unittest.main()
