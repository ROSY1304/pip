// Función que se ejecuta cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    fetchNotebooksList();
});

// Función para obtener la lista de notebooks desde la API
function fetchNotebooksList() {
    fetch('https://pip-yc7y.onrender.com/documentos')
        .then(response => response.json())
        .then(data => {
            const notebooksList = document.getElementById('notebooks-list');
            notebooksList.innerHTML = ''; // Limpiar la lista antes de agregar los items

            if (data.length === 0) {
                notebooksList.innerHTML = '<li>No se encontraron archivos .ipynb</li>';
                return;
            }

            // Agregar cada archivo a la lista
            data.forEach(notebook => {
                const li = document.createElement('li');
                li.textContent = notebook;
                li.onclick = () => fetchNotebookContent(notebook);
                notebooksList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error al obtener la lista de notebooks:', error);
        });
}

// Función para obtener el contenido de un notebook
function fetchNotebookContent(notebookName) {
    fetch(`https://pip-yc7y.onrender.com/documentos/contenido/${notebookName}`)
        .then(response => response.json())
        .then(data => {
            const contentDiv = document.getElementById('content');
            contentDiv.innerHTML = ''; // Limpiar contenido previo

            // Filtrar el contenido dependiendo del tipo de notebook
            if (notebookName === 'REGRESION-Copy1.ipynb') {
                displayRegressionContent(data, contentDiv);
            } else if (notebookName === 'Arboles de decision.ipynb') {
                displayDecisionTreeContent(data, contentDiv);
            } else {
                contentDiv.innerHTML = '<p>Este notebook no está permitido para visualización.</p>';
            }
        })
        .catch(error => {
            console.error('Error al obtener el contenido del notebook:', error);
        });
}

// Mostrar solo las salidas relacionadas con "accuracy" en regresión
function displayRegressionContent(data, contentDiv) {
    data.forEach(cell => {
        if (cell.tipo === 'código') {
            const cellDiv = document.createElement('div');
            cellDiv.innerHTML = `
                <strong>Celda de Código:</strong>
            `;
            
            // Filtrar solo los resultados de "accuracy"
            cell.salidas.forEach(salida => {
                if (salida.tipo === 'texto' && salida.contenido.includes('accuracy')) {
                    cellDiv.innerHTML += `
                        <strong>Resultado de Accuracy:</strong>
                        <pre>${salida.contenido}</pre>
                    `;
                }
            });
            contentDiv.appendChild(cellDiv);
        }
    });
}

// Mostrar solo las imágenes y gráficos en el notebook de árboles de decisión
function displayDecisionTreeContent(data, contentDiv) {
    data.forEach(cell => {
        if (cell.tipo === 'código') {
            const cellDiv = document.createElement('div');
            cellDiv.innerHTML = `
                <strong>Celda de Código:</strong>
            `;

            // Mostrar solo las imágenes
            cell.salidas.forEach(salida => {
                if (salida.tipo === 'imagen') {
                    cellDiv.innerHTML += `
                        <strong>Gráfico de Árbol de Decisión:</strong>
                        <img src="data:image/png;base64,${salida.contenido}" alt="Imagen de salida"/>
                    `;
                }
            });
            contentDiv.appendChild(cellDiv);
        }
    });
}
