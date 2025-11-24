# 🐕 BuildWatchDog

> A modern, elegant CLI tool to monitor AWS CodeBuild jobs in real-time from your terminal

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/buildwatchdog)

BuildWatchDog eliminates the need to constantly refresh the AWS Console by bringing real-time CodeBuild monitoring directly to your terminal. Get instant updates, beautiful visualizations, and desktop notifications—all while staying in your workflow.


## ✨ Features

- 🎯 **Real-time Monitoring** - Track AWS CodeBuild jobs with live status updates
- 🎨 **Beautiful TUI** - Rich terminal interface with color-coded phases and status indicators
- 🔔 **Desktop Notifications** - Native notifications for build status changes (macOS & Linux)
- 🔒 **Secure** - Uses your local AWS CLI credentials—no API keys or embedded credentials
- ⚡ **Lightweight** - Pure Python with minimal dependencies
- 🛡️ **Robust Error Handling** - Graceful handling of network issues, credential errors, and timeouts
- 🔄 **Cross-Platform** - Works seamlessly on macOS and Linux

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- AWS CLI installed and configured ([Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- Valid AWS credentials with CodeBuild read permissions

### Install BuildWatchDog

```bash
# Clone the repository
git clone https://github.com/yourusername/buildwatchdog.git
cd buildwatchdog

# Install dependencies
pip install -r requirements.txt

# Make it executable (optional)
chmod +x buildwatchdog.py

# Or install globally
pip install -e .
```

## 🚀 Quick Start

```bash
# Monitor a build (replace with your actual build ID)
python buildwatchdog.py --build-id my-project:12345678-1234-1234-1234-123456789012

# With custom polling interval
python buildwatchdog.py --build-id <BUILD_ID> --interval 15

# Using a specific AWS profile
python buildwatchdog.py --build-id <BUILD_ID> --profile production

# Desktop notifications only
python buildwatchdog.py --build-id <BUILD_ID> --notify desktop
```

## 📖 Usage

```
buildwatchdog.py --build-id <BUILD_ID> [OPTIONS]

Required Arguments:
  --build-id BUILD_ID       AWS CodeBuild Build ID to monitor

Optional Arguments:
  --interval SECONDS        Polling interval in seconds (default: 10)
  --notify MODE            Notification method: terminal, desktop, or both (default: both)
  --profile PROFILE        AWS CLI profile to use (default: default profile)
  -h, --help               Show help message
```

## 🎯 How It Works

1. **Launch** - Start BuildWatchDog with your CodeBuild Build ID
2. **Monitor** - Watch real-time phase progression in a beautiful terminal interface
3. **Get Notified** - Receive instant desktop notifications when status changes
4. **Stay Focused** - No need to switch to AWS Console—everything in your terminal

### Build Phases Tracked

- ✅ SUBMITTED
- ✅ QUEUED
- ✅ PROVISIONING
- ✅ DOWNLOAD_SOURCE
- ✅ INSTALL
- ✅ PRE_BUILD
- ✅ BUILD
- ✅ POST_BUILD
- ✅ UPLOAD_ARTIFACTS
- ✅ FINALIZING
- ✅ COMPLETED

## 🎨 Interface Overview

```
┌─────────────────────────────── BuildWatchDog ────────────────────────────────┐
│ BuildWatchDog | Build: RevenueLeakage... | Project: RevenueLeakageManualDeploy     │
│ Status: 🟢 SUCCEEDED                                                               │
│                                                                                    │
│ Build Phases:                                                                      │
│ ╭────────────────────────────────────────────────────────────────────────╮  │
│ │ ✓ SUBMITTED          SUCCEEDED                                                │  │
│ │ ✓ QUEUED             SUCCEEDED                                                │  │
│ │ ✓ PROVISIONING       SUCCEEDED                                                │  │
│ │ ✓ DOWNLOAD_SOURCE    SUCCEEDED                                                │  │
│ │ ✓ BUILD              SUCCEEDED                                                │  │
│ │ ✓ POST_BUILD         SUCCEEDED                                                │  │
│ │ ✓ UPLOAD_ARTIFACTS   SUCCEEDED                                                │  │
│ │ ✓ COMPLETED          SUCCEEDED                                                │  │
│ ╰────────────────────────────────────────────────────────────────────────╯  │
│                                                                                    │
│ Recent Events:                                                                     │
│ ╭────────────────────────────────────────────────────────────────────────╮  │
│ │ Time      Event                                                               │  │
│ │ 11:14:16  Started monitoring - IN_PROGRESS                                    │  │
│ │ 11:15:51  Status changed to SUCCEEDED                                         │  │
│ ╰────────────────────────────────────────────────────────────────────────╯  │
└──────────────────── Press Ctrl+C to quit | Interval: 10s ──────────────────────┘
```

## 🔧 Configuration

### AWS Credentials

BuildWatchDog uses your local AWS CLI configuration. Ensure you have:

```bash
# Configure AWS CLI
aws configure

# Or use named profiles
aws configure --profile myprofile
```

### Required IAM Permissions

Your AWS credentials need the following permission:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Requirements

```
rich>=13.0.0
```

## 🐛 Troubleshooting

### "AWS CLI not found"
Install the AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### "Invalid AWS credentials"
Run `aws configure` to set up your credentials

### "Build ID not found"
Verify the build ID format: `project-name:uuid`

### Desktop notifications not working
- **macOS**: Notifications should work out of the box
- **Linux**: Install `notify-send` (usually in `libnotify-bin` package)
  ```bash
  sudo apt-get install libnotify-bin  # Debian/Ubuntu
  sudo yum install libnotify           # RHEL/CentOS
  ```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- Inspired by the need for better developer tooling around AWS CodeBuild

## 📬 Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Issues: [GitHub Issues](https://github.com/yourusername/buildwatchdog/issues)

---

Made with ❤️ for developers who live in the terminal