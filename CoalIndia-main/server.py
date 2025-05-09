from flask import Flask, render_template,request, redirect, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        print("✅ Message stored successfully!")
        return redirect('/success')
    except Exception as e:
        print(f"❌ Error: {e}")
        return "An error occurred. Please try again later."    

# Route to display success message
@app.route('/success')
def success():
    return "<h2>Message Sent Successfully!</h2>"

 
@app.route('/')
def home():
    
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        message = data['message']

        conn = sqlite3.connect('contact.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()
        conn.close()

        return jsonify({"message": "Form submitted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
