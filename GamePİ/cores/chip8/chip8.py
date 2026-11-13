import sys
import os
import random
import pygame

class CHIP8:
    def __init__(self):
        self.memory = bytearray(4096)
        self.V = bytearray(16)
        self.I = 0
        self.pc = 0x200
        self.display = [[0 for _ in range(64)] for _ in range(32)]
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = []
        self.keypad = [0] * 16

        font_set = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i, val in enumerate(font_set):
            self.memory[i] = val

    def load_rom(self, filepath):
        if not os.path.exists(filepath):
            print(f"Hata: ROM dosyası bulunamadı > {filepath} - chip8.py:41")
            return False
            
        with open(filepath, "rb") as f:
            rom_data = f.read()
            
        for i, byte in enumerate(rom_data):
            if 0x200 + i < 4096:
                self.memory[0x200 + i] = byte
        print(f"ROM başarıyla yüklendi: {filepath} ({len(rom_data)} bayt) - chip8.py:50")
        return True

    def emulate_cycle(self):
        if self.pc >= 4096:
            return

        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2

        nnn = opcode & 0x0FFF
        n = opcode & 0x000F
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        kk = opcode & 0x00FF
        first_nibble = (opcode & 0xF000) >> 12

        if opcode == 0x00E0:
            self.display = [[0 for _ in range(64)] for _ in range(32)]
        elif opcode == 0x00EE:
            self.pc = self.stack.pop()
        elif first_nibble == 0x1:
            self.pc = nnn
        elif first_nibble == 0x2:
            self.stack.append(self.pc)
            self.pc = nnn
        elif first_nibble == 0x3:
            if self.V[x] == kk:
                self.pc += 2
        elif first_nibble == 0x4:
            if self.V[x] != kk:
                self.pc += 2
        elif first_nibble == 0x5:
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif first_nibble == 0x6:
            self.V[x] = kk
        elif first_nibble == 0x7:
            self.V[x] = (self.V[x] + kk) & 0xFF
        elif first_nibble == 0x8:
            sub_op = opcode & 0x000F
            if sub_op == 0x0:
                self.V[x] = self.V[y]
            elif sub_op == 0x1:
                self.V[x] |= self.V[y]
            elif sub_op == 0x2:
                self.V[x] &= self.V[y]
            elif sub_op == 0x3:
                self.V[x] ^= self.V[y]
            elif sub_op == 0x4:
                res = self.V[x] + self.V[y]
                self.V[0xF] = 1 if res > 255 else 0
                self.V[x] = res & 0xFF
            elif sub_op == 0x5:
                self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif sub_op == 0x6:
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
            elif sub_op == 0x7:
                self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif sub_op == 0xE:
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF
        elif first_nibble == 0x9:
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif first_nibble == 0xA:
            self.I = nnn
        elif first_nibble == 0xB:
            self.pc = nnn + self.V[0]
        elif first_nibble == 0xC:
            self.V[x] = random.randint(0, 255) & kk
        elif first_nibble == 0xD:
            x_coord = self.V[x] % 64
            y_coord = self.V[y] % 32
            height = n
            self.V[0xF] = 0
            for row in range(height):
                if y_coord + row >= 32:
                    break
                pixel_byte = self.memory[self.I + row]
                for col in range(8):
                    if x_coord + col >= 64:
                        break
                    if (pixel_byte & (0x80 >> col)) != 0:
                        if self.display[y_coord + row][x_coord + col] == 1:
                            self.V[0xF] = 1
                        self.display[y_coord + row][x_coord + col] ^= 1
        elif first_nibble == 0xE:
            if kk == 0x9E:
                if self.keypad[self.V[x]] != 0:
                    self.pc += 2
            elif kk == 0xA1:
                if self.keypad[self.V[x]] == 0:
                    self.pc += 2
        elif first_nibble == 0xF:
            if kk == 0x07:
                self.V[x] = self.delay_timer
            elif kk == 0x0A:
                pressed = False
                for i, key in enumerate(self.keypad):
                    if key != 0:
                        self.V[x] = i
                        pressed = True
                        break
                if not pressed:
                    self.pc -= 2
            elif kk == 0x15:
                self.delay_timer = self.V[x]
            elif kk == 0x18:
                self.sound_timer = self.V[x]
            elif kk == 0x1E:
                self.I = (self.I + self.V[x]) & 0xFFFF
            elif kk == 0x29:
                self.I = self.V[x] * 5
            elif kk == 0x33:
                val = self.V[x]
                self.memory[self.I] = val // 100
                self.memory[self.I + 1] = (val % 100) // 10
                self.memory[self.I + 2] = val % 10
            elif kk == 0x55:
                for i in range(x + 1):
                    self.memory[self.I + i] = self.V[i]
            elif kk == 0x65:
                for i in range(x + 1):
                    self.V[i] = self.memory[self.I + i]

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python  <rom_dosyasi_yolu> - chip8.py:181")
        return

    rom_path = sys.argv[1]
    
    chip8 = CHIP8()
    if not chip8.load_rom(rom_path):
        return

    pygame.init()
    SCALE = 12
    screen = pygame.display.set_mode((64 * SCALE, 32 * SCALE))
    pygame.display.set_caption(f"CHIP-8 Emülatör Çekirdeği - {os.path.basename(rom_path)}")
    clock = pygame.time.Clock()

    key_map = {
        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
    }

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in key_map:
                    chip8.keypad[key_map[event.key]] = 1
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                if event.key in key_map:
                    chip8.keypad[key_map[event.key]] = 0

        for _ in range(10):
            chip8.emulate_cycle()

        if chip8.delay_timer > 0:
            chip8.delay_timer -= 1
        if chip8.sound_timer > 0:
            chip8.sound_timer -= 1

        screen.fill((10, 10, 15))
        for y in range(32):
            for x in range(64):
                if chip8.display[y][x] == 1:
                    pygame.draw.rect(screen, (0, 255, 130), (x * SCALE, y * SCALE, SCALE, SCALE))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()