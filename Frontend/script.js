// Función para convertir una dataURL a un objeto Blob
// Permite extraer la información del tipo MIME y decodificar la cadena en base64,
// convirtiéndola en un arreglo de bytes para finalmente crear el Blob.
function dataURLToBlob(dataURL) {
  // Separa la cadena por comas para obtener el encabezado y la data en base64
  var arr = dataURL.split(','),
      // Extrae el tipo MIME usando una expresión regular
      mime = arr[0].match(/:(.*?);/)[1],
      // Decodifica la parte de la data en base64
      bstr = atob(arr[1]),
      n = bstr.length,
      // Crea un arreglo de bytes con el tamaño de la cadena decodificada
      u8arr = new Uint8Array(n);
  // Recorre cada carácter y asigna su código en el arreglo de bytes
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  // Retorna un nuevo Blob usando el arreglo de bytes y el tipo MIME obtenido
  return new Blob([u8arr], { type: mime });
}

// Función para guardar datos en sessionStorage
// Recopila los datos de ciertos elementos del DOM y los almacena en sessionStorage
function guardarDatos() {

  // Se crea un objeto con los datos obtenidos de diferentes elementos usando querySelector
  const datos = {
    
    // Datos principales
    cosechador: document.querySelector('.valor') ? document.querySelector('.valor').textContent.trim() : '',
    dmd: document.querySelector('.valor3') ? document.querySelector('.valor3').textContent.trim() : '',
    esquejesLargos: document.querySelector('.valor12') ? document.querySelector('.valor12').textContent.trim() : '',
    hojaEnBase: document.querySelector('.valor14') ? document.querySelector('.valor14').textContent.trim() : '',
    esquejesCortos: document.querySelector('.valor13') ? document.querySelector('.valor13').textContent.trim() : '',
    conteoEsquejes: document.querySelector('.valor2') ? document.querySelector('.valor2').textContent.trim() : '',
    promedioTallo: document.querySelector('.valor-promTalloD') ? document.querySelector('.valor-promTalloD').textContent.trim() : '',
    promedioAreaFoliar: document.querySelector('.valor15') ? document.querySelector('.valor15').textContent.trim() : '',
    promedioLongitud: document.querySelector('.valor4') ? document.querySelector('.valor4').textContent.trim() : '',
    promedioDiametro: document.querySelector('.valor8') ? document.querySelector('.valor8').textContent.trim() : '',
    // Datos adicionales
    variedad: document.querySelector('.valor1')?.textContent.trim() || '',
    cuttings: document.querySelector('.EsqXbol')?.textContent.trim() || '',
    promLongitud: document.querySelector('.valor4')?.textContent.trim() || '',
    promLongitudMayor: document.querySelector('.valor5')?.textContent.trim() || '',
    promLongitudMenor: document.querySelector('.valor6')?.textContent.trim() || '',
    desvLongitud: document.querySelector('.valor7')?.textContent.trim() || '',
    promDiametro: document.querySelector('.valor8')?.textContent.trim() || '',
    promDiametroMayor: document.querySelector('.valor9')?.textContent.trim() || '',
    promDiametroMenor: document.querySelector('.valor10')?.textContent.trim() || '',
    desvDiametro: document.querySelector('.valor11')?.textContent.trim() || '',
    promAreaFoliar: document.querySelector('.valor15')?.textContent.trim() || '',
    promAreaFoliarMayor: document.querySelector('.valor16')?.textContent.trim() || '',
    promAreaFoliarMenor: document.querySelector('.valor17')?.textContent.trim() || '',
    desvAreaFoliar: document.querySelector('.valor18')?.textContent.trim() || ''
  };

  // Guarda en sessionStorage el objeto datos convertido a cadena JSON
  sessionStorage.setItem('datosGuardados', JSON.stringify(datos));
  console.log('Datos guardados:', datos);
}

// Espera a que todo el contenido del DOM se cargue
document.addEventListener("DOMContentLoaded", function() {
  // Se obtienen referencias a elementos de video, canvas y el botón de escaneo
  const video = document.getElementById("videoElement");
  const canvas = document.getElementById("canvas");
  const scan = document.getElementById('scan');

  // Enumerar dispositivos de video para seleccionar la cámara USB
  navigator.mediaDevices.enumerateDevices()
    .then(devices => {
      // Filtra los dispositivos para obtener solo aquellos de video (videoinput)
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      // Busca en el label la palabra "usb" (en minúsculas) para identificar la cámara USB
      const usbCamera = videoDevices.find(device => device.label.toLowerCase().includes("usb"));
      // Si no se encuentra, usa el primer dispositivo de video disponible
      const selectedDeviceId = usbCamera ? usbCamera.deviceId : videoDevices[0].deviceId;
      return navigator.mediaDevices.getUserMedia({
        video: {
          deviceId: { exact: selectedDeviceId },
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
    })
    .then(function(stream) {
      // Asigna el stream obtenido al elemento de video y lo reproduce
      video.srcObject = stream;
      video.play();
    })
    .catch(function(err) {
      // Manejo de errores en caso de que no se pueda obtener el stream de la cámara
      console.log("Error al obtener el stream de la cámara: " + err);
      
    });

  // Clase para la gestión de la cámara y comunicación con Arduino (con partes comentadas)
  class Camera {
    constructor() {
      // Configuración del vendor USB y velocidad (estos valores pueden ser para comunicación con Arduino)
      this.usbVendor = 0x2341;
      this.usbSpeed = 9600;
    }
    // Inicializa la cámara y el puerto serial, se encontró código comentado que sugiere conexión con Arduino
    async initialize() {
      try {
        // Código comentado: comunicación con Arduino
      } catch (error) {
        console.error('Error initializing camera and serial port:', error);
      }
    }
    // Envía un mensaje o comando a Arduino (por el momento, código comentado)
    async sendMessage(message) {
      try {
        // Código comentado: envío de comandos al Arduino
      } catch (error) {
        console.error('Error sending message:', error);
      }
    }
    // Lee mensajes del Arduino, código comentado
    async readMessages() {
      try {
        // Código comentado: lectura de mensajes del Arduino
      } catch (error) {
        console.error('Error reading message:', error);
      }
    }
    // Función para manejar los mensajes recibidos, lógica de control del motor (actualmente comentado)
    handleMessage(message) {
      // Código comentado: lógica de control de motor
    }

    // Método scan para realizar el escaneo: limpiar elementos, capturar imagen y analizar datos
    async scan() {
      try {
        // Ejecuta la función "limpiar" para cada uno de los elementos especificados
        await Promise.all([
          limpiar('.valor'),
          limpiar('.valor1'),
          limpiar('.valor2'),
          limpiar('.valor3'),
          limpiar('.valor4'),
          limpiar('.valor5'),
          limpiar('.valor6'),
          limpiar('.valor7'),
          limpiar('.valor8'),
          limpiar('.valor9'),
          limpiar('.valor10'),
          limpiar('.valor11'),
          limpiar('.valor12'),
          limpiar('.valor13'),
          limpiar('.valor14'),
          limpiar('.valor15'),
          limpiar('.valor16'),
          limpiar('.valor17'),
          limpiar('.valor18'),
          limpiar('.EsqXbol'),
          limpiar('.valor-cosechador'),
          limpiar('.valor-contEsqD'),
          limpiar('.valor-promTalloD'),
          limpiar('.valor-dmdD'),
          limpiar('.valor-esqLargoD'),
          limpiar('.valor-esqCortoD'),
          limpiar('.valor-hbD')
        ]);
      } catch(e) {
        console.error("Error limpiando elementos:", e);
      }

      console.log('Iniciando escaneo...');
      // Llama a la función que realiza la lectura del QR (o datos) iniciales
      await scanQr();

      try {
        // Realiza una solicitud al endpoint /capture_image para capturar y procesar la imagen
        const responseCapture = await fetch('http://localhost:8000/capture_image');
        if (!responseCapture.ok) {
          throw new Error(`Error en /capture_image: ${responseCapture.statusText}`);
        }
        const dataCapture = await responseCapture.json();
        console.log('Imagen capturada y procesada:', dataCapture);

        // Si la respuesta contiene un preview de la imagen, lo asigna a un elemento img en el DOM
        if (dataCapture.preview) {
          document.getElementById('capturedImg').src = `data:image/jpeg;base64,${dataCapture.preview}`;
        }

        // Llama a función que actualiza la imagen en el sitio web
        cargarImagen();

      } catch (error) {
        console.error('Error al capturar la imagen:', error);
      }

      // Tras 3 segundos, llama a la función getAnalisis para obtener y actualizar los datos analíticos
      setTimeout(() => {
        getAnalisis();
      }, 3000);
    }
  }

  // Se crea una instancia de la clase Camera
  const camera = new Camera();

  // Evento de click en el botón "scan" para iniciar el proceso de escaneo
  scan.addEventListener('click', async function() {
    // Ejecuta el método scan de la instancia camera
    camera.scan();
    try {
      // Solicita al endpoint /start_scan/ para iniciar otro proceso de escaneo
      const respuesta = await fetch('http://localhost:8000/start_scan/');
      const datos = await respuesta.json();
      // Si la respuesta contiene un mensaje, muestra una alerta con dicho mensaje
      if (datos && datos.mensaje) {
        alert(datos.mensaje);
      } else {
        console.error("La respuesta no contiene la propiedad 'mensaje':", datos);
      }
    } catch (error) {
      console.error('Error al ejecutar la función:', error);
    }
  });
});

// Función para escanear el QR o bien para obtener los valores iniciales
async function scanQr() {
  try {
    // Solicita al endpoint /get_values_iniciales para obtener datos
    const response = await fetch('http://localhost:8000/get_values_iniciales');
    if (!response.ok) {
      throw new Error('La respuesta de la red no fue correcta');
    }
    const data = await response.json();
    // Actualiza el contenido de ciertos elementos del DOM con los datos recibidos
    document.querySelector('.valor').textContent = data.harvester;
    document.querySelector('.valor1').textContent = data.variety;
    document.querySelector('.valor3').textContent = parseFloat(data.medCM).toFixed(2);
    document.querySelector('.EsqXbol').textContent = parseInt(data.cuttings);
  } catch (error) {
    console.error('Hubo un problema con la operación de fetch:', error);
  }
}

// Función para limpiar el contenido de un elemento especificado por la clase
// Devuelve una promesa que se resuelve cuando el elemento se limpia o se rechaza si no se encuentra
function limpiar(cla) {
  return new Promise((resolve, reject) => {
    try {
      const elemento = document.querySelector(cla);
      if (elemento) {
        elemento.textContent = '';
        resolve();
      } else {
        reject(`No se encontró ningún elemento con la clase '${cla}'`);
      }
    } catch (error) {
      reject(error);
    }
  });
}

// Función para cargar la imagen generada por FastAPI
// Agrega un timestamp a la URL de la imagen para evitar problemas de cacheo y establece la imagen en el DOM cuando se carga
function cargarImagen() {
  const timestamp = new Date().getTime();
  const rutaImagen = `http://localhost:8000/images/result_imagen1.jpg?timestamp=${timestamp}`;
  // Crea un nuevo objeto Image para verificar la carga de la imagen
  const imgCheck = new Image();

  // Función que se ejecuta cuando la imagen se carga correctamente
  imgCheck.onload = function() {
    const imgElement = document.getElementById('imagen1');
    if (imgElement) {
      imgElement.src = rutaImagen;
      console.log("✅ Imagen cargada exitosamente.");
    } else {
      console.warn("⚠️ No se encontró el elemento con id 'imagen1'");
    }
  };

  // Función que se ejecuta en caso de error al cargar la imagen,
  // reintentando cargarla después de 1 segundo
  imgCheck.onerror = function() {
    console.log("⏳ La imagen aún no está disponible, reintentando...");
    setTimeout(cargarImagen, 1000);
  };

  // Establece la URL de la imagen para iniciar la carga
  imgCheck.src = rutaImagen;
}

// Función para obtener y actualizar datos de análisis desde el servidor
async function getAnalisis() {
  try {
    // Realiza una solicitud GET al endpoint /analisis/
    const response = await fetch('http://localhost:8000/analisis/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    if (!response.ok) {
      throw new Error(`Error en la solicitud: ${response.statusText}`);
    }
    const data = await response.json();
    console.log('Respuesta del servidor:', data);
    
    // Actualiza el contenido de varios elementos del DOM con los datos analíticos recibidos
    document.querySelector('.valor4').textContent = parseFloat(data.length).toFixed(1) + " cm";
    document.querySelector('.valor11').textContent = (parseFloat(data.diameter).toFixed(3)/2 + " mm / " + parseFloat(data.average_diameter).toFixed(3) + " mm");
    document.querySelector('.valor12').textContent = parseInt(data.stem_l);
    document.querySelector('.valor13').textContent = parseInt(data.stem_s);
    document.querySelector('.valor14').textContent = parseInt(data.count_hb);
    document.querySelector('.valor5').textContent = parseFloat(data.max_esqueje).toFixed(1) + " cm";
    document.querySelector('.valor6').textContent = parseFloat(data.min_esqueje).toFixed(1) + " cm";
    document.querySelector('.valor15').textContent = parseFloat(data.average_area_foliar).toFixed(2) + " mm²";
    document.querySelector('.valor7').textContent = parseFloat(data.desviacion_estandar_longitud).toFixed(3) + " cm";
    document.querySelector('.valor8').textContent = parseFloat(data.promedio_diametro).toFixed(3) + " cm";
    document.querySelector('.valor9').textContent = parseFloat(data.max_diameter).toFixed(3) + " cm";
    document.querySelector('.valor10').textContent = parseFloat(data.promedio_diametro_menor).toFixed(3) + " cm";
    document.querySelector('.valor16').textContent = parseFloat(data.max_area_foliar).toFixed(2) + " mm²";
    document.querySelector('.valor17').textContent = parseFloat(data.min_area_foliar).toFixed(2) + " mm²";
    document.querySelector('.valor18').textContent = parseFloat(data.std_area_foliar).toFixed(2) + " mm²";
  } catch (error) {
    console.error('Error al llamar a /analisis/:', error);
  }
}

// Función para llamar a /controlModel/ y actualizar algunos valores (detección de corte)
// Realiza una solicitud fetch y actualiza el conteo de tallos
function cuttingDetect() {
  fetch('http://localhost:8000/controlModel/')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Actualiza el contenido del elemento con la clase .valor2 con el conteo obtenido
      document.querySelector('.valor2').textContent = parseInt(data.count_stem);
      setTimeout(() => {}, 2000);
    })
    .catch(error => {
      console.error('Error al obtener los valores:', error);
      alert('Error al obtener los valores. Por favor, intenta de nuevo más tarde.');
    });
}
