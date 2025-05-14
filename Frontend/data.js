function generarTablas(numero, fecha) {
    const numeroDeGrupos = 3;
    
    if (numeroDeGrupos == 0){
        alert('No hay registro del cosechador para esa fecha');
        return;
    }

    const datosPorGrupo = [
        [
            { fecha: '2023-06-01', esquejes: 150, codigo: 'ABC123' },
            { fecha: '2023-06-02', esquejes: 200, codigo: 'XYZ789' },
            { fecha: '2023-06-03', esquejes: 175, codigo: 'LMN456' }
        ],
        [
            { fecha: '2023-06-04', esquejes: 160, codigo: 'DEF456' },
            { fecha: '2023-06-05', esquejes: 210, codigo: 'UVW123' },
            { fecha: '2023-06-06', esquejes: 185, codigo: 'NOP789' }
        ],
        [
            { fecha: '2023-06-07', esquejes: 170, codigo: 'GHI789' },
            { fecha: '2023-06-08', esquejes: 220, codigo: 'QRS456' },
            { fecha: '2023-06-09', esquejes: 190, codigo: 'TUV123' }
        ]
    ];

    const tablesContainer = document.getElementById('tables-container');
    tablesContainer.innerHTML = ""; // Clear previous tables
    var  vd = "";
    for (let i = 0; i < numeroDeGrupos; i++){
        if(i == 0){
            vd =  "Petrusk";
        }else if (i ==1){
            vd="Yellow";
        }else{vd = "Baltica"}
        const tableContainer = document.createElement('div');
        tableContainer.classList.add('table-container');

        const tableTitle = document.createElement('h1');
        tableTitle.textContent = `Variedad ${vd}`;
        tableContainer.appendChild(tableTitle);

        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Esquejes en Bolsa</th>
                    <th>Código de Cosechador</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        tableContainer.appendChild(table);

        const tableBody = table.querySelector('tbody');
        datosPorGrupo[i].forEach(item => {
            const row = document.createElement('tr');
            const fechaCell = document.createElement('td');
            fechaCell.textContent = item.fecha;
            row.appendChild(fechaCell);

            const esquejesCell = document.createElement('td');
            esquejesCell.textContent = item.esquejes;
            row.appendChild(esquejesCell);

            const codigoCell = document.createElement('td');
            codigoCell.textContent = item.codigo;
            row.appendChild(codigoCell);

            tableBody.appendChild(row);
        });

        tablesContainer.appendChild(tableContainer);
    }

    // Mostrar el número y la fecha capturados
    console.log('Número de cosechador:', numero);
    console.log('Fecha:', fecha);
}

document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.getElementById('submitButton');
    submitButton.addEventListener('click', function(event) {
        event.preventDefault(); // Evita que el formulario se envíe

        // Captura los valores del formulario
        const numero = document.getElementById('numero').value;
        const fecha = document.getElementById('fecha').value;

        // Llama a la función para generar las tablas pasando los valores capturados
        generarTablas(numero, fecha);
    });
});


async function query_data() {
    console.log('ejecutando')
    const cosechador = document.getElementById('cosechador').value;
    let fecha = document.getElementById('fecha').value;
    console.log(cosechador)
    console.log(fecha)
    const response = await fetch(`http://localhost:8000/consulta?cosechador=${cosechador}&fecha=${fecha}`);
    const data = await response.json();
  }