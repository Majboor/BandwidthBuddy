# BandwidthBuddy

**Purpose**: BandwidthBuddy was created to give macOS users fine‑grained visibility and control over per‑application network usage—helping you spot idle consumers, catch anomalies, and throttle or kill bandwidth hogs that your ISP won’t.

---

## 🚀 Features

* **Per‑App Monitoring**: Fetches live network I/O for each process via `nettop`.
* **Menu‑Bar Display**: Real‑time usage bars show top consumers at a glance.
* **Alerts & Notifications**: macOS notifications fire when an app exceeds your custom threshold.
* **Process Control**: Kill or force‑kill misbehaving apps directly from the menu.
* **Grouping**: Automatically categorizes processes into “Browser”, “Programming & IDE”, “Extras”, “System”, or “Unknown.”
* **Auto‑Refresh**: Data updates every 10 seconds.

## ⚙️ Prerequisites

* **macOS** (Catalina or later)
* **Python 3.8+**

## 🛠️ Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/majboors/bandwidthbuddy.git
   cd bandwidthbuddy
   ```
2. **(No `requirements.txt` yet)**

   * We’re still building dependencies— please help create `requirements.txt`!
3. **Run the app**

   * Easiest: double-click `dist/wifimonitor.app`
   * Or via CLI:

     ```bash
     python SRC-Code/test26.py
     ```

> BandwidthBuddy uses [rumps](https://pypi.org/project/rumps/) and relies on macOS’s built‑in `nettop` tool.

## 📦 Usage

* Launch via one of the methods above.
* Click the menubar icon to see live network usage, kill processes, or quit.

## 🛡️ Configuration

Edit `SRC-Code/test26.py` to adjust:

* `ALERT_MB_THRESHOLD` (MB before alert)
* `RED_BAR_THRESHOLD_MB` (MB for red bar)
* `GROUPS` dictionary for process categories

## 🤝 Contributing

Looking for help to:

* **Dependencies**: Generate a complete `requirements.txt`.
* **Performance**: Optimize `nettop` parsing.
* **Features**: Add real per‑IP throttling, preferences panel, or logging.
* **Testing**: Write unit tests for parsing and UI callbacks.

Open issues or PRs; please follow PEP 8 and include tests.

## 📄 License

Released under the **MIT License**. See [LICENSE](LICENSE).

---

> *BandwidthBuddy* © 2025 Waleed Ajmal | [GitHub](https://github.com/majboors/) | [Email](mailto:info@techrealm.pk)
