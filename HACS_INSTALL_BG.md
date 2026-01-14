# 🚀 HACS Инсталация - Midea AC LAN ReMinchev Fix

## ✅ ВАЖНО: Midea-local се инсталира АВТОМАТИЧНО

Интеграцията е конфигурирана да инсталира автоматично всички необходими пакети (`midea-local>=6.5.0`).
**НЕ е нужна ръчна инсталация на пакети** освен ако нямате DNS/мрежови проблеми.

---

## Проблем: "Could not download, see log for details"

Ако HACS не може да изтегли автоматично, използвай **ръчна инсталация**.

---

## ✅ МЕТОД 1: Ръчна инсталация (РАБОТИ 100%)

### Стъпка 1: Изтегли файловете

**Опция А: През браузър**

1. Отвори: https://github.com/reminchev/midea_ac_lan/archive/refs/heads/master.zip
2. Изтегли zip файла
3. Разархивирай

**Опция Б: През git**

```bash
git clone https://github.com/reminchev/midea_ac_lan.git
```

### Стъпка 2: Копирай в Home Assistant

1. **Намери папката** `custom_components/midea_ac_lan` в изтегления архив
2. **Копирай цялата папка** в твоя Home Assistant:
   - Samba: `\\homeassistant\config\custom_components\midea_ac_lan\`
   - SSH: `/config/custom_components/midea_ac_lan/`

### Стъпка 3: Инсталирай midea-local (САМО при DNS проблеми)

**⚠️ ВАЖНО: Този стъпка е нужна САМО ако имате DNS/мрежов проблем!**

Нормално Home Assistant автоматично инсталира пакета. Ако видите грешка:

```bash
# SSH в Home Assistant
docker exec -it homeassistant bash

# Инсталирай пакета
pip install git+https://github.com/rokam/midea-local.git@v6.5.0

# Или ако имаш интернет към PyPI:
pip install midea-local==6.5.0

# Провери дали е инсталиран
pip list | grep midea

exit
```

### Стъпка 4: Рестартирай

```
Settings → System → Restart
```

---

## ✅ МЕТОД 2: През HACS (ако работи)

### Стъпка 1: Премахни старата интеграция

1. В HACS намери "Midea AC LAN"
2. Три точки → Remove

### Стъпка 2: Добави custom repository

1. HACS → Три точки (горе-дясно) → Custom repositories
2. Добави:
   ```
   Repository: https://github.com/reminchev/midea_ac_lan
   Category: Integration
   ```

### Стъпка 3: Инсталирай

1. Търси "Midea AC LAN (ReMinchev Fix)"
2. Download → Избери commit **34855f9** или по-нов
3. Restart Home Assistant

**⚠️ Ако получаваш "Could not download"** → Използвай **МЕТОД 1**

---

## 🔧 МЕТОД 3: През SSH (директно)

```bash
# SSH в Home Assistant
cd /config/custom_components

# Изтрий старата версия (ако има)
rm -rf midea_ac_lan

# Клонирай repo
git clone https://github.com/reminchev/midea_ac_lan.git temp_midea
mv temp_midea/custom_components/midea_ac_lan .
rm -rf temp_midea

# Рестартирай (midea-local ще се инсталира автоматично)
ha core restart
```

**📝 Забележка:** Midea-local пакетът ще се инсталира автоматично от Home Assistant при първо зареждане.  
**Ръчна инсталация е нужна САМО при DNS проблеми:**

```bash
# Само при проблеми:
docker exec -it homeassistant bash
pip install git+https://github.com/rokam/midea-local.git@v6.5.0
exit
```

---

## 🎯 Проверка дали работи

След рестартиране:

1. **Отвори Settings → System → Logs**
2. **Търси за "midea"**
3. **Не трябва да има:**
   - ❌ `No module named 'midealocal'`
   - ❌ `Requirements for midea_ac_lan not found`
   - ❌ `MAJOR_VERSION` грешки

4. **Отвори Settings → Devices & Services**
5. **Midea AC LAN** трябва да се показва без грешки ✅

---

## 🐛 Ако все още не работи

### Проверка 1: Дали файловете са правилно копирани

```bash
ls -la /config/custom_components/midea_ac_lan/
# Трябва да видиш: __init__.py, manifest.json, climate.py, и т.н.
```

### Проверка 2: Дали midea-local е инсталиран

```bash
docker exec -it homeassistant python -c "import midealocal; print(midealocal.__version__)"
# Трябва да изпише: 6.5.0
```

### Проверка 3: Дали manifest.json е правилен

```bash
cat /config/custom_components/midea_ac_lan/manifest.json
# Трябва да видиш: "version": "v0.6.11"
```

---

## 📞 Помощ

Ако нищо не работи, отвори issue с тази информация:

```bash
# Събери информация
cd /config/custom_components/midea_ac_lan
cat manifest.json > /config/debug_midea.txt
ls -la >> /config/debug_midea.txt
docker exec -it homeassistant pip list | grep midea >> /config/debug_midea.txt
```

Качи `debug_midea.txt` тук: https://github.com/reminchev/midea_ac_lan/issues
