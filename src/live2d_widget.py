"""
Live2D 渲染 Widget - 使用 OpenGL 渲染 Live2D 角色
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
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
    # 信號：點擊檢測到部位
    part_clicked = pyqtSignal(str)  # 發送 Hit Area ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.model_path: Optional[Path] = None
        
        # 動畫計時器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        
        # 視圖參數
        # 以「基準視窗尺寸」為參考，視窗變大/變小時，角色也跟著縮放
        self._base_widget_w = 340
        self._base_widget_h = 430  # 對應新視窗高度 480 - 輸入區 50
        # 增加縮放讓角色填滿更多空間，減少上下空白
        self._base_scale = 1.0  # 從 0.6 增加到 1.3，讓角色更大更貼齊邊界
        self.scale = self._base_scale
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
            self._update_scale_by_widget()
    
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
            
            # 依照 widget 尺寸更新角色縮放
            self._update_scale_by_widget()
            
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

    def _update_scale_by_widget(self):
        """
        以基準 widget 尺寸推算 scale，讓「視窗大小」與「角色大小」同步變化。
        這避免使用 GetCanvasSizePixel（其值常接近貼圖解析度，會把視窗撐爆）。
        """
        w = max(1, self.width())
        h = max(1, self.height())
        k = min(w / self._base_widget_w, h / self._base_widget_h)
        # 留一點邊距，避免裁切
        self.scale = max(0.1, self._base_scale * k * 0.98)

    def play_motion(self, motion_name: str, group: str = "") -> bool:
        """
        播放指定動作（目前使用 model3.json 的空名稱 motion group）。

        motion_name: "mtn_02" / "mtn_03" / "mtn_04" / "special_01" ...
        """
        if not LIVE2D_AVAILABLE or not self.model:
            return False

        motion_index_map = {
            "mtn_02": 0,
            "mtn_03": 1,
            "mtn_04": 2,
            "special_01": 3,
            "special_02": 4,
            "special_03": 5,
        }
        idx = motion_index_map.get(motion_name, 0)

        # live2d-py 的 StartMotion 第三參數通常是 MotionPriority enum
        priority = getattr(live2d, "MotionPriority", None)
        force = getattr(priority, "FORCE", None) if priority else None
        normal = getattr(priority, "NORMAL", None) if priority else None

        return self._start_motion_with_index(group, idx)

    def _start_motion_with_index(self, group: str, idx: int) -> bool:
        """
        以指定的 group + index 播放動作。
        用於不同角色共用的內部邏輯，會自動處理優先權與 fallback。
        """
        if not LIVE2D_AVAILABLE or not self.model:
            return False

        priority = getattr(live2d, "MotionPriority", None)
        force = getattr(priority, "FORCE", None) if priority else None
        normal = getattr(priority, "NORMAL", None) if priority else None

        try:
            if force is not None:
                self.model.StartMotion(group, idx, force)
            elif normal is not None:
                self.model.StartMotion(group, idx, normal)
            else:
                # 後備：某些版本可能接受 int
                self.model.StartMotion(group, idx, 3)
            return True
        except Exception:
            # 後備：嘗試隨機動作（不同版本參數型態不同）
            try:
                if force is not None:
                    self.model.StartRandomMotion(group, force)
                else:
                    self.model.StartRandomMotion(group, 3)
                return True
            except Exception:
                return False

    def play_motion_group(self, group: str, index: int = 0) -> bool:
        """
        直接以 motion group + index 播放動作。
        例如：group="Tap", index=0 / group="Tap@Body", index=0。
        """
        return self._start_motion_with_index(group, index)
    
    def mousePressEvent(self, event):
        """處理滑鼠點擊事件，檢測點擊的部位"""
        if not LIVE2D_AVAILABLE or not self.model:
            super().mousePressEvent(event)
            return
        
        if event.button() == Qt.MouseButton.LeftButton:
            # 獲取點擊位置（相對於 widget）
            x = int(event.position().x())
            y = int(event.position().y())
            
            try:
                # 使用 Live2D 的 HitPart 檢測點擊的部位
                hit_parts = self.model.HitPart(x, y, False)
                
                if hit_parts and len(hit_parts) > 0:
                    # HitPart 會回傳「命中的部件 PartId 列表」（通常第一個是最上層）
                    # 但 PartCore 往往覆蓋面積最大，容易壓過其他部件，所以優先挑選非 PartCore
                    hit_part_id = hit_parts[0]
                    for pid in hit_parts:
                        if pid and pid != "PartCore":
                            hit_part_id = pid
                            break
                    print(f"點擊部位: {hit_part_id}")
                    
                    # 發送信號
                    self.part_clicked.emit(hit_part_id)
                else:
                    # 如果沒有命中任何部位，嘗試使用 Hit Areas
                    # 注意：這需要根據實際的 Live2D API 調整
                    pass
                    
            except Exception as e:
                print(f"點擊檢測失敗: {e}")
        
        super().mousePressEvent(event)
    
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
