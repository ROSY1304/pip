from flask import Flask, jsonify, request, send_from_directory
import os
import nbformat
from flask_cors import CORS
import base64  # Importar base64 para codificar imágenes

app = Flask(__name__, static_folder='static')

# Habilitar CORS para la aplicación completa
CORS(app)

# Directorio donde están los documentos .ipynb
DOCUMENTS_FOLDER = 'documentos'
app.config['DOCUMENTS_FOLDER'] = DOCUMENTS_FOLDER

# Crear el directorio si no existe
if not os.path.exists(DOCUMENTS_FOLDER):
    os.makedirs(DOCUMENTS_FOLDER)

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')


@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    """
    Endpoint para obtener la lista de archivos .ipynb en el directorio configurado.
    """
    try:
        # Verifica si el directorio existe y obtiene los archivos .ipynb
        if not os.path.exists(DOCUMENTS_FOLDER):
            return jsonify({"mensaje": "El directorio de documentos no existe."}), 404

        archivos = [f for f in os.listdir(DOCUMENTS_FOLDER) if f.endswith('.ipynb')]

        if not archivos:
            return jsonify({"mensaje": "No hay archivos .ipynb en el directorio."}), 404

        return jsonify(archivos), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error al obtener los documentos: {str(e)}"}), 500


@app.route('/documentos/contenido/<nombre>', methods=['GET'])
def ver_contenido_documento(nombre):
    """
    Endpoint para obtener el contenido de un archivo .ipynb específico, incluyendo imágenes en celdas Markdown.
    """
    try:
        notebook_path = os.path.join(DOCUMENTS_FOLDER, nombre)
        
        if os.path.exists(notebook_path) and nombre.endswith('.ipynb'):
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = nbformat.read(f, as_version=4)

            contenido = []
            attachments = notebook_content.get('metadata', {}).get('attachments', {})

            for cell in notebook_content.cells:
                if cell.cell_type == 'code':
                    # Procesar celdas de código
                    cell_data = {
                        'tipo': 'código',
                        'contenido': cell.source,
                        'salidas': []
                    }
                    for output in cell.outputs:
                        if 'text' in output:
                            cell_data['salidas'].append({
                                'tipo': 'texto',
                                'contenido': output['text']
                            })
                        elif 'data' in output:
                            if 'image/png' in output['data']:
                                image_base64 = base64.b64encode(output['data']['image/png']).decode('utf-8')
                                data_url = f"data:image/png;base64,{image_base64}"
                                cell_data['salidas'].append({
                                    'tipo': 'imagen',
                                    'contenido': data_url
                                })
                    contenido.append(cell_data)

                elif cell.cell_type == 'markdown':
                    # Procesar celdas Markdown
                    markdown_content = cell.source
                    for attachment_name, attachment_data in cell.get('attachments', {}).items():
                        if 'image/png' in attachment_data:
                            # Generar Data URL a partir del adjunto
                            image_base64 = base64.b64encode(attachment_data['image/png']).decode('utf-8')
                            data_url = f"data:image/png;base64,{image_base64}"
                            # Reemplazar la referencia del attachment en el contenido Markdown
                            markdown_content = markdown_content.replace(
                                f"attachment:{attachment_name}",
                                data_url
                            )
                    contenido.append({
                        'tipo': 'texto',
                        'contenido': markdown_content
                    })

            return jsonify(contenido), 200
        else:
            return jsonify({'mensaje': 'Archivo no encontrado o formato incorrecto'}), 404
    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500


# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
