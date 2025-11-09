#!/usr/bin/env python3
"""
Windows 平台游戏构建脚本
使用 PyInstaller 打包为可执行文件
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

class WindowsGameBuilder:
    """Windows游戏构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src"
        self.assets_dir = self.project_root / "assets"
        self.dist_dir = self.project_root / "dist" / "windows"
        self.build_dir = self.project_root / "build"
        
        # 游戏信息
        self.game_name = "DodgeGame"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "A fun 2D dodging game built with Python and Pygame"
    
    def check_dependencies(self):
        """检查依赖是否安装"""
        try:
            import PyInstaller
            import pygame
            print("✅ 所有依赖已安装")
            return True
        except ImportError as e:
            print(f"❌ 缺少依赖: {e}")
            print("请运行: pip install pyinstaller pygame")
            return False
    
    def clean_previous_builds(self):
        """清理之前的构建文件"""
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
            print("✅ 清理之前的构建文件")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print("✅ 清理构建缓存")
    
    def collect_game_assets(self):
        """收集游戏资源文件"""
        assets_target = self.dist_dir / "assets"
        
        if assets_target.exists():
            shutil.rmtree(assets_target)
        
        # 复制资源文件
        if self.assets_dir.exists():
            shutil.copytree(self.assets_dir, assets_target)
            print("✅ 复制游戏资源文件")
        
        # 确保必要的目录存在
        required_dirs = ['images', 'sounds', 'fonts']
        for dir_name in required_dirs:
            dir_path = assets_target / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def create_pyinstaller_spec(self):
        """创建PyInstaller配置文件"""
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.src_dir / "main.py"}'],
    pathex=[str(self.project_root)],
    binaries=[],
    datas=[
        ('{self.assets_dir / "images"}', 'assets/images'),
        ('{self.assets_dir / "sounds"}', 'assets/sounds'), 
        ('{self.assets_dir / "fonts"}', 'assets/fonts'),
    ],
    hiddenimports=['pygame'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.game_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为True可显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(self.assets_dir / "images" / "icon.ico"),
)
'''
        
        spec_file = self.project_root / f"{self.game_name}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print("✅ 创建PyInstaller配置文件")
        return spec_file
    
    def build_executable(self):
        """构建可执行文件"""
        print("🚀 开始构建游戏...")
        
        # 创建spec文件
        spec_file = self.create_pyinstaller_spec()
        
        # 运行PyInstaller
        try:
            result = subprocess.run([
                'pyinstaller',
                '--clean',
                '--noconfirm',
                str(spec_file)
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ 游戏构建成功!")
                
                # 移动构建结果到目标目录
                temp_exe = self.project_root / "dist" / f"{self.game_name}.exe"
                if temp_exe.exists():
                    self.dist_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(temp_exe), str(self.dist_dir / f"{self.game_name}.exe"))
                    print(f"✅ 可执行文件位置: {self.dist_dir / f'{self.game_name}.exe'}")
            else:
                print(f"❌ 构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 构建过程中出错: {e}")
            return False
        
        return True
    
    def create_installer(self):
        """创建安装程序（可选）"""
        print("📦 创建安装程序...")
        
        # 这里可以集成 Inno Setup 或 NSIS
        # 暂时创建一个简单的ZIP包
        
        import zipfile
        
        zip_path = self.project_root / "website" / "downloads" / "windows" / f"{self.game_name}_v{self.version}.zip"
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加可执行文件
            exe_file = self.dist_dir / f"{self.game_name}.exe"
            if exe_file.exists():
                zipf.write(exe_file, exe_file.name)
            
            # 添加资源文件
            assets_dir = self.dist_dir / "assets"
            if assets_dir.exists():
                for root, dirs, files in os.walk(assets_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.dist_dir)
                        zipf.write(file_path, arcname)
        
        print(f"✅ 创建安装包: {zip_path}")
        return zip_path
    
    def run_tests(self):
        """运行测试确保构建质量"""
        print("🧪 运行测试...")
        
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 
                'tests/', 
                '-v',
                '--tb=short'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ 所有测试通过!")
                return True
            else:
                print(f"❌ 测试失败: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"❌ 测试执行出错: {e}")
            return False
    
    def build(self):
        """执行完整构建流程"""
        print(f"🎮 开始构建 {self.game_name} v{self.version} for Windows")
        print(f"📁 项目根目录: {self.project_root}")
        
        # 检查系统
        if platform.system() != 'Windows':
            print("⚠️  警告: 建议在Windows系统上运行此构建脚本")
        
        # 执行构建步骤
        steps = [
            ("检查依赖", self.check_dependencies),
            ("清理旧构建", self.clean_previous_builds),
            ("运行测试", self.run_tests),
            ("构建可执行文件", self.build_executable),
            ("收集资源文件", self.collect_game_assets),
            ("创建安装包", self.create_installer),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*50}")
            print(f"步骤: {step_name}")
            print(f"{'='*50}")
            
            if not step_func():
                print(f"❌ 步骤 '{step_name}' 失败，构建中止")
                return False
        
        print(f"\n🎉 构建完成! ")
        print(f"📦 安装包位置: website/downloads/windows/")
        print(f"⚡ 可执行文件: dist/windows/{self.game_name}.exe")
        
        return True

if __name__ == "__main__":
    builder = WindowsGameBuilder()
    success = builder.build()
    
    sys.exit(0 if success else 1)