// Клиентский скрипт проекта «Система учета домашних заготовок»

document.addEventListener("DOMContentLoaded", function () {
    // Автоматическое обновление года в футере
    const yearSpan = document.getElementById("current-year");
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear().toString();
    }
});
