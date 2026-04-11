# Aarya (आर्य)
> **Email address to digital footprint for OSINT**

[![PyPI version](https://badge.fury.io/py/aarya.svg)](https://badge.fury.io/py/aarya)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/aarya?period=total&units=NONE&left_color=GREY&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/aarya)

Aarya is an OSINT tool that validates the existence of email addresses across social media, shopping, and professional platforms (e.g. Instagram, Amazon, Spotify) and extracts rich metadata like Google Map contributions, reviews and account creation dates for proton mail.


![Aarya Demo](https://raw.githubusercontent.com/forshaur/aarya/refs/heads/main/src/aarya/gimp.png)

## 🚀 Features

* **Deep Analysis:** Goes beyond simple "Yes/No" results to extract rich metadata like Google Maps reviews, Profile Pictures, Gaia IDs, and ProtonMail key creation dates.
* **Full Visibility:** Reports positive hits, negative results, rate limits, and errors explicitly so you never miss a detail.
* **Smart Stealth:** Automatically fetches the latest real-world **User-Agents** from the web to bypass simple bot detection filters.
* **Elegant UI:** Professional, minimalist CLI design with responsive tables and clean link wrapping.

## ⚠️ Disclaimer
**Aarya is designed for educational purposes, authorized security research, and personal digital footprint analysis only.**

The developers are not responsible for any misuse of this tool. Scanning email addresses that do not belong to you or without the owner's explicit consent may violate privacy laws or platform Terms of Service in your jurisdiction. Use responsibly.

## 📦 Installation

### Option 1: Install via PyPI (Recommended)
It is recommended to use a virtual environment to prevent conflicts.

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install aarya
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install aarya
```

### Option 2: Install from Source (Development)
If you want the latest features or updates directly from the repository:
```bash
git clone https://github.com/forshaur/aarya.git
cd aarya
pip install .
```

# 🛠 Usage
### Basic Scan:
```bash 
aarya target@example.com
```
### Save Results:
```bash 
aarya target@example.com -o results.json
```

## 🆚 Aarya vs. Holehe
#### During development of this tool I came to know that another great tool was already there which was similar to Aarya.
### here is why Aarya outperforms.
| Feature | Holehe | Aarya |
| :--- | :--- | :--- |
| **Primary Output** | Email Existence (True/False) | **Identity Intelligence** (Real Names, Photos, Maps Reviews) |
| **Reliability** | Prone to False Negatives and >50% modules **don't work** | **High** (Explicitly detects Rate Limits vs. Not Found) |
| **Stealth** | Static Headers | **Dynamic** (Auto-fetches latest User-Agents) |
| **Focus** | Quantity (120+ Sites) | **Quality** (Deep scans of High-Value Targets) |
| **UI/UX** | Basic CLI | **Modern** (Rich Tables, Clickable Links, Summary Panels) |


## 🤝 Contributing
Contributions are welcome! If you want to add a new module (e.g., Pinterest, Adobe), please fork the repository and submit a Pull Request.

## 📜 License
This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.

## Other projects by me
[Adyant](https://github.com/forshaur/adyant) - Markov-chain based wordlist generator for URL path discovery.
> No matter how big a wordlist is, it's usually top-n segments from that wordlist. adyant helps you look for those rare paths without creating much noise. Quickly.


