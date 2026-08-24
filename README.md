# TuyaLight 🎵💡

Real-time, zero-delay bass-reactive lightshow engine for Tuya WiFi LED strips.

This project captures system audio (via WASAPI loopback), isolates bass frequencies, applies aggressive gamma-contrast,
calculates spectral centroid for dynamic colors, and sends high-speed Direct Jump (Music Mode) packets to local Tuya
devices.

## Features

- **60+ FPS Network Sync**: Background thread handling Wi-Fi packets.
- **Smart Envelope Follower**: Instant attack, smooth decay.
- **Vocal & Chord Filter**: Ignores mid/high frequencies (`BASS_DOMINANCE` filter).
- **Spectral Centroid**: Dynamic LED color based on bass pitch (sub-bass vs punchy kick).
- **Background Mode**: Run silently on Windows startup.

## Prerequisites (Windows)

1. **Python 3.10+**
2. **Make** (via Chocolatey). Open PowerShell as Administrator and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

choco install make
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/tuyalight.git
   cd tuyalight
   ```

2. Install dependencies (creates `venv` automatically):
   ```bash
   make install
   ```

3. Copy your Tuya credentials into `config.toml`.

## Configuration (`config.toml`)

Edit the `config.toml` file in the root directory:

- `device_id`, `ip`, `local_key`: Get these from your Tuya IoT Developer account.
- `smoothing`: Adjust visual smoothness (0.25 is recommended).
- `bass_dominance`: Set higher (e.g., 0.35) to ignore vocals/guitars completely.

## Usage

### Run in terminal (with live UI):

```bash
make run
```

### Run in background (Silent Mode):

To run the app silently without a terminal window:

```bash
venv\Scripts\python -m tuyalight run --background
```

### Windows Startup (Auto-start in background):

Enable the background service to start with Windows:

```bash
make startup-enable
```

To disable:

```bash
make startup-disable
```

## Development

Install pre-commit hooks for contributing:

```bash
make dev
make lint
```

## License

MIT
