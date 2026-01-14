# Инсталация на Midea AC LAN интеграция за Home Assistant 2026.1.1

## 🚨 КРИТИЧЕН ПРОБЛЕМ - BREAKING CHANGE В 2026.1.1

**Home Assistant 2026.1.1 премахна `MINOR_VERSION` от ConfigFlow API!**

Ако интеграцията ви **спря да работи** след обновяване от 2026.01 на 2026.1.1:

### ✅ БЪРЗА ПОПРАВКА

Проблемът е в [config_flow.py](custom_components/midea_ac_lan/config_flow.py) - използва се премахнатата константа `MINOR_VERSION`.

**Решение:**

```bash
# SSH в Home Assistant
cd /config/custom_components/midea_ac_lan

# Backup на файла
cp config_flow.py config_flow.py.backup

# Премахни MINOR_VERSION реда
sed -i '/MINOR_VERSION = 1/d' config_flow.py

# Рестартирай
ha core restart
```

**Или ръчно редактирай файла:**

1. Отвори `/config/custom_components/midea_ac_lan/config_flow.py`
2. Намери реда около line 106: `MINOR_VERSION = 1`
3. **Изтрий** целия ред
4. Запази файла
5. Рестартирай Home Assistant

След това интеграцията ще заработи нормално!

---

## ✅ НОРМАЛНА ИНСТАЛАЦИЯ

**Midea-local пакетът се инсталира АВТОМАТИЧНО!**

Интеграцията е конфигурирана да инсталира автоматично `midea-local>=6.5.0` пакета. Просто:

1. Инсталирайте интеграцията през HACS или ръчно
2. Рестартирайте Home Assistant
3. Добавете интеграцията от Settings → Devices & Services → Add Integration

Home Assistant автоматично ще свали и инсталира всички необходими пакети.

---

## ⚠️ ВАЖНО - Мрежов проблем в HAOS 2026.1.1

**Само ако видите грешка** за инсталация на пакети, има познат проблем с HAOS 2026.1.1.

**Грешката която виждате:**

```
Unable to install package midea-local==6.5.0: error: Failed to fetch
Caused by: dns error: failed to lookup address information: Name does not resolve
```

### Причини за проблема:

1. **Hyper-V мрежова изолация** - Hyper-V Virtual Switch може да блокира достъп до PyPI
2. **Hyper-V NAT конфигурация** - NAT network adapter може да има проблеми с DNS forwarding
3. **Home Assistant Supervisor изолация** - Supervisor контейнерът може да не споделя мрежовите настройки с основния контейнер
4. **Firewall блокира достъп до PyPI** - Някои мрежови конфигурации блокират достъп до files.pythonhosted.org
5. **Proxy/VPN конфликт** - Ако използвате proxy или VPN, може да блокира пакетната инсталация
6. **IPv6 проблеми** - Home Assistant може да опитва IPv6 което не работи във вашата мрежа
7. **Supervisor използва uv вместо pip** - Новият package manager може да има проблеми с мрежата

## 🔧 РАБОТЕЩИ РЕШЕНИЯ

### ✅ Решение 1: Поправка на Hyper-V мрежата (ПРЕПОРЪЧИТЕЛНО ЗА HYPER-V)

**Стъпка 1: Провери Hyper-V Virtual Switch настройките**

1. Отвори **Hyper-V Manager**
2. Избери **Virtual Switch Manager**
3. Уверете се че виртуалният switch е конфигуриран като **External Network**
4. Ако използваш Internal/Private switch, смени го на External

**Стъпка 2: Провери DNS настройките на Windows хоста**

```powershell
# В PowerShell на Windows хоста
Get-DnsClientServerAddress
# Провери дали DNS е 8.8.8.8 и 8.8.4.4
```

**Стъпка 3: Рестартирай VM-a**

```powershell
# В PowerShell на хоста
Stop-VM -Name "Home Assistant"
Start-VM -Name "Home Assistant"
```

**Стъпка 4: Тествай от HAOS**

```bash
# SSH в Home Assistant
ping -c 4 8.8.8.8
ping -c 4 pypi.org
nslookup files.pythonhosted.org

# Ако nslookup не работи, но ping работи:
docker exec -it homeassistant bash
curl -v https://pypi.org
exit
```

### ✅ Решение 2: Hyper-V NAT Network поправка

Ако използваш NAT Network, може да има проблеми с DNS forwarding:

```powershell
# В PowerShell на Windows хоста с Admin права
Get-NetNat
# Ако виждаш NAT network, опитай да го рестартираш:
Remove-NetNat -Name "Your NAT Name" -Confirm:$false
New-NetNat -Name "HomeAssistantNAT" -InternalIPInterfaceAddressPrefix "192.168.1.0/24"
```

**Или използвай External Switch вместо NAT:**

1. Hyper-V Manager → Virtual Switch Manager
2. Create External Virtual Switch
3. Свържи го към физическия network adapter
4. В настройките на HAOS VM смени network adapter към новия External Switch

### ✅ Решение 3: Директна инсталация в Home Assistant контейнера

```bash
# SSH в Home Assistant
docker exec -it homeassistant bash

# Опитайте директно от GitHub (заобикаля PyPI/Supervisor)
pip3 install --no-cache-dir git+https://github.com/rokam/midea-local.git@v6.5.0

# Провери инсталацията
python3 -c "import midealocal; print(midealocal.__version__)"
# Трябва да види: 6.5.0

exit
```

**След това премахни requirements от manifest.json:**

```bash
cd /config/custom_components/midea_ac_lan
cp manifest.json manifest.json.backup
sed -i 's/"requirements": \["midea-local>=6.5.0"\]/"requirements": []/' manifest.json
```

**Рестартирай Home Assistant**

### ✅ Решение 4: Използване на Windows хост за изтегляне (ИДЕАЛНО ЗА HYPER-V)

Тъй като използваш Hyper-V на Windows, можеш да изтеглиш пакета от Windows хоста:

**Стъпка 1: Изтегли от Windows хоста**

```powershell
# В PowerShell на Windows хоста
cd $env:USERPROFILE\Downloads
Invoke-WebRequest -Uri "https://files.pythonhosted.org/packages/a1/dd/8ef77aea86428f834c18f1dc2c6df5f60e1be41ba5cedf697518920eb5d2/midea_local-6.5.0-py3-none-any.whl" -OutFile "midea_local-6.5.0-py3-none-any.whl"

# Или от GitHub
Invoke-WebRequest -Uri "https://github.com/rokam/midea-local/archive/refs/tags/v6.5.0.tar.gz" -OutFile "midea-local-6.5.0.tar.gz"
```

**Стъпка 2: Копирай във VM чрез Samba share**

1. Отвори `\\homeassistant\config` от Windows Explorer
2. Копирай изтегления файл в `config` папката
3. Инсталирай през SSH:

```bash
# SSH в Home Assistant
docker exec -it homeassistant bash
pip3 install /config/midea_local-6.5.0-py3-none-any.whl
# Или ако си изтеглил tar.gz:
pip3 install /config/midea-local-6.5.0.tar.gz
exit
```

**Стъпка 3: Премахни requirements**

```bash
cd /config/custom_components/midea_ac_lan
sed -i 's/"requirements": \["midea-local>=6.5.0"\]/"requirements": []/' manifest.json
```

**Стъпка 4: Рестартирай**

```bash
ha core restart
```

1. **Редактирайте manifest.json:**

   ```json
   "requirements": [],
   ```

2. **Инсталирайте midea-local в системата:**

   ```bash
   docker exec -it homeassistant bash
   apk add --no-cache git
   pip install git+https://github.com/rokam/midea-local.git@v6.5.0
   exit
   ```

3. **Рестартирайте Home Assistant**

### ✅ Решение 6: Пълна диагностика на Hyper-V мрежата

**От Windows хоста (PowerShell с Admin):**

```powershell
# Провери VM network адаптера
Get-VMNetworkAdapter -VMName "Home Assistant"

# Провери виртуалния switch
Get-VMSwitch

# Провери дали има MAC address conflicts
Get-VMNetworkAdapter -VMName "Home Assistant" | Select-Object MacAddress

# Тествай connectivity от хоста
Test-NetConnection pypi.org -Port 443
Test-NetConnection files.pythonhosted.org -Port 443

# Ако не работи, рестартирай мрежата на VM:
Get-VMNetworkAdapter -VMName "Home Assistant" | Disconnect-VMNetworkAdapter
Start-Sleep -Seconds 5
Get-VMNetworkAdapter -VMName "Home Assistant" | Connect-VMNetworkAdapter -SwitchName "Your Switch Name"
```

**От HAOS (SSH):**

```bash
# Пълна мрежова диагностика
ha network info
ip addr show
ip route show
cat /etc/resolv.conf

# Тествай връзката
ping -c 4 8.8.8.8
ping -c 4 pypi.org
nslookup pypi.org
nslookup files.pythonhosted.org

# Тествай от контейнера
docker exec -it homeassistant bash
curl -v --connect-timeout 10 https://pypi.org
python3 -c "import urllib.request; print(urllib.request.urlopen('https://pypi.org').status)"
exit
```

**Ако Hyper-V блокира трафика:**

1. Изключи Windows Firewall временно за тест
2. Провери Windows Defender блокира ли трафика
3. Използвай External Network Switch (не NAT)
4. Уверете се че "Virtual Machine Monitoring" е включен в Firewall

# От Supervisor

ha supervisor logs | grep -i "midea\|pypi\|fetch\|dns"

````

**Стъпка 3: Временно изключи Supervisor за пакети**

Ако Supervisor блокира, инсталирай директно в контейнера:

```bash
docker exec -it homeassistant bash
pip3 install --user --no-cache-dir midea-local==6.5.0
exit
````

След това премахни `requirements` от manifest.json за да не се опитва Supervisor да инсталира:

```bash
cd /config/custom_components/midea_ac_lan
sed -i 's/"requirements": \["midea-local>=6.5.0"\]/"requirements": []/' manifest.json
```

**Стъпка 4: Рестартирай всичко**

```bash
ha core restart
```

## Проблем

След актуализация на Home Assistant OS 2026.1.1, интеграцията дава грешка:

```
Setup failed for custom integration 'midea_ac_lan': Requirements for midea_ac_lan not found: ['midea-local>=6.5.0']
```

## Решение

### Метод 1: Ръчна инсталация на midea-local пакета

1. **Влезте в SSH терминала на Home Assistant**
   - Инсталирайте SSH add-on ако нямате
   - Свържете се към Home Assistant

2. **Инсталирайте midea-local пакета ръчно:**

   ```bash
   docker exec -it homeassistant /bin/bash
   pip install midea-local==6.5.0
   exit
   ```

3. **Рестартирайте Home Assistant**
   - Настройки -> Система -> Рестартиране

### Метод 2: Използване на оригинална версия (временно)

Ако продължава да не работи, може временно да се върнете към версия без промени:

```bash
# В папката custom_components/midea_ac_lan/
git checkout b189730
```

След това рестартирайте Home Assistant.

### Метод 3: Изчистване на кеша

1. **Изтрийте cache файловете:**

   ```bash
   rm -rf /config/custom_components/midea_ac_lan/__pycache__
   rm -rf /config/custom_components/midea_ac_lan/*/__pycache__
   ```

2. **Рестартирайте Home Assistant**

## Промени във версия 0.6.11

Тази версия включва следните промени за съвместимост с Home Assistant 2026.1.1:

✅ Премахнати deprecated `MAJOR_VERSION` и `MINOR_VERSION` константи
✅ Премахнати версионни проверки за backwards compatibility
✅ `ClimateEntityFeature.TURN_ON` и `TURN_OFF` са винаги активни
✅ Опростени импорти и модернизиран код
✅ Добавен български превод (bg.json)

## Ако нищо не работи

### Опция A: Инсталация през HACS

1. Отворете HACS
2. Отидете на Integrations
3. Потърсете "Midea AC LAN"
4. Кликнете Reinstall
5. Рестартирайте Home Assistant

### Опция B: Пълна преинсталация

1. **Премахнете интеграцията:**

   ```bash
   rm -rf /config/custom_components/midea_ac_lan
   ```

2. **Копирайте отново файловете от този проект**

3. **Уверете се че manifest.json съдържа:**

   ```json
   "requirements": ["midea-local>=6.5.0"],
   "version": "v0.6.11"
   ```

4. **Рестартирайте Home Assistant**

## Проверка на лога

За да видите точната грешка:

1. Настройки -> Система -> Дневници
2. Търсете за "midea_ac_lan"
3. Проверете дали има грешки свързани с:
   - Python import грешки
   - Requirements грешки
   - Connection грешки

## Необходими изисквания

- Home Assistant OS 2026.1.1 или по-нова
- midea-local пакет версия 6.5.0 или по-нова
- Python 3.11 или по-нова

## Допълнителна помощ

Ако проблемът продължава:

1. Проверете дали имате интернет връзка в Home Assistant
2. Проверете дали pip може да инсталира пакети
3. Опитайте да инсталирате midea-local ръчно (вижте Метод 1)

За техническа поддръжка, отворете issue на: https://github.com/wuwentao/midea_ac_lan/issues
