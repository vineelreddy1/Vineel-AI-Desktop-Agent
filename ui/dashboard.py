import sys
import time
import threading
import logging
import config

try:
    from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit, QFrame, QComboBox,
        QSystemTrayIcon, QMenu, QSplitter, QCheckBox, QGroupBox
    )
    from PySide6.QtGui import QIcon, QFont, QColor
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False

from assistant.agent import Agent
from voice.speech_to_text import SpeechToText
from voice.wake_word import WakeWordDetector

logger = logging.getLogger("VineelAssistant.UI")

DARK_STYLESHEET = """
QMainWindow {
    background-color: #0F172A;
    color: #F8FAFC;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #F8FAFC;
}
QFrame.card {
    background-color: #1E293B;
    border-radius: 12px;
    border: 1px solid #334155;
    padding: 16px;
}
QLabel {
    font-size: 14px;
}
QLabel.title {
    font-size: 22px;
    font-weight: bold;
    color: #38BDF8;
}
QLabel.status-active {
    color: #10B981;
    font-weight: bold;
}
QLabel.status-idle {
    color: #94A3B8;
}
QPushButton {
    background-color: #0EA5E9;
    color: #FFFFFF;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    border: none;
}
QPushButton:hover {
    background-color: #0284C7;
}
QPushButton:pressed {
    background-color: #0369A1;
}
QPushButton.danger {
    background-color: #EF4444;
}
QPushButton.danger:hover {
    background-color: #DC2626;
}
QTextEdit, QLineEdit {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #F8FAFC;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
}
QTextEdit:focus, QLineEdit:focus {
    border: 1px solid #38BDF8;
}
"""


if HAS_PYSIDE:
    class VoiceListenerThread(QThread):
        command_detected = Signal(str)
        status_changed = Signal(str)
        log_signal = Signal(str)

        def __init__(self, stt, wake_detector, is_wake_word_mode=True):
            super().__init__()
            self.stt = stt
            self.wake_detector = wake_detector
            self.is_wake_word_mode = is_wake_word_mode
            self.running = True

        def run(self):
            self.status_changed.emit("LISTENING")
            while self.running:
                try:
                    spoken = self.stt.listen_command()
                    if spoken:
                        self.log_signal.emit(f"Voice detected: '{spoken}'")
                        is_wake, clean_cmd = self.wake_detector.process_input(
                            spoken, 
                            require_wake_word=self.is_wake_word_mode
                        )
                        if is_wake and clean_cmd:
                            self.status_changed.emit("PROCESSING")
                            self.command_detected.emit(clean_cmd)
                            time.sleep(1.0)
                        elif is_wake and not clean_cmd:
                            self.log_signal.emit("Wake word heard. Awaiting command...")
                except Exception as e:
                    logger.error(f"Error in VoiceListenerThread: {e}")
                time.sleep(0.1)

        def stop(self):
            self.running = False
            self.wait()


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(f"{config.APP_NAME} v{config.VERSION}")
            self.resize(950, 650)
            self.setStyleSheet(DARK_STYLESHEET)

            self.stt = SpeechToText()
            self.wake_detector = WakeWordDetector()
            self.agent = Agent(log_callback=self.append_log)
            self.listener_thread = None

            self.init_ui()
            self.init_tray()

        def init_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setSpacing(16)
            main_layout.setContentsMargins(20, 20, 20, 20)

            # Header Panel
            header_frame = QFrame()
            header_frame.setObjectName("header")
            header_frame.setProperty("class", "card")
            header_layout = QHBoxLayout(header_frame)

            title_lbl = QLabel(config.APP_NAME)
            title_lbl.setProperty("class", "title")

            self.status_lbl = QLabel("● IDLE")
            self.status_lbl.setProperty("class", "status-idle")

            header_layout.addWidget(title_lbl)
            header_layout.addStretch()
            header_layout.addWidget(self.status_lbl)

            main_layout.addWidget(header_frame)

            # Dashboard Cards Container
            cards_layout = QHBoxLayout()
            cards_layout.setSpacing(16)

            # Control Card
            ctrl_card = QFrame()
            ctrl_card.setProperty("class", "card")
            ctrl_layout = QVBoxLayout(ctrl_card)

            ctrl_title = QLabel("Assistant Controls")
            ctrl_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
            ctrl_layout.addWidget(ctrl_title)

            self.start_btn = QPushButton("🎙️ Start Assistant")
            self.start_btn.clicked.connect(self.toggle_assistant)
            ctrl_layout.addWidget(self.start_btn)

            self.stop_btn = QPushButton("🛑 Interrupt / Stop")
            self.stop_btn.setProperty("class", "danger")
            self.stop_btn.clicked.connect(self.interrupt_task)
            ctrl_layout.addWidget(self.stop_btn)

            self.wake_chk = QCheckBox(f"Wake-Word Mode ('{config.WAKE_WORD}')")
            self.wake_chk.setChecked(config.WAKE_WORD_ENABLED)
            ctrl_layout.addWidget(self.wake_chk)

            ctrl_layout.addStretch()
            cards_layout.addWidget(ctrl_card, stretch=1)

            # Status & Command Card
            status_card = QFrame()
            status_card.setProperty("class", "card")
            status_layout = QVBoxLayout(status_card)

            self.cmd_lbl = QLabel("Current Command: None")
            self.resp_lbl = QLabel("Assistant Response: Ready")
            self.action_lbl = QLabel("Active Tool Action: IDLE")

            status_layout.addWidget(self.cmd_lbl)
            status_layout.addWidget(self.resp_lbl)
            status_layout.addWidget(self.action_lbl)
            status_layout.addStretch()

            cards_layout.addWidget(status_card, stretch=2)
            main_layout.addLayout(cards_layout)

            # Real-time Activity Log
            log_group = QGroupBox("Activity Log & History")
            log_layout = QVBoxLayout(log_group)

            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            log_layout.addWidget(self.log_text)

            main_layout.addWidget(log_group, stretch=3)

            # Text Input Bar (CLI / Desktop Command Entry)
            input_layout = QHBoxLayout()
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Type command (e.g. 'Open Chrome and search YouTube for Java DSA')...")
            self.input_field.returnPressed.connect(self.send_text_command)

            send_btn = QPushButton("Send Command")
            send_btn.clicked.connect(self.send_text_command)

            input_layout.addWidget(self.input_field)
            input_layout.addWidget(send_btn)

            main_layout.addLayout(input_layout)

            self.append_log(f"{config.APP_NAME} initialized. System ready.")

        def init_tray(self):
            self.tray = QSystemTrayIcon(self)
            # Create system tray menu
            tray_menu = QMenu(self)
            
            show_act = tray_menu.addAction("Open Dashboard")
            show_act.triggered.connect(self.show)
            
            start_act = tray_menu.addAction("Start Assistant")
            start_act.triggered.connect(self.toggle_assistant)
            
            exit_act = tray_menu.addAction("Exit")
            exit_act.triggered.connect(QApplication.instance().quit)

            self.tray.setContextMenu(tray_menu)
            self.tray.show()

        def append_log(self, text: str):
            self.log_text.append(text)

        def toggle_assistant(self):
            if self.listener_thread and self.listener_thread.isRunning():
                self.listener_thread.stop()
                self.listener_thread = None
                self.start_btn.setText("🎙️ Start Assistant")
                self.status_lbl.setText("● IDLE")
                self.status_lbl.setProperty("class", "status-idle")
                self.append_log("Assistant stopped.")
            else:
                self.listener_thread = VoiceListenerThread(
                    self.stt, 
                    self.wake_detector, 
                    is_wake_word_mode=self.wake_chk.isChecked()
                )
                self.listener_thread.command_detected.connect(self.process_command)
                self.listener_thread.status_changed.connect(self.update_status)
                self.listener_thread.log_signal.connect(self.append_log)
                self.listener_thread.start()

                self.start_btn.setText("⏸️ Pause Assistant")
                self.status_lbl.setText("● LISTENING")
                self.status_lbl.setProperty("class", "status-active")
                self.append_log("Assistant listening for commands...")

        def update_status(self, status: str):
            self.status_lbl.setText(f"● {status}")

        def interrupt_task(self):
            self.agent.stop()
            self.append_log("TASK INTERRUPTED BY USER.")

        def send_text_command(self):
            text = self.input_field.text().strip()
            if text:
                self.input_field.clear()
                self.process_command(text)

        def process_command(self, cmd_text: str):
            self.cmd_lbl.setText(f"Current Command: '{cmd_text}'")
            self.status_lbl.setText("● PROCESSING")
            
            # Run agent execution in background thread to prevent UI freezing
            def run_bg():
                res = self.agent.execute_command(cmd_text)
                self.resp_lbl.setText(f"Assistant Response: {res.get('message', 'Done')}")
                self.status_lbl.setText("● IDLE")

            threading.Thread(target=run_bg, daemon=True).start()


def launch_gui():
    if not HAS_PYSIDE:
        print("PySide6 is not installed. Unable to launch graphical dashboard.")
        return
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
