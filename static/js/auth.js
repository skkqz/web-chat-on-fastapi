// Функция для показа уведомлений
function showNotification(message, type = 'error') {
    const notification = document.createElement('div');
    notification.classList.add('notification', type);
    notification.textContent = message;

    // Добавление уведомления на страницу
    document.body.appendChild(notification);

    // Показать уведомление с анимацией
    setTimeout(() => {
        notification.style.display = 'block';
        notification.style.opacity = '1';
    }, 100);

    // Убираем уведомление через 3 секунды
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.style.display = 'none';
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Добавляем обработку ошибок и уведомлений в формах

document.addEventListener('DOMContentLoaded', function() {
    // Переключение вкладок
    const tabs = document.querySelectorAll('.tab'); // Все вкладки
    const forms = document.querySelectorAll('.form-container > div'); // Все формы

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab; // Получение идентификатора связанной вкладки

            // Обновление активной вкладки
            tabs.forEach(t => t.classList.remove('active')); // Убираем активный класс со всех вкладок
            tab.classList.add('active'); // Добавляем активный класс текущей вкладке

            // Отображение активной формы
            forms.forEach(form => {
                form.classList.remove('active'); // Убираем активный класс у всех форм
                if (form.id === target) { // Показываем только форму с соответствующим идентификатором
                    form.classList.add('active');
                }
            });
        });
    });

    // Валидация и отправка формы
    const loginForm = document.getElementById('loginForm'); // Форма входа
    const registerForm = document.getElementById('registerForm'); // Форма регистрации

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Предотвращаем стандартное поведение формы

        const email = document.getElementById('loginEmail').value; // Получаем значение email
        const password = document.getElementById('loginPassword').value; // Получаем значение пароля

        if (!validateEmail(email)) { // Проверка формата email
            showNotification('Пожалуйста, введите корректный email');
            return;
        }

        if (password.length <= 2) { // Проверка длины пароля
            showNotification('Пароль должен быть не менее 3 символов');
            return;
        }

        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Указываем, что данные в формате JSON
                },
                body: JSON.stringify({ email, password }) // Отправляем email и пароль в формате JSON
            });

            if (response.ok) {
                // Успешная авторизация
                showNotification('Авторизация успешна!', 'success');
                window.location.href = '/chat'; // Перенаправление на страницу чата
            } else {
                const errorData = await response.json();
                showNotification(errorData.detail || 'Ошибка входа');
            }
        } catch (error) {
            console.error('Error:', error); // Лог ошибки в консоль
            showNotification('Ошибка соединения с сервером');
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Предотвращаем стандартное поведение формы

        const email = document.getElementById('registerEmail').value; // Получаем значение email
        const name = document.getElementById('registerName').value; // Получаем имя
        const password = document.getElementById('registerPassword').value; // Получаем пароль
        const passwordConfirm = document.getElementById('registerPasswordConfirm').value; // Подтверждение пароля

        if (!validateEmail(email)) { // Проверка формата email
            showNotification('Пожалуйста, введите корректный email');
            return;
        }

        if (name.length < 2) { // Проверка минимальной длины имени
            showNotification('Имя должно содержать минимум 3 символа');
            return;
        }

        if (password.length < 2) { // Проверка длины пароля
            showNotification('Пароль должен быть не менее 3 символов');
            return;
        }

        if (password !== passwordConfirm) { // Проверка совпадения паролей
            showNotification('Пароли не совпадают');
            return;
        }

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Указываем, что данные в формате JSON
                },
                body: JSON.stringify({ email, name, password, password_check: passwordConfirm }) // Отправляем данные пользователя в формате JSON
            });

            if (response.ok) {
                // Успешная регистрация
                showNotification('Регистрация успешна! Теперь вы можете войти.', 'success');
                document.querySelector('[data-tab="login"]').click(); // Переключение на вкладку входа
            } else {
                const errorData = await response.json();
                showNotification(errorData.detail || 'Ошибка регистрации');
            }
        } catch (error) {
            console.error('Error:', error); // Лог ошибки в консоль
            showNotification('Ошибка соединения с сервером');
        }
    });

    // Проверка формата email
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Регулярное выражение для проверки email
        return re.test(email); // Возвращает true, если формат email валиден
    }
});
