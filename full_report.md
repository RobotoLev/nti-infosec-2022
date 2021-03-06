# CODER SQUAD

---
## Инвентаризация

Базовая инвентаризация проводилась по подсетям `10.12.2.0/24`, `10.12.3.0/24`, `10.12.4.0/24`, `10.12.239.0/24`, `10.12.240.0/24` при помощи утилиты `nmap`.
Результаты доступны в репозитории в папке `init_inv` в виде скриншотов (сервера организаторов не включены).

### Linux 10.12.2.10 - DMZ
На первом хосте открыты 4 порта: 22 ssh, 80 и 8080 http-сервера, 3306 mysql.

### Windows 10.12.2.11 - DMZ
Сканируем директории дирбустом. Находим список директорий. Среди доступных видим директорию `/scripts`, где можно найти логи базы данных, а так же базовую инициализацию 6 юзеров.

### Windows 10.12.2.12 - DMZ
Открыты почтовые порты smtp, imap, pop3. Также мы открыли RDP 3389 и SSH 22. Открыты исходящие порты для подключения к серверу

### Windows 10.12.239.5 - АСУ ТП
На данной машине запущена база данных MSSQL SQLEXPRESS, OIK-SERVER. Базу хакер пытался взломать.

### Windows 10.12.239.6 - АСУ ТП
На данной машине запущен клиент OIK-CLIENT. 
Также имеются файлы с инструкцией по использованию платформы "Сервер ОИК Диспетчер"

### Windows 10.12.240.14 - АСУ ТП
На данной машине запущен сервер Smart EPS.
Клиенты Smart EPS: 10.12.240.6, 10.12.240.9, 10.12.240.10

### Windows 10.12.240.6 - АСУ ТП
На данной машине запущен веб-интерфейс программы Smart EPS на порту 80.

### Windows 10.12.4.6 - OFFICE
### Windows 10.12.3.50 - SERVERS
На данных машинах запущен сервис Windows Remote Management на портах 5985 и 5986(SSL), который уязвим к бруту паролей.


### 10.12.200.50 
По этому айпи адресу находится сервер злоумышленника, с которого были загружен вирус шифровальщик.
Открыты порты 22 и 8083, на последнем развернута система Nagios NSCA

### 10.12.1.254 - IDS
На этом айпи установлен Suricata IDS, используя hydra для перебора паролей можно найти следующий пароль для пользователя user `user:Tiffany1`
Подключившись по SSH, в домашней директории можно найти дамп траффика traf.pcap.

### Others
Также, нам удалось найти другие машины в сети по следующим адресам:

10.12.5.10

10.12.5.11

10.12.5.12

10.12.5.13

10.12.5.14

10.12.5.15

10.12.6.254

На всех машинах открыт только порт 22, но брутфорснуть пароль у нас не получилось т.к. не выдерживали наши машины

---
## Расследование

### 10.12.1.254 - IDS
Анализируя траффик, можно убедиться, что злоумышленник с адреса 10.12.200.50 сначала целенаменно атаковал 10.12.2.11.
После получения шелла, злоумышленник запустил сканер уязвимостей или дирсеарч в поиске резервных копий.

См. в системе проведения соревнования

---
## Возврат контроля

### Linux 10.12.2.11 - DMZ
Узнать версию drupal можно по адресу http://10.12.2.11/CHANGELOG.txt. Версия - 7.56. Эта версия уязвима.
Злоумышленник получил шелл shell.php используя уязвимость CVE-2018-7600.
```
use exploit/unix/webapp/drupal_drupalgeddon2
```
На сайте были обнаружены зашифрованные файлы в /var/www/html/ с расшифрением .encr.

Загружаем шелл как myshell.php, получаем доступ как www-data

### Linux 10.12.2.10 - DMZ
На 80 порту обнаруживается простой сайт на Wordpress со стандартным доступом admin/admin. 

В админке уже установлен плагин для просмотра файлов, задаем ему корневую папку в `/` и получаем доступ ко всей файловой системе от имени `www-data`.
Загружаем веб-шелл, получаем доступ к командной строке от имени `www-data`.

При анализе логов и конфигов серверной части (`nginx` и `uwsgi`) находим Flask-приложение в `/home/user/SolarApp_back/` и его бекап в `/home/cadm/SolarApp_back/`.
Бекап readonly, у user-а имеем write-права.

При анализе `/etc/sudoers` замечаем, что `www-data` может запускать Python 2 под sudo без пароля.
Загружаем reverse shell, запускаем его под sudo, получаем root-доступ через шелл.
Генерируем пару ключей ed25519, публичный кладем в `/root/.ssh`, приватный копируем на свою машину. Получаем ssh-доступ под рутом.

У нас есть root-доступ, поэтому генерируем новые пароли для `cadm`, `admin` и `root` (все они в `passwords.txt`).
Пользователя `user` в системе не существует, хотя папка его и есть.

### Windows 10.12.2.12 - DMZ
Эксплуатируем уязвимость CVE-2017-0143 и попадаем на машину.
`sudo msfconsole`

`use exploit/windows/smb/ms17_010_eternalblue`

`set RHOST 10.12.2.12`

`run`

Устранить ее можно закрыв порт 445 используя фаерволл или обновив Windows до последней версии.
`
netsh advfirewall firewall add rule dir=in action=block protocol=tcp localport=445 name=“Block_TCP-445”
` - блокирует порт 445

Находим уязвимый сервис `SLMail.exe` версии 5.5, которая уязвима к RCE при переполнении буфера CVE-2003-0264.
Так как данный почтовый сервис больше не поддерживается разработчиками и версия 5.5 является последней и уязвимой.
Мы предлагаем удалить SLMail с коипьютера и заменить его на альтернативный почтвый сервер, к примеру бесплатный open-source hMailServer.

В локальной сети обнаружены компьютеры FRIT-SLMAIL(10.12.2.12) и CLEAN-DRUPAL(10.12.2.11).

Возвращаем доступ к cadm:

`shell`

`net user cadm ASdasdas6Dda76`
### Windows 10.12.4.8 - OFFICE
Данная машина также подвержена уязвимости CVE-2017-0143, ее фикс и использование было уже описано выше.
После открытия сессии meterpreter, мы восстанавливаем доступ к системе, сменив пароль у пользователя cadm. Новый пароль - RandomPassword777. Доступ по RDP/SSH восстановлен. 

При анализе истории подключений по ssh можно обнаружить подключение с айпи адреса `192.168.122.1`.
Также, в сохраненных ключах ssh можно обнаружить ключ, заканчивающийся на `D+NX Generated-By-Nova`.
Этот же ключ встречается на всех машинах, по нему совершались входы с `192.168.224.43` и `192.168.224.254`.

В локальной сети были обнаружены компьютеры BUCHGARM(10.12.4.8), CUSTARM, ENGGENERAL, SYSADMINARM.

### Windows 10.12.239.5 - АСУ ТП
Данная машина также подвержена уязвимости CVE-2017-0143, ее фикс и использование было уже описано выше.
После открытия сессии meterpreter, мы восстанавливаем доступ к системе, сменив пароль у пользователя cadm. Новый пароль - LOLLOL123lOLLOL. Доступ по RDP/SSH восстановлен. 

На данной машине запущен сервер ОИК Диспетчер НТ.

### Windows 10.12.240.14 - АСУ ТП
Данная машина также подвержена уязвимости CVE-2017-0143, ее фикс и использование было уже описано выше.
После открытия сессии meterpreter, мы восстанавливаем доступ к системе, сменив пароль у пользователя cadm. Новый пароль - RandomPassword777. Доступ по RDP/SSH восстановлен. 

На данной машине запущен EnLogicSvcForPLClib, это контроллер SCADA ЭНТЕК.

---
## Расшифровка файлов

### Linux 10.12.2.10 - DMZ
Python-приложение не работает, т.к. не имеет доступа к базе: в коде прописан доступ `root/root`, вероятно злоумышленник изменил доступы в базе.

Был восстановлен бекап базы данных из файла сохранения. Легитимный доступ для конечного пользователя к приложению восстановлен.

### Windows 10.12.239.6 - АСУ ТП
На данной машине в директории C:/Share были обнаружены зашифрованные файлы с расширением .crpt.
Также мы обнаружили файл C:/Random.ps1, который был загружен злоумышленником с целью зашифровать файлы в папке C:/Share, используя алгоритм шифрования AES CBC и случайный ключ.
Чтобы злоумышленник мог расшифровать файлы, скрипт отправляет ключ и IV на его сервер.
В системных логах Powershell можно найти скачивание этого скрипта с `http://10.12.200.50/Random.ps1` и запуск с аргументом -IP 10.12.200.50.
Из этого можно сделать вывод, что атака на данную машину произошла 05.03.2022 14:05:25 от имени company/Administrator. (см. `crpt_ransom_log.txt`)

Также можно найти ключ и IV в адресе запроса: `key=kwyuLuIM66SllKElfnJbFBZz+8LHa/jLVd34xLsNr3M=&iv=XZ1uD7cFGJwKx7AhqgGp5g==`
Используя ключ можно расшифровать все файлы из папки Share, к примеру файл FLAG.txt: `Fama bona volat lente et mala fama repente.`
(все расшифрованные файлы лежат в папке decrypted)

### Windows 10.12.2.14 - АСУ ТП
На сервере SCADA можно найти базу данных enlogic.plc формата SQLite 3. Она не зашифрована, можно ее открыть и прочитать логи.

---
## Остановка распространения  

### Linux 10.12.2.10 - DMZ
Меняем пароль админки Wordpress на `E1Jsw0)*(8dx`.

Исходное Python-приложение было уязвимо к SQL-инъекции. Приложение переписано, уязвимость исправлена. Исправленный код в `app.py`.

### Windows 10.12.239.6 - АСУ ТП
Данная машина была подвержена атаке со стороны злоумышленника. После выполнения, скрипт Random.ps1 выключил сохранение точек восстановления, защитник Windows и фаерволл.
Все эти пункты были исправлены.

На всех машинах подсети АСУ ТП был полностью заблокирован доступ к айпи 10.12.200.50 во избежание дальшейших атак злоумышленника.
