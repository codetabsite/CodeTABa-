import json
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

CONFIG_DIR  = Path.home() / ".config" / "codetab"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_api_key() -> str:
    env = os.environ.get("GROQ_API_KEY", "")
    if env:
        return env
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return data.get("groq_api_key", "")
        except Exception:
            pass
    return ""


def save_api_key(key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = {}
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    data["groq_api_key"] = key
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    os.environ["GROQ_API_KEY"] = key


class ApiKeyDialog(QDialog):
    def __init__(self, parent=None, first_run: bool = True):
        super().__init__(parent)
        self.setWindowTitle("CodeTab AI — API Key Kurulumu")
        self.setMinimumWidth(480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._build_ui(first_run)
        self._apply_style()

    def _build_ui(self, first_run: bool):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel(" CodeTab AI")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #58a6ff;")
        layout.addWidget(title)

        if first_run:
            info = QLabel(
                "İlk çalıştırma — Groq API key gerekiyor.\n"
                "Ücretsiz key almak için: <a href='https://console.groq.com/keys' "
                "style='color:#58a6ff'>console.groq.com/keys</a>"
            )
        else:
            info = QLabel("API key'i güncelleyin:")
        info.setOpenExternalLinks(True)
        info.setWordWrap(True)
        info.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(info)

        key_lbl = QLabel("Groq API Key:")
        key_lbl.setStyleSheet("color: #e6edf3; font-size: 13px;")
        layout.addWidget(key_lbl)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("gsk_...")
        self.key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.key_input)

        self.show_btn = QPushButton(" Göster")
        self.show_btn.setObjectName("secondary")
        self.show_btn.setFixedWidth(90)
        self.show_btn.clicked.connect(self._toggle_echo)
        show_row = QHBoxLayout()
        show_row.addStretch()
        show_row.addWidget(self.show_btn)
        layout.addLayout(show_row)

        self.save_btn = QPushButton("Kaydet ve Başlat ➤")
        self.save_btn.setObjectName("send_btn")
        self.save_btn.clicked.connect(self._save)
        layout.addWidget(self.save_btn)

        if not first_run:
            cancel = QPushButton("İptal")
            cancel.setObjectName("secondary")
            cancel.clicked.connect(self.reject)
            layout.addWidget(cancel)

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog, QWidget {
                background-color: #0d1117;
                color: #e6edf3;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
            }
            QLineEdit {
                background-color: #161b22;
                border: 2px solid #30363d;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #e6edf3;
            }
            QLineEdit:focus { border: 2px solid #58a6ff; }
            QPushButton#send_btn {
                background-color: #238636;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 22px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#send_btn:hover { background-color: #2ea043; }
            QPushButton#secondary {
                background-color: #21262d;
                color: #8b949e;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 12px;
            }
            QPushButton#secondary:hover { background-color: #30363d; color: #e6edf3; }
        """)

    def _toggle_echo(self):
        if self.key_input.echoMode() == QLineEdit.Password:
            self.key_input.setEchoMode(QLineEdit.Normal)
            self.show_btn.setText(" Gizle")
        else:
            self.key_input.setEchoMode(QLineEdit.Password)
            self.show_btn.setText(" Göster")

    def _save(self):
        key = self.key_input.text().strip()
        if not key.startswith("gsk_") or len(key) < 20:
            QMessageBox.warning(
                self, "Geçersiz Key",
                "API key 'gsk_' ile başlamalı ve geçerli olmalıdır."
            )
            return
        save_api_key(key)
        self.accept()
