"""
桌面視窗模組 - 實現透明背景的桌面角色顯示視窗
"""
import sys
from pathlib import Path
from typing import Optional, List

from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPainter, QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QSizePolicy
)

from src.live2d_widget import Live2DWidget
from src.chat_bubble import ChatBubble
from src.llm_client import LLMClient
from src.character_interaction import CharacterInteraction
from src.character_library import CharacterInfo


class LLMStreamWorker(QThread):
    """
    在背景執行 LLM 串流請求的工作執行緒。
    透過 signal 將片段回傳給主執行緒更新 UI。
    """
    chunk_received = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, llm_client: LLMClient, message: str):
        super().__init__()
        self.llm_client = llm_client
        self.message = message
        self._stop_requested = False

    def stop(self):
        """要求停止串流（盡快結束迭代）"""
        self._stop_requested = True

    def run(self):
        try:
            for delta in self.llm_client.stream_message(self.message):
                if self._stop_requested:
                    break
                if delta:
                    self.chunk_received.emit(delta)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class DesktopCharacterWindow(QMainWindow):
    """透明背景的桌面角色顯示視窗"""
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        parent=None,
        characters: Optional[List[CharacterInfo]] = None,
        initial_character_id: Optional[str] = None,
    ):
        super().__init__(parent)
        self._drag_position = QPoint()
        self.model_path = model_path
        self.characters: List[CharacterInfo] = characters or []
        self._current_character_index: int = 0
        self.live2d_widget: Optional[Live2DWidget] = None
        self.chat_bubble: Optional[ChatBubble] = None
        self.llm_client: Optional[LLMClient] = None
        self.text_input: Optional[QLineEdit] = None
        self.voice_button: Optional[QPushButton] = None
        self.switch_character_button: Optional[QPushButton] = None
        self.send_button: Optional[QPushButton] = None
        self.character_interaction: Optional[CharacterInteraction] = None
        self._interaction_locked = False
        self._interaction_lock_timer = QTimer(self)
        self._interaction_lock_timer.setSingleShot(True)
        self._interaction_lock_timer.timeout.connect(self._unlock_interaction)

        # LLM 串流相關狀態
        self._llm_worker: Optional[LLMStreamWorker] = None
        self._current_stream_text: str = ""
        self._is_streaming: bool = False

        # 根據 initial_character_id 設定目前角色
        if self.characters and initial_character_id:
            for idx, c in enumerate(self.characters):
                if c.id == initial_character_id:
                    self._current_character_index = idx
                    self.model_path = c.model_path
                    break
            else:
                # 找不到指定 ID 時，沿用傳入的 model_path 或第一個角色
                if not self.model_path:
                    self._current_character_index = 0
                    self.model_path = self.characters[0].model_path
        elif self.characters and not self.model_path:
            # 若未指定 model_path，預設使用角色清單第一個
            self._current_character_index = 0
            self.model_path = self.characters[0].model_path

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
        
        # 視窗大小：根據角色比例調整，減少上下空白
        # 寬度保持 340，高度縮小以減少空白（角色約佔中間，上下各留一點空間給泡泡框和輸入框）
        self.setFixedSize(340, 480)  # 從 620 縮小到 480，減少空白
        
        # 創建中央 Widget 和布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 創建 Live2D Widget
        self.live2d_widget = Live2DWidget(self)
        self.live2d_widget.model_loaded.connect(self._on_model_loaded)
        self.live2d_widget.part_clicked.connect(self._on_part_clicked)
        layout.addWidget(self.live2d_widget, stretch=1)
        
        # 創建對話泡泡框（獨立置頂小視窗；不在透明視窗內）
        # 注意：目前泡泡框不是主透明視窗的一部分，而是額外的 top-level widget
        self.chat_bubble = ChatBubble()
        
        # 創建輸入區域
        input_widget = QWidget(self)
        self._input_height = 50
        input_widget.setFixedHeight(self._input_height)
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 5, 10, 5)
        input_layout.setSpacing(5)

        # 發送 / 停止按鈕（Enter / 黑色方形）
        self.send_button = QPushButton("⏎", self)
        self.send_button.setFixedSize(40, 40)
        self._send_style_normal = """
            QPushButton {
                background-color: rgba(120, 200, 120, 220);
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(135, 215, 135, 255);
            }
            QPushButton:pressed {
                background-color: rgba(100, 180, 100, 255);
            }
        """
        self._send_style_stop = """
            QPushButton {
                background-color: rgba(0, 0, 0, 220);
                border: none;
                border-radius: 20px;
                font-size: 18px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(20, 20, 20, 255);
            }
            QPushButton:pressed {
                background-color: rgba(40, 40, 40, 255);
            }
        """
        self.send_button.setStyleSheet(self._send_style_normal)
        self.send_button.setToolTip("發送訊息")
        self.send_button.clicked.connect(self._on_send_message)
        input_layout.addWidget(self.send_button)

        # 角色切換按鈕（若有多個角色才顯示）
        if self.characters and len(self.characters) > 1:
            self.switch_character_button = QPushButton(self)
            self.switch_character_button.setFixedSize(60, 40)
            self.switch_character_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 200, 120, 220);
                    border: none;
                    border-radius: 20px;
                    font-size: 11px;
                    padding: 0 6px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 210, 140, 255);
                }
                QPushButton:pressed {
                    background-color: rgba(235, 180, 110, 255);
                }
            """)
            self.switch_character_button.clicked.connect(self._on_switch_character)
            # 設定初始按鈕文字
            current = self._get_current_character()
            if current:
                self.switch_character_button.setText(current.name)
                self.switch_character_button.setToolTip("切換角色")
            input_layout.addWidget(self.switch_character_button)
        
        # 文本輸入框
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("輸入訊息...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(240, 240, 240, 200);
                border: 2px solid rgba(200, 200, 200, 200);
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 12px;
                color: rgb(0, 0, 0);
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
        
        # 初始化角色互動管理器與載入模型
        if self.model_path:
            self._init_character_state(self.model_path)
        
        # 設置初始位置（桌面右下角）
        self._set_initial_position()

    def _lock_interaction(self, ms: int = 5000):
        """鎖定角色互動一段時間，避免回覆被連續點擊刷掉"""
        self._interaction_locked = True
        self._interaction_lock_timer.start(ms)

    def _unlock_interaction(self):
        self._interaction_locked = False
    
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

    def _get_current_character(self) -> Optional[CharacterInfo]:
        """取得目前選擇的角色資訊"""
        if not self.characters:
            return None
        if 0 <= self._current_character_index < len(self.characters):
            return self.characters[self._current_character_index]
        return self.characters[0]

    def _init_character_state(self, model_path: Path):
        """
        依據指定的模型路徑初始化互動管理器與 Live2D 模型。
        用於初次載入與角色切換後。
        """
        self.character_interaction = CharacterInteraction(model_path)
        self.load_character(model_path)

    def _on_switch_character(self):
        """切換到下一個角色"""
        if not self.characters:
            return

        # 換下一個角色
        self._current_character_index = (self._current_character_index + 1) % len(self.characters)
        current = self._get_current_character()
        if not current:
            return

        self.model_path = current.model_path
        # 更新互動管理與模型
        self._init_character_state(self.model_path)

        # 更新按鈕文字
        if self.switch_character_button:
            self.switch_character_button.setText(current.name)
    
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
        """處理發送 / 停止訊息"""
        # 若正在串流中，按鈕行為改為「停止」
        if self._is_streaming:
            self._stop_streaming()
            return

        if not self.text_input or not self.llm_client:
            return

        message = self.text_input.text().strip()
        if not message:
            return

        # 清空輸入框
        self.text_input.clear()

        # 開始串流顯示，並在期間鎖定角色點擊
        self._start_streaming(message)
    
    def _on_voice_input(self):
        """處理語音輸入按鈕點擊"""
        # TODO: 後續整合 Gemini STT API
        if self.chat_bubble:
            self.chat_bubble.show_message("語音輸入功能準備中...", duration=3000)
            self._update_bubble_position()

    def _start_streaming(self, message: str):
        """啟動 LLM 串流回應"""
        if not self.llm_client:
            return

        # UI 初始化：顯示思考中文字，並放置泡泡框位置
        if self.chat_bubble:
            self.chat_bubble.show_message("思考中...", duration=0)
            self._update_bubble_position()

        # 狀態切換為串流中，鎖定角色互動
        self._is_streaming = True
        self._interaction_locked = True

        # 變更按鈕為停止圖示（黑色方形）
        if self.send_button:
            self.send_button.setText("■")
            self.send_button.setToolTip("停止生成")
            self.send_button.setStyleSheet(self._send_style_stop)

        # 啟動背景工作執行緒
        self._current_stream_text = ""
        self._llm_worker = LLMStreamWorker(self.llm_client, message)
        self._llm_worker.chunk_received.connect(self._on_stream_chunk)
        self._llm_worker.error.connect(self._on_stream_error)
        self._llm_worker.finished.connect(self._on_stream_finished)
        self._llm_worker.start()

    def _stop_streaming(self):
        """使用者主動停止串流"""
        if self._llm_worker and self._is_streaming:
            self._llm_worker.stop()
        # 真正的結束與 UI 還原在 _on_stream_finished 中處理

    def _end_streaming_state(self):
        """結束串流狀態，還原 UI 與互動"""
        self._is_streaming = False
        self._interaction_locked = False
        self._llm_worker = None

        if self.send_button:
            self.send_button.setText("⏎")
            self.send_button.setToolTip("發送訊息")
            self.send_button.setStyleSheet(self._send_style_normal)

    def _on_stream_chunk(self, delta: str):
        """接收 LLM 串流片段，累積並更新泡泡框"""
        self._current_stream_text += delta
        if self.chat_bubble:
            # 串流期間僅更新文字內容，不重置滾動與淡入動畫
            self.chat_bubble.set_text_live(self._current_stream_text)
            self._update_bubble_position()

    def _on_stream_error(self, error_msg: str):
        """處理串流中的錯誤"""
        if self.chat_bubble:
            self.chat_bubble.show_message(error_msg, duration=5000)
            self._update_bubble_position()
        self._end_streaming_state()

    def _on_stream_finished(self):
        """串流自然結束或被停止後呼叫"""
        # 若有最終內容，只更新文字內容並設置自動隱藏，不重新觸發淡入動畫（避免閃爍）
        if self._current_stream_text and self.chat_bubble:
            # 使用 set_text_live 更新內容，不重置滾動位置
            self.chat_bubble.set_text_live(self._current_stream_text)
            # 設置自動隱藏計時器（如果尚未設置）
            if self.chat_bubble.auto_hide_timer.remainingTime() <= 0:
                self.chat_bubble.auto_hide_timer.start(15000)
            self._update_bubble_position()

        self._end_streaming_state()
    
    def _update_bubble_position(self):
        """更新對話泡泡框位置（顯示在角色上方）"""
        if not self.chat_bubble:
            return

        # 以 Live2D 渲染區（接近角色頭部）作為錨點，而不是用整個主視窗 top
        if self.live2d_widget:
            top_left = self.live2d_widget.mapToGlobal(QPoint(0, 0))
            bubble_x = top_left.x() + (self.live2d_widget.width() - self.chat_bubble.width()) // 2
            bubble_y = top_left.y() - self.chat_bubble.height() - 8
        else:
            window_rect = self.geometry()
            bubble_x = window_rect.x() + (window_rect.width() - self.chat_bubble.width()) // 2
            bubble_y = window_rect.y() - self.chat_bubble.height() - 8
        
        # 確保不超出螢幕
        screen = QApplication.primaryScreen().geometry()
        if bubble_y < screen.y():
            # 如果上方放不下，就放在角色下方（但仍在輸入框上方）
            if self.live2d_widget:
                bottom_left = self.live2d_widget.mapToGlobal(QPoint(0, self.live2d_widget.height()))
                bubble_y = bottom_left.y() + 8
            else:
                window_rect = self.geometry()
                bubble_y = window_rect.y() + window_rect.height() + 8
        
        self.chat_bubble.move(bubble_x, bubble_y)
    
    def _on_part_clicked(self, hit_area_id: str):
        """處理角色部位點擊事件"""
        if not self.character_interaction or not self.live2d_widget:
            return

        # 回覆後 5 秒內或 LLM 串流期間禁止再次觸發，避免刷掉泡泡框內容
        if self._interaction_locked or self._is_streaming:
            return
        
        # 由 HitPart 回傳的 PartId 推斷互動區域，取得動作與回應
        inferred_area_id, motion_name, response = self.character_interaction.get_interaction_for_part(hit_area_id)

        current = self._get_current_character()
        played = False

        # 依不同角色，選擇最適合該模型的 motion group
        if current:
            char_id = current.id

            # Mao: 使用原本 "" group + 固定索引映射
            if char_id == "mao_pro_en":
                played = self.live2d_widget.play_motion(motion_name, group="")

            # Hiyori: 使用 Tap / Tap@Body / Flick 等命名 group
            elif char_id == "hiyori_pro_zh":
                group = "Tap"
                index = 0
                if inferred_area_id in ("HitAreaBody", "HitAreaBelly", "HitAreaChest"):
                    # 以身體相關的 Tap@Body 為主
                    group = "Tap@Body"
                    index = 0
                elif inferred_area_id in ("HitAreaHand", "HitAreaFoot"):
                    group = "Flick"
                    index = 0
                played = self.live2d_widget.play_motion_group(group, index)

            # Miku: 使用 Tap / Flick 系列
            elif char_id == "miku_pro_jp":
                group = "Tap"
                index = 0
                if inferred_area_id in ("HitAreaBody", "HitAreaBelly", "HitAreaChest"):
                    # 第二個 Tap 動作略帶不同表現
                    group = "Tap"
                    index = 1
                elif inferred_area_id in ("HitAreaHand", "HitAreaFoot"):
                    group = "Flick"
                    index = 0
                played = self.live2d_widget.play_motion_group(group, index)

        # 若沒有對應角色或上述播放失敗，退回原本行為以避免完全無反應
        if not played:
            played = self.live2d_widget.play_motion(motion_name, group="")

        if not played:
            print("[INFO]  can't start motion.")
        
        # 顯示回應
        if self.chat_bubble:
            self.chat_bubble.show_message(response, duration=5000)
            self._update_bubble_position()
            self._lock_interaction(5000)
    
    def moveEvent(self, event):
        """處理視窗移動事件，同步更新泡泡框位置"""
        super().moveEvent(event)
        if self.chat_bubble and self.chat_bubble.isVisible():
            self._update_bubble_position()
