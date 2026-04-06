# 🚀 Quick Start Guide

Get the AI Interview Platform running in **under 5 minutes**!

## ⚡ Fast Setup

### 1️⃣ Open PowerShell in project folder

```powershell
cd Desktop
cd "AI-Powered Interview Simulation Platform"
```

### 2️⃣ Create & activate virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*You should see `(venv)` at the start of your terminal line*

### 3️⃣ Install dependencies

```powershell
pip install -r requirements.txt
```

### 4️⃣ Run the application

```powershell
python app.py
```

✅ You should see:
```
🚀 AI Interview Simulation Platform - Starting...
📊 Backend: Flask | Database: SQLite | AI Engines: Active
🌐 Server running on: http://localhost:5000
📖 Login at: http://localhost:5000/login
```

### 5️⃣ Open in browser

Go to: **http://localhost:5000**

---

## 📝 First-Time Setup

1. **Register** a new account
   - Username: `testuser`
   - Password: `testpass123`

2. **Explore Dashboard**
   - View your stats
   - See interview options

3. **Start Interview**
   - Choose interview type (HR/Technical/Product)
   - Answer 5-7 questions
   - Get instant feedback

4. **View Results**
   - Check your score
   - See skill breakdown
   - Read AI suggestions

---

## ⏹️ Stop the Server

Press: **Ctrl+C** in the terminal

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError" | Run: `pip install -r requirements.txt` |
| "Port 5000 in use" | Change port in app.py (last line) |
| Styling broken | Refresh browser: Ctrl+Shift+R |
| Database error | Delete `database.db` and restart |

---

## 📞 Need Help?

See **README.md** for detailed documentation.

---

**Ready? Go to: http://localhost:5000** 🚀
