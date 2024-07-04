from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_script', methods=['POST', 'GET'])
def run_script():
    subprocess.run(['python', 'script/sunkiss.py'], check=True)

if __name__ == '__main__':
    app.run(debug=True)
