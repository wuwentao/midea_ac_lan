#!/bin/bash
# Скрипт за поправка на DNS проблема в Home Assistant 2026.1.1

echo "================================================"
echo "MIDEA AC LAN - ПОПРАВКА НА DNS/REQUIREMENTS ПРОБЛЕМА"
echo "================================================"
echo ""

# Функция за проверка дали сме в Docker контейнера
if [ -f /.dockerenv ]; then
    echo "✅ В Home Assistant Docker контейнер"
    IN_DOCKER=1
else
    echo "❌ НЕ сте в Home Assistant контейнер!"
    echo "Моля, първо изпълнете: docker exec -it homeassistant bash"
    exit 1
fi

echo ""
echo "Стъпка 1: Тестване на мрежовата връзка..."
echo "-------------------------------------------"

# Тест 1: Ping към Google DNS
if ping -c 2 8.8.8.8 &> /dev/null; then
    echo "✅ Мрежата работи (ping 8.8.8.8)"
    NETWORK_OK=1
else
    echo "❌ Няма мрежова връзка!"
    NETWORK_OK=0
fi

# Тест 2: DNS резолюция
if nslookup pypi.org &> /dev/null; then
    echo "✅ DNS работи (nslookup pypi.org)"
    DNS_OK=1
else
    echo "❌ DNS НЕ работи!"
    DNS_OK=0
fi

# Тест 3: Достъп до PyPI
if curl -Is https://pypi.org | head -n 1 | grep -q "200"; then
    echo "✅ PyPI е достъпен"
    PYPI_OK=1
else
    echo "❌ PyPI НЕ е достъпен!"
    PYPI_OK=0
fi

echo ""
echo "Стъпка 2: Инсталиране на midea-local..."
echo "-------------------------------------------"

# Опит 1: Директно от PyPI
if [ $PYPI_OK -eq 1 ]; then
    echo "Опит 1: Инсталация от PyPI..."
    if pip install --no-cache-dir midea-local==6.5.0; then
        echo "✅ Успешна инсталация от PyPI!"
        exit 0
    fi
fi

# Опит 2: От GitHub
echo "Опит 2: Инсталация от GitHub..."
if pip install --no-cache-dir git+https://github.com/rokam/midea-local.git@v6.5.0; then
    echo "✅ Успешна инсталация от GitHub!"
    exit 0
fi

# Опит 3: От GitHub архив
echo "Опит 3: Инсталация от GitHub архив..."
cd /tmp
if wget https://github.com/rokam/midea-local/archive/refs/tags/v6.5.0.tar.gz; then
    if pip install v6.5.0.tar.gz; then
        echo "✅ Успешна инсталация от архив!"
        rm v6.5.0.tar.gz
        exit 0
    fi
fi

echo ""
echo "================================================"
echo "❌ АВТОМАТИЧНАТА ИНСТАЛАЦИЯ НЕ УСПЯ"
echo "================================================"
echo ""
echo "РЪЧНИ СТЪПКИ:"
echo ""
echo "1. Поправете DNS настройките:"
echo "   Settings → System → Network"
echo "   Primary DNS: 8.8.8.8"
echo "   Secondary DNS: 8.8.4.4"
echo ""
echo "2. Премахнете requirements временно:"
echo "   Редактирайте: /config/custom_components/midea_ac_lan/manifest.json"
echo "   Променете: \"requirements\": [\"midea-local==6.5.0\"]"
echo "   На: \"requirements\": []"
echo ""
echo "3. Изтеглете файла от друг компютър:"
echo "   https://github.com/rokam/midea-local/archive/refs/tags/v6.5.0.zip"
echo "   Копирайте го в /config/ и инсталирайте ръчно"
echo ""
echo "За повече информация вижте: FIX_DNS_PROBLEM.md"
echo ""

exit 1
