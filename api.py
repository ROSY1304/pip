from flask import Flask, jsonify, request, send_from_directory, send_file
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
    """
    Lista todos los archivos .ipynb disponibles en la carpeta DOCUMENTS_FOLDER.
    """
    try:
        # Obtener la lista de archivos .ipynb en la carpeta documentos
        archivos = [f for f in os.listdir(DOCUMENTS_FOLDER) if f.endswith('.ipynb')]

        if not archivos:
            return jsonify({"mensaje": "No hay archivos .ipynb en el directorio."}), 404

        # Retornar la lista de archivos
        return jsonify(archivos), 200
    except FileNotFoundError:
        return jsonify({"mensaje": "No se encontró el directorio de documentos"}), 404
    except Exception as e:
        return jsonify({"mensaje": str(e)}), 500

@app.route('/documentos/contenido/<nombre>', methods=['GET'])
def ver_contenido_documento(nombre):
    """
    Extrae contenido específico de las celdas de los notebooks permitidos.
    """
    try:
        notebook_path = os.path.join(DOCUMENTS_FOLDER, nombre)

        if os.path.exists(notebook_path) and nombre.endswith('.ipynb'):
            if nombre == 'REGRESION-Copy1.ipynb':
                # Extraer solo la última celda
                with open(notebook_path, 'r', encoding='utf-8') as f:
                    notebook_content = nbformat.read(f, as_version=4)
                    if len(notebook_content.cells) >= 146:
                        celda_146 = notebook_content.cells[145]
                        if celda_146.cell_type == 'code':
                            contenido = procesar_solo_salidas(celda_146)
                        else:
                            contenido = [{"mensaje": "La celda 146 no es de tipo código."}]
                    else:
                        contenido = [{"mensaje": "El notebook no tiene suficientes celdas para mostrar la celda 146."}]
                return jsonify(contenido), 200

            elif nombre == 'Arboles de decision.ipynb':
                # Enviar la imagen especificada
                image_path = "/home/rosy/Documentos/api/grafico.png"
                if os.path.exists(image_path):
                    return send_file(image_path, mimetype='image/png')
                else:
                    return jsonify({'mensaje': 'La imagen especificada no se encuentra en el servidor.'}), 404

            else:
                return jsonify({'mensaje': 'Este archivo no está permitido para visualización'}), 403

        else:
            return jsonify({'mensaje': 'Archivo no encontrado o formato incorrecto'}), 404
    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500

def procesar_solo_salidas(celda):
    """
    Procesa una celda de código para devolver solo las salidas (sin mostrar el código).
    """
    salidas = []
    for output in celda.outputs:
        if 'text' in output:
            salidas.append({
                'tipo': 'texto',
                'contenido': output['text']
            })
        elif 'data' in output:
            if 'image/png' in output['data']:
                salidas.append({
                    'tipo': 'imagen',
                    'contenido': output['data']['image/png']
                })
            elif 'application/json' in output['data']:
                salidas.append({
                    'tipo': 'json',
                    'contenido': output['data']['application/json']
                })
            elif 'text/html' in output['data']:
                salidas.append({
                    'tipo': 'html',
                    'contenido': output['data']['text/html']
                })
    return salidas

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
