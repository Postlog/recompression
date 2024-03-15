# recompression

Реализация метода рекомпрессии для задачи сопоставления с образцом, курсовая работа за 7 семестр.

# Запуск

Для запуска выполните следующие шаги
1. Установите зависимости через `pip install -r requirements.txt`
2. Выполните команду  `python main.py --help` чтобы посмотреть как пользоваться:
    - Ключ `-z3` добавляет к списку используемых эвристик подсчет констант
    - Ключ `-pref-suff` добавляет к списку используемых эвристик сравнение префиксов и суффиксов
    - Если указан `-output <PATH>`, то по указанному пути будет сохранено изображение итогового дерева
    - Обязятаельный позиционный аргумент `equation` - сопоставление в виде `...=...`
   
   Пример: `python main.py -z3 -pref-suff ZbXYbX=abcab -output ZbXYbX=abcab.svg`

