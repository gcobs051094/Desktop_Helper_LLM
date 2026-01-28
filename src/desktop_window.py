"""
桌面視窗模組 - 實現透明背景的桌面角色顯示視窗
"""
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QSizePolicy
)

from src.live2d_widget import Live2DWidget
from src.chat_bubble import ChatBubble
from src.llm_client import LLMClient


class DesktopCharacterWindow(QMainWindow):
    """透明背景的桌面角色顯示視窗"""
    
    def __init__(self, model_path: Optional[Path] = None, parent=None):
        super().__init__(parent)
        self._drag_position = QPoint()
        self.model_path = model_path
        self.live2d_widget: Optional[Live2DWidget] = None
        self.chat_bubble: Optional[ChatBubble] = None
        self.llm_client: Optional[LLMClient] = None
        self.text_input: Optional[QLineEdit] = None
        self.voice_button: Optional[QPushButton] = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI 設置"""
        # 設置無邊框、透明背景、置頂
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 設置透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 設置視窗大小（可根據角色大小調整）
        self.setFixedSize(400, 700)  # 增加高度以容納輸入框
        
        # 創建中央 Widget 和布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 創建 Live2D Widget
        self.live2d_widget = Live2DWidget(self)
        self.live2d_widget.model_loaded.connect(self._on_model_loaded)
        layout.addWidget(self.live2d_widget, stretch=1)
        
        # 創建對話泡泡框（獨立視窗，不加入布局）
        self.chat_bubble = ChatBubble()
        
        # 創建輸入區域
        input_widget = QWidget(self)
        input_widget.setFixedHeight(50)
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 5, 10, 5)
        input_layout.setSpacing(5)
        
        # 文本輸入框
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("輸入訊息...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 2px solid rgba(200, 200, 200, 200);
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: rgba(100, 150, 255, 255);
            }
        """)
        self.text_input.returnPressed.connect(self._on_send_message)
        input_layout.addWidget(self.text_input, stretch=1)
        
        # 語音輸入按鈕
        self.voice_button = QPushButton("🎤", self)
        self.voice_button.setFixedSize(40, 40)
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 150, 255, 200);
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(100, 150, 255, 255);
            }
            QPushButton:pressed {
                background-color: rgba(80, 130, 235, 255);
            }
        """)
        self.voice_button.setToolTip("語音輸入（準備中）")
        self.voice_button.clicked.connect(self._on_voice_input)
        input_layout.addWidget(self.voice_button)
        
        layout.addWidget(input_widget)
        
        # 初始化 LLM 客戶端
        try:
            self.llm_client = LLMClient()
            print("LLM 客戶端初始化成功")
        except Exception as e:
            print(f"LLM 客戶端初始化失敗: {e}")
            print("對話功能將不可用")
        
        # 載入模型（如果提供了路徑）
        if self.model_path:
            self.load_character(self.model_path)
        
        # 設置初始位置（桌面右下角）
        self._set_initial_position()
    
    def _set_initial_position(self):
        """設置視窗初始位置"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 50
        y = screen.height() - self.height() - 100
        self.move(x, y)
    
    def load_character(self, model_path: Path):
        """
        載入角色模型
        
        Args:
            model_path: Live2D 模型文件路徑（.model3.json）
        """
        if self.live2d_widget:
            self.model_path = Path(model_path)
            self.live2d_widget.load_model(self.model_path)
    
    def _on_model_loaded(self, success: bool):
        """處理模型載入完成事件"""
        if success:
            print("角色模型已成功載入並顯示")
            # 開始播放待機動畫
            if self.live2d_widget:
                self.live2d_widget.start_idle_motion()
        else:
            print("角色模型載入失敗，顯示佔位符")
    
    def closeEvent(self, event):
        """處理視窗關閉事件"""
        if self.chat_bubble:
            self.chat_bubble.close()
        if self.live2d_widget:
            self.live2d_widget.cleanup()
        event.accept()
    
    def mousePressEvent(self, event):
        """處理滑鼠按下事件（用於拖動）"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """處理滑鼠移動事件（拖動視窗）"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        """處理雙擊事件（可選：切換顯示/隱藏）"""
        # TODO: 實現雙擊切換顯示狀態
        pass
    
    def _on_send_message(self):
        """處理發送訊息"""
        if not self.text_input:
            return
        
        message = self.text_input.text().strip()
        if not message:
            return
        
        # 清空輸入框
        self.text_input.clear()
        
        # 顯示載入中的泡泡框
        if self.chat_bubble:
            self.chat_bubble.show_message("思考中...", duration=0)
            self._update_bubble_position()
        
        # 發送訊息到 LLM
        if self.llm_client:
            try:
                response = self.llm_client.send_message(message)
                # 顯示回應
                if self.chat_bubble:
                    self.chat_bubble.show_message(response, duration=15000)
                    self._update_bubble_position()
            except Exception as e:
                error_msg = f"錯誤: {str(e)}"
                if self.chat_bubble:
                    self.chat_bubble.show_message(error_msg, duration=5000)
                    self._update_bubble_position()
        else:
            error_msg = "LLM 客戶端未初始化"
            if self.chat_bubble:
                self.chat_bubble.show_message(error_msg, duration=3000)
                self._update_bubble_position()
    
    def _on_voice_input(self):
        """處理語音輸入按鈕點擊"""
        # TODO: 後續整合 Gemini STT API
        if self.chat_bubble:
            self.chat_bubble.show_message("語音輸入功能準備中...", duration=3000)
            self._update_bubble_position()
    
    def _update_bubble_position(self):
        """更新對話泡泡框位置（顯示在角色上方）"""
        if not self.chat_bubble:
            return
        
        # 獲取視窗位置和大小
        window_rect = self.geometry()
        
        # 計算泡泡框位置（角色上方居中）
        bubble_x = window_rect.x() + (window_rect.width() - self.chat_bubble.width()) // 2
        bubble_y = window_rect.y() - self.chat_bubble.height() - 20
        
        # 確保不超出螢幕
        screen = QApplication.primaryScreen().geometry()
        if bubble_y < screen.y():
            bubble_y = window_rect.y() + window_rect.height() + 20
        
        self.chat_bubble.move(bubble_x, bubble_y)
    
    def moveEvent(self, event):
        """處理視窗移動事件，同步更新泡泡框位置"""
        super().moveEvent(event)
        if self.chat_bubble and self.chat_bubble.isVisible():
            self._update_bubble_position()
