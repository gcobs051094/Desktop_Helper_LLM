"""
Desktop Helper - 主程式入口點
在 Windows 桌面上顯示動漫角色形象的 LLM 助手
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from src.desktop_window import DesktopCharacterWindow
from src.character_loader import CharacterLoader
from src.character_library import get_default_character, get_available_characters


def main():
    """主函數"""
    # 創建應用程式
    app = QApplication(sys.argv)
    
    # 設置應用程式名稱
    app.setApplicationName("Desktop Helper")
    
    # 從角色素材庫取得角色
    try:
        default_character = get_default_character()
        all_characters = get_available_characters()
    except Exception as e:
        print(f"錯誤：找不到任何可用的角色模型: {e}")
        sys.exit(1)
    
    # 載入角色配置（目前僅驗證文件存在）
    try:
        loader = CharacterLoader(default_character.model_path)
        config = loader.load_model_config()
        print(f"成功載入角色模型: {config.get('Version', 'Unknown')}")
        print(f"Moc 文件: {loader.get_moc_path()}")
    except Exception as e:
        print(f"載入角色模型時發生錯誤: {e}")
        sys.exit(1)
    
    # 創建並顯示桌面視窗（傳入角色清單與預設角色）
    window = DesktopCharacterWindow(
        model_path=default_character.model_path,
        characters=all_characters,
        initial_character_id=default_character.id,
    )
    window.show()
    
    print("桌面角色視窗已啟動")
    print("提示：可以拖動視窗移動位置")
    
    # 運行應用程式
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
