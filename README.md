# test-kanal
ВСЕМ ПРИВЕТ!
ДАННЫЙ СКРИПТ ПОЗВОЛЯЕТ ИЗ ГУГЛ ТАБЛИЦ С НАСТРАИВАЕМОЙ ПЕРИОДИЧНОСТЬЮ СИНХРОНИЗИРОВАТЬ ДАННЫЕ В БАЗУ ДАННЫХ POSTGRESQL

УСТАНОВКА

1.Настроить сервисную учетную запись google cloud (согласно инструкции)
2. получить файл ключа в формате credential.json
3. указать в настройках файла config.ini параметры подключения к заранее созданой базы данных на postgresql
4. В файле requiremens.txt установить все библиотеки python для запуска
5. Либо в файле setup.txt с помощью командной строки выполнить установку библиотек
6. Данная версия работает без докера
7. установить среду интерпретатора python 3.10
8. Проверить наличие доступа к файлу test.xlsx в гугл таблицах
9. Запустить с командной строки python main.py
