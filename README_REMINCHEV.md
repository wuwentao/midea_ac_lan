# Midea AC LAN - ReMinchev Fix за Home Assistant 2026.1.1

## � ВАЖНО - BREAKING CHANGE В 2026.1.1

**Home Assistant 2026.1.1 премахна `MINOR_VERSION` от ConfigFlow API!**

Ако интеграцията ви спря да работи след обновяване:

```bash
cd /config/custom_components/midea_ac_lan
sed -i '/MINOR_VERSION = 1/d' config_flow.py
ha core restart
```

Или изтеглете **версия v0.6.17** която вече е поправена!

---

## 🔥 Какво е това?

Това е **поправена версия** на Midea AC LAN интеграцията, която работи с **Home Assistant OS 2026.1.1**.

Оригиналният проект: https://github.com/wuwentao/midea_ac_lan

## ⚡ Какво е поправено в v0.6.17?

✅ **Премахната `MINOR_VERSION` константа** - Отстранен breaking change в HA 2026.1.1  
✅ **Премахнати deprecated `MAJOR_VERSION`** - Отстранени остарели API  
✅ **Модернизиран код** - Премахнати backwards compatibility проверки  
✅ **Опростени imports** - Директно използване на нови API-та  
✅ **Български превод** - Добавен `translations/bg.json`  
✅ **Hyper-V поддръжка** - Специални инструкции за Hyper-V виртуализация

## 📦 Инсталация

### Метод 1: Чрез HACS (препоръчвам)

1. Отвори **HACS** в Home Assistant
2. Кликни на **трите точки** (⋮) горе-дясно
3. Избери **"Custom repositories"**
4. Добави:
   - **Repository:** `https://github.com/reminchev/midea_ac_lan`
   - **Category:** `Integration`
5. Кликни **"Add"**
6. Затвори и търси за **"Midea AC LAN (ReMinchev Fix)"**
7. Кликни **"Download"**
8. **Restart Home Assistant**

### Метод 2: Ръчна инсталация

```bash
cd /config/custom_components
rm -rf midea_ac_lan
git clone https://github.com/reminchev/midea_ac_lan.git
mv midea_ac_lan/custom_components/midea_ac_lan .
rm -rf midea_ac_lan
```

### Метод 3: Директно изтегляне

1. Изтегли: https://github.com/reminchev/midea_ac_lan/archive/refs/heads/master.zip
2. Разархивирай
3. Копирай `custom_components/midea_ac_lan` в `/config/custom_components/`
4. Restart Home Assistant

## ⚠️ DNS Проблем?

Ако получаваш грешка:

```
dns error: failed to lookup address information
```

**Бърза поправка:**

1. Settings → System → Network
2. DNS Primary: `8.8.8.8`
3. DNS Secondary: `8.8.4.4`
4. Restart

**Пълни инструкции:** Виж [FIX_DNS_PROBLEM.md](FIX_DNS_PROBLEM.md)

## 🔧 Инсталация на midea-local пакет

След инсталация на интеграцията, инсталирай пакета:

```bash
docker exec -it homeassistant bash
pip install midea-local==6.5.0
exit
```

Ако PyPI не работи:

```bash
docker exec -it homeassistant bash
pip install git+https://github.com/rokam/midea-local.git@v6.5.0
exit
```

## 📋 Изисквания

- Home Assistant OS 2026.1.1 или по-нова
- Python 3.11+
- midea-local 6.5.0+

## 🌍 Поддържани езици

- 🇬🇧 English
- 🇧🇬 Български (ново!)
- 🇩🇪 Deutsch
- 🇫🇷 Français
- 🇭🇺 Magyar
- 🇷🇺 Русский
- 🇸🇰 Slovenčina
- 🇨🇳 简体中文

## 📚 Документация

- [README_FIX_BG.md](README_FIX_BG.md) - Бърза поправка на DNS проблем
- [FIX_DNS_PROBLEM.md](FIX_DNS_PROBLEM.md) - Подробни инструкции
- [ИНСТАЛАЦИЯ_BG.md](ИНСТАЛАЦИЯ_BG.md) - Пълно ръководство на български

## 🐛 Проблеми?

Отвори issue: https://github.com/reminchev/midea_ac_lan/issues

## 📝 Промени спрямо оригинала

### Версия 0.6.11 (ReMinchev Fix)

**Поправки за HA 2026.1.1:**

- Премахнати `MAJOR_VERSION`, `MINOR_VERSION` от всички файлове
- Премахнати версионни проверки (`if (MAJOR_VERSION, MINOR_VERSION) >= ...`)
- Премахнато `_enable_turn_on_off_backwards_compatibility`
- Директно използване на `ConfigFlowResult` от `config_entries`
- Директно използване на `DeviceInfo` от `helpers.device_registry`
- Опростени async API calls

**Нови функции:**

- Български превод (bg.json)
- DNS troubleshooting инструкции
- Автоматичен fix скрипт

## ⭐ Кредити

Оригинален проект: [wuwentao/midea_ac_lan](https://github.com/wuwentao/midea_ac_lan)  
Поправки за HA 2026.1.1: @reminchev  
midea-local библиотека: @rokam

## 📄 Лиценз

Същият като оригиналния проект
