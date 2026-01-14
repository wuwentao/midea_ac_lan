# БЪРЗА ПОПРАВКА ЗА DNS ПРОБЛЕМА

## Проблемът

```
dns error: failed to lookup address information: Name does not resolve
```

Home Assistant OS 2026.1.1 не може да достигне PyPI за изтегляне на midea-local пакета.

## БЪРЗА ПОПРАВКА (5 минути)

### Стъпка 1: Поправете DNS

1. Отворете **Settings** → **System** → **Network**
2. Намерете вашия network адаптер
3. Кликнете **IPv4** или **IPv6** настройки
4. Променете DNS на:
   ```
   Primary DNS: 8.8.8.8
   Secondary DNS: 8.8.4.4
   ```
5. Запазете и рестартирайте

### Стъпка 2: Ако DNS не помага - Премахнете requirements

**Опция A: През File Editor (лесно)**

1. Отворете File Editor в Home Assistant
2. Намерете: `/config/custom_components/midea_ac_lan/manifest.json`
3. Намерете реда:
   ```json
   "requirements": ["midea-local==6.5.0"],
   ```
4. Променете на:
   ```json
   "requirements": [],
   ```
5. Запазете файла

**Опция B: През SSH**

```bash
cd /config/custom_components/midea_ac_lan
cp manifest.json manifest.json.backup
sed -i 's/"requirements": \["midea-local==6.5.0"\]/"requirements": []/' manifest.json
```

### Стъпка 3: Инсталирайте midea-local ръчно

```bash
# Влезте в Home Assistant контейнера
docker exec -it homeassistant bash

# Опитайте директно от GitHub (заобикаля PyPI)
pip install --no-cache-dir git+https://github.com/rokam/midea-local.git@v6.5.0

# АКО горното не работи, опитайте от archive:
cd /tmp
wget https://github.com/rokam/midea-local/archive/refs/tags/v6.5.0.tar.gz
pip install v6.5.0.tar.gz

# Излезте от контейнера
exit
```

### Стъпка 4: Рестартирайте Home Assistant

Settings → System → Restart

## Проверка дали работи

След рестартиране отидете на:

- **Settings** → **Devices & Services**
- Търсете за грешки свързани с midea_ac_lan
- Ако няма червени грешки - работи! ✅

## Ако все още не работи

### Опция 1: Изтеглете файла от друг компютър

1. **От компютър с работещ интернет изтеглете:**
   - https://github.com/rokam/midea-local/archive/refs/tags/v6.5.0.zip

2. **Разархивирайте и качете през Samba share:**
   - Копирайте папката в `/config/temp/`

3. **Инсталирайте през SSH:**
   ```bash
   docker exec -it homeassistant bash
   cd /config/temp/midea-local-6.5.0
   pip install .
   exit
   ```

### Опция 2: Използвайте по-стара версия

Може временно да използвате версията преди промените:

```bash
cd /config/custom_components/midea_ac_lan
git checkout b189730
```

## Тестване на мрежата

За да разберете причината, тествайте:

```bash
# SSH в Home Assistant
ha network info
ping -c 4 8.8.8.8
ping -c 4 google.com
nslookup pypi.org
curl -I https://pypi.org
```

Ако ping на 8.8.8.8 работи, но nslookup не работи = DNS проблем
Ако нищо не работи = Firewall/Router проблем

## Допълнителни проверки

```bash
# Проверете настройките на DNS
cat /etc/resolv.conf

# Проверете routing
ip route show

# Проверете дали има ProxyProxy/VPN който блокира
```

## Свържете се за помощ

Ако нищо не работи, отворете issue с тази информация:

```bash
# Съберете диагностична информация
ha network info > /config/network_info.txt
cat /etc/resolv.conf >> /config/network_info.txt
ping -c 4 8.8.8.8 >> /config/network_info.txt
nslookup pypi.org >> /config/network_info.txt
```

Качете network_info.txt като attachment към issue.
