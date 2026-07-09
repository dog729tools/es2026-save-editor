# Esports Manager 2026 Save Editor / Редактор сохранений

**ENGLISH**

A save editor for **Esports Manager 2026** with a GUI on PySide6.  
Allows you to open `SlotData.mpack`, edit data by section, and save it back to the game.

> This project is not an official tool by the game developers.
> Always keep a backup copy of your save.

## What is it for? 

Use this tool if you want to:
- edit players, staff, and other data right from the save file;
- change skill values and see skill history charts;
- quickly search entries by ID/nickname/name;
- save changes directly back to `SlotData.mpack`, with an automatic `.bak` backup.

Under the hood: MessagePack is unpacked → readable JSON → edited → packed back.

## Key Features

- GUI editor for save file sections (`section_10`, `section_11`, `section_22`, etc.)
- RU/EN interface support
- Search entries (handy for large sections)
- Skill editor with history charts
- Skill value limit: **0..20**
- Automatic backup creation when saving: `SlotData.mpack.bak`
- Works only with Save folder (no need for the game installation path)

## Project Structure

- `mpack_gui.py` — main GUI application
- `mpack_codec.py` — MessagePack/JSON codec and section assembler
- `editor_config.json` — field/type/display config
- `section_profile.json` — `field_*` aliases and section names
- `start_mpack_gui.bat` — quick start for Windows
- `workdir/` — working directory for extracted slot data

## Requirements

- Windows
- Python 3.10+ (3.11+ recommended)
- Packages:
  - `msgpack`
  - `PySide6`

## Installation

From your Save folder root:

```powershell
python -m pip install msgpack PySide6
```

## Launching

Option 1 (recommended):

```powershell
python mpack_gui.py
```

Option 2:

```powershell
start_mpack_gui.bat
```

## How to use

1. Start the editor.
2. Make sure the Save folder path was detected correctly.
3. Select a slot (e.g. `20075`) and click **Load**.
4. Open the needed section in the tabs.
5. Find a record using search and make your changes.
6. Click **Save to mpack**.
7. Check that `SlotData.mpack.bak` was created/updated next to your file.

## Important Notes

- Make a backup copy of your entire Save folder before testing the tool!
- If the game misbehaves after editing, restore `SlotData.mpack` from `.bak`.
- Section `45` contains built-in text data (manifest/csv/json-strings) and is rarely needed for gameplay edits.
- Save file format is sensitive to data types; avoid manual edits of large JSONs unless necessary.

## Typical Restore Scenario

If you "break" your save:

1. Close the editor.
2. Rename the current `SlotData.mpack` (e.g., to `SlotData.mpack.bad`).
3. Rename `SlotData.mpack.bak` to `SlotData.mpack`.
4. Open the editor again and reload the slot.

## Roadmap (optional)

- more user-friendly contract editor (structured forms instead of raw JSON)
- more sections and field decoding
- better value validation

## Disclaimer

Use at your own risk. The tool author is not responsible for save corruption.

---

**РУССКИЙ**

Редактор сохранений для **Esports Manager 2026** с графическим интерфейсом на PySide6.  
Позволяет открыть `SlotData.mpack`, редактировать данные по секциям и сохранять обратно в игру.

> Проект не является официальным инструментом разработчиков игры.  
> Всегда держите резервную копию своего сохранения.

## Что это и зачем

Этот инструмент нужен, если вы хотите:
- править игроков, персонал и другие данные прямо из сейва;
- менять значения навыков и смотреть историю навыков на графике;
- быстро искать записи по ID/нику/имени;
- сохранять изменения обратно в `SlotData.mpack` с автоматическим созданием `.bak`.

Внутри используется распаковка MessagePack → читаемый JSON → редактирование → упаковка обратно.

## Основные возможности

- GUI-редактор секций сейва (`section_10`, `section_11`, `section_22` и т.д.)
- Поддержка RU/EN интерфейса
- Поиск по записям (удобно для больших секций)
- Редактор навыков с графиком истории
- Ограничение значения навыка: **0..20**
- Автоматическое создание бэкапа при сохранении: `SlotData.mpack.bak`
- Работа только с папкой Save (без привязки к пути установки игры)

## Структура проекта

- `mpack_gui.py` — основное GUI-приложение
- `mpack_codec.py` — кодек MessagePack/JSON и сборщик секций
- `editor_config.json` — конфиг полей, типов и отображения
- `section_profile.json` — алиасы `field_*` и названия секций
- `start_mpack_gui.bat` — быстрый запуск под Windows
- `workdir/` — рабочая директория для распакованных данных слота

## Требования

- Windows
- Python 3.10+ (рекомендован 3.11+)
- Пакеты:
  - `msgpack`
  - `PySide6`

## Установка

Из корня папки Save:

```powershell
python -m pip install msgpack PySide6
```

## Запуск

Вариант 1 (рекомендуется):

```powershell
python mpack_gui.py
```

Вариант 2:

```powershell
start_mpack_gui.bat
```

## Как пользоваться

1. Запустите редактор.
2. Убедитесь, что путь к папке Save определился верно.
3. Выберите слот (например, `20075`) и нажмите **Загрузить**.
4. Откройте нужную секцию во вкладках.
5. Найдите запись через поиск и внесите изменения.
6. Нажмите **Сохранить в mpack**.
7. Проверьте, что появился или обновился `SlotData.mpack.bak`.

## Важные замечания

- Перед первыми экспериментами сделайте отдельную копию всей папки Save!
- Если после правок игра ведет себя странно, верните `SlotData.mpack` из `.bak`.
- Секция `45` содержит встроенные текстовые данные (manifest/csv/json-строки) и обычно не нужна для геймплейных правок.
- Формат сейва чувствителен к типам данных; не редактируйте большие JSON-файлы вручную без необходимости.

## Типовой сценарий восстановления

Если ''сломали'' сейв:

1. Закройте редактор.
2. Переименуйте текущий `SlotData.mpack` (например, в `SlotData.mpack.bad`).
3. Переименуйте `SlotData.mpack.bak` в `SlotData.mpack`.
4. Снова откройте редактор и загрузите слот.

## Дорожная карта (опционально)

- более удобный редактор контрактов (структурные формы вместо raw JSON)
- дополнительные секции и расшифровка полей
- улучшенная валидация значений

## Disclaimer / Отказ от ответственности

Использование на свой риск. Автор инструмента не несет ответственности за повреждение сейвов.
