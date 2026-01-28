"""
Live2D 渲染 Widget - 使用 OpenGL 渲染 Live2D 角色
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

try:
    import live2d.v3 as live2d
    LIVE2D_AVAILABLE = True
except ImportError:
    try:
        import live2d.v2 as live2d
        LIVE2D_AVAILABLE = True
    except ImportError:
        LIVE2D_AVAILABLE = False
        print("警告: live2d-py 未安裝，無法渲染 Live2D 角色")
        print("請執行: pip install live2d-py")


class Live2DWidget(QOpenGLWidget):
    """使用 OpenGL 渲染 Live2D 角色的 Widget"""
    
    # 信號：模型載入完成
    model_loaded = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.model_path: Optional[Path] = None
        
        # 動畫計時器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        
        # 視圖參數
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # 初始化標記
        self._initialized = False
        
    def initializeGL(self):
        """初始化 OpenGL"""
        if not LIVE2D_AVAILABLE:
            return
        
        try:
            # 初始化 Live2D
            live2d.init()
            
            # 對於 v3，需要初始化 OpenGL
            if hasattr(live2d, 'glInit'):
                live2d.glInit()
            
            self._initialized = True
            print("Live2D 初始化成功")
            
            # 如果已經有模型路徑，載入模型
            if self.model_path:
                self._load_model_internal()
        except Exception as e:
            print(f"Live2D 初始化失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def resizeGL(self, w: int, h: int):
        """處理視窗大小變化"""
        if self.model and w > 0 and h > 0:
            self.model.Resize(w, h)
    
    def paintGL(self):
        """繪製 Live2D 角色"""
        if not LIVE2D_AVAILABLE or not self.model or not self._initialized:
            return
        
        try:
            # 清除背景（透明）
            live2d.clearBuffer(0.0, 0.0, 0.0, 0.0)
            
            # 更新模型（動畫、物理等）
            self.model.Update()
            
            # 設置偏移和縮放
            if self.offset_x != 0.0 or self.offset_y != 0.0:
                self.model.SetOffset(self.offset_x, self.offset_y)
            if self.scale != 1.0:
                self.model.SetScale(self.scale)
            
            # 繪製模型
            self.model.Draw()
        except Exception as e:
            print(f"渲染錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    def load_model(self, model_path: Path):
        """
        載入 Live2D 模型
        
        Args:
            model_path: .model3.json 或 .model.json 文件路徑
        """
        if not LIVE2D_AVAILABLE:
            self.model_loaded.emit(False)
            return
        
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            print(f"錯誤: 模型文件不存在: {self.model_path}")
            self.model_loaded.emit(False)
            return
        
        # 如果已經初始化，直接載入；否則標記為待載入
        if self._initialized:
            self._load_model_internal()
        # 否則等待 initializeGL 完成後載入
    
    def _load_model_internal(self):
        """內部方法：實際載入模型"""
        if not LIVE2D_AVAILABLE or not self._initialized:
            return
        
        try:
            self.makeCurrent()
            
            # 創建模型實例
            self.model = live2d.LAppModel()
            
            # 載入模型文件
            model_path_str = str(self.model_path)
            if live2d.LIVE2D_VERSION == 3:
                # v3 版本需要指定 maskBufferCount（可選）
                self.model.LoadModelJson(model_path_str, maskBufferCount=100)
            else:
                # v2 版本
                self.model.LoadModelJson(model_path_str)
            
            # 調整視窗大小
            w, h = self.width(), self.height()
            if w > 0 and h > 0:
                self.model.Resize(w, h)
            else:
                # 如果視窗大小還未設置，使用預設大小
                self.model.Resize(400, 600)
            
            # 開始動畫計時器
            if not self.animation_timer.isActive():
                self.animation_timer.start(16)  # ~60 FPS
            
            # 嘗試播放待機動畫
            try:
                self.model.StartRandomMotion("Idle", priority=1)
            except:
                # 如果沒有 Idle 動畫，嘗試其他動畫組
                try:
                    self.model.StartRandomMotion("", priority=1)
                except:
                    pass  # 沒有動畫也沒關係
            
            print(f"成功載入 Live2D 模型: {self.model_path}")
            self.model_loaded.emit(True)
            
        except Exception as e:
            print(f"載入 Live2D 模型失敗: {e}")
            import traceback
            traceback.print_exc()
            self.model_loaded.emit(False)
    
    def start_idle_motion(self):
        """開始播放待機動畫"""
        if self.model:
            try:
                self.model.StartRandomMotion("Idle", priority=1)
            except Exception as e:
                print(f"播放待機動畫失敗: {e}")
                # 嘗試其他動畫組
                try:
                    self.model.StartRandomMotion("", priority=1)
                except:
                    pass
    
    def cleanup(self):
        """清理資源"""
        # 停止計時器
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        
        # 清理模型
        self.model = None
        
        # 清理 Live2D
        if LIVE2D_AVAILABLE and self._initialized:
            try:
                live2d.dispose()
            except Exception as e:
                print(f"清理 Live2D 失敗: {e}")
