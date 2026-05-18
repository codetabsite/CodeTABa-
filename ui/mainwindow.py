import os
import subprocess
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QComboBox,
    QLabel, QFrame, QStatusBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor

from ai.model import CodeTabModel
from ui.api_key_dialog import ApiKeyDialog, save_api_key


class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, question, topic, model):
        super().__init__()
        self.question = question
        self.topic = topic
        self.model = model

    def run(self):
        try:
            answer = self.model.ask(f"[{self.topic}] {self.question}")
            self.response_ready.emit(answer)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ModelLoader(QThread):
    done = pyqtSignal(object)
    failed = pyqtSignal(str)

    def run(self):
        try:
            self.done.emit(CodeTabModel())
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeTab AI ⚡ — Teknofest")
        self.setMinimumSize(900, 620)
        self.model = None
        self._apply_style()
        self._setup_ui()
        self._load_model()

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0d1117;
                color: #e6edf3;
                font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
            }
            QTextEdit {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                color: #e6edf3;
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
                min-width: 90px;
            }
            QPushButton#send_btn:hover { background-color: #2ea043; }
            QPushButton#send_btn:disabled { background-color: #21262d; color: #8b949e; }
            QPushButton#secondary {
                background-color: #21262d;
                color: #8b949e;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 12px;
            }
            QPushButton#secondary:hover { background-color: #30363d; color: #e6edf3; }
            QComboBox {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #e6edf3;
                min-width: 200px;
            }
            QComboBox QAbstractItemView {
                background-color: #161b22;
                border: 1px solid #30363d;
                color: #e6edf3;
            }
            QStatusBar {
                background-color: #161b22;
                color: #8b949e;
                font-size: 11px;
                border-top: 1px solid #30363d;
            }
            QFrame#sep { background-color: #30363d; max-height: 1px; }
        """)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 12, 16, 8)

        header = QHBoxLayout()
        left = QVBoxLayout()

        title = QLabel("⚡ CodeTab AI")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #58a6ff;")

        subtitle = QLabel("Linux Komutları  •  Matematik  •  Python / C++  |  Teknofest")
        subtitle.setStyleSheet("color: #8b949e; font-size: 11px;")

        left.addWidget(title)
        left.addWidget(subtitle)
        header.addLayout(left)
        header.addStretch()

        self.status_dot = QLabel("⏳ Bağlanıyor...")
        self.status_dot.setStyleSheet("color: #d29922; font-size: 12px;")
        header.addWidget(self.status_dot)
        layout.addLayout(header)

        sep = QFrame(); sep.setObjectName("sep"); sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        topic_row = QHBoxLayout()
        topic_lbl = QLabel("Konu:")
        topic_lbl.setStyleSheet("color: #8b949e; font-size: 12px;")
        self.topic_combo = QComboBox()
        self.topic_combo.addItems([
            "🐧  Linux Komutları",
            "📐  Matematik",
            "🐍  Python Kodlama",
            "⚙️   C++ Kodlama",
        ])
        topic_row.addWidget(topic_lbl)
        topic_row.addWidget(self.topic_combo)
        topic_row.addStretch()

        self.terminal_btn = QPushButton("💻 Terminal")
        self.terminal_btn.setObjectName("secondary")
        self.terminal_btn.clicked.connect(self._toggle_terminal)

        self.clear_btn = QPushButton("🗑 Temizle")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._clear)

        self.apikey_btn = QPushButton("🔑 API Key")
        self.apikey_btn.setObjectName("secondary")
        self.apikey_btn.clicked.connect(self._change_api_key)

        topic_row.addWidget(self.terminal_btn)
        topic_row.addWidget(self.clear_btn)
        topic_row.addWidget(self.apikey_btn)
        layout.addLayout(topic_row)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        layout.addWidget(self.chat, 1)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setPlaceholderText("Terminal çıktısı...")
        self.terminal.setMaximumHeight(160)
        self.terminal.setVisible(False)
        layout.addWidget(self.terminal)

        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Sorunuzu yazın...")
        self.input.returnPressed.connect(self._send)

        self.send_btn = QPushButton("Gönder ➤")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.clicked.connect(self._send)
        self.send_btn.setEnabled(False)

        input_row.addWidget(self.input)
        input_row.addWidget(self.send_btn)
        layout.addLayout(input_row)

        self.statusBar().showMessage("Groq API'ye bağlanılıyor...")

        self._msg("CodeTab AI",
            "Merhaba! Ben CodeTab AI 🤖\n"
            "Linux komutları, matematik ve kodlama konularında yardımcı olabilirim.\n"
            "Sorunuzu yazın ve Enter'a basın!", ai=True)

    def _load_model(self):
        self.loader = ModelLoader()
        self.loader.done.connect(self._on_ready)
        self.loader.failed.connect(self._on_fail)
        self.loader.start()

    def _on_ready(self, model):
        self.model = model
        self.status_dot.setText("🟢 Groq API Bağlı")
        self.status_dot.setStyleSheet("color: #3fb950; font-size: 12px;")
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("Hazır — Llama3 70B aktif")

    def _on_fail(self, err):
        self.status_dot.setText("🔴 Bağlantı Hatası")
        self.status_dot.setStyleSheet("color: #f85149; font-size: 12px;")
        self.statusBar().showMessage(f"Hata: {err}")
        QMessageBox.warning(self, "API Hatası",
            f"{err}\n\nTerminalde şunu çalıştır:\nexport GROQ_API_KEY='gsk_...'")

    def _send(self):
        question = self.input.text().strip()
        if not question or not self.model:
            return

        topic = self.topic_combo.currentText().strip()
        self._msg("Sen", question, ai=False)
        self.input.clear()
        self.send_btn.setEnabled(False)
        self.statusBar().showMessage("⏳ Yanıt üretiliyor...")

        if "Linux" in topic and self._linux_komutu_mu(question):
            self._terminalde_calistir(question)

        self.worker = AIWorker(question, topic, self.model)
        self.worker.response_ready.connect(self._on_response)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _linux_komutu_mu(self, text):
        cmds = ["ls","pwd","cd","mkdir","rm","cp","mv","cat","grep",
                "find","ps","df","du","chmod","echo","tar","ping","ip"]
        return text.split()[0].lower() in cmds

    def _terminalde_calistir(self, cmd):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
            out = r.stdout or r.stderr or "(çıktı yok)"
            self.terminal.setVisible(True)
            self.terminal.append(f"<span style='color:#3fb950'>$ {cmd}</span>\n{out}\n")
        except Exception as e:
            self.terminal.append(f"Hata: {e}")

    def _on_response(self, response):
        self._msg("CodeTab AI", response, ai=True)
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("Hazır")

    def _on_error(self, err):
        self._msg("CodeTab AI", f"⚠️ Hata: {err}", ai=True)
        self.send_btn.setEnabled(True)
        self.statusBar().showMessage("Hata oluştu")

    def _msg(self, sender, text, ai=True):
        color = "#58a6ff" if ai else "#3fb950"
        icon  = "🤖" if ai else "👤"
        text  = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        html  = (f"<div style='margin:6px 0'>"
                 f"<b style='color:{color}'>{icon} {sender}</b><br>"
                 f"<span style='white-space:pre-wrap;color:#e6edf3'>{text}</span>"
                 f"</div><hr style='border:none;border-top:1px solid #21262d'>")
        self.chat.append(html)
        c = self.chat.textCursor()
        c.movePosition(QTextCursor.End)
        self.chat.setTextCursor(c)

    def _clear(self):
        self.chat.clear()
        self.terminal.clear()
        if self.model:
            self.model.gecmisi_temizle()

    def _toggle_terminal(self):
        v = not self.terminal.isVisible()
        self.terminal.setVisible(v)
        self.terminal_btn.setText("💻 Terminal Gizle" if v else "💻 Terminal")

    def _change_api_key(self):
        dialog = ApiKeyDialog(self, first_run=False)
        if dialog.exec_() == dialog.Accepted:
            self.model = None
            self.send_btn.setEnabled(False)
            self.status_dot.setText("⏳ Yeniden bağlanıyor...")
            self.status_dot.setStyleSheet("color: #d29922; font-size: 12px;")
            self._load_model()
