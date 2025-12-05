# Aarya (आर्य)
> **The Advanced OSINT Email Scanner**

[![PyPI version](https://badge.fury.io/py/aarya.svg)](https://badge.fury.io/py/aarya)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Aarya is an OSINT tool that validates the existence of email addresses across social media, shopping, and professional platforms (e.g. Instagram, Amazon, Spotify).

* It leverages **Asynchronous HTTP Requests (httpx)** to perform lightning-fast, concurrent checks without the overhead of a web browser.
* It silently verifies accounts using "Forgot Password" APIs, registration endpoints, and public profile scrapes.

![Aarya Demo](https://raw.githubusercontent.com/forshaur/aarya/refs/heads/main/src/aarya/gimp.png)

## 🚀 Features

* **Deep Analysis:** Goes beyond simple "Yes/No" results to extract rich metadata like Google Maps reviews, Profile Pictures, Gaia IDs, and ProtonMail key creation dates.
* **Full Visibility:** Reports positive hits, negative results, rate limits, and errors explicitly so you never miss a detail.
* **Smart Stealth:** Automatically fetches the latest real-world **User-Agents** from the web to bypass simple bot detection filters.
* **Elegant UI:** Professional, minimalist CLI design with responsive tables and clean link wrapping.


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

## 🔍 Use Cases in Recon & Intel

### 1. Verification & Validation
Confirm if a target email is active. A "ghost" email (no accounts anywhere) is a high-risk indicator for fraud or burner accounts, whereas an email with established accounts verifies the identity exists.

### 2. Social Engineering Context
Aarya helps Red Teamers map the digital footprint of a target. Knowing a target uses Duolingo or Wattpad allows for highly tailored phishing pretexts (e.g., "Your Duolingo streak is in danger" vs generic corporate emails).

### 3. Identity Correlation
By extracting unique identifiers like the **Google Gaia ID** or **ProtonMail public key date**, Aarya helps correlate an email address with real-world timelines, locations, and other digital identities across the web.

### 4. Credibility of Credential Reuse (Post-Exploitation)
If a target's password is compromised (via phishing or a data breach) for one verified platform, Aarya provides a precise roadmap of *other* active services where that same password might be reused, highlighting critical risks for credential stuffing attacks.

### 5. Corporate OpSec Auditing
Security teams can scan corporate email domains to detect "Shadow IT" or policy violations. Discovering that an employee used their official `name@company.com` address to sign up for **Instagram** or **Amazon** highlights potential attack surfaces and credential leakage risks.

### 6. OSINT Pivot Points
Aarya acts as a signpost for deeper investigation. A confirmed **Google** account signals an investigator to search for public Maps reviews or Photos. A confirmed **Instagram** account invites a search for public profile associated with that email. The tool identifies *where* to look next for public data.

### 7. Credibility Analysis (Anti-Fraud)
In fraud investigations, account age acts as a trust signal. An email address linked to a **ProtonMail** key created 3 years ago or a **Google** account with Maps contributions from 2019 is far more likely to be legitimate than a "fresh" email with absolutely no digital footprint.

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




## ⚠️ Disclaimer
**Aarya is designed for educational purposes, authorized security research, and personal digital footprint analysis only.**

The developers are not responsible for any misuse of this tool. Scanning email addresses that do not belong to you or without the owner's explicit consent may violate privacy laws or platform Terms of Service in your jurisdiction. Use responsibly.

## 🤝 Contributing
Contributions are welcome! If you want to add a new module (e.g., Pinterest, Adobe), please fork the repository and submit a Pull Request.

## 📜 License
This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.
