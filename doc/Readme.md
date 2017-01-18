# Технический облик (требования)

Локальная БД хранится в зашифрованном файле.
Записи извлекаются по необходимости и удаляются из памяти, если больше не нужны.
Удаленные записи хранятся также зашифрованными.
При синхронизации не расшифровываются.

БД: id-value storage, структурированные данные хранятся в json
При открытии БД создается индекс, при изменении БД в памяти индекс меняется в памяти
Специфика приложения позволит обойтись оперативной памятью для индекса

Пример: отобрать только записи тасков из БД или только notes
    Проходим по индексу, открываем каждую запись, проверяем, что это, добавляем в список
    Нет плана хранить индексы с указаниями на контент в оперативной памяти

# Валидация AES

* http://csrc.nist.gov/groups/STM/cavp/
* http://csrc.nist.gov/groups/STM/cavp/documents/aes/AESAVS.pdf
* http://www.inconteam.com/software-development/41-encryption/55-aes-test-vectors
* http://csrc.nist.gov/groups/STM/cavp/block-ciphers.html#aes http://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf

# TODO
* Изучить и использовать http://keepass.info/help/base/security.html
