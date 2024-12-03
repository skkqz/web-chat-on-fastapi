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
            showError('loginEmail');
            return;
        }

        if (password.length <= 2) { // Проверка длины пароля
            showError('loginPassword');
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
                window.location.href = '/chat'; // Перенаправление на страницу чата
            } else {
                const errorData = await response.json();
                alert(errorData.detail || 'Ошибка входа'); // Вывод ошибки
            }
        } catch (error) {
            console.error('Error:', error); // Лог ошибки в консоль
            alert('Ошибка соединения с сервером');
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Предотвращаем стандартное поведение формы

        const email = document.getElementById('registerEmail').value; // Получаем значение email
        const name = document.getElementById('registerName').value; // Получаем имя
        const password = document.getElementById('registerPassword').value; // Получаем пароль
        const passwordConfirm = document.getElementById('registerPasswordConfirm').value; // Подтверждение пароля

        if (!validateEmail(email)) { // Проверка формата email
            showError('registerEmail');
            return;
        }

        if (name.length < 2) { // Проверка минимальной длины имени
            showError('registerName');
            return;
        }

        if (password.length < 6) { // Проверка длины пароля
            showError('registerPassword');
            return;
        }

        if (password !== passwordConfirm) { // Проверка совпадения паролей
            showError('registerPasswordConfirm');
            return;
        }

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Указываем, что данные в формате JSON
                },
                body: JSON.stringify({ email, name, password }) // Отправляем данные пользователя в формате JSON
            });

            if (response.ok) {
                // Успешная регистрация
                alert('Регистрация успешна! Теперь вы можете войти.'); // Уведомление об успешной регистрации
                document.querySelector('[data-tab="login"]').click(); // Переключение на вкладку входа
            } else {
                const errorData = await response.json();
                alert(errorData.detail || 'Ошибка регистрации'); // Вывод ошибки
            }
        } catch (error) {
            console.error('Error:', error); // Лог ошибки в консоль
            alert('Ошибка соединения с сервером');
        }
    });

    // Проверка формата email
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Регулярное выражение для проверки email
        return re.test(email); // Возвращает true, если формат email валиден
    }

    // Отображение ошибки для поля ввода
    function showError(inputId) {
        const input = document.getElementById(inputId); // Получаем элемент ввода по ID
        const errorDiv = input.nextElementSibling; // Находим соседний элемент для отображения ошибки
        input.classList.add('shake'); // Добавляем класс анимации "тряски"
        errorDiv.style.display = 'block'; // Показываем сообщение об ошибке

        setTimeout(() => {
            input.classList.remove('shake'); // Убираем анимацию
        }, 300);

        input.addEventListener('input', () => {
            errorDiv.style.display = 'none'; // Убираем сообщение об ошибке при вводе
        }, { once: true });
    }
});
