# Contributing to DrowsApp Studio

Thank you for your interest in contributing to **DrowsApp Studio**! We welcome bug reports, feature enhancements, documentation improvements, and pull requests.

---

## 🛠️ Getting Started

### 1. Fork and Clone
1. Fork the repository on GitHub: [https://github.com/Aeonsmith/DrowsApp-Studio](https://github.com/Aeonsmith/DrowsApp-Studio)
2. Clone your fork locally:
   ```powershell
   git clone https://github.com/YOUR_USERNAME/DrowsApp-Studio.git
   cd DrowsApp-Studio
   ```

### 2. Set Up Development Environment
1. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install project dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🌿 Branching & Development Workflow

1. Create a new topic branch from `main`:
   ```powershell
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```
2. Implement your changes following existing code conventions and modular patterns.
3. Test all modules locally to verify zero regressions:
   ```powershell
   python main.py
   ```

---

## 📝 Code Conventions & Standards

- **Python Style**: Adhere to PEP 8 style standards.
- **Modularity**: Place reusable backend logic in `modules/` and keep GUI components encapsulated as `tk.Frame` subclasses.
- **Thread Safety**: Never block the main Tkinter UI thread with heavy computational or I/O loops (e.g. video capture, audio playback, or heavy matrix multiplications). Decouple background tasks using Python daemon threads or asynchronous worker queues.
- **Error Handling**: Gracefully handle missing webcam hardware, audio drivers, and missing model files.

---

## 💬 Commit Guidelines

Write clear, declarative commit messages using conventional prefixes:
- `feat:` for new features or user-facing enhancements
- `fix:` for bug fixes
- `docs:` for documentation updates
- `refactor:` for code restructuring without behavioral changes
- `perf:` for performance optimizations

When committing, include co-author attribution where appropriate:
```text
feat: add dark mode theme toggle to canvas studio

Co-Authored-By: Warp <agent@warp.dev>
```

---

## 🚀 Submitting a Pull Request (PR)

1. Push your branch to your GitHub fork:
   ```powershell
   git push -u origin feature/your-feature-name
   ```
2. Open a Pull Request targeting the `main` branch of `Aeonsmith/DrowsApp-Studio`.
3. Provide a concise summary of the changes, problem solved, and verification steps taken (e.g. test results or screenshots).

---

## 🐛 Reporting Bugs & Suggesting Features

- **Bug Reports**: Open an issue detailing your OS, Python version, steps to reproduce, and any error tracebacks.
- **Feature Requests**: Open an issue describing the proposed feature, intended use case, and potential implementation approach.

---

## 📜 Code of Conduct

Be welcoming, respectful, and constructive in all community interactions.
