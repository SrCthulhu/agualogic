// Obtiene el elemento del botón
const button = document.getElementById("counter");

// Inicializa una variable para el contador
let contador = 0;

// Agrega un controlador de eventos para el clic del botón
button.addEventListener("click", function () {
    // Incrementa el contador en 1 cada vez que se hace clic
    contador++;

    // Actualiza el texto del botón con el nuevo valor del contador
    button.innerText = `- 1 + ${contador}`;

    // Realiza una solicitud AJAX al servidor para actualizar el contador
    updateCounterOnServer(contador);
});

// Función para realizar una solicitud AJAX al servidor y actualizar el contador en el servidor
function updateCounterOnServer(newCount) {
    // Crea un objeto XMLHttpRequest
    const xhr = new XMLHttpRequest();

    // Configura la solicitud POST para enviar el nuevo contador al servidor
    xhr.open("POST", "/update-counter", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    // Define la función de devolución de llamada cuando la solicitud se completa
    xhr.onload = function () {
        if (xhr.status === 200) {
            // La solicitud se completó correctamente
            console.log("Contador actualizado en el servidor.");
        } else {
            // Hubo un error en la solicitud
            console.error("Error al actualizar el contador en el servidor.");
        }
    };

    // Convierte los datos a formato JSON
    const data = JSON.stringify({ count: newCount });

    // Envía la solicitud con los datos JSON
    xhr.send(data);
}
