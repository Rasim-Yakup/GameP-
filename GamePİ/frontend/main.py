import sys
import os
import subprocess
import pygame

pygame.init()
pygame.joystick.init()

# Gamepad Kontrolü
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"[GAMEPAD BAĞLANDI]: {joystick.get_name()} - main.py:14")
else:
    print("[BİLGİ]: Gamepad algılanmadı, klavye kontrolleri aktif. - main.py:16")

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TÜBİTAK Modüler Retro Konsol Arayüzü")

BG_COLOR = (18, 18, 24)
PANEL_COLOR = (30, 30, 42)
ACCENT_COLOR = (0, 220, 130)
TEXT_WHITE = (240, 240, 245)
TEXT_GRAY = (140, 140, 160)

try:
    font = pygame.font.SysFont("Arial", 28)
    title_font = pygame.font.SysFont("Arial", 40, bold=True)
    small_font = pygame.font.SysFont("Arial", 20)
except:
    font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 24)

# Modüler Sistemler ve Emülatör Tanımları
systems = [
    {
        "name": "CHIP-8 (Özel Motor)",
        "folder": "chip8",
        "ext": ".ch8",
        "emulator": ["python", "cores/chip8/chip8.py"]
    },
    {
        "name": "Game Boy",
        "folder": "gameboy",
        "ext": ".gb",
        "emulator": "mgba-qt" # Linux/Pi üzerinde mGBA arayüz komutu
    },
    {
        "name": "PlayStation Portable (PSP)",
        "folder": "psp",
        "ext": ".iso",
        "emulator": "ppssppsdl" # Linux/Pi üzerinde PSP emülatör komutu
    }
]

def load_games_from_folders():
    for sys_info in systems:
        sys_info["games"] = []
        folder_path = os.path.join("roms", sys_info["folder"])
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            continue
            
        for filename in os.listdir(folder_path):
            if filename.endswith(sys_info["ext"]):
                game_title = os.path.splitext(filename)[0].capitalize()
                rom_full_path = os.path.join(folder_path, filename)
                sys_info["games"].append({
                    "title": game_title,
                    "rom": rom_full_path
                })

load_games_from_folders()

current_system_index = 0
current_game_index = 0

def launch_current_game():
    system = systems[current_system_index]
    if not system["games"]:
        print("Bu konsolda çalıştırılacak oyun bulunamadı! - main.py:85")
        return
        
    game = system["games"][current_game_index]
    print(f"\n[BAŞLATILIYOR] Sistem: {system['name']} | Oyun: {game['title']} - main.py:89")
    
    try:
        pygame.display.iconify()
        
        # Emülatör çalıştırma komutu (Liste veya tekil komut desteği)
        if isinstance(system["emulator"], list):
            cmd = system["emulator"] + [game["rom"]]
            subprocess.run(cmd)
        else:
            # Sistemde emülatör yüklü değilse hata yakalama için subprocess
            subprocess.run([system["emulator"], game["rom"]], shell=False)
            
        print("> Oyun sonlandırıldı, arayüze dönülüyor. - main.py:102")
        pygame.display.set_mode((WIDTH, HEIGHT))
    except Exception as e:
        print(f"Hata: Emülatör başlatılamadı > {e} - main.py:105")
        pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            system = systems[current_system_index]
            if event.key == pygame.K_LEFT:
                current_system_index = (current_system_index - 1) % len(systems)
                current_game_index = 0 
            elif event.key == pygame.K_RIGHT:
                current_system_index = (current_system_index + 1) % len(systems)
                current_game_index = 0
            elif event.key == pygame.K_UP:
                if system["games"]:
                    current_game_index = (current_game_index - 1) % len(system["games"])
            elif event.key == pygame.K_DOWN:
                if system["games"]:
                    current_game_index = (current_game_index + 1) % len(system["games"])
            elif event.key == pygame.K_RETURN:
                launch_current_game()
            elif event.key == pygame.K_ESCAPE:
                running = False

        elif event.type == pygame.JOYBUTTONDOWN:
            system = systems[current_system_index]
            if event.button == 0: # Gamepad 'A' veya 'X' tuşu
                launch_current_game()
                
        elif event.type == pygame.JOYHATMOTION:
            hat_x, hat_y = event.value
            system = systems[current_system_index]
            
            if hat_x == -1:
                current_system_index = (current_system_index - 1) % len(systems)
                current_game_index = 0
            elif hat_x == 1:
                current_system_index = (current_system_index + 1) % len(systems)
                current_game_index = 0
            elif hat_y == 1:
                if system["games"]:
                    current_game_index = (current_game_index - 1) % len(system["games"])
            elif hat_y == -1:
                if system["games"]:
                    current_game_index = (current_game_index + 1) % len(system["games"])

    # Görsel Arayüz Çizimleri
    header_rect = pygame.Rect(0, 0, WIDTH, 90)
    pygame.draw.rect(screen, PANEL_COLOR, header_rect)
    
    active_system = systems[current_system_index]
    sys_title = title_font.render(f"<  {active_system['name']}  >", True, ACCENT_COLOR)
    screen.blit(sys_title, (WIDTH // 2 - sys_title.get_width() // 2, 25))

    start_y = 150
    games_list = active_system["games"]
    
    if games_list:
        for i, game in enumerate(games_list):
            item_rect = pygame.Rect(80, start_y + (i * 75), WIDTH - 160, 60)
            if i == current_game_index:
                pygame.draw.rect(screen, PANEL_COLOR, item_rect, border_radius=10)
                pygame.draw.rect(screen, ACCENT_COLOR, item_rect, 2, border_radius=10)
                text_color = TEXT_WHITE
            else:
                text_color = TEXT_GRAY

            game_surface = font.render(game["title"], True, text_color)
            screen.blit(game_surface, (item_rect.x + 20, item_rect.y + 15))
    else:
        no_game_text = font.render(f"roms/{active_system['folder']} klasöründe oyun bulunamadı.", True, TEXT_GRAY)
        screen.blit(no_game_text, (WIDTH // 2 - no_game_text.get_width() // 2, 250))
        
        info_text = small_font.render("Oyun dosyasını ilgili klasörlere atıp arayüzü yeniden başlatın.", True, (100, 100, 120))
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 300))

    footer_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
    pygame.draw.rect(screen, PANEL_COLOR, footer_rect)
    
    footer_text = small_font.render("[Klavye / Kol] Konsol Değiştir | Oyun Seç | [ENTER / Kol Tuşu] Oyna", True, TEXT_GRAY)
    screen.blit(footer_text, (WIDTH // 2 - footer_text.get_width() // 2, HEIGHT - 35))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()