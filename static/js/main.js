function incrementar(id) {
    const input = document.getElementById(id);
    let value = parseInt(input.value, 10);
    if (isNaN(value)) value = 0;
    input.value = value + 1;
}

function decrementar(id) {
    const input = document.getElementById(id);
    let value = parseInt(input.value, 10);
    if (isNaN(value)) value = 0;
    input.value = value - 1;
}

function resetear(id) {
    const input = document.getElementById(id);
    input.value = "Null";
}
