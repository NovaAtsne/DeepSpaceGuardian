import pygame
import sys
import random
import math
import json
import os
from pygame import mixer

# 初始化pygame
pygame.init()
mixer.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("太空射击游戏")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
GRAY = (128, 128, 128)
LIGHT_BLUE = (100, 100, 255)

# 游戏时钟
clock = pygame.time.Clock()
FPS = 60

# 创建数据文件夹
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# 字体初始化 - 使用思源黑体，如果找不到则使用默认字体
def load_font(font_path, size):
    try:
        return pygame.font.Font(font_path, size)
    except:
        print(f"警告: 无法加载字体 {font_path}，使用默认字体")
        return pygame.font.Font(None, size)

# 尝试加载思源黑体，你需要将字体文件放在游戏目录下
SOURCE_HAN_SANS_PATH = "SourceHanSansHWSC-Regular.otf"  # 思源黑体 HW 字体文件
if not os.path.exists(SOURCE_HAN_SANS_PATH):
    print(f"警告: 找不到字体文件 {SOURCE_HAN_SANS_PATH}，请确保字体文件在游戏目录中")

# 创建字体对象
font_small = load_font(SOURCE_HAN_SANS_PATH, 24)
font_medium = load_font(SOURCE_HAN_SANS_PATH, 32)
font_large = load_font(SOURCE_HAN_SANS_PATH, 48)
font_title = load_font(SOURCE_HAN_SANS_PATH, 64)

class Player:
    def __init__(self):
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250
        
    def update(self):
        keys = pygame.key.get_pressed()
        # 使用WASD控制移动
        if keys[pygame.K_a] and self.rect.left > 0:  # A - 左
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:  # D - 右
            self.rect.x += self.speed
        if keys[pygame.K_w] and self.rect.top > 0:  # W - 上
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:  # S - 下
            self.rect.y += self.speed
            
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return Bullet(self.rect.centerx, self.rect.top)
        return None
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
    def reset(self):
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.health = self.max_health

class Enemy:
    def __init__(self, level=1):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed = random.randint(2, 3) + level * 0.1  # 随关卡增加速度
        self.health = 20 + level * 2  # 随关卡增加生命值
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            return True
        return False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10
        
    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            return True
        return False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.power_type = power_type  # 'health', 'speed', 'weapon'
        self.image = pygame.Surface((30, 30))
        
        if power_type == 'health':
            self.image.fill(GREEN)
        elif power_type == 'speed':
            self.image.fill(BLUE)
        else:
            self.image.fill(YELLOW)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            return True
        return False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class BossEnemy:
    def __init__(self, level=1):
        self.image = pygame.Surface((100, 100))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = -100
        self.speed = 2
        self.health = 200 + level * 20  # 随关卡增加生命值
        self.max_health = self.health
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 1000 - level * 20  # 随关卡增加射击频率
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 50:
            self.rect.x += self.speed
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.speed = -self.speed
                
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            return EnemyBullet(self.rect.centerx, self.rect.bottom)
        return None
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # 绘制血条
        health_bar_width = 80
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.rect.centerx - health_bar_width//2, self.rect.bottom + 5, health_bar_width, 5))
        pygame.draw.rect(surface, GREEN, (self.rect.centerx - health_bar_width//2, self.rect.bottom + 5, health_bar_width * health_ratio, 5))

class EnemyBullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((8, 20))
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 7
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            return True
        return False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.enabled = enabled
        
    def draw(self, surface):
        if not self.enabled:
            color = GRAY
        else:
            color = self.hover_color if self.is_hovered else self.color
            
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_color = WHITE if self.enabled else GRAY
        text_surface = font_medium.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos) and self.enabled
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos) and self.enabled
        return False

class LevelSelect:
    def __init__(self, max_unlocked_level=1):
        self.buttons = []
        self.max_unlocked_level = max_unlocked_level
        self.max_level = 32
        self.active = False
        self.create_buttons()
        
    def create_buttons(self):
        self.buttons = []
        button_width = 100
        button_height = 60
        margin = 20
        start_x = 100
        start_y = 150
        
        for i in range(self.max_level):
            row = i // 8
            col = i % 8
            x = start_x + col * (button_width + margin)
            y = start_y + row * (button_height + margin)
            
            enabled = (i + 1) <= self.max_unlocked_level
            color = LIGHT_BLUE if enabled else GRAY
            hover_color = BLUE if enabled else GRAY
            
            self.buttons.append(Button(
                x, y, button_width, button_height, 
                f"{i+1}", color, hover_color, enabled
            ))
        
        # 返回主菜单按钮
        self.buttons.append(Button(
            300, 500, 200, 50, 
            "返回主菜单", (100, 100, 100), (150, 150, 150), True
        ))
        
    def set_max_unlocked_level(self, level):
        self.max_unlocked_level = level
        self.create_buttons()
        
    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, event):
                if button.text == "返回主菜单":
                    self.active = False
                    return "menu"
                elif button.text.isdigit():
                    level = int(button.text)
                    if level <= self.max_unlocked_level:
                        self.active = False
                        return level
        return None
                    
    def draw(self, surface):
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # 绘制标题
        title_text = font_title.render("选择关卡", True, WHITE)
        surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))
        
        # 绘制提示
        hint_text = font_small.render(f"已解锁关卡: 1-{self.max_unlocked_level}", True, WHITE)
        surface.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, 120))
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)

class Menu:
    def __init__(self):
        self.buttons = [
            Button(300, 200, 200, 50, "开始游戏", (0, 100, 0), (0, 150, 0)),
            Button(300, 270, 200, 50, "游戏设置", (100, 100, 0), (150, 150, 0)),
            Button(300, 340, 200, 50, "高分记录", (100, 0, 100), (150, 0, 150)),
            Button(300, 410, 200, 50, "退出游戏", (100, 0, 0), (150, 0, 0))
        ]
        self.active = True
        
    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, event):
                if button.text == "开始游戏":
                    self.active = False
                    return "level_select"
                elif button.text == "退出游戏":
                    pygame.quit()
                    sys.exit()
        return None
                    
    def draw(self, surface):
        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # 绘制标题
        title_text = font_title.render("太空射击游戏", True, WHITE)
        surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(surface)

class LevelSystem:
    def __init__(self):
        self.current_level = 1
        self.max_level = 32
        self.enemies_spawned = 0
        self.enemies_to_spawn = 0
        self.level_complete = False
        self.boss_spawned = False
        self.boss = None
        self.last_spawn_time = 0
        self.spawn_delay = 400  # 降低生成延迟，提高刷新频率（每秒2-3个）
        
    def start_level(self, level):
        self.current_level = level
        self.enemies_spawned = 0
        self.enemies_to_spawn = level * 50  # 每关敌人数量 = 关卡数 × 50
        self.level_complete = False
        self.boss_spawned = False
        self.boss = None
        self.last_spawn_time = pygame.time.get_ticks()
        
    def update(self, current_time, enemies):
        # 生成普通敌人 - 提高刷新频率
        if (not self.level_complete and 
            self.enemies_spawned < self.enemies_to_spawn and 
            current_time - self.last_spawn_time > self.spawn_delay):
            
            enemies.append(Enemy(self.current_level))
            self.enemies_spawned += 1
            self.last_spawn_time = current_time
        
        # 检查是否应该生成Boss（每5关一个Boss）
        if (not self.boss_spawned and 
            self.enemies_spawned >= self.enemies_to_spawn and 
            self.current_level % 5 == 0):
            
            self.boss = BossEnemy(self.current_level)
            self.boss_spawned = True
            
        # 检查关卡是否完成
        if (self.enemies_spawned >= self.enemies_to_spawn and 
            len(enemies) == 0 and 
            (not self.boss_spawned or (self.boss and self.boss.health <= 0))):
            
            self.level_complete = True
            
    def is_level_complete(self):
        return self.level_complete
        
    def draw_level_info(self, surface):
        level_text = font_medium.render(f"关卡: {self.current_level}/{self.max_level}", True, WHITE)
        enemies_text = font_small.render(f"敌人: {self.enemies_spawned}/{self.enemies_to_spawn}", True, WHITE)
        
        surface.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))
        surface.blit(enemies_text, (SCREEN_WIDTH - enemies_text.get_width() - 10, 50))
        
        # 绘制Boss血条（如果存在）
        if self.boss and self.boss.health > 0:
            boss_text = font_small.render("BOSS!", True, RED)
            surface.blit(boss_text, (SCREEN_WIDTH//2 - boss_text.get_width()//2, 10))

class GameSettings:
    def __init__(self):
        self.settings_file = os.path.join(DATA_FOLDER, "game_settings.json")
        self.default_settings = {
            "sound_volume": 0.5,
            "music_volume": 0.3,
            "difficulty": "normal",
            "controls": {
                "left": pygame.K_a,      # 改为A
                "right": pygame.K_d,     # 改为D
                "up": pygame.K_w,        # 改为W
                "down": pygame.K_s,      # 改为S
                "shoot": pygame.K_SPACE
            }
        }
        self.load_settings()
        
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载设置文件时出错: {e}，使用默认设置")
                self.settings = self.default_settings.copy()
                self.save_settings()
        else:
            self.settings = self.default_settings.copy()
            self.save_settings()
            
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"保存设置文件时出错: {e}")
            
    def get_setting(self, key):
        return self.settings.get(key, self.default_settings.get(key))
        
    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

class UserData:
    def __init__(self):
        self.data_file = os.path.join(DATA_FOLDER, "user_data.json")
        self.default_data = {
            "max_unlocked_level": 1,
            "scores": {},
            "total_play_time": 0
        }
        self.load_data()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载用户数据时出错: {e}，使用默认数据")
                self.data = self.default_data.copy()
                self.save_data()
        else:
            self.data = self.default_data.copy()
            self.save_data()
            
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"保存用户数据时出错: {e}")
            
    def get_max_unlocked_level(self):
        return self.data.get("max_unlocked_level", 1)
        
    def unlock_level(self, level):
        current_max = self.get_max_unlocked_level()
        if level > current_max:
            self.data["max_unlocked_level"] = level
            self.save_data()
            
    def save_score(self, level, score):
        if str(level) not in self.data["scores"] or score > self.data["scores"][str(level)]:
            self.data["scores"][str(level)] = score
            self.save_data()

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.3
        self.sound_volume = 0.5
        self.current_music = None
        
    def load_sound(self, name, filepath):
        try:
            self.sounds[name] = pygame.mixer.Sound(filepath)
        except pygame.error as e:
            print(f"无法加载音效 {filepath}: {e}")
            
    def play_sound(self, name):
        if name in self.sounds:
            try:
                self.sounds[name].set_volume(self.sound_volume)
                self.sounds[name].play()
            except pygame.error as e:
                print(f"播放音效 {name} 时出错: {e}")
            
    def play_music(self, filepath, loop=True):
        try:
            if self.current_music != filepath:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = filepath
        except pygame.error as e:
            print(f"播放音乐 {filepath} 时出错: {e}")
            
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.running = True
        self.game_over = False
        self.menu = Menu()
        self.settings = GameSettings()
        self.user_data = UserData()
        self.sound_manager = SoundManager()
        self.level_system = LevelSystem()
        self.level_select = LevelSelect(self.user_data.get_max_unlocked_level())
        self.level_transition_timer = 0
        self.show_level_complete = False
        self.current_state = "menu"  # menu, level_select, gameplay
        
        # 加载音乐
        self.load_music()
        
    def load_music(self):
        # 尝试加载音乐文件
        darkness_music = "darkness.mp3"
        aspiration_music = "aspiration_woods.mp3"
        
        if os.path.exists(darkness_music):
            self.darkness_music = darkness_music
        else:
            print(f"警告: 找不到音乐文件 {darkness_music}")
            self.darkness_music = None
            
        if os.path.exists(aspiration_music):
            self.aspiration_music = aspiration_music
        else:
            print(f"警告: 找不到音乐文件 {aspiration_music}")
            self.aspiration_music = None
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif self.current_state == "menu":
                result = self.menu.handle_events(event)
                if result == "level_select":
                    self.current_state = "level_select"
                    self.level_select.active = True
                    if self.darkness_music:
                        self.sound_manager.play_music(self.darkness_music)
                        
            elif self.current_state == "level_select":
                result = self.level_select.handle_events(event)
                if result == "menu":
                    self.current_state = "menu"
                    if self.darkness_music:
                        self.sound_manager.play_music(self.darkness_music)
                elif isinstance(result, int):
                    self.current_state = "gameplay"
                    self.level_system.start_level(result)
                    if self.aspiration_music:
                        self.sound_manager.play_music(self.aspiration_music)
                        
            elif self.current_state == "gameplay":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        bullet = self.player.shoot()
                        if bullet:
                            self.bullets.append(bullet)
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.current_state = "menu"
                        if self.darkness_music:
                            self.sound_manager.play_music(self.darkness_music)
                    
    def update(self):
        if self.current_state != "gameplay":
            return
            
        if not self.game_over:
            current_time = pygame.time.get_ticks()
            
            # 处理关卡完成过渡
            if self.show_level_complete:
                if current_time - self.level_transition_timer > 2000:  # 2秒后进入下一关
                    self.show_level_complete = False
                    # 解锁下一关
                    next_level = self.level_system.current_level + 1
                    self.user_data.unlock_level(next_level)
                    self.level_select.set_max_unlocked_level(self.user_data.get_max_unlocked_level())
                    
                    if next_level <= self.level_system.max_level:
                        self.current_state = "level_select"
                        if self.darkness_music:
                            self.sound_manager.play_music(self.darkness_music)
                    else:
                        self.game_over = True  # 游戏通关
                return
                
            self.player.update()
            
            # 更新关卡系统
            self.level_system.update(current_time, self.enemies)
            
            # 更新Boss
            if self.level_system.boss:
                self.level_system.boss.update()
                boss_bullet = self.level_system.boss.shoot()
                if boss_bullet:
                    self.enemy_bullets.append(boss_bullet)
                
            # 更新敌人
            for enemy in self.enemies[:]:
                if enemy.update():
                    self.enemies.remove(enemy)
                    
            # 更新子弹
            for bullet in self.bullets[:]:
                if bullet.update():
                    self.bullets.remove(bullet)
                    
            # 更新敌人子弹
            for bullet in self.enemy_bullets[:]:
                if bullet.update():
                    self.enemy_bullets.remove(bullet)
                    
            # 检测子弹与敌人碰撞
            for bullet in self.bullets[:]:
                for enemy in self.enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.health -= 10
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.player.score += 10
                            
            # 检测子弹与Boss碰撞
            if self.level_system.boss:
                for bullet in self.bullets[:]:
                    if bullet.rect.colliderect(self.level_system.boss.rect):
                        self.level_system.boss.health -= 5
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        if self.level_system.boss.health <= 0:
                            self.player.score += 100  # Boss击败奖励
                            self.level_system.boss = None
                            
            # 检测玩家与敌人碰撞
            for enemy in self.enemies[:]:
                if self.player.rect.colliderect(enemy.rect):
                    self.player.health -= 10
                    self.enemies.remove(enemy)
                    if self.player.health <= 0:
                        self.game_over = True
                        self.user_data.save_score(self.level_system.current_level, self.player.score)
                        
            # 检测玩家与敌人子弹碰撞
            for bullet in self.enemy_bullets[:]:
                if self.player.rect.colliderect(bullet.rect):
                    self.player.health -= 5
                    self.enemy_bullets.remove(bullet)
                    if self.player.health <= 0:
                        self.game_over = True
                        self.user_data.save_score(self.level_system.current_level, self.player.score)
                        
            # 检测玩家与Boss碰撞
            if self.level_system.boss and self.player.rect.colliderect(self.level_system.boss.rect):
                self.player.health -= 20
                if self.player.health <= 0:
                    self.game_over = True
                    self.user_data.save_score(self.level_system.current_level, self.player.score)
            
            # 检查关卡是否完成
            if self.level_system.is_level_complete() and not self.show_level_complete:
                self.show_level_complete = True
                self.level_transition_timer = current_time
                self.user_data.save_score(self.level_system.current_level, self.player.score)
        
    def draw(self):
        screen.fill(BLACK)
        
        if self.current_state == "menu":
            self.menu.draw(screen)
        elif self.current_state == "level_select":
            self.level_select.draw(screen)
        elif self.current_state == "gameplay":
            if self.show_level_complete:
                self.draw_level_complete(screen)
            else:
                # 绘制游戏对象
                self.player.draw(screen)
                for enemy in self.enemies:
                    enemy.draw(screen)
                for bullet in self.bullets:
                    bullet.draw(screen)
                for bullet in self.enemy_bullets:
                    bullet.draw(screen)
                    
                if self.level_system.boss:
                    self.level_system.boss.draw(screen)
                    
                # 绘制UI
                self.draw_ui(screen)
                
                if self.game_over:
                    self.draw_game_over(screen)
                
        pygame.display.flip()
        
    def draw_ui(self, surface):
        # 绘制生命值
        health_text = font_medium.render(f"生命值: {self.player.health}", True, WHITE)
        score_text = font_medium.render(f"分数: {self.player.score}", True, WHITE)
        surface.blit(health_text, (10, 10))
        surface.blit(score_text, (10, 50))
        
        # 绘制生命值条
        health_bar_width = 200
        health_ratio = self.player.health / self.player.max_health
        pygame.draw.rect(surface, RED, (10, 90, health_bar_width, 20))
        pygame.draw.rect(surface, GREEN, (10, 90, health_bar_width * health_ratio, 20))
        
        # 绘制控制提示
        controls_text = font_small.render("移动: WASD  射击: 空格  返回: ESC", True, WHITE)
        surface.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 30))
        
        # 绘制关卡信息
        self.level_system.draw_level_info(surface)
        
    def draw_level_complete(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        if self.level_system.current_level < self.level_system.max_level:
            level_text = font_large.render(f"关卡 {self.level_system.current_level} 完成!", True, GREEN)
            next_level_text = font_medium.render(f"得分: {self.player.score}", True, WHITE)
            unlock_text = font_small.render(f"已解锁关卡 {self.level_system.current_level + 1}", True, YELLOW)
        else:
            level_text = font_large.render("游戏通关!", True, YELLOW)
            next_level_text = font_medium.render(f"最终得分: {self.player.score}", True, WHITE)
            unlock_text = font_small.render("恭喜你完成了所有关卡!", True, YELLOW)
            
        surface.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        surface.blit(next_level_text, (SCREEN_WIDTH//2 - next_level_text.get_width()//2, SCREEN_HEIGHT//2))
        surface.blit(unlock_text, (SCREEN_WIDTH//2 - unlock_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
        
    def draw_game_over(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        if self.level_system.current_level >= self.level_system.max_level:
            game_over_text = font_large.render("游戏通关!", True, YELLOW)
            score_text = font_medium.render(f"最终分数: {self.player.score}", True, WHITE)
        else:
            game_over_text = font_large.render("游戏结束!", True, RED)
            score_text = font_medium.render(f"最终分数: {self.player.score}", True, WHITE)
            
        restart_text = font_medium.render("按 R 键重新开始", True, WHITE)
        menu_text = font_small.render("按 ESC 返回主菜单", True, WHITE)
        
        surface.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        surface.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 10))
        surface.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
        surface.blit(menu_text, (SCREEN_WIDTH//2 - menu_text.get_width()//2, SCREEN_HEIGHT//2 + 90))
        
    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.game_over = False
        self.show_level_complete = False
        
    def run(self):
        # 开始播放主菜单音乐
        if self.darkness_music:
            self.sound_manager.play_music(self.darkness_music)
            
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()