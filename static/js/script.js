// Función para obtener el contenido de un notebook
function fetchNotebookContent(notebookName) {
    fetch(`https://pip-yc7y.onrender.com/documentos/contenido/${notebookName}`)
        .then(response => response.json())
        .then(data => {
            const contentDiv = document.getElementById('content');
            contentDiv.innerHTML = ''; // Limpiar contenido previo

            // Mostrar el contenido de las celdas
            data.forEach(cell => {
                const cellDiv = document.createElement('div');
                if (cell.tipo === 'código') {
                    cellDiv.innerHTML = `
                        <strong>Celda de Código:</strong>
                        <pre>${cell.contenido}</pre>
                    `;

                    // Mostrar las salidas
                    cell.salidas.forEach(salida => {
                        if (salida.tipo === 'texto') {
                            // Solo mostrar los resultados de accuracy
                            cellDiv.innerHTML += `
                                <strong>Resultado de Accuracy:</strong>
                                <pre>${salida.contenido}</pre>
                            `;
                        }
                    });
                }
                contentDiv.appendChild(cellDiv);
            });
        })
        .catch(error => {
            console.error('Error al obtener el contenido del notebook:', error);
        });
}
