# NET Kitten

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Linux%20|%20macOS-lightgrey)
![Category](https://img.shields.io/badge/Category-Cybersecurity-red)

> Static network reconnaissance tool with multi-target support, parallel port scanning, banner grabbing, and structured report generation.

*This is a learning project — full explanations of each module are in the source code comments.*

---

## What It Does

- **Ping Sweep** — discovers live hosts on a network range (CIDR notation supported)
- **TCP Port Scanning** — multi-threaded scanner with configurable port ranges
- **Banner Grabbing** — captures service banners to identify software versions
- **Service Detection** — identifies 17 common protocols (SSH, HTTP, FTP, RDP, etc.)
- **Report Generation** — structured terminal output + optional `.txt` export
- **Parallel Execution** — uses `ThreadPoolExecutor` for fast concurrent scanning

---

## Quick Start

```bash
git clone https://github.com/yourusername/netscout.git
cd netscout
python3 netscout.py --target 192.168.1.0/24 --scan all
```

> ⚠️ **Legal Notice** — Only use NETSCOUT on networks and systems you own or have explicit written permission to test. Unauthorized scanning is illegal.

---

## Usage

```
python3 netscout.py --target <IP or CIDR> [options]
```

| Flag | Description | Default |
|------|-------------|---------|
| `--target` | Single IP or CIDR range (required) | — |
| `--scan` | `ping` \| `ports` \| `all` | `all` |
| `--ports` | Port range or list (e.g. `1-1024` or `22,80,443`) | `1-1024` |
| `--timeout` | Connection timeout in seconds | `1.0` |
| `--output` | Save report to a `.txt` file | — |

### Examples

```bash
# Scan a single host (all modes)
python3 netscout.py --target 192.168.1.1

# Ping sweep only on a /24 subnet
python3 netscout.py --target 10.0.0.0/24 --scan ping

# Port scan with custom range and save report
python3 netscout.py --target 192.168.1.100 --scan ports --ports 1-65535 --output report.txt

# Check specific ports only
python3 netscout.py --target 192.168.1.1 --ports 22,80,443,3306,8080

# Fast scan with lower timeout
python3 netscout.py --target 192.168.1.0/24 --timeout 0.5
```

---

## Stack

**Language:** Python 3.8+  
**Concurrency:** `concurrent.futures.ThreadPoolExecutor`  
**Networking:** `socket`, `subprocess`  
**Utilities:** `argparse`, `ipaddress`, `datetime`  

*No external dependencies — pure Python standard library.*

---

## Project Structure

```
netscout/
├── netscout.py          # Entry point & CLI argument parser
├── modules/
│   ├── __init__.py      # Package initializer
│   ├── ping.py          # Parallel ping sweep engine
│   ├── scanner.py       # TCP port scanner + banner grabber
│   └── report.py        # Terminal & file report generator
├── requirements.txt     # Dependencies (none required)
├── LICENSE              # MIT License
└── README.md            # You are here
```

---

## How It Works

### Ping Sweep
Sends ICMP echo requests using the system `ping` binary via `subprocess`. Uses thread pools to scan up to 50 hosts simultaneously, dramatically reducing total scan time vs sequential execution.

### Port Scanner
Opens raw TCP connections via `socket.connect_ex()`. A return code of `0` indicates an open port. Immediately attempts to receive a banner from the service before closing the socket. Up to 100 ports are scanned in parallel per host.

### Service Identification
Compares open port numbers against a local dictionary of 17 well-known port-to-service mappings (IANA standard). Falls back to `"unknown"` for unrecognized ports.

### Report Engine
Formats results with ANSI color codes for terminal output. Strips color codes when writing to file to ensure clean plain-text output.

---

## Roadmap

- [ ] OS fingerprinting via TTL analysis
- [ ] UDP port scanning support  
- [ ] JSON/CSV report export
- [ ] CVE lookup for detected service versions
- [ ] Traceroute integration
- [ ] WHOIS lookup for public IPs

---

## Author

Built as a hands-on learning project in network security fundamentals.

**Matteo Adorni** — [LinkedIn](https://linkedin.com) | [GitHub](https://github.com)

---

## License

MIT — see [LICENSE](./LICENSE) for details.
