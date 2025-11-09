import pygame
import random
import sys
import os
import json
import getpass
import smtplib
from email.mime.text import MIMEText
from pygame.locals import *

pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("障碍躲避游戏")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
GREEN = (0, 255, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

class GameState:
    MAIN_MENU = 0
    USER_CREATION = 1
    LEVEL_SELECT = 2
    SETTINGS = 3
    IN_GAME = 4
    PAUSE_MENU = 5
    CONTINUE_PROMPT = 6
    ACCOUNT_MANAGEMENT = 7

DIFFICULTIES = {
    "简单": {
        "speed": 3, 
        "frequency": 30, 
        "score_multiplier": 1,
        "obstacle_count_factor": 10,
        "boss_health": 2000
    },
    "普通": {
        "speed": 4, 
        "frequency": 25, 
        "score_multiplier": 1.2,
        "obstacle_count_factor": 15,
        "boss_health": 5000
    },
    "困难": {
        "speed": 5, 
        "frequency": 20, 
        "score_multiplier": 1.5,
        "obstacle_count_factor": 25,
        "boss_health": 10000
    },
    "你确定？": {
        "speed": 7, 
        "frequency": 15, 
        "score_multiplier": 2,
        "obstacle_count_factor": 50,
        "boss_health": 40000
    }
}

def get_user_data_path():
    username = getpass.getuser()
    path = f"C:\\Users\\{username}\\AppData\\LocalLow\\thisicenoicy\\dodge"
    if not os.path.exists(path):
        os.makedirs(path)
    return path

class Button:
    def __init__(self, x, y, width, height, text, image_path="assets/button.png"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont('simhei', 24)
        
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        except:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, LIGHT_BLUE, (0, 0, width, height), border_radius=5)
            pygame.draw.rect(self.image, BLACK, (0, 0, width, height), 2, border_radius=5)
        
        self.is_hovered = False
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        if self.is_hovered:
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            s.fill((255, 255, 255, 50))
            surface.blit(s, self.rect)
        
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class DodgeGame:
    def __init__(self):
        self.state = GameState.USER_CREATION
        self.clock = pygame.time.Clock()
        self.font = self.load_font()
        self.large_font = pygame.font.SysFont('simhei', 48)
        self.medium_font = pygame.font.SysFont('simhei', 36)
        self.small_font = pygame.font.SysFont('simhei', 24)
        
        self.score = 0
        self.level = 1
        self.max_unlocked_level = 1
        self.difficulty = "普通"
        self.fullscreen = False
        self.player_name = ""
        self.users = []
        self.saved_game = None
        
        self.player_size = 30
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - self.player_size - 10
        self.player_speed = 5
        
        self.obstacles = []
        self.bullets = []
        self.special_blocks = []
        self.obstacle_width = 70
        self.obstacle_height = 30
        self.obstacle_speed = 4
        self.obstacle_frequency = 30
        self.bullet_speed = 10
        self.bullet_cooldown = 0
        self.obstacles_generated = 0
        self.obstacles_target = 0
        
        self.game_over = False
        self.game_paused = False
        self.immunity_count = 2  # 玩家免疫碰撞次数
        self.last_collision_time = 0  # 上次碰撞时间
        
        self.load_images()
        self.load_user_data()
        self.load_music()
        
        if self.users:
            self.state = GameState.MAIN_MENU
    
    def load_images(self):
        try:
            self.bullet_img = pygame.image.load('assets/bullet.png').convert_alpha()
            self.bullet_img = pygame.transform.scale(self.bullet_img, (15, 30))
            
            self.pause_img = pygame.image.load('assets/shoping.png').convert_alpha()
            self.pause_img = pygame.transform.scale(self.pause_img, (100, 100))
            
            self.game_over_img = pygame.image.load('assets/game_over.png').convert_alpha()
            self.game_over_img = pygame.transform.scale(self.game_over_img, (400, 200))
            
            self.account_img = pygame.image.load('assets/account.png').convert_alpha()
            self.account_img = pygame.transform.scale(self.account_img, (50, 50))
        except Exception as e:
            print(f"加载图片失败: {e}")
            self.bullet_img = pygame.Surface((15, 30), pygame.SRCALPHA)
            pygame.draw.rect(self.bullet_img, BLUE, (0, 0, 15, 30))
            
            self.pause_img = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.pause_img, RED, (30, 20, 20, 60))
            pygame.draw.rect(self.pause_img, RED, (50, 20, 20, 60))
            
            self.game_over_img = pygame.Surface((400, 200), pygame.SRCALPHA)
            pygame.draw.rect(self.game_over_img, RED, (0, 0, 400, 200), border_radius=10)
            text = self.large_font.render("游戏结束", True, WHITE)
            self.game_over_img.blit(text, (200 - text.get_width()//2, 100 - text.get_height()//2))
            
            self.account_img = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.account_img, BLUE, (25, 25), 25)
    
    def load_music(self):
        try:
            pygame.mixer.music.load('assets/music/gamebgm.mp3')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            print("无法加载背景音乐")
    
    def load_level_music(self):
        try:
            pygame.mixer.music.load('assets/music/levelbgm.mp3')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            print("无法加载关卡音乐")
    
    def load_font(self):
        try:
            return pygame.font.SysFont('simhei', 36)
        except:
            try:
                return pygame.font.SysFont('microsoftyahei', 36)
            except:
                print("警告：找不到中文字体，中文可能显示为方框")
                return pygame.font.SysFont(None, 36)
    
    def load_user_data(self):
        user_file = os.path.join(get_user_data_path(), "users.json")
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users = data.get("users", [])
                self.max_unlocked_level = data.get("max_unlocked_level", 1)
    
    def save_user_data(self):
        user_file = os.path.join(get_user_data_path(), "users.json")
        data = {
            "users": self.users[:5],
            "max_unlocked_level": self.max_unlocked_level
        }
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_game_state(self):
        if self.state == GameState.IN_GAME or self.state == GameState.PAUSE_MENU:
            save_data = {
                "level": self.level,
                "score": self.score,
                "player_x": self.player_x,
                "obstacles": self.obstacles,
                "bullets": self.bullets,
                "special_blocks": self.special_blocks,
                "obstacles_generated": self.obstacles_generated,
                "obstacles_target": self.obstacles_target,
                "player_name": self.player_name,
                "difficulty": self.difficulty
            }
            self.saved_game = save_data
    
    def load_game_state(self):
        if self.saved_game and self.saved_game.get("player_name") == self.player_name:
            self.level = self.saved_game["level"]
            self.score = self.saved_game["score"]
            self.player_x = self.saved_game["player_x"]
            self.obstacles = self.saved_game["obstacles"]
            self.bullets = self.saved_game["bullets"]
            self.special_blocks = self.saved_game["special_blocks"]
            self.obstacles_generated = self.saved_game["obstacles_generated"]
            self.obstacles_target = self.saved_game["obstacles_target"]
            self.difficulty = self.saved_game.get("difficulty", "普通")
            return True
        return False
    
    def create_new_user(self, name):
        if name and name not in [u["name"] for u in self.users]:
            self.users.insert(0, {"name": name, "scores": {}})
            if len(self.users) > 5:
                self.users = self.users[:5]
            self.player_name = name
            self.save_user_data()
            return True
        return False
    
    def rename_user(self, old_name, new_name):
        if new_name and new_name not in [u["name"] for u in self.users]:
            for user in self.users:
                if user["name"] == old_name:
                    user["name"] = new_name
                    if self.player_name == old_name:
                        self.player_name = new_name
                    self.save_user_data()
                    return True
        return False
    
    def delete_user(self, name):
        self.users = [u for u in self.users if u["name"] != name]
        if self.player_name == name:
            self.player_name = ""
            if self.users:
                self.player_name = self.users[0]["name"]
            else:
                self.state = GameState.USER_CREATION
        self.save_user_data()
        return True
    
    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.game_paused = False
        self.obstacles = []
        self.bullets = []
        self.special_blocks = []
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - self.player_size - 10
        self.bullet_cooldown = 0
        self.obstacles_generated = 0
        self.immunity_count = 2  # 重置免疫次数
        self.last_collision_time = 0  # 重置碰撞时间
        
        difficulty_settings = DIFFICULTIES[self.difficulty]
        base_speed = difficulty_settings["speed"]
        base_freq = difficulty_settings["frequency"]
        
        self.obstacles_target = difficulty_settings["obstacle_count_factor"] * self.level
        
        level_multiplier = 1 + (self.level - 1) * 0.1
        self.obstacle_speed = base_speed * level_multiplier
        self.obstacle_frequency = max(5, base_freq - (self.level - 1) * 2)
        
        if self.level == 21:
            self.create_special_block()
        elif self.level == 22:
            self.obstacle_frequency = 5
    
    def create_special_block(self):
        x = random.randint(0, WIDTH - 100)
        y = -100
        color = random.choice(COLORS)
        difficulty_settings = DIFFICULTIES[self.difficulty]
        
        self.special_blocks.append({
            "x": x,
            "y": y,
            "width": 100,
            "height": 100,
            "color": color,
            "health": difficulty_settings["boss_health"],
            "max_health": difficulty_settings["boss_health"],
            "spawn_timer": 0
        })
    
    def update_special_blocks(self):
        for block in self.special_blocks[:]:
            block["y"] += self.obstacle_speed * 0.5
            
            block["spawn_timer"] += 1
            if block["spawn_timer"] >= 60:
                self.obstacles.append({
                    "x": block["x"] + random.randint(0, 50), 
                    "y": block["y"] + 100,
                    "health": 25
                })
                block["spawn_timer"] = 0
            
            for bullet in self.bullets[:]:
                if (bullet[0] > block["x"] and bullet[0] < block["x"] + block["width"] and
                    bullet[1] > block["y"] and bullet[1] < block["y"] + block["height"]):
                    block["health"] -= 5
                    self.bullets.remove(bullet)
                    if block["health"] <= 0:
                        self.special_blocks.remove(block)
                        self.score += 100 * DIFFICULTIES[self.difficulty]["score_multiplier"]
                        break
            
            if block["y"] > HEIGHT:
                self.special_blocks.remove(block)
    
    def draw_player(self):
        pygame.draw.rect(screen, BLUE, (self.player_x, self.player_y, self.player_size, self.player_size))
    
    def create_obstacle(self):
        x = random.randint(0, WIDTH - self.obstacle_width)
        y = -self.obstacle_height
        self.obstacles.append({
            "x": x,
            "y": y,
            "health": 25
        })
        self.obstacles_generated += 1
    
    def create_bullet(self):
        if self.bullet_cooldown <= 0:
            self.bullets.append([self.player_x + self.player_size//2 - 7, self.player_y])
            self.bullet_cooldown = 12  # 冷却时间改为12帧(0.2秒)
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet[1] -= self.bullet_speed
            
            for obstacle in self.obstacles[:]:
                if (bullet[0] > obstacle["x"] and bullet[0] < obstacle["x"] + self.obstacle_width and
                    bullet[1] > obstacle["y"] and bullet[1] < obstacle["y"] + self.obstacle_height):
                    obstacle["health"] -= 5
                    if obstacle["health"] <= 0:
                        self.obstacles.remove(obstacle)
                        self.score += 1 * DIFFICULTIES[self.difficulty]["score_multiplier"]
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
            
            if bullet[1] < -30:
                self.bullets.remove(bullet)
    
    def draw_obstacles(self):
        for obstacle in self.obstacles:
            health_ratio = obstacle["health"] / 25
            color = (
                max(50, int(255 * health_ratio)),
                max(50, int(255 * (1 - health_ratio))),
                50
            )
            pygame.draw.rect(screen, color, (obstacle["x"], obstacle["y"], self.obstacle_width, self.obstacle_height))
        
        for block in self.special_blocks:
            pygame.draw.rect(screen, block["color"], 
                           (block["x"], block["y"], block["width"], block["height"]))
            health_ratio = block["health"] / block["max_health"]
            bar_width = 100
            pygame.draw.rect(screen, RED, (block["x"], block["y"] - 15, bar_width, 8))
            pygame.draw.rect(screen, GREEN, (block["x"], block["y"] - 15, bar_width * health_ratio, 8))
    
    def draw_bullets(self):
        for bullet in self.bullets:
            screen.blit(self.bullet_img, (bullet[0], bullet[1]))
    
    def update_obstacles(self):
        for obstacle in self.obstacles[:]:
            obstacle["y"] += self.obstacle_speed
            if obstacle["y"] > HEIGHT:
                self.obstacles.remove(obstacle)
        
        if self.level == 22 and random.randint(1, 10) == 1:
            self.create_obstacle()
    
    def check_collision(self):
        current_time = pygame.time.get_ticks()
        # 检查碰撞冷却时间(1秒内不会重复检测碰撞)
        if current_time - self.last_collision_time < 1000:
            return False
            
        for obstacle in self.obstacles:
            if (self.player_x < obstacle["x"] + self.obstacle_width and
                self.player_x + self.player_size > obstacle["x"] and
                self.player_y < obstacle["y"] + self.obstacle_height and
                self.player_y + self.player_size > obstacle["y"]):
                self.last_collision_time = current_time
                return True
        
        for block in self.special_blocks:
            if (self.player_x < block["x"] + block["width"] and
                self.player_x + self.player_size > block["x"] and
                self.player_y < block["y"] + block["height"] and
                self.player_y + self.player_size > block["y"]):
                self.last_collision_time = current_time
                return True
        
        return False
    
    def check_level_complete(self):
        if self.level == 22:
            return False
        
        if self.level == 21:
            return len(self.special_blocks) == 0 and len(self.obstacles) == 0
        else:
            return self.obstacles_generated >= self.obstacles_target and len(self.obstacles) == 0
    
    def show_score(self):
        score_text = self.font.render(f"分数: {int(self.score)}", True, BLACK)
        screen.blit(score_text, (10, 10))
        level_text = self.font.render(f"关卡: {self.level}/22", True, BLACK)
        screen.blit(level_text, (10, 50))
        difficulty_text = self.font.render(f"难度: {self.difficulty}", True, BLACK)
        screen.blit(difficulty_text, (10, 90))
        
        # 显示剩余免疫次数
        immunity_text = self.small_font.render(f"免疫次数: {self.immunity_count}", True, BLACK)
        screen.blit(immunity_text, (10, 130))
        
        if self.level != 22 and self.level != 21:
            progress_text = self.small_font.render(
                f"障碍物: {self.obstacles_generated}/{self.obstacles_target}", 
                True, BLACK
            )
            screen.blit(progress_text, (10, 170))
    
    def show_game_over(self):
        screen.blit(self.game_over_img, (WIDTH//2 - 200, HEIGHT//2 - 150))
        
        restart_text = self.small_font.render("按R键重新开始本关", True, BLACK)
        menu_text = self.small_font.render("按M键返回主菜单", True, BLACK)
        
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 100))
    
    def show_level_complete(self):
        complete_text = self.medium_font.render("关卡完成!", True, GREEN)
        next_text = self.small_font.render("按空格键进入下一关", True, BLACK)
        menu_text = self.small_font.render("按Q键返回主菜单", True, BLACK)
        
        screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2))
        screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 40))
        
        if self.level == self.max_unlocked_level and self.level < 22:
            self.max_unlocked_level += 1
            self.save_user_data()
    
    def show_continue_prompt(self):
        prompt_text = self.medium_font.render("发现存档!", True, BLUE)
        continue_text = self.small_font.render("按空格键继续游戏", True, BLACK)
        new_text = self.small_font.render("按Q键返回主菜单", True, BLACK)
        
        screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 - 80))
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(new_text, (WIDTH//2 - new_text.get_width()//2, HEIGHT//2 + 20))
    
    def show_pause_menu(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        screen.blit(s, (0, 0))
        
        screen.blit(self.pause_img, (WIDTH//2 - 50, HEIGHT//2 - 150))
        
        resume_btn = Button(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50, "继续游戏")
        restart_btn = Button(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50, "重新开始")
        menu_btn = Button(WIDTH//2 - 100, HEIGHT//2 + 110, 200, 50, "主菜单")
        
        mouse_pos = pygame.mouse.get_pos()
        resume_btn.check_hover(mouse_pos)
        restart_btn.check_hover(mouse_pos)
        menu_btn.check_hover(mouse_pos)
        
        resume_btn.draw(screen)
        restart_btn.draw(screen)
        menu_btn.draw(screen)
        
        return resume_btn, restart_btn, menu_btn
    
    def show_main_menu(self):
        screen.fill(WHITE)
        
        title = self.large_font.render("障碍躲避游戏", True, DARK_BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        play_btn = Button(WIDTH//2 - 150, 200, 300, 60, "开始游戏")
        settings_btn = Button(WIDTH//2 - 150, 280, 300, 60, "设置")
        feedback_btn = Button(WIDTH//2 - 150, 360, 300, 60, "反馈")
        exit_btn = Button(WIDTH//2 - 150, 440, 300, 60, "退出游戏")
        
        account_btn_rect = pygame.Rect(WIDTH - 70, 20, 50, 50)
        screen.blit(self.account_img, account_btn_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        play_btn.check_hover(mouse_pos)
        settings_btn.check_hover(mouse_pos)
        feedback_btn.check_hover(mouse_pos)
        exit_btn.check_hover(mouse_pos)
        
        play_btn.draw(screen)
        settings_btn.draw(screen)
        feedback_btn.draw(screen)
        exit_btn.draw(screen)
        
        if self.player_name:
            user_text = self.small_font.render(f"当前用户: {self.player_name}", True, BLACK)
            screen.blit(user_text, (WIDTH - user_text.get_width() - 20, 80))
        
        return play_btn, settings_btn, feedback_btn, exit_btn, account_btn_rect
    
    def show_account_management(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400)
        pygame.draw.rect(screen, WHITE, dialog_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2, border_radius=10)
        
        title = self.medium_font.render("账户管理", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 180))
        
        users_text = self.small_font.render("当前用户:", True, BLACK)
        screen.blit(users_text, (WIDTH//2 - 180, HEIGHT//2 - 140))
        
        user_buttons = []
        for i, user in enumerate(self.users[:5]):
            user_rect = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 - 110 + i*50, 360, 40)
            pygame.draw.rect(screen, LIGHT_BLUE, user_rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, user_rect, 2, border_radius=5)
            
            name_text = self.small_font.render(user["name"], True, BLACK)
            screen.blit(name_text, (user_rect.x + 10, user_rect.y + 10))
            
            if user["name"] == self.player_name:
                pygame.draw.rect(screen, GREEN, user_rect, 2, border_radius=5)
            
            user_buttons.append(user_rect)
        
        rename_btn = Button(WIDTH//2 - 180, HEIGHT//2 + 60, 80, 40, "重命名")
        new_btn = Button(WIDTH//2 - 80, HEIGHT//2 + 60, 80, 40, "新建")
        delete_btn = Button(WIDTH//2 + 20, HEIGHT//2 + 60, 80, 40, "删除")
        cancel_btn = Button(WIDTH//2 - 80, HEIGHT//2 + 120, 160, 40, "取消")
        
        mouse_pos = pygame.mouse.get_pos()
        rename_btn.check_hover(mouse_pos)
        new_btn.check_hover(mouse_pos)
        delete_btn.check_hover(mouse_pos)
        cancel_btn.check_hover(mouse_pos)
        
        rename_btn.draw(screen)
        new_btn.draw(screen)
        delete_btn.draw(screen)
        cancel_btn.draw(screen)
        
        return user_buttons, rename_btn, new_btn, delete_btn, cancel_btn
    
    def show_rename_dialog(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2, border_radius=10)
        
        title = self.medium_font.render("重命名用户", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))
        
        input_rect = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 - 40, 360, 40)
        pygame.draw.rect(screen, LIGHT_BLUE, input_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_rect, 2, border_radius=5)
        
        confirm_btn = Button(WIDTH//2 - 80, HEIGHT//2 + 20, 160, 40, "确认")
        cancel_btn = Button(WIDTH//2 - 80, HEIGHT//2 + 70, 160, 40, "取消")
        
        mouse_pos = pygame.mouse.get_pos()
        confirm_btn.check_hover(mouse_pos)
        cancel_btn.check_hover(mouse_pos)
        
        confirm_btn.draw(screen)
        cancel_btn.draw(screen)
        
        return input_rect, confirm_btn, cancel_btn
    
    def show_new_user_dialog(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(screen, WHITE, dialog_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2, border_radius=10)
        
        title = self.medium_font.render("新建用户", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 80))
        
        input_rect = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 - 40, 360, 40)
        pygame.draw.rect(screen, LIGHT_BLUE, input_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_rect, 2, border_radius=5)
        
        confirm_btn = Button(WIDTH//2 - 80, HEIGHT//2 + 20, 160, 40, "创建")
        cancel_btn = Button(WIDTH//2 - 80, HEIGHT//2 + 70, 160, 40, "取消")
        
        mouse_pos = pygame.mouse.get_pos()
        confirm_btn.check_hover(mouse_pos)
        cancel_btn.check_hover(mouse_pos)
        
        confirm_btn.draw(screen)
        cancel_btn.draw(screen)
        
        return input_rect, confirm_btn, cancel_btn
    
    def show_feedback_dialog(self):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        screen.blit(s, (0, 0))
        
        dialog_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(screen, WHITE, dialog_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, dialog_rect, 2, border_radius=10)
        
        title = self.medium_font.render("发送反馈", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 130))
        
        input_rect = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 - 80, 360, 150)
        pygame.draw.rect(screen, LIGHT_BLUE, input_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_rect, 2, border_radius=5)
        
        send_btn = Button(WIDTH//2 - 90, HEIGHT//2 + 90, 180, 40, "发送")
        cancel_btn = Button(WIDTH//2 - 90, HEIGHT//2 + 140, 180, 40, "取消")
        
        mouse_pos = pygame.mouse.get_pos()
        send_btn.check_hover(mouse_pos)
        cancel_btn.check_hover(mouse_pos)
        
        send_btn.draw(screen)
        cancel_btn.draw(screen)
        
        return input_rect, send_btn, cancel_btn
    
    def send_feedback(self, message):
        try:
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['Subject'] = f"Dodge Game 反馈 - 用户: {self.player_name}"
            msg['From'] = 'game.feedback@example.com'
            msg['To'] = 'thisice123@outlook.com'
            
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login('your_email@example.com', 'your_password')
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"发送反馈失败: {e}")
            return False
    
    def show_level_select(self):
        screen.fill(WHITE)
        
        title = self.medium_font.render("选择关卡", True, DARK_BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        level_buttons = []
        for i in range(22):
            row = i // 5
            col = i % 5
            x = 150 + col * 100
            y = 120 + row * 100
            
            if i + 1 <= self.max_unlocked_level:
                btn = Button(x, y, 80, 80, str(i+1))
            else:
                btn = Button(x, y, 80, 80, "?")
            
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)
            level_buttons.append(btn)
        
        back_btn = Button(50, HEIGHT - 80, 100, 50, "返回")
        back_btn.check_hover(pygame.mouse.get_pos())
        back_btn.draw(screen)
        
        return level_buttons, back_btn
    
    def show_settings(self):
        screen.fill(WHITE)
        
        title = self.medium_font.render("设置", True, DARK_BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        difficulty_text = self.small_font.render("游戏难度:", True, BLACK)
        screen.blit(difficulty_text, (WIDTH//2 - 200, 120))
        
        difficulty_buttons = []
        for i, diff in enumerate(DIFFICULTIES.keys()):
            btn = Button(WIDTH//2 - 150 + i*120, 160, 110, 50, diff)
            if self.difficulty == diff:
                btn.color = GREEN
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)
            difficulty_buttons.append(btn)
        
        fullscreen_text = self.small_font.render("全屏模式:", True, BLACK)
        screen.blit(fullscreen_text, (WIDTH//2 - 200, 240))
        
        fullscreen_btn = Button(WIDTH//2, 240, 100, 40, "开启" if self.fullscreen else "关闭", 
                              GREEN if self.fullscreen else RED)
        fullscreen_btn.check_hover(pygame.mouse.get_pos())
        fullscreen_btn.draw(screen)
        
        back_btn = Button(WIDTH//2 - 100, HEIGHT - 80, 200, 50, "返回主菜单")
        back_btn.check_hover(pygame.mouse.get_pos())
        back_btn.draw(screen)
        
        return difficulty_buttons, fullscreen_btn, back_btn
    
    def show_user_creation(self):
        screen.fill(WHITE)
        
        title = self.large_font.render("创建用户", True, DARK_BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        input_rect = pygame.Rect(WIDTH//2 - 150, 200, 300, 50)
        pygame.draw.rect(screen, LIGHT_BLUE, input_rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_rect, 2, border_radius=5)
        
        input_text = self.medium_font.render(self.player_name, True, BLACK)
        screen.blit(input_text, (input_rect.x + 10, input_rect.y + 10))
        
        create_btn = Button(WIDTH//2 - 100, 280, 200, 50, "创建用户")
        create_btn.check_hover(pygame.mouse.get_pos())
        create_btn.draw(screen)
        
        if self.users:
            users_text = self.small_font.render("已有用户:", True, BLACK)
            screen.blit(users_text, (WIDTH//2 - users_text.get_width()//2, 350))
            
            for i, user in enumerate(self.users[:5]):
                user_btn = Button(WIDTH//2 - 100, 390 + i*60, 200, 50, user["name"])
                user_btn.check_hover(pygame.mouse.get_pos())
                user_btn.draw(screen)
        
        return input_rect, create_btn
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    
    def run(self):
        input_active = False
        current_buttons = []
        feedback_text = ""
        show_feedback = False
        level_complete = False
        show_account_management = False
        show_rename_dialog = False
        show_new_user_dialog = False
        rename_user = ""
        new_name = ""
        temp_name = ""
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if show_feedback and input_active:
                        if event.key == pygame.K_RETURN:
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            feedback_text = feedback_text[:-1]
                        else:
                            feedback_text += event.unicode
                    
                    elif show_rename_dialog and input_active:
                        if event.key == pygame.K_RETURN:
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            new_name = new_name[:-1]
                        else:
                            new_name += event.unicode
                    
                    elif show_new_user_dialog and input_active:
                        if event.key == pygame.K_RETURN:
                            input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            temp_name = temp_name[:-1]
                        else:
                            temp_name += event.unicode
                    
                    elif self.state == GameState.USER_CREATION:
                        if input_active:
                            if event.key == pygame.K_RETURN:
                                input_active = False
                            elif event.key == pygame.K_BACKSPACE:
                                self.player_name = self.player_name[:-1]
                            else:
                                self.player_name += event.unicode
                    
                    elif self.state == GameState.IN_GAME:
                        if event.key == pygame.K_ESCAPE:
                            self.game_paused = not self.game_paused
                            if self.game_paused:
                                self.state = GameState.PAUSE_MENU
                            else:
                                self.state = GameState.IN_GAME
                        elif event.key == pygame.K_r and self.game_over:
                            self.reset_game()
                        elif event.key == pygame.K_m and self.game_over:
                            self.state = GameState.MAIN_MENU
                            self.load_music()
                        elif event.key == pygame.K_SPACE:  # 空格键发射子弹
                            self.create_bullet()
                        elif event.key == pygame.K_SPACE and level_complete:
                            if self.level < 22:
                                self.level += 1
                                self.reset_game()
                                level_complete = False
                    
                    elif self.state == GameState.PAUSE_MENU:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.IN_GAME
                            self.game_paused = False
                    
                    elif self.state == GameState.CONTINUE_PROMPT:
                        if event.key == pygame.K_SPACE:
                            if self.load_game_state():
                                self.state = GameState.IN_GAME
                                self.load_level_music()
                        elif event.key == pygame.K_q:
                            self.state = GameState.MAIN_MENU
                            self.load_music()
                    
                    elif level_complete:
                        if event.key == pygame.K_SPACE and self.level < 22:
                            self.level += 1
                            self.reset_game()
                            level_complete = False
                        elif event.key == pygame.K_q:
                            self.state = GameState.MAIN_MENU
                            self.load_music()
                            level_complete = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if show_account_management:
                        user_buttons, rename_btn, new_btn, delete_btn, cancel_btn = current_buttons
                        
                        for i, rect in enumerate(user_buttons):
                            if rect.collidepoint(mouse_pos) and i < len(self.users):
                                self.player_name = self.users[i]["name"]
                                show_account_management = False
                                break
                        
                        if rename_btn.rect.collidepoint(mouse_pos):
                            if self.player_name:
                                rename_user = self.player_name
                                show_rename_dialog = True
                                show_account_management = False
                                new_name = ""
                        elif new_btn.rect.collidepoint(mouse_pos):
                            if len(self.users) < 5:
                                show_new_user_dialog = True
                                show_account_management = False
                                temp_name = ""
                        elif delete_btn.rect.collidepoint(mouse_pos):
                            if self.player_name:
                                self.delete_user(self.player_name)
                        elif cancel_btn.rect.collidepoint(mouse_pos):
                            show_account_management = False
                    
                    elif show_rename_dialog:
                        input_rect, confirm_btn, cancel_btn = current_buttons
                        if input_rect.collidepoint(mouse_pos):
                            input_active = True
                        elif confirm_btn.rect.collidepoint(mouse_pos):
                            if new_name and self.rename_user(rename_user, new_name):
                                show_rename_dialog = False
                                input_active = False
                        elif cancel_btn.rect.collidepoint(mouse_pos):
                            show_rename_dialog = False
                            input_active = False
                    
                    elif show_new_user_dialog:
                        input_rect, confirm_btn, cancel_btn = current_buttons
                        if input_rect.collidepoint(mouse_pos):
                            input_active = True
                        elif confirm_btn.rect.collidepoint(mouse_pos):
                            if temp_name and self.create_new_user(temp_name):
                                show_new_user_dialog = False
                                input_active = False
                        elif cancel_btn.rect.collidepoint(mouse_pos):
                            show_new_user_dialog = False
                            input_active = False
                    
                    elif show_feedback:
                        input_rect, send_btn, cancel_btn = current_buttons
                        if input_rect.collidepoint(mouse_pos):
                            input_active = True
                        elif send_btn.rect.collidepoint(mouse_pos):
                            if self.send_feedback(feedback_text):
                                print("反馈发送成功!")
                            show_feedback = False
                            input_active = False
                        elif cancel_btn.rect.collidepoint(mouse_pos):
                            show_feedback = False
                            input_active = False
                    
                    elif self.state == GameState.USER_CREATION:
                        input_rect, create_btn = current_buttons
                        if input_rect.collidepoint(mouse_pos):
                            input_active = True
                        elif create_btn.rect.collidepoint(mouse_pos):
                            if self.create_new_user(self.player_name):
                                self.state = GameState.MAIN_MENU
                        
                        for i, user in enumerate(self.users[:5]):
                            user_btn_rect = pygame.Rect(WIDTH//2 - 100, 390 + i*60, 200, 50)
                            if user_btn_rect.collidepoint(mouse_pos):
                                self.player_name = user["name"]
                                self.state = GameState.MAIN_MENU
                    
                    elif self.state == GameState.MAIN_MENU:
                        play_btn, settings_btn, feedback_btn, exit_btn, account_btn = current_buttons
                        if play_btn.rect.collidepoint(mouse_pos):
                            if self.saved_game and self.saved_game.get("player_name") == self.player_name:
                                self.state = GameState.CONTINUE_PROMPT
                            else:
                                self.state = GameState.LEVEL_SELECT
                        elif settings_btn.rect.collidepoint(mouse_pos):
                            self.state = GameState.SETTINGS
                        elif feedback_btn.rect.collidepoint(mouse_pos):
                            show_feedback = True
                            feedback_text = ""
                            input_active = True
                        elif exit_btn.rect.collidepoint(mouse_pos):
                            pygame.quit()
                            sys.exit()
                        elif account_btn.collidepoint(mouse_pos):
                            show_account_management = True
                    
                    elif self.state == GameState.LEVEL_SELECT:
                        level_buttons, back_btn = current_buttons
                        if back_btn.rect.collidepoint(mouse_pos):
                            self.state = GameState.MAIN_MENU
                        else:
                            for i, btn in enumerate(level_buttons):
                                if btn.rect.collidepoint(mouse_pos) and i + 1 <= self.max_unlocked_level:
                                    self.level = i + 1
                                    self.reset_game()
                                    self.state = GameState.IN_GAME
                                    self.load_level_music()
                                    break
                    
                    elif self.state == GameState.SETTINGS:
                        difficulty_buttons, fullscreen_btn, back_btn = current_buttons
                        if back_btn.rect.collidepoint(mouse_pos):
                            self.state = GameState.MAIN_MENU
                        elif fullscreen_btn.rect.collidepoint(mouse_pos):
                            self.toggle_fullscreen()
                        else:
                            for i, btn in enumerate(difficulty_buttons):
                                if btn.rect.collidepoint(mouse_pos):
                                    self.difficulty = list(DIFFICULTIES.keys())[i]
                                    break
                    
                    elif self.state == GameState.PAUSE_MENU:
                        resume_btn, restart_btn, menu_btn = current_buttons
                        if resume_btn.rect.collidepoint(mouse_pos):
                            self.state = GameState.IN_GAME
                            self.game_paused = False
                        elif restart_btn.rect.collidepoint(mouse_pos):
                            self.reset_game()
                            self.state = GameState.IN_GAME
                        elif menu_btn.rect.collidepoint(mouse_pos):
                            self.save_game_state()
                            self.state = GameState.MAIN_MENU
                            self.load_music()
            
            if self.state == GameState.IN_GAME and not self.game_paused and not self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a] and self.player_x > 0:
                    self.player_x -= self.player_speed
                if keys[pygame.K_d] and self.player_x < WIDTH - self.player_size:
                    self.player_x += self.player_speed
                # 空格键连续发射
                if keys[pygame.K_SPACE]:
                    self.create_bullet()
                
                if self.bullet_cooldown > 0:
                    self.bullet_cooldown -= 1
                
                if (self.level != 22 and 
                    self.obstacles_generated < self.obstacles_target and 
                    random.randint(1, self.obstacle_frequency) == 1):
                    self.create_obstacle()
                
                self.update_obstacles()
                self.update_bullets()
                
                if self.level == 21:
                    self.update_special_blocks()
                    if len(self.special_blocks) == 0 and not level_complete:
                        self.create_special_block()
                
                if self.check_collision():
                    if self.immunity_count > 0:
                        self.immunity_count -= 1
                    else:
                        self.game_over = True
                
                if self.check_level_complete() and not level_complete:
                    level_complete = True
            
            if self.state == GameState.IN_GAME:
                screen.fill(WHITE)
                self.draw_player()
                self.draw_obstacles()
                self.draw_bullets()
                self.show_score()
                
                if self.game_over:
                    self.show_game_over()
                elif level_complete:
                    self.show_level_complete()
                elif self.game_paused:
                    screen.blit(self.pause_img, (WIDTH//2 - 50, HEIGHT//2 - 50))
            
            elif self.state == GameState.MAIN_MENU:
                current_buttons = self.show_main_menu()
            
            elif self.state == GameState.LEVEL_SELECT:
                current_buttons = self.show_level_select()
            
            elif self.state == GameState.SETTINGS:
                current_buttons = self.show_settings()
            
            elif self.state == GameState.USER_CREATION:
                current_buttons = self.show_user_creation()
            
            elif self.state == GameState.PAUSE_MENU:
                current_buttons = self.show_pause_menu()
            
            elif self.state == GameState.CONTINUE_PROMPT:
                screen.fill(WHITE)
                self.show_continue_prompt()
            
            if show_account_management:
                current_buttons = self.show_account_management()
            
            if show_rename_dialog:
                current_buttons = self.show_rename_dialog()
                
                name_surf = self.small_font.render(new_name, True, BLACK)
                screen.blit(name_surf, (WIDTH//2 - 170, HEIGHT//2 - 30))
            
            if show_new_user_dialog:
                current_buttons = self.show_new_user_dialog()
                
                name_surf = self.small_font.render(temp_name, True, BLACK)
                screen.blit(name_surf, (WIDTH//2 - 170, HEIGHT//2 - 30))
            
            if show_feedback:
                input_rect, send_btn, cancel_btn = self.show_feedback_dialog()
                current_buttons = (input_rect, send_btn, cancel_btn)
                
                feedback_surf = self.small_font.render(feedback_text, True, BLACK)
                screen.blit(feedback_surf, (input_rect.x + 10, input_rect.y + 10))
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = DodgeGame()
    game.run()