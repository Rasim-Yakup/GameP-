#!/bin/bash



echo "=== GamePi Evrensel Otomatik Kurulum Başlatılıyor ==="



# 1. Bozuk PPA kalıntılarını temizle ve sistemi güncelle

echo "[1/4] Paket kaynakları güncelleniyor..."

sudo rm -f /etc/apt/sources.list.d/*ppsspp*

sudo apt update



# 2. Gerekli temel araçları ve Pygame'i kur

echo "[2/4] Sistem paketleri ve Pygame kuruluyor..."

sudo apt install -y wget tar xz-utils python3-pygame libsdl2-2.0-0



# 3. mGBA (Game Boy) Kurulumu (Hem Pi hem Ubuntu deposunda mevcut)

echo "[3/4] mGBA (Game Boy) kuruluyor..."

sudo apt install -y mgba-qt

if command -v mgba-qt &> /dev/null; then

    mkdir -p ~/mgba-10.4-linux-x64

    ln -sf $(which mgba-qt) ~/mgba-10.4-linux-x64/mgba-qt

    echo "-> mGBA başarıyla bağlandı."

fi



# 4. PPSSPP (PSP) Kurulumu (Mimariye Göre Otomatik Seçim)

echo "[4/4] PPSSPP (PSP) kuruluyor..."

mkdir -p ~/PPSSPP

rm -f ~/PPSSPP/PPSSPPlinux



# Önce standart apt deposundan dene (Raspberry Pi OS'ta direkt buradan kurulur)

if sudo apt install -y ppsspp 2>/dev/null; then

    EMU_BIN=$(which ppsspp || which PPSSPPSDL)

    printf "#!/bin/bash\nexec $EMU_BIN \"\$@\"\n" > ~/PPSSPP/PPSSPPlinux

    chmod +x ~/PPSSPP/PPSSPPlinux

    echo "-> PPSSPP (APT) başarıyla kuruldu."

else

    # APT'de yoksa (Ubuntu gibi) Snap üzerinden kur ve wrapper oluştur

    echo "-> APT deposunda bulunamadı, Snap üzerinden kuruluyor..."

    sudo snap install ppsspp-emu

    printf '#!/bin/bash\nexec /snap/bin/ppsspp-emu.ppsspp-sdl "$@"\n' > ~/PPSSPP/PPSSPPlinux

    chmod +x ~/PPSSPP/PPSSPPlinux

    echo "-> PPSSPP (Snap) başarıyla kuruldu."

fi



echo "=== Kurulum Tamamlandı! 'python3 frontend/main.py' ile başlatabilirsiniz. ===" 