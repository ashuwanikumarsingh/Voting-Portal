from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
import sqlite3
import os
import pandas as pd
from datetime import datetime
import secrets
from voter_generator import VoterGenerator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database setup
DB_FOLDER = os.path.join(os.path.dirname(__file__), 'databases')
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# Initialize voter generator
voter_generator = VoterGenerator(DB_FOLDER)

def get_db_connection(db_name):
    db_path = os.path.join(DB_FOLDER, f'{db_name}.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_databases():
    # Users database
    conn = get_db_connection('users')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dob TEXT NOT NULL,
        age INTEGER NOT NULL,
        aadhaar TEXT UNIQUE NOT NULL,
        city TEXT NOT NULL,
        nri TEXT NOT NULL,
        phone TEXT,
        pin TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Elections database
    conn.execute('''CREATE TABLE IF NOT EXISTS elections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        election_number TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

    # Votes database
    conn = get_db_connection('votes')
    conn.execute('''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        election_id INTEGER NOT NULL,
        vote TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

    # Invalid attempts database
    conn = get_db_connection('invalid_attempts')
    conn.execute('''CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aadhaar TEXT NOT NULL,
        reason TEXT NOT NULL,
        closed_attempt TEXT NOT NULL DEFAULT 'No',
        underage_attempt TEXT NOT NULL DEFAULT 'No',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

    # Ensure invalid attempts columns exist for older databases
    conn = get_db_connection('invalid_attempts')
    def add_column_if_missing(connection, table, column, definition):
        existing = [row['name'] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in existing:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    add_column_if_missing(conn, 'attempts', 'closed_attempt', "TEXT NOT NULL DEFAULT 'No'")
    add_column_if_missing(conn, 'attempts', 'underage_attempt', "TEXT NOT NULL DEFAULT 'No'")
    conn.commit()
    conn.close()

    # Parties database
    conn = get_db_connection('parties')
    conn.execute('''CREATE TABLE IF NOT EXISTS parties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        code TEXT UNIQUE NOT NULL,
        flag TEXT NOT NULL,
        color TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM parties")
    if cursor.fetchone()[0] == 0:
        default_parties = [
            ('BJP', 'BJP', '🟠', '#f97316'),
            ('Congress', 'INC', '🟢', '#22c55e'),
            ('AIMIM', 'AIMIM', '🟡', '#fde047'),
            ('TMC', 'TMC', '🟣', '#a855f7'),
            ('Samajwadi Party', 'SP', '🔵', '#2563eb'),
            ('AAP', 'AAP', '⚪', '#0ea5e9')
        ]
        conn.executemany('INSERT INTO parties (name, code, flag, color) VALUES (?, ?, ?, ?)', default_parties)
    conn.commit()
    conn.close()

    # Create default election
    conn = get_db_connection('users')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM elections")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO elections (election_number) VALUES (?)", ('001',))
    conn.commit()
    conn.close()

init_databases()

def get_user_aadhaar(user_id):
    conn = get_db_connection('users')
    user = conn.execute('SELECT aadhaar FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user['aadhaar'] if user else 'Unknown'


def log_invalid_attempt(aadhaar, reason, closed=False, underage=False):
    conn = get_db_connection('invalid_attempts')
    conn.execute(
        'INSERT INTO attempts (aadhaar, reason, closed_attempt, underage_attempt) VALUES (?, ?, ?, ?)',
        (aadhaar, reason, 'Yes' if closed else 'No', 'Yes' if underage else 'No')
    )
    conn.commit()
    conn.close()


@app.route('/')
def home():
    # Check if there's an active election and if counting is done
    conn = get_db_connection('users')
    election = conn.execute('SELECT * FROM elections ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    
    results = None
    show_results = False
    if election and election['status'] == 'counting_done':
        conn = get_db_connection('votes')
        results = conn.execute('''
            SELECT vote, COUNT(*) as count
            FROM votes
            WHERE election_id = ?
            GROUP BY vote
            ORDER BY count DESC
        ''', (election['id'],)).fetchall()
        conn.close()
        show_results = True
    
    return render_template('index.html', results=results, show_results=show_results, election=election)

@app.route('/login_default')
def login_default():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        aadhaar = request.form['aadhaar']
        city = request.form['city']
        nri = request.form['nri']
        phone = request.form.get('phone', '')
        pin = request.form['pin']

        # Validate pin
        if not pin.isdigit() or len(pin) != 4:
            flash('PIN must be exactly 4 digits.', 'error')
            return redirect(url_for('register'))

        # Calculate age
        birth_date = datetime.strptime(dob, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        try:
            conn = get_db_connection('users')
            conn.execute('''INSERT INTO users (name, dob, age, aadhaar, city, nri, phone, pin)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (name, dob, age, aadhaar, city, nri, phone, pin))
            conn.commit()
            conn.close()

            flash('Registration successful! Please remember your 4-digit PIN.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Aadhaar number already registered!', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        pin = request.form['pin']

        # Check for admin login
        if aadhaar == '452545254525' and pin == '4525':
            session['admin'] = True
            session['user_type'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        # Check for Election Commission
        if aadhaar == '111111111111' and pin == '1111':
            session['admin'] = True
            session['user_type'] = 'election_commission'
            return redirect(url_for('admin_dashboard'))

        # Regular user login
        conn = get_db_connection('users')
        user = conn.execute('SELECT * FROM users WHERE aadhaar = ? AND pin = ?',
                          (aadhaar, pin)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_age'] = user['age']
            return redirect(url_for('vote'))
        else:
            flash('Invalid credentials!', 'error')

    return render_template('login.html')

@app.route('/forgot_pin', methods=['GET', 'POST'])
def forgot_pin():
    if request.method == 'POST':
        phone = request.form['phone']
        if not phone:
            flash('Phone number is required.', 'error')
            return redirect(url_for('forgot_pin'))
        
        conn = get_db_connection('users')
        user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
        if user:
            new_pin = str(secrets.randbelow(10000)).zfill(4)
            conn.execute('UPDATE users SET pin = ? WHERE phone = ?', (new_pin, phone))
            conn.commit()
            flash(f'Your new PIN is: {new_pin}. Please save it securely.', 'success')
            return redirect(url_for('login'))
        else:
            flash('No user found with this phone number.', 'error')
        conn.close()
    
    return render_template('forgot_pin.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Check if voting is closed
    conn = get_db_connection('users')
    election = conn.execute('SELECT * FROM elections ORDER BY id DESC LIMIT 1').fetchone()
    voting_closed = election['status'] == 'closed'
    counting_done = election['status'] == 'counting_done'
    conn.close()

    conn = get_db_connection('parties')
    parties = conn.execute('SELECT * FROM parties ORDER BY id').fetchall()
    conn.close()

    if voting_closed or counting_done:
        aadhaar = get_user_aadhaar(session['user_id'])
        log_invalid_attempt(aadhaar, 'Voting closed', closed=True, underage=False)
        flash('❌ Voting is closed. Please wait for the next election.', 'error')
        return redirect(url_for('view_results'))

    if request.method == 'POST':
        user_age = session.get('user_age', 0)
        if user_age < 18:
            aadhaar = get_user_aadhaar(session['user_id'])
            log_invalid_attempt(aadhaar, 'Underage voting attempt', closed=False, underage=True)
            flash('❌ You are not eligible to vote (under 18).', 'error')
            return redirect(url_for('vote'))

        vote_choice = request.form['vote']
        user_id = session['user_id']

        conn = get_db_connection('votes')
        conn.execute('INSERT INTO votes (user_id, election_id, vote) VALUES (?, ?, ?)',
                    (user_id, election['id'], vote_choice))
        conn.commit()
        conn.close()

        flash('Vote cast successfully!', 'success')
        return redirect(url_for('vote'))

    return render_template('vote.html', parties=parties)

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))

    user_type = session.get('user_type', 'admin')

    # Get election status
    conn = get_db_connection('users')
    election = conn.execute('SELECT * FROM elections ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()

    conn = get_db_connection('parties')
    parties = conn.execute('SELECT * FROM parties ORDER BY id').fetchall()
    conn.close()
    
    # Get voter generator status
    generator_status = voter_generator.get_status()

    return render_template('admin_dashboard.html', election=election, user_type=user_type, parties=parties, generator_status=generator_status)

@app.route('/manage_parties', methods=['POST'])
def manage_parties():
    if not session.get('admin'):
        return redirect(url_for('login'))

    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    flag = request.form.get('flag', '').strip() or '🏳️'
    color = request.form.get('color', '#0ea5e9').strip() or '#0ea5e9'

    if not name or not code:
        flash('Party name and code are required.', 'error')
        return redirect(url_for('admin_dashboard'))

    try:
        conn = get_db_connection('parties')
        conn.execute('INSERT INTO parties (name, code, flag, color) VALUES (?, ?, ?, ?)',
                    (name, code, flag, color))
        conn.commit()
        conn.close()
        flash(f'Party {name} added successfully.', 'success')
    except sqlite3.IntegrityError:
        flash('Party name or code already exists.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/toggle_voting', methods=['POST'])
def toggle_voting():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = get_db_connection('users')
    election = conn.execute('SELECT * FROM elections ORDER BY id DESC LIMIT 1').fetchone()

    if election['status'] == 'open':
        conn.execute('UPDATE elections SET status = ? WHERE id = ?',
                    ('closed', election['id']))
    elif election['status'] == 'closed':
        conn.execute('UPDATE elections SET status = ? WHERE id = ?',
                    ('counting_done', election['id']))
    elif election['status'] == 'counting_done':
        next_number = str(int(election['election_number']) + 1).zfill(3)
        conn.execute('INSERT INTO elections (election_number, status) VALUES (?, ?)',
                    (next_number, 'open'))

    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/start_counting', methods=['POST'])
def start_counting():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = get_db_connection('users')
    election = conn.execute('SELECT * FROM elections ORDER BY id DESC LIMIT 1').fetchone()
    conn.execute('UPDATE elections SET status = ? WHERE id = ?',
                ('counting_done', election['id']))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/start_voter_generator', methods=['POST'])
def start_voter_generator():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    voter_generator.start()
    flash('✅ Voter generator started! Random voters will be registered and voted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/stop_voter_generator', methods=['POST'])
def stop_voter_generator():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    status = voter_generator.get_status()
    voter_generator.stop()
    flash(f'⛔ Voter generator stopped. Total voters generated: {status["voter_count"]}', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/generator_status', methods=['GET'])
def generator_status():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    status = voter_generator.get_status()
    return jsonify(status)

@app.route('/realtime_votes', methods=['GET'])
def realtime_votes():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    votes = voter_generator.get_realtime_votes()
    return jsonify(votes)

@app.route('/past_elections')
def past_elections():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    # Get all completed elections
    conn = get_db_connection('users')
    elections = conn.execute('SELECT * FROM elections WHERE status = ? ORDER BY id DESC', ('counting_done',)).fetchall()
    conn.close()
    
    # Get results for each election
    past_results = []
    for election in elections:
        conn = get_db_connection('votes')
        results = conn.execute('''
            SELECT vote, COUNT(*) as count
            FROM votes
            WHERE election_id = ?
            GROUP BY vote
            ORDER BY count DESC
        ''', (election['id'],)).fetchall()
        conn.close()
        
        past_results.append({
            'election': election,
            'results': results
        })
    
    return render_template('past_elections.html', past_results=past_results)

@app.route('/results')
def public_results():
    # Check if there's a completed election to show results
    conn = get_db_connection('users')
    election = conn.execute('SELECT * FROM elections WHERE status = ? ORDER BY id DESC LIMIT 1', ('counting_done',)).fetchone()
    conn.close()

    results = None
    if election:
        if election['status'] == 'counting_done':
            conn = get_db_connection('votes')
            results = conn.execute('''
                SELECT vote, COUNT(*) as count
                FROM votes
                WHERE election_id = ?
                GROUP BY vote
                ORDER BY count DESC
            ''', (election['id'],)).fetchall()
            conn.close()
        else:
            results = []

    return render_template('index.html', results=results, election=election, show_results=(election is not None and election['status'] == 'counting_done'))

@app.route('/view_results')
def view_results():
    return redirect(url_for('public_results'))

@app.route('/view_database/<db_name>')
def view_database(db_name):
    if not session.get('admin'):
        return redirect(url_for('login'))

    if db_name not in ['users', 'votes', 'invalid_attempts', 'parties']:
        return "Invalid database", 400

    conn = get_db_connection(db_name)
    if db_name == 'users':
        rows = conn.execute("SELECT id, name, dob, age, aadhaar, city, nri, phone, created_at FROM users ORDER BY id DESC").fetchall()
        columns = ['ID', 'Name', 'DOB', 'Age', 'Aadhaar', 'City', 'NRI', 'Phone', 'Created At']
    elif db_name == 'votes':
        rows = conn.execute("SELECT id, user_id, election_id, vote, timestamp FROM votes ORDER BY id DESC").fetchall()
        columns = ['ID', 'User ID', 'Election ID', 'Vote', 'Timestamp']
    elif db_name == 'parties':
        rows = conn.execute("SELECT id, name, code, flag, color, created_at FROM parties ORDER BY id DESC").fetchall()
        columns = ['ID', 'Name', 'Code', 'Flag', 'Color', 'Created At']
    else:
        rows = conn.execute("SELECT id, aadhaar, reason, timestamp FROM attempts ORDER BY id DESC").fetchall()
        columns = ['ID', 'Aadhaar', 'Reason', 'Timestamp']
    conn.close()

    return render_template('database_view.html', db_name=db_name, columns=columns, rows=rows)

@app.route('/download/<db_name>')
def download_database(db_name):
    if not session.get('admin'):
        return redirect(url_for('login'))

    if db_name not in ['users', 'votes', 'invalid_attempts', 'parties']:
        return "Invalid database", 400

    conn = get_db_connection(db_name)
    if db_name == 'users':
        df = pd.read_sql_query("SELECT id, name, dob, age, aadhaar, city, nri, phone, created_at FROM users", conn)
    elif db_name == 'votes':
        df = pd.read_sql_query("SELECT * FROM votes", conn)
    elif db_name == 'parties':
        df = pd.read_sql_query("SELECT id, name, code, flag, color, created_at FROM parties", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM attempts", conn)
    conn.close()

    excel_path = os.path.join(DB_FOLDER, f'{db_name}_data.xlsx')
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)