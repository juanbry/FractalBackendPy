from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hola Fractal, esto fue hecho en Flask por Juan Carranza'

if __name__ == '__main__':
    app.run(debug=True)  # Esto ejecutará el servidor de desarrollo
