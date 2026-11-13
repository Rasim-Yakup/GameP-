
import sys
import os
import subprocess
import pygame

pygame.init()
pygame.joystick.init()

# Ekran Boyutları ve Tam Ekran (Fullscreen) Ayarı
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("GamePi Linux/Windows Edition - Retro Konsol")

# Renk Paleti (Modern Koyu Tema)
BG_COLOR = (15, 17, 23)
PANEL_COLOR = (26, 29, 39)
ACCENT_COLOR = (0, 230, 140)
WARNING_COLOR = (255, 170, 50)
TEXT_WHITE = (245, 245, 250)
TEXT_GRAY = (145, 150, 170)

font = pygame.font.SysFont("DejaVu Sans", 26)
title_font = pygame.font.SysFont("DejaVu Sans", 38, bold=True)
small_font = pygame.font.SysFont("DejaVu Sans", 18)

# Gamepad Yönetimi (Dinamik / Sonradan Takma Desteği)
joystick = None

def check_joystick():
    global joystick
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        if joystick is None:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
    else:
        joystick = None

check_joystick()

# Klasörlerin Otomatik Oluşturulması
REQUIRED_DIRS = [
    "roms/chip8",
    "roms/gameboy",
    "roms/psp",
    "cores/chip8"
]
for d in REQUIRED_DIRS:
    os.makedirs(d, exist_ok=True)

# Sistem Tanımları ve Emülatör Yolları
systems = [
    {
        "name": "CHIP-8 (Dahili Motor)",
        "folder": "chip8",
        "ext": ".ch8",
        "type": "python",
        "path": os.path.join("cores", "chip8", "chip8.py")
    },
    {
        "name": "Game Boy (mGBA)",
        "folder": "gameboy",
        "ext": ".gb",
        "type": "exe",
        "path": os.path.expanduser("~/mgba-10.4-linux-x64/mgba-qt")
    },
    {
        "name": "PlayStation Portable (PPSSPP)",
        "folder": "psp",
        "ext": ".iso",
        "type": "exe",
        "path": os.path.expanduser("~/PPSSPP/PPSSPPlinux")
    }
]

def scan_games():
    for sys_info in systems:
        sys_info["games"] = []
        folder_path = os.path.join("roms", sys_info["folder"])
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(sys_info["ext"]):
                    sys_info["games"].append({
                        "title": os.path.splitext(filename)[0],
                        "rom": os.path.join(folder_path, filename)
                    })

scan_games()

current_sys = 0
current_game = 0
status_message = "Hazır. Bir oyun seçin."
status_color = ACCENT_COLOR

def launch_game():
    global status_message, status_color, screen
    system = systems[current_sys]
    
    if not system["games"]:
        status_message = "Hata: Bu klasörde oyun bulunamadı!"
        status_color = WARNING_COLOR
        return

    game = system["games"][current_game]
    emu_path = system["path"]

    if system["type"] != "python" and not os.path.exists(emu_path):
        status_message = f"Eksik Emülatör: '{emu_path}' bulunamadı!"
        status_color = WARNING_COLOR
        return

    status_message = f"Başlatılıyor: {game['title']}..."
    status_color = ACCENT_COLOR
    
    try:
        # Pygame ekranını simge durumuna küçült
        pygame.display.iconify()
        
        # Emülatörü tam ekran başlat
        if system["type"] == "python":
            proc = subprocess.Popen([sys.executable, emu_path, game["rom"]])
        elif "ppsspp" in emu_path.lower():
            proc = subprocess.Popen([emu_path, "--fullscreen", game["rom"]])
        elif "mgba" in emu_path.lower():
            proc = subprocess.Popen([emu_path, game["rom"]])
        else:
            proc = subprocess.Popen([emu_path, game["rom"]])
            
        # Oyun oynanırken arka planda gamepad çıkış kombinasyonunu dinleyebiliriz
        # veya kullanıcı emülatörü kapatana kadar bekleriz. 
        # mGBA/PPSSPP açıkken doğrudan süreci sonlandırmak istersek proc.terminate() kullanılabilir.
        proc.wait()
            
        # Emülatör kapandığında tam ekran arayüzü geri yükle
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.event.clear()
        status_message = "Arayüze dönüldü."
        status_color = ACCENT_COLOR
    except Exception as e:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        status_message = f"Başlatma hatası: {str(e)}"
        status_color = WARNING_COLOR

clock = pygame.time.Clock()
running = True

while running:
    check_joystick()

    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.JOYDEVICEADDED:
            check_joystick()
        elif event.type == pygame.JOYDEVICEREMOVED:
            check_joystick()

        elif event.type == pygame.KEYDOWN:
            sys_obj = systems[current_sys]
            if event.key == pygame.K_LEFT:
                current_sys = (current_sys - 1) % len(systems)
                current_game = 0
            elif event.key == pygame.K_RIGHT:
                current_sys = (current_sys + 1) % len(systems)
                current_game = 0
            elif event.key == pygame.K_UP and sys_obj["games"]:
                current_game = (current_game - 1) % len(sys_obj["games"])
            elif event.key == pygame.K_DOWN and sys_obj["games"]:
                current_game = (current_game + 1) % len(sys_obj["games"])
            elif event.key == pygame.K_RETURN:
                launch_game()
            elif event.key == pygame.K_r:
                scan_games()
                status_message = "Oyun listesi yenilendi."
                status_color = ACCENT_COLOR
            elif event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == pygame.JOYBUTTONDOWN:
            # Standart Gamepad Tuş Eşlemesi:
            # Button 0 (A Tuşu): Oyunu Başlat
            if event.button == 0:  
                launch_game()
            # Örnek: Button 6 (Select) veya Button 8/9 gibi tuşlarla hızlı çıkış/kısayol eklenebilir.

        elif event.type == pygame.JOYHATMOTION:
            hx, hy = event.value
            sys_obj = systems[current_sys]
            if hx == -1:
                current_sys = (current_sys - 1) % len(systems)
                current_game = 0
            elif hx == 1:
                current_sys = (current_sys + 1) % len(systems)
                current_game = 0
            elif hy == 1 and sys_obj["games"]:
                current_game = (current_game - 1) % len(sys_obj["games"])
            elif hy == -1 and sys_obj["games"]:
                current_game = (current_game + 1) % len(sys_obj["games"])

        elif event.type == pygame.JOYAXISMOTION:
            sys_obj = systems[current_sys]
            if event.axis == 0:
                if event.value < -0.7:
                    current_sys = (current_sys - 1) % len(systems)
                    current_game = 0
                    pygame.time.delay(200)
                elif event.value > 0.7:
                    current_sys = (current_sys + 1) % len(systems)
                    current_game = 0
                    pygame.time.delay(200)
            elif event.axis == 1 and sys_obj["games"]:
                if event.value < -0.7:
                    current_game = (current_game - 1) % len(sys_obj["games"])
                    pygame.time.delay(150)
                elif event.value > 0.7:
                    current_game = (current_game + 1) % len(sys_obj["games"])
                    pygame.time.delay(150)

    # Üst Bar (Konsol Seçici)
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, WIDTH, 95))
    active_sys = systems[current_sys]
    title_surf = title_font.render(f"◀   {active_sys['name']}   ▶", True, ACCENT_COLOR)
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 22))

    # Emülatör Kurulum Durum Göstergesi
    emu_exists = (active_sys["type"] == "python") or os.path.exists(active_sys["path"])
    emu_status_txt = "Emülatör Durumu: KURULU" if emu_exists else f"Emülatör Eksik ({active_sys['path']})"
    emu_status_col = ACCENT_COLOR if emu_exists else WARNING_COLOR
    emu_surf = small_font.render(emu_status_txt, True, emu_status_col)
    screen.blit(emu_surf, (WIDTH // 2 - emu_surf.get_width() // 2, 108))

    # Oyun Listesi
    start_y = 155
    games = active_sys["games"]
    if games:
        for i, g in enumerate(games):
            rect = pygame.Rect(100, start_y + i * 68, WIDTH - 200, 56)
            if i == current_game:
                pygame.draw.rect(screen, PANEL_COLOR, rect, border_radius=8)
                pygame.draw.rect(screen, ACCENT_COLOR, rect, 2, border_radius=8)
                col = TEXT_WHITE
            else:
                col = TEXT_GRAY
            g_surf = font.render(g["title"], True, col)
            screen.blit(g_surf, (rect.x + 20, rect.y + 10))
    else:
        empty_surf = font.render(f"'roms/{active_sys['folder']}' klasörüne {active_sys['ext']} dosyası atın.", True, TEXT_GRAY)
        screen.blit(empty_surf, (WIDTH // 2 - empty_surf.get_width() // 2, 280))

    # Alt Bilgi ve Durum Çubuğu
    pygame.draw.rect(screen, PANEL_COLOR, (0, HEIGHT - 75, WIDTH, 75))
    
    st_surf = small_font.render(status_message, True, status_color)
    screen.blit(st_surf, (30, HEIGHT - 62))

    gp_text = f"Gamepad: {joystick.get_name()[:25]}" if joystick else "Gamepad: Bağlı Değil"
    gp_surf = small_font.render(gp_text, True, TEXT_GRAY)
    screen.blit(gp_surf, (WIDTH - gp_surf.get_width() - 30, HEIGHT - 62))

    help_surf = small_font.render("[D-Pad / Analog] Gezin  |  [A Tuşu] Seç/Başlat  |  [R] Yenile", True, TEXT_GRAY)
    screen.blit(help_surf, (WIDTH // 2 - help_surf.get_width() // 2, HEIGHT - 32))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
