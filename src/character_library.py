"""
角色素材庫模組
集中管理專案內可用的 Live2D 角色與其模型路徑，方便在 UI 中切換角色。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class CharacterInfo:
    """單一角色的基礎資訊"""

    id: str        # 內部使用的識別碼（例如: "mao_pro_en"）
    name: str      # 顯示在按鈕上的名稱
    model_path: Path  # 對應的 .model3.json 路徑


def _build_characters() -> List[CharacterInfo]:
    """
    建立內建角色清單。
    若某些素材資料夾不存在，會自動略過該角色。
    """
    characters: List[CharacterInfo] = []

    # Mao (預設角色 / EN)
    mao_model = PROJECT_ROOT / "mao_pro_en" / "mao_pro_en" / "runtime" / "mao_pro.model3.json"
    if mao_model.exists():
        characters.append(
            CharacterInfo(
                id="mao_pro_en",
                name="Mao",
                model_path=mao_model,
            )
        )

    # Hiyori (繁中)
    hiyori_model = PROJECT_ROOT / "hiyori_pro_zh" / "hiyori_pro_zh" / "runtime" / "hiyori_pro_t11.model3.json"
    if hiyori_model.exists():
        characters.append(
            CharacterInfo(
                id="hiyori_pro_zh",
                name="Hiyori",
                model_path=hiyori_model,
            )
        )

    # Miku (日文)
    miku_model = PROJECT_ROOT / "miku_pro_jp" / "miku_pro_jp" / "runtime" / "miku_sample_t04.model3.json"
    if miku_model.exists():
        characters.append(
            CharacterInfo(
                id="miku_pro_jp",
                name="Miku",
                model_path=miku_model,
            )
        )

    return characters


_CHARACTERS: List[CharacterInfo] = _build_characters()


def get_available_characters() -> List[CharacterInfo]:
    """取得目前專案中可用的角色清單（已存在素材的角色）。"""
    return list(_CHARACTERS)


def get_default_character() -> CharacterInfo:
    """
    取得預設角色。
    預設規則：
    1. 若 Mao 存在，優先使用 Mao
    2. 否則回傳第一個可用角色
    3. 若完全沒有可用角色，丟出例外讓呼叫端決定如何處理
    """
    if not _CHARACTERS:
        raise RuntimeError("目前沒有可用的角色素材，請確認素材資料夾是否存在。")

    for c in _CHARACTERS:
        if c.id == "mao_pro_en":
            return c

    return _CHARACTERS[0]

