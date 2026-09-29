"""FreeCAD 環境設定スクリプト

- macOS: Gestureスタイル（トラックパッド向け）
- Windows: TinkerCADスタイル（マウス向け・Onshape互換）
"""

from pathlib import Path
import sys
import FreeCAD
import FreeCADGui


def setup_onshape_preferences():
    view_param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")

    # -------------------------------------------------------------
    # 1. ナビゲーションスタイルの選択
    # -------------------------------------------------------------
    # 【自動判別】MacならGesture、WindowsならTinkerCAD
    if sys.platform == "darwin":
        nav_style = "Gui::GestureNavigationStyle"  # macOS (トラックパッド推奨)
    else:
        nav_style = "Gui::TinkerCADNavigationStyle"  # Windows (マウス推奨)

    # 手動で強制固定したい場合は、上のif文を消して以下をアンコメントしてください
    # nav_style = "Gui::GestureNavigationStyle"    # Mac用 (Gesture)
    # nav_style = "Gui::TinkerCADNavigationStyle"  # Win用 (TinkerCAD)

    view_param.SetString("NavigationStyle", nav_style)

    # -------------------------------------------------------------
    # 2. ズーム・表示オプション
    # -------------------------------------------------------------
    # カーソル位置を中心にズーム
    view_param.SetBool("ZoomAtCursor", True)

    # ズーム方向の反転 (Macのナチュラルスクロール等で違和感がある場合は True)
    view_param.SetBool("InvertZoom", False)

    # アニメーション補間
    view_param.SetBool("UseAnimation", True)

    # -------------------------------------------------------------
    # 3. 現在開いている画面への即時反映
    # -------------------------------------------------------------
    try:
        if FreeCADGui.ActiveDocument and FreeCADGui.ActiveDocument.ActiveView:
            FreeCADGui.ActiveDocument.ActiveView.setNavigationStyle(nav_style)
    except Exception:
        pass

    style_name = "Gesture" if "Gesture" in nav_style else "TinkerCAD"
    FreeCAD.Console.PrintMessage(
        f">> スタイルを [{style_name}] に設定しました（OS: {sys.platform}）。\n"
    )


setup_onshape_preferences()