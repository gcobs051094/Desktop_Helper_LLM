"""
Desktop Helper - 主程式入口點
在 Windows 桌面上顯示動漫角色形象的 LLM 助手
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from src.desktop_window import DesktopCharacterWindow
from src.character_loader import CharacterLoader


def main():
    """主函數"""
    # 創建應用程式
    app = QApplication(sys.argv)
    
    # 設置應用程式名稱
    app.setApplicationName("Desktop Helper")
    
    # 查找角色模型文件
    project_root = Path(__file__).parent
    model_path = project_root / "mao_pro_en" / "mao_pro_en" / "runtime" / "mao_pro.model3.json"
    
    if not model_path.exists():
        print(f"錯誤：找不到角色模型文件: {model_path}")
        print("請確保角色模型文件存在於專案目錄中")
        sys.exit(1)
    
    # 載入角色配置（目前僅驗證文件存在）
    try:
        loader = CharacterLoader(model_path)
        config = loader.load_model_config()
        print(f"成功載入角色模型: {config.get('Version', 'Unknown')}")
        print(f"Moc 文件: {loader.get_moc_path()}")
    except Exception as e:
        print(f"載入角色模型時發生錯誤: {e}")
        sys.exit(1)
    
    # 創建並顯示桌面視窗（傳入模型路徑）
    window = DesktopCharacterWindow(model_path=model_path)
    window.show()
    
    print("桌面角色視窗已啟動")
    print("提示：可以拖動視窗移動位置")
    
    # 運行應用程式
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
