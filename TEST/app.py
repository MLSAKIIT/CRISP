from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

PORT = 8001

@app.route('/', methods=['GET'])
def home():
    try:
        # Open a database connection and fetch entries
        with sqlite3.connect('./Captured_requests.db') as database:
            cursor = database.cursor()
            cursor.execute('SELECT * FROM all_requests ORDER BY Request_Number DESC')
            entries = cursor.fetchall()  # Fetch all results

        # Render the entries in the template
        return render_template("home.html", entries=entries)

    except sqlite3.Error as e:
        # Handle database connection or query errors
        print(f"Database error: {e}")
        return "An error occurred while fetching data from the database."

if __name__ == "__main__":
    app.run(port=PORT)
