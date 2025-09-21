# Система аутентификации и авторизации

Собственная система аутентификации и авторизации с JWT-токенами, управлением сессиями и гибкой системой прав доступа.

## 📋 Описание проекта

Проект представляет собой полноценную систему управления пользователями с:

- **JWT-аутентификацией** (access + refresh токены)
- **Управлением сессиями** (активные сессии, отзыв токенов)
- **Гибкой системой прав доступа** (RBAC)
- **Защитой от брутфорса** (rate limiting)
- **Мгновенным разлогиниванием** при деактивации пользователя
- **RESTful API** с документацией Swagger

## 🏗️ Архитектура
```aiignore
auth_app/
├── models/ # Модели данных
├── serializers/ # Сериализаторы DRF
├── views/ # View-классы API
├── authentication.py # JWT-аутентификация
├── permissions.py # Пользовательские разрешения
├── signals.py # Сигналы Django
├── utils/ # Вспомогательные функции
└── urls.py # Маршруты API
```


## 🗃️ Структура базы данных

### 1. Пользователи

#### `auth_app_customusermodel`
Основная модель пользователя

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGINT (PK) | Уникальный идентификатор |
| email | VARCHAR(255) UNIQUE | Email пользователя |
| password | VARCHAR(128) | Хэш пароля |
| first_name | VARCHAR(150) | Имя |
| last_name | VARCHAR(150) | Фамилия |
| middle_name | VARCHAR(150) NULL | Отчество |
| is_active | BOOLEAN | Активен ли аккаунт |
| is_staff | BOOLEAN | Может ли входить в админку |
| is_superuser | BOOLEAN | Суперпользователь |
| date_joined | DATETIME | Дата регистрации |
| last_login | DATETIME NULL | Последний вход |
| updated_at | DATETIME | Дата обновления профиля |
| force_logout_at | DATETIME NULL | Дата принудительного разлогинивания |

### 2. Токены

#### `auth_app_issuetokenmodel`
Выданные токены (refresh)

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGINT (PK) | Уникальный идентификатор |
| jti | UUID UNIQUE | Уникальный ID токена |
| user_id | BIGINT (FK) | Ссылка на пользователя |
| issued_at | DATETIME | Дата выдачи |
| expires_at | DATETIME | Дата истечения |
| is_revoked | BOOLEAN | Отозван ли токен |
| revoke_at | DATETIME NULL | Дата отзыва |
| token_type | VARCHAR(10) | Тип токена (refresh) |
| ip_address | INET NULL | IP-адрес выдачи |
| user_agent | TEXT | User-Agent клиента |
| last_used_at | DATETIME NULL | Последнее использование |

#### `auth_app_blacklisttoken`
Отозванные токены

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGINT (PK) | Уникальный идентификатор |
| jti | UUID | Уникальный ID токена |
| user_id | BIGINT (FK) | Ссылка на пользователя |
| blacklist_at | DATETIME | Дата добавления в черный список |
| expires_at | DATETIME | Дата истечения токена |

### 3. Система прав доступа

#### `auth_group`
Группы пользователей

| Поле | Тип | Описание |
|------|-----|----------|
| id | INT (PK) | Уникальный идентификатор |
| name | VARCHAR(150) UNIQUE | Название группы |

#### `auth_permission`
Разрешения

| Поле | Тип | Описание |
|------|-----|----------|
| id | INT (PK) | Уникальный идентификатор |
| name | VARCHAR(255) | Название разрешения |
| content_type_id | INT (FK) | Тип контента |
| codename | VARCHAR(100) | Кодовое имя |

#### `auth_user_groups`
Связь пользователей и групп (ManyToMany)

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGINT (PK) | Уникальный идентификатор |
| user_id | BIGINT (FK) | Пользователь |
| group_id | INT (FK) | Группа |

#### `auth_user_user_permissions`
Связь пользователей и разрешений (ManyToMany)

| Поле | Тип | Описание |
|------|-----|----------|
| id | BIGINT (PK) | Уникальный идентификатор |
| user_id | BIGINT (FK) | Пользователь |
| permission_id | INT (FK) | Разрешение |

## 🔐 Механизм аутентификации

### 1. Регистрация