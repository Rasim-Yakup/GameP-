#!/bin/bash

# TÜBİTAK Modüler Retro Konsol (GamePi) - Otomatik Kurulum Betiği
# Bu betik Linux / Raspberry Pi OS tabanlı sistemlerde çalıştırılmak üzere hazırlanmıştır.

echo "=================================================="
echo "  GamePi Otomatik Kurulum ve Yapılandırma Başlıyor  "
echo "=================================================="

# 1. Adım: Sistem paket yöneticisini güncelle
echo "[1/4] Sistem paketleri güncelleniyor..."
sudo apt update && sudo apt upgrade -y

# 2. Adım: Python, Pip ve Pygame kütüphanelerini kur
echo "[2/4] Python ve Pygame bağımlılıkları yükleniyor..."
sudo apt install -y python3 python3-pip python3-pygame

# 3. Adım: Emülatörleri (mGBA ve PPSSPP) kur
echo "[3/4] Konsol emülatörleri (mGBA, PPSSPP) indiriliyor..."
sudo apt install -y mgba-qt ppsspp

# 4. Adım: ROM ve Sistem Klasör yapısını oluştur
echo "[4/4] Proje dizinleri ve ROM klasörleri hazırlanıyor..."
mkdir -p roms/chip8
mkdir -p roms/gameboy
mkdir -p roms/psp
mkdir -p cores/chip8

echo "=================================================="
echo "  KURULUM TAMAMLANDI!                             "
echo "  Konsolu çalıştırmak için: python3 frontend/main.py"
echo "=================================================="