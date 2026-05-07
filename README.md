# RAT_BLUE v3.0

<div align="center">

```
    ██████╗  █████╗ ████████╗     ██████╗ ██╗     ██╗   ██╗███████╗
    ██╔══██╗██╔══██╗╚══██╔══╝     ██╔══██╗██║     ██║   ██║██╔════╝
    ██████╔╝███████║   ██║        ██████╔╝██║     ██║   ██║█████╗  
    ██╔══██╗██╔══██║   ██║        ██╔══██╗██║     ██║   ██║██╔══╝  
    ██║  ██║██║  ██║   ██║███████╗██████╔╝███████╗╚██████╔╝███████╗
    ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝╚══════╝╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝
```

**Advanced Bluetooth Exploitation Framework**

*Autonomous Android RAT with Telegram C2*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-green.svg)](https://www.linux.org/)
[![License](https://img.shields.io/badge/License-Educational-red.svg)](LICENSE)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Commands](#commands) • [Disclaimer](#disclaimer)

</div>

---

## 📋 Overview

RAT_BLUE is an advanced Android exploitation framework that combines Bluetooth spoofing with ADB exploitation to achieve full remote access to target devices. The framework features autonomous target hunting, Telegram-based command and control, and comprehensive data exfiltration capabilities.

### Key Capabilities

- **Bluetooth Spoofing** - Masquerades as trusted audio devices (AirPods, TWS earbuds)
- **Autonomous Exploitation** - Automatically detects and exploits nearby Android devices
- **Telegram C2** - Remote control via Telegram bot with real-time command execution
- **Data Exfiltration** - Extracts contacts, SMS, screenshots, and system information
- **Screen Mirroring** - Real-time screen control via scrcpy
- **Persistent Access** - Maintains connection via WiFi ADB after initial pairing

---

## <3 Features

### Exploitation Vector

```
Bluetooth Spoofing → Device Pairing → ADB Connection → Full System Access
```

- Spoofs as common Bluetooth audio devices
- Automatic target detection and prioritization
- Exploits trust relationship after pairing
- Establishes persistent ADB connection
- Deploys Telegram bot for remote control

### Data Collection

- **Contacts** - Full contact database extraction
- **SMS Messages** - Inbox and sent messages
- **Screenshots** - Real-time screen capture
- **System Info** - Device model, Android version, IP addresses
- **Installed Apps** - Package list with focus on sensitive apps
- **Screen Mirror** - Live screen control

### Command & Control

Remote control via Telegram bot with the following commands:

| Command | Description |
|---------|-------------|
| `/screenshot` | Capture device screen |
| `/contacts` | Extract contact list |
| `/sms` | Extract SMS messages |
| `/apps` | List installed applications |
| `/info` | Get device information |
| `/help` | Show command menu |

---

## 🛠️ Installation

### Prerequisites

- Linux system (Arch Linux recommended)
- Python 3.8+
- Bluetooth adapter
- ADB tools
- Telegram bot token

### Dependencies

```bash
# Arch Linux
sudo pacman -S python python-requests android-tools scrcpy bluez bluez-utils bluez-deprecated-tools

# Debian/Ubuntu
sudo apt install python3 python3-requests adb scrcpy bluez bluetooth
```

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/RAT_BLUE.git
cd RAT_BLUE

# Configure Telegram bot
# Edit rat_blue_auto.py and set:
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_CHAT_ID

# Enable Bluetooth
sudo systemctl start bluetooth
sudo systemctl enable bluetooth
```

---

## + Usage

### Basic Exploitation

```bash
# Run autonomous exploitation mode
python3 rat_blue_auto.py
```

The framework will:
1. Spoof as a Bluetooth audio device
2. Scan for nearby Android devices
3. Attempt automatic pairing
4. Establish ADB connection upon successful pairing
5. Deploy Telegram bot for remote control
6. Exfiltrate initial data package

### Target Device Requirements

- Bluetooth enabled and discoverable
- USB debugging enabled (for ADB access)
- Android 5.0+ (API 21+)

### Telegram Control

After successful exploitation, control the device via Telegram:

```
/screenshot - Get current screen
/contacts - Download contact list
/sms - Extract SMS messages
/info - View device details
```

---

## 📱 Attack Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RAT_BLUE Attack Chain                     │
└─────────────────────────────────────────────────────────────┘

1. RECONNAISSANCE
   └─> Bluetooth scan for nearby devices
   └─> Identify Android phones by MAC prefix
   └─> Prioritize targets

2. INITIAL ACCESS
   └─> Spoof as trusted audio device
   └─> Wait for victim to pair
   └─> Establish Bluetooth connection

3. EXPLOITATION
   └─> Leverage ADB over network
   └─> Gain shell access
   └─> Deploy persistence mechanisms

4. COMMAND & CONTROL
   └─> Activate Telegram bot
   └─> Establish C2 channel
   └─> Accept remote commands

5. DATA EXFILTRATION
   └─> Extract sensitive data
   └─> Send to Telegram
   └─> Maintain access
```

---

## <3 Technical Details

### Bluetooth Spoofing

The framework uses `hciconfig` and `bluetoothctl` to manipulate Bluetooth adapter properties:

- **Device Class**: `0x240404` (Wearable Headset Device)
- **Device Name**: Randomized from common TWS earbuds
- **Pairing Mode**: Auto-accept enabled

### ADB Exploitation

Requires USB debugging to be enabled on target device:

- Initial connection via USB or WiFi ADB
- Persistent connection maintained via `adb tcpip 5555`
- Full shell access with `adb shell` commands

### Data Exfiltration

All extracted data is sent to Telegram bot:

- Contacts parsed and formatted
- SMS messages cleaned and structured
- Screenshots sent as images
- System info compiled into reports

---

## 📊 Detection & Prevention

### For Security Researchers

**Indicators of Compromise:**

- Unexpected Bluetooth pairing requests from audio devices
- ADB connection from unknown IP addresses
- Unusual network traffic to Telegram API
- Suspicious process: `scrcpy`, `adb`

**Detection Methods:**

```bash
# Check for active ADB connections
adb devices

# Monitor Bluetooth connections
bluetoothctl devices

# Check for suspicious processes
ps aux | grep -E 'adb|scrcpy'
```

### For Users

**Protection Measures:**

1. Disable Bluetooth when not in use
2. Disable USB debugging in Developer Options
3. Only pair with known devices
4. Review paired devices regularly
5. Use Bluetooth security settings (require PIN)

---


---

## 🔬 Research & Development

### Architecture

```
rat_blue_auto.py
├── Bluetooth Spoofing Module
├── Device Scanner
├── ADB Exploitation Engine
├── Telegram Bot Integration
└── Data Exfiltration Pipeline
```

### Future Enhancements

- [ ] WiFi ADB automatic setup
- [ ] Root privilege escalation
- [ ] Keylogger implementation
- [ ] Camera/microphone access
- [ ] Location tracking
- [ ] WhatsApp database extraction
- [ ] Encrypted C2 channel

---

## 📚 References

- [Android Debug Bridge (ADB)](https://developer.android.com/studio/command-line/adb)
- [Bluetooth Security](https://www.bluetooth.com/learn-about-bluetooth/key-attributes/bluetooth-security/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [scrcpy - Screen Mirroring](https://github.com/Genymobile/scrcpy)

---

## 🤝 Contributing

Contributions are welcome for educational and research purposes.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License for educational purposes only.

**USE AT YOUR OWN RISK**

---

## 👤 Author

Built By ZeronX.. No limits, No bullshit..

**Contact:** [nulajak] DM DC

---

## 🌟 Acknowledgments

- Android Open Source Project
- Bluetooth SIG
- Telegram Team
- Security Research Community

---

<div align="center">


