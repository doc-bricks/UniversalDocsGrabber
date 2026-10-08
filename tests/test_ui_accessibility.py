#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UniversalDocsGrabber - Barrierefreiheits- und UX-Vertragstests (WCAG 2.1 AA / BITV 2.0)
======================================================================================
Hermetische Testsuite zur Verifikation von Barrierefreiheitsattributen,
Tastaturbedienbarkeit, Dialogmodalität, Menüleiste, Statusleiste und i18n-Konsistenz.
"""

from __future__ import annotations

import os

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QPushButton,
    QTreeWidget,
)

from UniversalDocsGrabberV1 import (
    APP_NAME,
    AccountDialog,
    Document,
    MailAccount,
    MainWindow,
    ProfileDialog,
    SearchProfile,
)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def qapp():
    """Stellt sicher, dass eine QApplication-Instanz existiert."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def clean_window(tmp_path, monkeypatch):
    """Erstellt ein isoliertes MainWindow mit temporären Pfaden."""
    cfg_file = tmp_path / "config_test.json"
    docs_file = tmp_path / "docs_test.json"
    monkeypatch.setattr("UniversalDocsGrabberV1.CONFIG_FILE", cfg_file)
    monkeypatch.setattr("UniversalDocsGrabberV1.DOCS_DB", docs_file)

    win = MainWindow()
    win.base_path = str(tmp_path / "downloads")
    yield win
    win.close()


def test_mainwindow_menubar_actions_and_shortcuts(qapp, clean_window):
    """Prüft die vollständige Menüleiste, Aktionen und Tastaturkürzel."""
    win = clean_window
    mb = win.menuBar()
    assert mb is not None
    assert len(mb.actions()) >= 6  # Datei, Bearbeiten, Aktionen, Ansicht, Sprache, Hilfe

    # Menüs existieren
    assert hasattr(win, "menu_file")
    assert hasattr(win, "menu_edit")
    assert hasattr(win, "menu_actions")
    assert hasattr(win, "menu_view")
    assert hasattr(win, "menu_language")
    assert hasattr(win, "menu_help")

    # Tastaturkürzel prüfen
    assert win.act_open_base_folder.shortcut().toString() == "Ctrl+O"
    assert win.act_export_library.shortcut().toString() == "Ctrl+E"
    assert win.act_exit.shortcut().toString() == "Ctrl+Q"

    assert win.act_add_profile.shortcut().toString() == "Ctrl+N"
    assert win.act_edit_profile.shortcut().toString() == "F2"
    assert win.act_add_account.shortcut().toString() == "Ctrl+Shift+A"
    assert win.act_save_settings.shortcut().toString() == "Ctrl+S"

    assert win.act_start_all.shortcut().toString() == "Ctrl+R"

    assert win.act_view_accounts.shortcut().toString() == "Ctrl+1"
    assert win.act_view_docs.shortcut().toString() == "Ctrl+2"
    assert win.act_view_settings.shortcut().toString() == "Ctrl+3"
    assert win.act_view_log.shortcut().toString() == "Ctrl+4"

    assert win.act_shortcuts.shortcut().toString() == "F1"
    assert win.act_about.shortcut().toString() == "Shift+F1"

    # Tab-Navigation per Action
    win.act_view_settings.trigger()
    assert win.tabs.currentIndex() == 2
    win.act_view_docs.trigger()
    assert win.tabs.currentIndex() == 1
    win.act_view_accounts.trigger()
    assert win.tabs.currentIndex() == 0


def test_shortcuts_dialog_modal_and_a11y(qapp, clean_window):
    """Prüft den barrierefreien F1-Tastaturkürzel-Dialog auf Modalität und WCAG-Konformität."""
    win = clean_window
    dialog = win.show_shortcuts_dialog()
    try:
        assert dialog is not None
        assert isinstance(dialog, QDialog)
        assert dialog.isModal() is True
        assert "Tastaturkürzel" in dialog.windowTitle()
        assert "Tastaturkürzel" in dialog.accessibleName()

        # Tree-Struktur prüfen
        trees = dialog.findChildren(QTreeWidget)
        assert len(trees) >= 1
        tree = trees[0]
        assert tree.topLevelItemCount() >= 5

        # Kategorien prüfen
        categories = [tree.topLevelItem(i).text(0) for i in range(tree.topLevelItemCount())]
        assert "Datei" in categories
        assert "Bearbeiten" in categories
        assert "Aktionen" in categories
        assert "Ansicht" in categories
        assert "Hilfe" in categories

        # WCAG 2.1 AA / BITV 2.0 Hinweis
        labels = dialog.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("WCAG 2.1 AA" in t and "BITV 2.0" in t for t in texts)

        # Standard-Schließen-Button
        buttons = dialog.findChildren(QPushButton)
        close_btns = [b for b in buttons if "Schließen" in b.text() or "Close" in b.text()]
        assert len(close_btns) >= 1
        assert close_btns[0].isDefault() is True
    finally:
        dialog.close()


def test_about_dialog_modal_and_a11y(qapp, clean_window):
    """Prüft den barrierefreien Über-Dialog auf Modalität, Version und Lizenzangaben."""
    win = clean_window
    dialog = win.show_about_dialog()
    try:
        assert dialog is not None
        assert isinstance(dialog, QDialog)
        assert dialog.isModal() is True
        assert "Über UniversalDocsGrabber" in dialog.windowTitle()

        labels = dialog.findChildren(QLabel)
        texts = " ".join(lbl.text() for lbl in labels)
        assert APP_NAME in texts or "UniversalDocsGrabber" in texts
        assert "MIT" in texts
        assert "doc-bricks" in texts
    finally:
        dialog.close()


def test_mainwindow_statusbar_and_live_updates(qapp, clean_window):
    """Prüft die barrierefreie Statusleiste und permanente Zähler."""
    win = clean_window
    sb = win.statusBar()
    assert sb is not None
    assert "Statusleiste" in sb.accessibleName()

    assert hasattr(win, "status_label")
    assert "Bereit" in win.status_label.text()

    assert hasattr(win, "status_profiles_count")
    assert hasattr(win, "status_docs_count")
    assert "0 Profile" in win.status_profiles_count.text()
    assert "0 Dokumente" in win.status_docs_count.text()

    # Nach Hinzufügen eines Profils
    p = SearchProfile("p1", "Rechnungen", "Finanzen", "Acc1", "Rechnung", "", "", "Invoices", True)
    win.profiles.append(p)
    win.refresh_ui()
    assert "1 Profile" in win.status_profiles_count.text()

    # Nach Hinzufügen eines Dokuments
    d = Document(profile="Rechnungen", filename="inv.pdf", date="2026-10-09", path="/path/inv.pdf", sender="telekom@de")
    win.documents.append(d)
    win.refresh_ui()
    assert "1 Dokumente" in win.status_docs_count.text()


def test_accessible_document_table_keyboard_navigation(qapp, clean_window, monkeypatch):
    """Prüft Tastatursteuerung der Dokumententabelle (Enter=Öffnen, Ctrl+C=Pfad kopieren)."""
    win = clean_window
    d = Document(profile="Rechnungen", filename="inv.pdf", date="2026-10-09", path="C:/tmp/inv.pdf", sender="telekom@de")
    win.documents.append(d)
    win.refresh_ui()

    opened_paths = []

    def mock_open_doc(r, c):
        item = win.table.item(r, 0)
        if item:
            opened_paths.append(item.data(Qt.ItemDataRole.UserRole))

    monkeypatch.setattr(win, "open_doc", mock_open_doc)

    win.table.selectRow(0)
    assert win.table.currentRow() == 0

    # Simuliere Enter
    enter_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    win.table.keyPressEvent(enter_event)
    assert len(opened_paths) == 1
    assert opened_paths[0] == "C:/tmp/inv.pdf"

    # Simuliere Ctrl+C
    copy_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_C, Qt.KeyboardModifier.ControlModifier)
    win.table.keyPressEvent(copy_event)
    cb_text = QApplication.clipboard().text()
    assert cb_text == "C:/tmp/inv.pdf"
    assert "kopiert" in win.statusBar().currentMessage()


def test_accessible_profile_tree_and_account_table_keyboard(qapp, clean_window, monkeypatch):
    """Prüft Tastatursteuerung im Profil-Baum (Enter=Bearbeiten, Del=Löschen) und Konten-Tabelle."""
    win = clean_window
    p = SearchProfile("p1", "Telekom", "Telefon", "Acc1", "Rechnung", "", "", "Telekom", True)
    win.profiles.append(p)
    a = MailAccount("Acc1", "imap.test.de", "user@test.de", 993, "INBOX")
    win.accounts.append(a)
    win.refresh_ui()

    edited = []
    deleted_profiles = []
    deleted_accounts = []

    monkeypatch.setattr(win, "edit_prof", lambda item, col: edited.append(item.text(0)))
    monkeypatch.setattr(win, "del_prof", lambda: deleted_profiles.append(True))
    monkeypatch.setattr(win, "del_acc", lambda: deleted_accounts.append(True))

    # Navigiere zum Profil-Child-Item
    root = win.tree.topLevelItem(0)
    assert root is not None
    child = root.child(0)
    assert child is not None
    win.tree.setCurrentItem(child)

    # Enter auf Profil -> edit_prof
    enter_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
    win.tree.keyPressEvent(enter_event)
    assert len(edited) == 1
    assert edited[0] == "Telekom"

    # Del auf Profil -> del_prof
    del_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
    win.tree.keyPressEvent(del_event)
    assert len(deleted_profiles) == 1

    # Del auf Account-Tabelle -> del_acc
    win.list_acc.selectRow(0)
    win.list_acc.keyPressEvent(del_event)
    assert len(deleted_accounts) == 1


def test_dialog_form_accessibility_attributes(qapp):
    """Prüft Accessible Names und Tooltips in AccountDialog und ProfileDialog."""
    # AccountDialog
    acc_dlg = AccountDialog()
    assert acc_dlg.isModal() is False  # vor exec
    assert acc_dlg.accessibleName() == "IMAP Account"
    assert acc_dlg.n.accessibleName() == "Kontoname"
    assert acc_dlg.h.accessibleName() == "Host-Server"
    assert acc_dlg.p.accessibleName() == "Port"
    assert acc_dlg.u.accessibleName() == "Benutzername"
    assert acc_dlg.f.accessibleName() == "Suchordner"
    assert acc_dlg.pw.accessibleName() == "Passwort"
    assert len(acc_dlg.n.toolTip()) > 0
    assert len(acc_dlg.pw.toolTip()) > 0

    # ProfileDialog
    accounts = [MailAccount("TestAcc", "imap.test.de", "u@t.de", 993, "INBOX")]
    prof_dlg = ProfileDialog(accounts=accounts)
    assert prof_dlg.accessibleName() == "Suchprofil (IMAP)"
    assert prof_dlg.inp_name.accessibleName() == "Profilname"
    assert prof_dlg.inp_group.accessibleName() == "Gruppe"
    assert prof_dlg.cb_acc.accessibleName() == "Konto auswählen"
    assert prof_dlg.inp_subj.accessibleName() == "Betreff-Filter"
    assert prof_dlg.inp_send.accessibleName() == "Absender-Filter"
    assert prof_dlg.inp_gmail_query.accessibleName() == "Gmail-Suchanfrage"
    assert prof_dlg.inp_folder.accessibleName() == "Zielordner"
    assert prof_dlg.chk_active.accessibleName() == "Profil aktiv"


def test_dynamic_language_switch_retranslates_menu_and_statusbar(qapp, clean_window):
    """Prüft, ob der dynamische Sprachwechsel alle 6 Sprachen paritätisch in Menüs und Statusleiste reflektiert."""
    win = clean_window

    # Deutsch
    win.set_ui_language("de")
    assert win.menu_file.title() == "&Datei"
    assert win.menu_edit.title() == "&Bearbeiten"
    assert win.menu_help.title() == "&Hilfe"
    assert win.status_label.text() == "Bereit"
    assert "ä" in win.menu_edit.title() or "ö" in win.act_open_base_folder.text() or "ü" in win.act_shortcuts.text()

    # English
    win.set_ui_language("en")
    assert win.menu_file.title() == "&File"
    assert win.menu_edit.title() == "&Edit"
    assert win.menu_help.title() == "&Help"
    assert win.status_label.text() == "Ready"

    # Español
    win.set_ui_language("es")
    assert win.menu_file.title() == "&Archivo"
    assert win.menu_edit.title() == "&Editar"
    assert win.menu_help.title() == "&Ayuda"
    assert win.status_label.text() == "Listo"

    # 简体中文
    win.set_ui_language("zh")
    assert "文件" in win.menu_file.title()
    assert "编辑" in win.menu_edit.title()
    assert "帮助" in win.menu_help.title()
    assert win.status_label.text() == "就绪"

    # 日本語
    win.set_ui_language("ja")
    assert "ファイル" in win.menu_file.title()
    assert "編集" in win.menu_edit.title()
    assert "ヘルプ" in win.menu_help.title()
    assert win.status_label.text() == "準備完了"

    # Русский
    win.set_ui_language("ru")
    assert win.menu_file.title() == "&Файл"
    assert win.menu_edit.title() == "&Правка"
    assert win.menu_help.title() == "&Справка"
    assert win.status_label.text() == "Готово"

    # Zurück auf Deutsch
    win.set_ui_language("de")
    assert win.menu_file.title() == "&Datei"


def test_menu_actions_state_sync_with_selection_and_guards(qapp, clean_window):
    """Prüft die Synchronisation der Menü-Aktionen mit Selektion und Identity-Guard."""
    win = clean_window
    p = SearchProfile("p1", "Telekom", "Telefon", "Acc1", "Rechnung", "", "", "Telekom", True)
    win.profiles.append(p)
    a = MailAccount("Acc1", "imap.test.de", "user@test.de", 993, "INBOX")
    win.accounts.append(a)
    win.refresh_ui()

    # Ohne Selektion
    win.tree.setCurrentItem(None)
    win.list_acc.setCurrentCell(-1, -1)
    win._update_profile_delete_action_state()
    win._update_account_delete_action_state()

    assert win.act_del_profile.isEnabled() is False
    assert win.act_edit_profile.isEnabled() is False
    assert win.act_del_account.isEnabled() is False

    # Mit Selektion im Profil-Tree
    root = win.tree.topLevelItem(0)
    child = root.child(0)
    win.tree.setCurrentItem(child)
    assert win.act_del_profile.isEnabled() is True
    assert win.act_edit_profile.isEnabled() is True

    # Mit Selektion in Account-Tabelle
    win.list_acc.selectRow(0)
    assert win.act_del_account.isEnabled() is True
