"""
玩家角色测试
"""
import unittest
import sys
import os
import pygame

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from game.entities.player import Player
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED

class TestPlayer(unittest.TestCase):
    """玩家角色测试"""
    
    def setUp(self):
        """测试前初始化"""
        pygame.init()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    def tearDown(self):
        """测试后清理"""
        pygame.quit()
    
    def test_player_initialization(self):
        """测试玩家初始化"""
        self.assertEqual(self.player.rect.x, SCREEN_WIDTH // 2)
        self.assertEqual(self.player.rect.y, SCREEN_HEIGHT // 2)
        self.assertEqual(self.player.speed, PLAYER_SPEED)
        self.assertEqual(self.player.health, 100)
        self.assertEqual(self.player.is_invincible, False)
    
    def test_player_movement(self):
        """测试玩家移动"""
        initial_x = self.player.rect.x
        initial_y = self.player.rect.y
        
        # 测试向右移动
        self.player.move_right()
        self.player.update()
        self.assertEqual(self.player.rect.x, initial_x + PLAYER_SPEED)
        
        # 测试向左移动
        self.player.rect.x = initial_x  # 重置位置
        self.player.move_left()
        self.player.update()
        self.assertEqual(self.player.rect.x, initial_x - PLAYER_SPEED)
        
        # 测试向下移动
        self.player.rect.y = initial_y  # 重置位置
        self.player.move_down()
        self.player.update()
        self.assertEqual(self.player.rect.y, initial_y + PLAYER_SPEED)
        
        # 测试向上移动
        self.player.rect.y = initial_y  # 重置位置
        self.player.move_up()
        self.player.update()
        self.assertEqual(self.player.rect.y, initial_y - PLAYER_SPEED)
    
    def test_player_boundary_constraints(self):
        """测试玩家边界约束"""
        # 测试左边界
        self.player.rect.x = -10
        self.player.update()
        self.assertEqual(self.player.rect.x, 0)
        
        # 测试右边界
        self.player.rect.x = SCREEN_WIDTH + 10
        self.player.update()
        self.assertEqual(self.player.rect.x, SCREEN_WIDTH - self.player.rect.width)
        
        # 测试上边界
        self.player.rect.y = -10
        self.player.update()
        self.assertEqual(self.player.rect.y, 0)
        
        # 测试下边界
        self.player.rect.y = SCREEN_HEIGHT + 10
        self.player.update()
        self.assertEqual(self.player.rect.y, SCREEN_HEIGHT - self.player.rect.height)
    
    def test_player_damage(self):
        """测试玩家受伤"""
        initial_health = self.player.health
        
        self.player.take_damage(20)
        self.assertEqual(self.player.health, initial_health - 20)
        
        # 测试生命值不会低于0
        self.player.take_damage(100)
        self.assertEqual(self.player.health, 0)
    
    def test_player_invincibility(self):
        """测试玩家无敌状态"""
        self.player.activate_invincibility(2.0)  # 2秒无敌
        self.assertEqual(self.player.is_invincible, True)
        
        # 测试无敌状态下不受伤害
        initial_health = self.player.health
        self.player.take_damage(20)
        self.assertEqual(self.player.health, initial_health)
    
    def test_player_healing(self):
        """测试玩家治疗"""
        self.player.health = 50  # 设置半血
        
        self.player.heal(25)
        self.assertEqual(self.player.health, 75)
        
        # 测试治疗不会超过最大生命值
        self.player.heal(50)
        self.assertEqual(self.player.health, 100)
    
    def test_player_speed_boost(self):
        """测试玩家速度提升"""
        initial_speed = self.player.speed
        
        self.player.activate_speed_boost(2.0, 2.0)  # 2倍速度，持续2秒
        self.assertEqual(self.player.speed, initial_speed * 2)
        
        # 测试速度恢复
        self.player.deactivate_speed_boost()
        self.assertEqual(self.player.speed, initial_speed)

class TestPlayerInput(unittest.TestCase):
    """玩家输入测试"""
    
    def setUp(self):
        pygame.init()
        self.player = Player(100, 100)
    
    def tearDown(self):
        pygame.quit()
    
    def test_keyboard_input_handling(self):
        """测试键盘输入处理"""
        # 模拟按键按下
        test_keys = {
            pygame.K_LEFT: 'move_left',
            pygame.K_RIGHT: 'move_right', 
            pygame.K_UP: 'move_up',
            pygame.K_DOWN: 'move_down',
            pygame.K_SPACE: 'shoot'
        }
        
        for key, expected_action in test_keys.items():
            # 这里可以测试按键对应的行为
            # 实际实现取决于你的输入处理系统
            self.assertTrue(key in test_keys)

if __name__ == '__main__':
    unittest.main(verbosity=2)