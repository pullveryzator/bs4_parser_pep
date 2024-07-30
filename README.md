# Проект парсинга pep

PEP Parser - это простой в использовании парсер документации Python, который позволяет загружать, выводить и управлять документацией PEP (Python Enhancement Proposals).

## Установка

Для использования PEP Parser необходимо иметь установленный Python 3.x. Склонируйте или загрузите этот репозиторий на свой компьютер.

bash
git clone https://github.com/pullveryzator/bs4_parser_pep.git
cd bs4_parser_pep/src
python -m venv venv
source venv/Scripts/activate
pip install - r requirements.txt


## Использование

Вы можете запустить парсер, используя следующую команду:

bash
python main.py [опции] {режим работы}


### Режимы работы

* `whats-new` - Получает информацию о нововведениях в последней версии Python.
* `latest-versions` - Получает информацию о последних версиях Python.
* `download` - Позволяет скачать документацию.
* `pep` - Получение информации о статусах PEP.

### Опции

- `-h`, `--help`  : Показать это сообщение и выйти.
- `-c`, `--clear-cache` : Очистить кеш.
- `-o {pretty,file}`, `--output {pretty,file}` : Определяет способ вывода данных. Доступные варианты:
- `pretty` - Читаемый формат вывода.
- `file`   - Сохранить вывод в файл.

### Примеры

1. Получить информацию о нововведениях в последней версии Python:
   
bash
python main.py whats-new


2. Получить информацию о последних версиях Python с выводом в человеко-читаемом формате:
   
bash
python main.py latest-versions -o pretty


3. Сохранить информацию о статусах PEP в файл:
   
bash
python main.py pep -o file


4. Очистить кеш:
   
bash
python main.py {режим работы} -c
