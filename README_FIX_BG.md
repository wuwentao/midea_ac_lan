# 🔧 БЪРЗА ПОПРАВКА - Home Assistant 2026.1.1

## 🚨 КРИТИЧНИ ПРОБЛЕМИ В 2026.1.1

### Проблем 1: Интеграцията спира да работи

**Грешка:**

```
AttributeError: MINOR_VERSION
Setup failed for custom integration 'midea_ac_lan'
```

**Причина:** Home Assistant 2026.1.1 премахна `MINOR_VERSION` от ConfigFlow API.

**Решение:**

```bash
cd /config/custom_components/midea_ac_lan
sed -i '/MINOR_VERSION = 1/d' config_flow.py
ha core restart
```

### Проблем 2: DNS грешка при инсталация на пакети

```
Unable to install package midea-local==6.5.0
Caused by: dns error: failed to lookup address information: Name does not resolve
```

## 🚀 БЪРЗО РЕШЕНИЕ (избери едно):

### ✅ РЕШЕНИЕ 1: Поправи DNS (2 минути)

**В Home Assistant UI:**

1. Settings → System → Network
2. Намери твоя network адаптер
3. IPv4 Configuration → промени DNS:
   - `8.8.8.8` (primary)
   - `8.8.4.4` (secondary)
4. Restart Home Assistant

---

### ✅ РЕШЕНИЕ 2: Премахни requirements (1 минута)

**File Editor метод:**

1. Отвори **File Editor** add-on
2. Намери: `/config/custom_components/midea_ac_lan/manifest.json`
3. Промени реда:
   ```json
   "requirements": ["midea-local==6.5.0"],
   ```
   на:
   ```json
   "requirements": [],
   ```
4. Save

**SSH метод:**

```bash
cd /config/custom_components/midea_ac_lan
cp manifest.json manifest.json.backup
# Редактирай manifest.json и премахни requirements
nano manifest.json
```

След това инсталирай пакета ръчно:

```bash
docker exec -it homeassistant bash
pip install git+https://github.com/rokam/midea-local.git@v6.5.0
exit
```

Restart Home Assistant.

---

### ✅ РЕШЕНИЕ 3: Изтегли и качи ръчно (5 минути)

**От компютър с работещ интернет:**

1. Изтегли: https://github.com/rokam/midea-local/archive/refs/tags/v6.5.0.zip
2. Разархивирай
3. Качи папката в Home Assistant през Samba/SFTP: `/config/temp/midea-local-6.5.0/`
4. SSH в Home Assistant:
   ```bash
   docker exec -it homeassistant bash
   cd /config/temp/midea-local-6.5.0
   pip install .
   exit
   ```
5. Restart Home Assistant

---

### ✅ РЕШЕНИЕ 4: Използвай готовия скрипт

```bash
# Копирай fix_requirements.sh в /config/
# След това:
docker exec -it homeassistant bash
bash /config/fix_requirements.sh
exit
```

---

## 🔍 Диагностика

Ако не работи, провери мрежата:

```bash
# В Home Assistant SSH:
ha network info
ping -c 4 8.8.8.8
nslookup pypi.org
curl -I https://pypi.org
```

**Какво означават резултатите:**

- ✅ ping работи, nslookup не работи = **DNS проблем** → РЕШЕНИЕ 1
- ❌ нищо не работи = **Firewall/Router проблем** → Провери router
- ✅ всичко работи = **Временен PyPI проблем** → РЕШЕНИЕ 2 или 3

---

## 📝 Файлове които съм създал

- `FIX_DNS_PROBLEM.md` - Подробни инструкции
- `fix_requirements.sh` - Автоматичен скрипт за поправка
- `manifest_no_requirements.json` - Backup манифест без requirements
- `ИНСТАЛАЦИЯ_BG.md` - Пълно ръководство
- `translations/bg.json` - Български превод

---

## ⚡ След като проблемът е решен

1. Restart Home Assistant
2. Отиди на Settings → Devices & Services
3. Провери дали Midea AC LAN се зарежда без грешки
4. Готово! 🎉

---

## 🆘 Все още не работи?

1. Провери logs: Settings → System → Logs
2. Търси за грешки с "midea"
3. Отвори issue с log-овете: https://github.com/wuwentao/midea_ac_lan/issues

Приложи тази информация:

```bash
ha network info > /config/debug.txt
cat /etc/resolv.conf >> /config/debug.txt
pip list | grep midea >> /config/debug.txt
```
