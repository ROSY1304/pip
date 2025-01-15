from flask import Flask, jsonify, send_from_directory, send_file
import os
import nbformat
from flask_cors import CORS

app = Flask(__name__, static_folder='static')

# Habilitar CORS para la aplicación completa
CORS(app)

# Directorio donde están los documentos .ipynb
DOCUMENTS_FOLDER = 'documentos'
app.config['DOCUMENTS_FOLDER'] = DOCUMENTS_FOLDER

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

# Endpoint para listar los documentos disponibles
@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    try:
        # Validar que el directorio existe
        if not os.path.exists(DOCUMENTS_FOLDER):
            return jsonify({"mensaje": "El directorio de documentos no existe"}), 404

        archivos = [f for f in os.listdir(DOCUMENTS_FOLDER) if f.endswith('.ipynb')]

        if not archivos:
            return jsonify({"mensaje": "No hay archivos .ipynb en el directorio"}), 404

        return jsonify(archivos), 200
    except Exception as e:
        return jsonify({"mensaje": str(e)}), 500

@app.route('/documentos/contenido/<nombre>', methods=['GET'])
def ver_contenido_documento(nombre):
    try:
        notebook_path = os.path.join(DOCUMENTS_FOLDER, nombre)

        # Validar existencia del archivo
        if not os.path.exists(notebook_path):
            return jsonify({'mensaje': 'Archivo no encontrado'}), 404

        # Validar extensión del archivo
        if not nombre.endswith('.ipynb'):
            return jsonify({'mensaje': 'Formato de archivo no soportado'}), 400

        if nombre == 'REGRESION-Copy1.ipynb':
            # Extraer solo la salida de la celda 146 (sin código)
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = nbformat.read(f, as_version=4)

            if len(notebook_content.cells) > 146:
                celda = notebook_content.cells[146]
                if celda.cell_type == 'code':
                    salidas = procesar_salidas_celda(celda)
                    return jsonify({'tipo': 'salidas', 'contenido': salidas}), 200
            return jsonify({'mensaje': 'La celda 146 no existe o no contiene salidas'}), 404

        elif nombre == 'Arboles de decision.ipynb':
            # Solo devolver la imagen asociada, sin mostrar celdas
            return send_file('/home/rosy/Documentos/api/grafico.png', mimetype='image/png')

        return jsonify({'mensaje': 'Este archivo no está permitido para visualización'}), 403

    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500

def procesar_salidas_celda(celda):
    """
    Procesa las salidas de una celda de código para devolverlas en formato JSON.
    """
    salidas = []
    for output in celda.outputs:
        if 'text' in output:
            salidas.append({'tipo': 'texto', 'contenido': output['text']})
        elif 'data' in output:
            if 'image/png' in output['data']:
                salidas.append({'tipo': 'imagen', 'contenido': output['data']['image/png']})
            elif 'application/json' in output['data']:
                salidas.append({'tipo': 'json', 'contenido': output['data']['application/json']})
            elif 'text/html' in output['data']:
                salidas.append({'tipo': 'html', 'contenido': output['data']['text/html']})
    return salidas

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
