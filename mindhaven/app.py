from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "mindhaven_serenity_secret_safe_key_98765"

EMOTION_META = {
    "Calm": {"emoji": "🌿", "color": "#7EA172"},
    "Grateful": {"emoji": "✨", "color": "#E9C46A"},
    "Hopeful": {"emoji": "🌱", "color": "#52B788"},
    "Anxious": {"emoji": "⚡", "color": "#E76F51"},
    "Overwhelmed": {"emoji": "🌊", "color": "#457B9D"},
    "Exhausted": {"emoji": "💤", "color": "#6D6875"},
    "Sad": {"emoji": "🌧️", "color": "#4A6FA5"},
    "Frustrated": {"emoji": "🔥", "color": "#D62828"}
}

@app.context_processor
def inject_metadata():
    return dict(emotion_meta=EMOTION_META)

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("welcome.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for("register"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing = cursor.fetchone()

        if existing:
            flash("That username is taken. Feel free to choose an anonymous pseudonym.", "error")
            cursor.close()
            conn.close()
            return redirect(url_for("register"))

        pwd_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, pwd_hash))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Welcome to your sanctuary. Please sign in to begin.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}. Take a gentle breath.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Your privacy is safe with us.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out safely. Take care of yourself today.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    today = date.today()

    # Check if mood logged today
    cursor.execute(
        "SELECT * FROM mood_logs WHERE user_id = %s AND logged_date = %s ORDER BY id DESC LIMIT 1",
        (user_id, today)
    )
    today_mood = cursor.fetchone()

    # Recent mood logs
    cursor.execute(
        "SELECT * FROM mood_logs WHERE user_id = %s ORDER BY logged_date DESC, id DESC LIMIT 5",
        (user_id,)
    )
    recent_moods = cursor.fetchall()

    # Gratitudes
    cursor.execute(
        "SELECT * FROM gratitudes WHERE user_id = %s ORDER BY id DESC LIMIT 4",
        (user_id,)
    )
    gratitudes = cursor.fetchall()

    # Recent diary entry snippet
    cursor.execute(
        "SELECT * FROM diary_entries WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    latest_diary = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        today_str=today.strftime("%A, %B %d"),
        today_mood=today_mood,
        recent_moods=recent_moods,
        gratitudes=gratitudes,
        latest_diary=latest_diary
    )

@app.route("/mood/log", methods=["POST"])
def log_mood():
    if "user_id" not in session:
        return redirect(url_for("login"))

    emotion = request.form.get("emotion")
    intensity = int(request.form.get("intensity", 5))
    trigger = request.form.get("trigger_category", "General")
    note = request.form.get("note", "").strip()
    today = date.today()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO mood_logs (user_id, emotion, intensity, trigger_category, note, logged_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (session["user_id"], emotion, intensity, trigger, note, today)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Your emotional check-in has been recorded. Honoring your feelings is courage.", "success")
    return redirect(url_for("dashboard"))

@app.route("/gratitude/add", methods=["POST"])
def add_gratitude():
    if "user_id" not in session:
        return redirect(url_for("login"))

    content = request.form.get("content", "").strip()
    if content:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO gratitudes (user_id, content, logged_date) VALUES (%s, %s, %s)",
            (session["user_id"], content, date.today())
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Small moments of gratitude ground our nervous system. Added!", "success")

    return redirect(url_for("dashboard"))

# --- PRIVATE DIARY FEATURE ---
@app.route("/diary")
def diary():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    search_query = request.args.get("q", "").strip()
    mood_filter = request.args.get("mood", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    base_sql = "SELECT * FROM diary_entries WHERE user_id = %s"
    params = [user_id]

    if search_query:
        base_sql += " AND (title LIKE %s OR content LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    if mood_filter:
        base_sql += " AND mood_tag = %s"
        params.append(mood_filter)

    base_sql += " ORDER BY created_at DESC"

    cursor.execute(base_sql, tuple(params))
    entries = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("diary.html", entries=entries, search_query=search_query, mood_filter=mood_filter)

@app.route("/diary/create", methods=["POST"])
def create_diary():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip() or "Untitled Reflection"
    content = request.form.get("content", "").strip()
    mood_tag = request.form.get("mood_tag", "Reflective")

    if not content:
        flash("Diary content cannot be empty.", "error")
        return redirect(url_for("diary"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO diary_entries (user_id, title, content, mood_tag) VALUES (%s, %s, %s, %s)",
        (session["user_id"], title, content, mood_tag)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Your private thoughts are safely locked in your sanctuary journal. 📖", "success")
    return redirect(url_for("diary"))

@app.route("/diary/delete/<int:entry_id>", methods=["POST"])
def delete_diary(entry_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diary_entries WHERE id = %s AND user_id = %s", (entry_id, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Diary entry deleted.", "info")
    return redirect(url_for("diary"))

# --- ZEN CALM OASIS FEATURE ---
@app.route("/calm-zone")
def calm_zone():
    return render_template("calm_zone.html")

@app.route("/shredder", methods=["GET", "POST"])
def shredder():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        thought = request.form.get("thought", "").strip()
        action_type = request.form.get("action_type")
        emotion_tag = request.form.get("emotion_tag", "Overwhelmed")

        if not thought:
            flash("Please write a thought before releasing it.", "info")
            return redirect(url_for("shredder"))

        if action_type == "burn":
            flash("🔥 Thought incinerated into the void. It has no power over you now. Breathe easy.", "success")
            return render_template("shredder.html", burned=True)
        elif action_type == "share":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO vents (user_id, content, emotion_tag) VALUES (%s, %s, %s)",
                (session["user_id"], thought, emotion_tag)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Your thought was shared completely anonymously on the Empathy Wall. You are not alone.", "success")
            return redirect(url_for("vent_wall"))

    return render_template("shredder.html", burned=False)

@app.route("/vents")
def vent_wall():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT v.*,
            (SELECT COUNT(*) FROM empathy_reactions er WHERE er.vent_id = v.id AND er.user_id = %s AND er.reaction_type = 'hug') AS has_hugged,
            (SELECT COUNT(*) FROM empathy_reactions er WHERE er.vent_id = v.id AND er.user_id = %s AND er.reaction_type = 'support') AS has_supported
        FROM vents v
        ORDER BY v.id DESC
        LIMIT 20
    """
    cursor.execute(query, (user_id, user_id))
    vents = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("vent_wall.html", vents=vents)

@app.route("/vents/react/<int:vent_id>/<string:reaction_type>", methods=["POST"])
def react_vent(vent_id, reaction_type):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if reaction_type not in ["hug", "support"]:
        return redirect(url_for("vent_wall"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM empathy_reactions WHERE vent_id = %s AND user_id = %s AND reaction_type = %s",
        (vent_id, user_id, reaction_type)
    )
    already = cursor.fetchone()

    if not already:
        cursor.execute(
            "INSERT INTO empathy_reactions (vent_id, user_id, reaction_type) VALUES (%s, %s, %s)",
            (vent_id, user_id, reaction_type)
        )
        if reaction_type == "hug":
            cursor.execute("UPDATE vents SET hugs_count = hugs_count + 1 WHERE id = %s", (vent_id,))
        else:
            cursor.execute("UPDATE vents SET support_count = support_count + 1 WHERE id = %s", (vent_id,))
        conn.commit()
        flash("Empathy sent. Kindness echoes. 🤍", "success")
    else:
        flash("You already sent support to this soul! 🌸", "info")

    cursor.close()
    conn.close()
    return redirect(url_for("vent_wall"))

@app.route("/grounding")
def grounding():
    return render_template("grounding.html")

@app.route("/analytics")
def analytics():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_logs, AVG(intensity) AS avg_intensity FROM mood_logs WHERE user_id = %s", (user_id,))
    summary = cursor.fetchone()

    cursor.execute(
        """
        SELECT trigger_category, COUNT(*) AS count, ROUND(AVG(intensity), 1) as avg_stress
        FROM mood_logs
        WHERE user_id = %s
        GROUP BY trigger_category
        ORDER BY count DESC
        """,
        (user_id,)
    )
    triggers = cursor.fetchall()

    cursor.execute(
        """
        SELECT emotion, COUNT(*) AS count
        FROM mood_logs
        WHERE user_id = %s
        GROUP BY emotion
        ORDER BY count DESC
        """,
        (user_id,)
    )
    emotions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "analytics.html",
        summary=summary,
        triggers=triggers,
        emotions=emotions
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
