from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-key")
DB = os.path.join(os.path.dirname(__file__), "quizboard.db")

QUIZZES = {
    "python": {"title": "Python Basics", "questions": [
        ("Which keyword defines a Python function?", ["function", "def", "define", "fun"], 1),
        ("Which type stores True or False?", ["str", "int", "bool", "list"], 2),
        ("What is 3 * 2?", ["5", "6", "9", "32"], 1),
        ("Which symbol starts a Python comment?", ["//", "<!--", "#", "/*"], 2),
        ("Which collection stores key-value pairs?", ["List", "Tuple", "Dictionary", "Set"], 2)]},
    "web": {"title": "Web Development", "questions": [
        ("What does HTML stand for?", ["HyperText Markup Language", "HighText Machine Language", "Hyper Tool Multi Language", "HomeText Markup Language"], 0),
        ("Which language styles a web page?", ["SQL", "CSS", "Python", "C"], 1),
        ("Which HTML tag creates a hyperlink?", ["<link>", "<href>", "<a>", "<url>"], 2),
        ("Which keyword declares a block-scoped JavaScript variable?", ["var", "let", "define", "dim"], 1),
        ("Which HTTP method commonly retrieves data?", ["GET", "POST", "DELETE", "PATCH"], 0)]},
    "database": {"title": "Database Fundamentals", "questions": [
        ("What does SQL stand for?", ["Structured Query Language", "Simple Question Language", "System Query List", "Sequential Query Logic"], 0),
        ("Which key uniquely identifies a row?", ["Foreign key", "Primary key", "Duplicate key", "Search key"], 1),
        ("Which command retrieves database records?", ["GET", "OPEN", "SELECT", "FETCH TABLE"], 2),
        ("Which command adds a new row?", ["INSERT", "UPDATE", "ALTER", "DROP"], 0),
        ("What is the purpose of a foreign key?", ["Style a table", "Connect related tables", "Delete a database", "Rename columns"], 1)]}
}

BASE = r'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{ title }} | QuizBoard</title><style>
*{box-sizing:border-box}body{margin:0;background:#f7f6fc;color:#211d35;font-family:Arial,sans-serif;line-height:1.6}nav{background:#fff;padding:18px 7%;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e9e5f3}nav a{text-decoration:none;color:#6250d9;font-weight:bold;margin-left:20px}.logo{font-size:23px;margin-left:0}main{max-width:1050px;width:90%;margin:35px auto;min-height:70vh}.hero{background:linear-gradient(120deg,#654be0,#9b82ff);color:#fff;padding:48px;border-radius:22px;margin-bottom:35px}.hero h1{font-size:42px;line-height:1.2;margin:10px 0}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.card,.panel{background:#fff;padding:25px;border-radius:17px;border:1px solid #e9e5f3;margin-bottom:18px}.card h2{font-size:21px}.btn{display:inline-block;border:0;border-radius:9px;padding:12px 17px;background:#6d54e8;color:#fff;text-decoration:none;font-weight:bold;cursor:pointer}.btn:hover{background:#5139c7}.dark{background:#211d35}input[type=text]{width:100%;padding:13px;border:1px solid #d9d3eb;border-radius:9px;margin:8px 0 18px}.option{display:block;padding:13px;margin:10px 0;border:1px solid #e5e0f0;border-radius:10px;cursor:pointer}.option:hover{background:#f3f0ff}.progress{background:#e8e3f7;height:8px;border-radius:10px;margin:20px 0}.bar{height:8px;background:#6d54e8;border-radius:10px;width:0}.muted{color:#77718b}table{width:100%;border-collapse:collapse;background:white}th,td{text-align:left;padding:13px;border-bottom:1px solid #eeeaf5}th{background:#eeeaff}footer{text-align:center;padding:25px;background:white;color:#77718b}[hidden]{display:none!important}@media(max-width:700px){.grid{grid-template-columns:1fr}.hero{padding:28px}.hero h1{font-size:32px}nav{padding:15px 5%}nav a{margin-left:8px}main{width:92%}.panel{padding:18px}table{font-size:13px}}
</style></head><body><nav><a class="logo" href="{{ url_for('home') }}">QuizBoard</a><div><a href="{{ url_for('home') }}">Quizzes</a><a href="{{ url_for('leaderboard') }}">Leaderboard</a></div></nav><main>{{ content|safe }}</main><footer>QuizBoard · Learn, play and improve</footer></body></html>'''

def page(content, title="QuizBoard", **context):
    return render_template_string(BASE, content=render_template_string(content, **context), title=title)

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, player TEXT NOT NULL, quiz TEXT NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL, percentage REAL NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

@app.route('/')
def home():
    return page('''<section class="hero"><p>LEARN · PLAY · IMPROVE</p><h1>Your knowledge.<br>Your next level.</h1><p>Choose a quiz, test your skills and see your score on the leaderboard.</p><a class="btn dark" href="#quizzes">Explore quizzes ↓</a></section><h2 id="quizzes">Choose your quiz</h2><div class="grid">{% for key, quiz in quizzes.items() %}<section class="card"><p class="muted">5 questions · Multiple choice</p><h2>{{ quiz.title }}</h2><p>Test your knowledge and improve your skills.</p><a class="btn" href="{{ url_for('start_quiz', key=key) }}">Start quiz →</a></section>{% endfor %}</div>''', 'Home', quizzes=QUIZZES)

@app.route('/start/<key>', methods=['GET','POST'])
def start_quiz(key):
    if key not in QUIZZES: return redirect(url_for('home'))
    if request.method == 'POST':
        player = ' '.join(request.form.get('player','').split())[:40]
        if not player: return 'Please enter your name.', 400
        session['player'], session['quiz'] = player, key
        return redirect(url_for('take_quiz', key=key))
    return page('''<section class="panel"><h1>{{ quiz.title }}</h1><p class="muted">There are 5 questions. Select the best answer.</p><form method="post"><label for="player">Enter your name</label><input id="player" name="player" maxlength="40" placeholder="Your name" required><button class="btn" type="submit">Start quiz →</button></form></section>''', QUIZZES[key]['title'], quiz=QUIZZES[key])

@app.route('/quiz/<key>')
def take_quiz(key):
    if key not in QUIZZES or session.get('quiz') != key: return redirect(url_for('home'))
    quiz = QUIZZES[key]
    return page(r'''<section class="panel"><h1>{{ quiz.title }}</h1><p>Player: <strong>{{ player }}</strong></p><p>Time remaining: <strong id="timer">02:00</strong></p><div class="progress"><div class="bar" id="bar"></div></div><form id="quizForm" method="post" action="{{ url_for('submit_quiz', key=key) }}">{% for q in quiz.questions %}{% set qi = loop.index0 %}<section class="question" {% if not loop.first %}hidden{% endif %}><p class="muted">Question {{ loop.index }} of {{ quiz.questions|length }}</p><h2>{{ q[0] }}</h2>{% for option in q[1] %}<label class="option"><input type="radio" name="q{{ qi }}" value="{{ loop.index0 }}"> {{ option }}</label>{% endfor %}<button class="btn next" type="button">{% if loop.last %}Review answers →{% else %}Next →{% endif %}</button></section>{% endfor %}<section id="review" hidden><h2>Ready to submit?</h2><p>Unanswered questions count as incorrect.</p><button class="btn" type="submit">Submit quiz</button></section></form></section><script>
const sections=[...document.querySelectorAll('.question')],review=document.getElementById('review'),bar=document.getElementById('bar'),form=document.getElementById('quizForm');let remaining=120,finished=false;function showQuestion(n){sections.forEach((s,i)=>s.hidden=i!==n);review.hidden=true;bar.style.width=((n+1)/sections.length*100)+'%'}document.querySelectorAll('.next').forEach((button,i)=>button.addEventListener('click',()=>{if(!sections[i].querySelector('input:checked')){alert('Please select an answer.');return}if(i<sections.length-1)showQuestion(i+1);else{sections.forEach(s=>s.hidden=true);review.hidden=false;bar.style.width='100%'}}));form.addEventListener('submit',()=>finished=true);function tick(){document.getElementById('timer').textContent=String(Math.floor(remaining/60)).padStart(2,'0')+':'+String(remaining%60).padStart(2,'0');if(remaining<=0&&!finished){finished=true;form.submit();return}if(remaining>0)remaining--;if(!finished)setTimeout(tick,1000)}tick();</script>''', quiz['title'], quiz=quiz, key=key, player=session.get('player','Player'))

@app.route('/submit/<key>', methods=['POST'])
def submit_quiz(key):
    if key not in QUIZZES or session.get('quiz') != key: return redirect(url_for('home'))
    quiz=QUIZZES[key]; score=0; review=[]
    for i,q in enumerate(quiz['questions']):
        try: selected=int(request.form.get(f'q{i}',''))
        except (ValueError,TypeError): selected=-1
        correct=selected==q[2]; score+=int(correct)
        chosen=q[1][selected] if 0<=selected<len(q[1]) else 'Not answered'
        review.append({'question':q[0],'selected':chosen,'answer':q[1][q[2]],'correct':correct})
    total=len(quiz['questions']); percentage=round(score*100/total,1); player=session.get('player','Player')
    with sqlite3.connect(DB) as con: con.execute('INSERT INTO results (player,quiz,score,total,percentage) VALUES (?,?,?,?,?)',(player,quiz['title'],score,total,percentage))
    session.pop('quiz',None); session['last_result']={'player':player,'quiz':quiz['title'],'score':score,'total':total,'percentage':percentage,'review':review}
    return redirect(url_for('result'))

@app.route('/result')
def result():
    r=session.get('last_result')
    if not r: return redirect(url_for('home'))
    return page('''<section class="panel"><h1>Quiz completed, {{ r.player }}!</h1><p>You completed {{ r.quiz }}.</p><h2>Your score: {{ r.score }}/{{ r.total }}</h2><h2>{{ r.percentage }}%</h2><a class="btn" href="{{ url_for('leaderboard') }}">View leaderboard</a> <a class="btn dark" href="{{ url_for('home') }}">Try another quiz</a></section><h2>Answer review</h2>{% for a in r.review %}<section class="card"><h3>{{ loop.index }}. {{ a.question }}</h3><p>Your answer: {{ a.selected }}</p>{% if a.correct %}<p style="color:green">Correct!</p>{% else %}<p style="color:#c33">Correct answer: {{ a.answer }}</p>{% endif %}</section>{% endfor %}''','Results',r=r)

@app.route('/leaderboard')
def leaderboard():
    with sqlite3.connect(DB) as con:
        con.row_factory=sqlite3.Row
        rows=con.execute('SELECT player,quiz,score,total,percentage,created_at FROM results ORDER BY percentage DESC,score DESC,created_at ASC LIMIT 100').fetchall()
    return page('''<h1>🏆 Leaderboard</h1><p class="muted">Top quiz attempts, ranked by percentage and score.</p><section class="panel">{% if rows %}<table><thead><tr><th>Rank</th><th>Player</th><th>Quiz</th><th>Score</th><th>Percentage</th></tr></thead><tbody>{% for row in rows %}<tr><td>{% if loop.index==1 %}🥇{% elif loop.index==2 %}🥈{% elif loop.index==3 %}🥉{% else %}{{ loop.index }}{% endif %}</td><td>{{ row.player }}</td><td>{{ row.quiz }}</td><td>{{ row.score }}/{{ row.total }}</td><td>{{ row.percentage }}%</td></tr>{% endfor %}</tbody></table>{% else %}<h2>No scores yet!</h2><p>Take a quiz to become the first player on the leaderboard.</p>{% endif %}</section><a class="btn" href="{{ url_for('home') }}">← Back to quizzes</a>''','Leaderboard',rows=rows)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
