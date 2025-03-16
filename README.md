# CodeMerger

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CodeMerger - это настольное приложение, которое помогает анализировать и экспортировать структуру файлов и содержимое вашего проекта. Оно было создано для упрощения обмена кодом с ИИ-ассистентами, предоставляя чистое, организованное представление вашей кодовой базы.
![image](https://github.com/user-attachments/assets/eb484e92-08c9-43b8-bfd4-cf2aba11b92d)



## Возможности

- **Анализ структуры проекта**: Сканирование любой папки для анализа её файловой структуры
- **Извлечение содержимого**: Извлечение и отображение содержимого текстовых файлов
- **Умное определение бинарных файлов**: Автоматическое определение и пропуск бинарных файлов
- **Настраиваемые ограничения**: Установка максимального размера файла. Поле для настройки обрезки содержимого файлов при парсиге, с исключением(через запятую)
- **Фильтрация файлов**: Фильтрация файлов по статусу (OK, ОШИБКА, БИНАРНЫЙ и т.д.)
- **Возможности поиска**: Поиск по имени файла или содержимому файла
- **Варианты экспорта**: Экспорт вашего проекта в формате Markdown или JSON
- **Шаблоны игнорирования**: Установка шаблонов для игнорирования определенных файлов или директорий
- **Многопоточная обработка**: Быстрое сканирование с параллельной обработкой

## Зачем нужен CodeMerger?

При работе с ИИ-ассистентами, такими как ChatGPT, Claude или GitHub Copilot, обмен структурой проекта и кодом необходим для получения точной помощи. CodeMerger упрощает этот процесс путем:

1. Создания чистого, организованного представления вашей кодовой базы
2. Фильтрации бинарных файлов и больших файлов, которые не имеют отношения к делу
3. Предоставления содержимого в формате, который легко передать (Markdown или JSON)
4. Предоставления вам контроля над тем, какая информация включена

## Установка

### Предварительные требования

- Python 3.6 или выше
- Необходимые пакеты: tkinter, charset-normalizer, binaryornot

### Настройка

1. Клонируйте этот репозиторий или загрузите исходный код

```bash
git clone https://github.com/yourusername/codemerger.git
cd codemerger
```

2. Установите необходимые зависимости

```bash
pip install charset-normalizer binaryornot
```

3. Запустите приложение

```bash
python manager.py
```

## Использование

1. **Выберите папку**: Нажмите кнопку "Выбрать", чтобы выбрать папку, которую вы хотите проанализировать
2. **Начните сканирование**: Нажмите кнопку "Старт", чтобы начать сканирование выбранной папки
3. **Просмотр результатов**: Просмотрите список файлов, чтобы увидеть все файлы в проекте
4. **Фильтрация файлов**: Используйте выпадающее меню для фильтрации файлов по статусу
5. **Поиск**: Используйте поля поиска для поиска файлов по имени или содержимому
6. **Просмотр содержимого**: Дважды щелкните на файле, чтобы просмотреть его содержимое
7. **Экспорт**: Нажмите "Экспорт MD" или "Экспорт JSON", чтобы сохранить структуру проекта и содержимое

## Конфигурация

CodeMerger можно настроить через пользовательский интерфейс или путем редактирования файла `codemerger_config.json`:

- **Максимальная длина содержимого**: Ограничение количества символов для извлечения из каждого файла
- **Максимальный размер файла**: Пропуск файлов, размер которых превышает указанный размер (в КБ)
- **Исключенные файлы**: Список имен файлов, которые следует исключить из извлечения содержимого
- **Шаблоны игнорирования**: Шаблоны, которые следует игнорировать при сканировании (например, `*.log`, `node_modules/*`)

## Форматы экспорта

### Markdown

Экспорт в Markdown включает:
- Сводку проекта с количеством файлов
- Структуру папок
- Детали файлов (расширение, размер, кодировка)
- Содержимое файла с подсветкой синтаксиса

### JSON

Экспорт в JSON включает:
- Метаданные проекта
- Полную структуру папок
- Детали и содержимое файлов
- Информацию о статусе и ошибках файлов

## Вклад в проект

Вклады приветствуются! Пожалуйста, не стесняйтесь отправлять Pull Request.

## Лицензия

Этот проект лицензирован под лицензией MIT - см. файл LICENSE для получения подробной информации.
