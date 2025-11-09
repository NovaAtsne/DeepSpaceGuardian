"""
游戏核心逻辑测试
"""
import unittest
import sys
import os
import pygame

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from game.core import Game
from utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class TestGame(unittest.TestCase):
    """游戏核心功能测试"""
    
    def setUp(self):
        """测试前初始化"""
        # 初始化pygame（仅用于测试）
        pygame.init()
        self.game = Game()
    
    def tearDown(self):
        """测试后清理"""
        pygame.quit()
    
    def test_game_initialization(self):
        """测试游戏初始化"""
        self.assertIsNotNone(self.game.screen)
        self.assertIsNotNone(self.game.clock)
        self.assertEqual(self.game.running, True)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.level, 1)
    
    def test_game_dimensions(self):
        """测试游戏窗口尺寸"""
        self.assertEqual(self.game.screen.get_width(), SCREEN_WIDTH)
        self.assertEqual(self.game.screen.get_height(), SCREEN_HEIGHT)
    
    def test_score_increment(self):
        """测试分数增加"""
        initial_score = self.game.score
        self.game.add_score(100)
        self.assertEqual(self.game.score, initial_score + 100)
    
    def test_level_progression(self):
        """测试关卡进度"""
        self.game.score = 1000  # 设置足够分数升级
        self.game.check_level_up()
        self.assertEqual(self.game.level, 2)
    
    def test_collision_detection(self):
        """测试碰撞检测"""
        # 创建测试矩形
        rect1 = pygame.Rect(100, 100, 50, 50)
        rect2 = pygame.Rect(120, 120, 50, 50)  # 重叠的矩形
        rect3 = pygame.Rect(200, 200, 50, 50)  # 不重叠的矩形
        
        self.assertTrue(self.game.check_collision(rect1, rect2))
        self.assertFalse(self.game.check_collision(rect1, rect3))
    
    def test_game_over_condition(self):
        """测试游戏结束条件"""
        self.game.game_over = True
        self.assertEqual(self.game.running, False)
    
    def test_reset_game(self):
        """测试游戏重置"""
        self.game.score = 1000
        self.game.level = 3
        self.game.game_over = True
        
        self.game.reset()
        
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.level, 1)
        self.assertEqual(self.game.game_over, False)
        self.assertEqual(self.game.running, True)

class TestGamePerformance(unittest.TestCase):
    """游戏性能测试"""
    
    def test_frame_rate(self):
        """测试帧率稳定性"""
        pygame.init()
        game = Game()
        
        # 模拟运行几帧
        for _ in range(10):
            game.clock.tick(FPS)
            # 帧率应该在合理范围内
            self.assertLessEqual(game.clock.get_fps(), FPS + 5)
        
        pygame.quit()

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)