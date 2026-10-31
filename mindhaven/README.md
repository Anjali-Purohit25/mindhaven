# 🌿 MindHaven — Mental Health Support & Emotional Sanctuary

A full-stack web application built with **HTML5, CSS3, Python (Flask), and MySQL**.

---

## 🌟 Why this project stands out in an Interview
1. **Meaningful Social & Psychological Impact:** Solves real human struggles around stress, anxiety, imposter syndrome, and burnout. Interviewers deeply appreciate mission-driven projects.
2. **Data Privacy & Ethics:** 
   - Anonymized community venting with **zero toxic comments** allowed (only silent empathy hugs/support reactions).
   - **The Thought Shredder:** Permanently destroys heavy/intrusive thoughts from server memory with zero database footprint for psychological release.
   - Secure password hashing using PBKDF2/SHA256 (`werkzeug.security`).
3. **Advanced Relational SQL Queries:**
   - Aggregations and grouping (`GROUP BY trigger_category`, `AVG(intensity)`, `COUNT(*)`) to calculate weekly stress factors.
   - Unique constraints on empathy reactions to prevent duplicate clicks per user.
4. **Accessible Frontend Design:**
   - 100% pure CSS3 **4-7-8 Deep Relaxation Breathing Pacer** with keyframe animations.
   - 5-4-3-2-1 Sensory Grounding Technique for acute anxiety attacks.
   - Soothing, serene color palette (Sage green, warm ivory, soft lavender) adhering to psychological color theory.

---

## 📁 Project Architecture
```text
C:\Users\Dell\mindhaven\
│
├── app.py              # Flask controllers, session handling & routes
├── db.py               # MySQL connection pool handler
├── schema.sql          # Relational database schema & seed vents
├── init_db.py          # Database initializer script
├── run.bat             # 1-click launcher for Windows
│
├── static/
│   └── css/
│       └── style.css   # Calming styling, 4-7-8 breathing animation
│
└── templates/
    ├── base.html       # Base navigation, alerts & emergency helpline footer
    ├── welcome.html    # Peaceful landing page
    ├── login.html      # Confidential sign in
    ├── register.html   # Anonymous pseudonym registration
    ├── dashboard.html  # Daily emotional check-in & gratitude journal
    ├── shredder.html   # The Thought Shredder (burn into the void)
    ├── vent_wall.html  # Anonymous community empathy wall (hugs & support)
    ├── grounding.html  # 4-7-8 breathing circle & 5-4-3-2-1 grounding toolkit
    └── analytics.html  # SQL aggregate insights (stress triggers & averages)
```

---

## 🗄️ Database Tables (`mindhaven_db`)
- **`users`**: Confidential credentials and password hashes.
- **`mood_logs`**: Emotion type, intensity (1-10), life trigger category, reflection note, and log date.
- **`vents`**: Anonymous community posts with emotional tags and reaction counters.
- **`empathy_reactions`**: Tracks virtual hugs (🫂) and support (🤍) with composite unique constraints.
- **`gratitudes`**: Daily grounding notes to rewire negative thought loops.

---

## 🚀 How to Run
1. Make sure MySQL is running in XAMPP.
2. Open terminal in `C:\Users\Dell\mindhaven` and run:
   ```bash
   python app.py
   ```
   *(Or double-click `run.bat`!)*
3. Visit: **http://127.0.0.1:5000** in your browser.
