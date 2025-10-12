from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {"status": "OK"}

if __name__ == '__main__':
    app.run(port=8000, debug=False, host='0.0.0.0')
