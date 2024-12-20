// Глобальные переменные
let selectedUserId = null;
let socket = null;
let messagePollingInterval = null;

// Функция выхода из аккаунта
async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/auth';
        } else {
            console.error('Ошибка при выходе');
        }
    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
    }
}

// Функция выбора пользователя
async function selectUser(userId, userName, event) {
    selectedUserId = userId;
    document.getElementById('chatHeader').innerHTML = `<span>Чат с ${userName}</span><button class="logout-button" id="logoutButton">Выход</button>`;
    document.getElementById('messageInput').disabled = false;
    document.getElementById('sendButton').disabled = false;

    document.querySelectorAll('.user-item').forEach(item => item.classList.remove('active'));
    event.target.classList.add('active');

    const messagesContainer = document.getElementById('messages');
    messagesContainer.innerHTML = '';
    messagesContainer.style.display = 'block';

    document.getElementById('logoutButton').onclick = logout;

    await loadMessages(userId);
    connectWebSocket();
    startMessagePolling(userId);
}

// Загрузка сообщений
async function loadMessages(userId) {
    try {
        const response = await fetch(`/chat/messages/${userId}`);
        const messages = await response.json();

        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = messages.map(message =>
            createMessageElement(message.content, message.recipient_id)
        ).join('');

        // Прокрутка к последнему сообщению
        scrollToBottom(messagesContainer);
    } catch (error) {
        console.error('Ошибка загрузки сообщений:', error);
    }
}

// Подключение WebSocket
function connectWebSocket() {
    if (socket) socket.close();

    socket = new WebSocket(`ws://${window.location.host}/chat/ws/${selectedUserId}`);

    socket.onopen = () => console.log('WebSocket соединение установлено');

    socket.onmessage = (event) => {
        const incomingMessage = JSON.parse(event.data);
        if (incomingMessage.recipient_id === selectedUserId) {
            addMessage(incomingMessage.content, incomingMessage.recipient_id);

            // Прокрутка к последнему сообщению
            const messagesContainer = document.getElementById('messages');
            scrollToBottom(messagesContainer);
        }
    };

    socket.onclose = () => console.log('WebSocket соединение закрыто');
}

// Отправка сообщения
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (message && selectedUserId) {
        const payload = {recipient_id: selectedUserId, content: message};

        try {
            await fetch('/chat/messages', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            // WebSocket отправляет сообщение, сервер обработает и вернет его клиенту
            socket.send(JSON.stringify(payload));

            // Убираем локальное добавление, так как WebSocket обработает это
            messageInput.value = '';
        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
        }
    }
}

// Добавление сообщения в чат
function addMessage(text, recipient_id) {
    const messagesContainer = document.getElementById('messages');
    messagesContainer.insertAdjacentHTML('beforeend', createMessageElement(text, recipient_id));
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Создание HTML элемента сообщения
function createMessageElement(text, recipient_id) {
    const isMyMessage = recipient_id !== selectedUserId;
    const messageClass = isMyMessage ? 'my-message' : 'other-message';
    return `<div class="message ${messageClass}">${text}</div>`;
}

// Прокрутка к последнему сообщению
function scrollToBottom(container) {
    container.scrollTop = container.scrollHeight;
}

// Запуск опроса новых сообщений
function startMessagePolling(userId) {
    clearInterval(messagePollingInterval);
    messagePollingInterval = setInterval(() => loadMessages(userId), 1000);
}

// Обработка нажатий на пользователя
function addUserClickListeners() {
    document.querySelectorAll('.user-item').forEach(item => {
        item.onclick = event => selectUser(item.getAttribute('data-user-id'), item.textContent, event);
    });
}

// Первоначальная настройка событий нажатия на пользователей
addUserClickListeners();

// Обновление списка пользователей
async function fetchUsers() {
  try {
    const response = await fetch('/auth/users');
    const users = await response.json();
    const userList = document.getElementById('userList');
    // Очищаем текущий список пользователей
    userList.innerHTML = '';
    // Генерация списка пользователей
    users.forEach(user => {
      if (user.id !== currentUserId) {
        const userElement = document.createElement('div');
        userElement.classList.add('user-item');
        userElement.setAttribute('data-user-id', user.id);
        userElement.textContent = user.name;
        // Применение класса online для онлайн-пользователей
        if (user.online_status) {
          userElement.classList.add('online');
        }
        userList.appendChild(userElement);
      }
    });
    // Повторно добавляем обработчики событий для каждого пользователя
    addUserClickListeners();
  } catch (error) {
    console.error('Ошибка при загрузке списка пользователей:', error);
  }
}


// События при загрузке страницы
document.addEventListener('DOMContentLoaded', fetchUsers);
setInterval(fetchUsers, 10000); // Обновление каждые 10 секунд

// Обработчики для кнопки отправки и ввода сообщения
document.getElementById('sendButton').onclick = sendMessage;
document.getElementById('messageInput').onkeypress = async (e) => {
    if (e.key === 'Enter') {
        await sendMessage();
    }
};