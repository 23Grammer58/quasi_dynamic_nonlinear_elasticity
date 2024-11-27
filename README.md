# Квазидинамическое решение краевой задачи двухоносного растяжения гиперупругого материала

Этот проект предоставляет инструменты для обработки сеток с использованием библиотек `pathlib`, `meshio` и `gmsh`. Требуется, чтобы в корневой папке проекта находился файл `./model`, необходимый для работы скриптов.

## Требования

Перед началом убедитесь, что у вас установлены:
- Python версии 3.8 или выше
- `pip` (установщик Python-пакетов)

## Установка

Чтобы настроить окружение и установить необходимые библиотеки, выполните следующие шаги:

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your_username/your_repository.git
   cd your_repository
   ```

2. Установите требуемые Python-библиотеки:
   ```bash
   pip install pathlib meshio gmsh
   ```

## Структура проекта

Проект ожидает следующую структуру директории:

```
model # Файл модели (обязателен для работы)
quasi_dynamic_nonlinear_elasticity/              
├── run.py     # Основной скрипт
├── README.md  # Этот файл
```

Скомпилированный файл `./model` необходим для корректной работы скриптов. Убедитесь, что он находится в корневой папке проекта. Для установки обратитесь [сюда](https://github.com/23Grammer58/membrane_model). 

## Использование

1. **Запуск основного скрипта**:
   Выполните команду для запуска основного скрипта:
   ```bash
   python run.py
   ```

2. **Проверка зависимостей**:
   Если какой-либо библиотеки не хватает, установите её с помощью команды:
   ```bash
   pip install <имя_библиотеки>
   ```

3. **Убедитесь в наличии файла `./model`**:
   Скрипт не запустится, если в корневой папке проекта отсутствует файл `./model`.

## Лицензия

Проект распространяется под лицензией MIT. Подробности можно найти в файле `LICENSE`.
