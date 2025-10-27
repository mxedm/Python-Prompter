# Python Prompter

A simple, web-based teleprompter application controlled from a separate device. Ideal for local setups using a laptop for control and a tablet or second monitor as the prompter display.

## Features

- **Web-based Interface**: No complex software installation needed on the prompter device, just a web browser.
- **Remote Control**: Control the prompter from a separate browser window or device in real-time.
- **Multiple File Formats**: Load scripts from `.txt`, `.docx`, and `.rtf` files.
- **Real-time Controls & Shortcuts**:
  - **Start/Stop**: `Spacebar` to toggle scrolling.
  - **Speed**: Adjust with UI buttons or `ArrowUp` / `ArrowDown`.
  - **Jump**: Move through the script with `PageUp` / `PageDown`.
  - **Font Size**: Adjust with UI buttons or `A` / `Z`.
  - **Mirror/Flip**: Flip text horizontally (`X`) and vertically (`Y`) for physical teleprompter mirrors.
  - **Fit to Screen**: Automatically scale font to fit the prompter screen (`F`).
- **Status Dashboard**: The control panel shows the status of the server, connected prompters, and script state.

## Quick Start

These instructions assume you have Python 3 installed.

### 1. Create and activate a virtual environment

```bash
# For macOS / Linux
python -m venv .venv
source .venv/bin/activate

# For Windows
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run server

```bash
python app.py
```

4. Open control UI on the primary display: http://localhost:5000/
5. Open prompter on the second display: http://localhost:5000/prompter

These do not have to be on the server. Replace localhost with the server's IP if using a different computer.

Notes

- The prompter page is read-only — all controls are on the control page.
- Upload `.txt` (split paragraphs with a blank line), '.rtf', or `.docx` (mammoth is used if installed) files.
- Defaults for speed/font/flip use the HTML control values. Controls send Socket.IO events to the prompter.

# SUPER SIMPLE START

To start the teleprompter server, just run:

```bash
python prompter.py
```

That's it.

The control UI will be at http://localhost:5000/
The prompter UI is on http://localhost:5000/prompter
