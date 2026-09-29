"""FreeCAD 起動時自動設定スクリプト (macOS / Windows 共通)
- ナビゲーションスタイル自動適用 (Mac: Gesture / Win: TinkerCAD)
- Onshape互換「N」キー正対ショートカット

注意:
  FreeCAD は InitGui.py を exec(code, globals, locals) のように globals と locals を
  別々の辞書で実行するため、トップレベルで import / def した名前は、関数の中から
  参照できない (NameError になる)。
  そのため全処理を 1 つの関数 _onshape_workflow_main() にまとめ、import も関数内で行う。
  内部関数はクロージャ経由で名前を解決できるので安全。
"""


def _onshape_workflow_main():
    import sys

    import FreeCAD
    import FreeCADGui
    from PySide import QtCore, QtGui, QtWidgets

    SHORTCUT_NAME = "OnshapeNShortcut"

    def setup_navigation():
        """ナビゲーションスタイルをOSに合わせて設定"""
        view_param = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")
        nav_style = (
            "Gui::GestureNavigationStyle"
            if sys.platform == "darwin"
            else "Gui::TinkerCADNavigationStyle"
        )
        view_param.SetString("NavigationStyle", nav_style)
        view_param.SetBool("ZoomAtCursor", True)
        view_param.SetBool("InvertZoom", False)
        view_param.SetBool("UseAnimation", True)

    def do_normal_to():
        """Onshape風 Nキー挙動

        1. スケッチ編集中: スケッチ平面に正対
        2. 面やオブジェクト選択中: 選択要素に正対 (Std_AlignToSelection)
        3. 未選択: 正面 (Std_ViewFront)
        """
        try:
            # 数値入力フォームやテキスト入力中は誤爆を防ぐ
            focused = QtWidgets.QApplication.focusWidget()
            if isinstance(
                focused,
                (
                    QtWidgets.QLineEdit,
                    QtWidgets.QTextEdit,
                    QtWidgets.QPlainTextEdit,
                    QtWidgets.QSpinBox,
                    QtWidgets.QDoubleSpinBox,
                ),
            ):
                return

            doc = FreeCADGui.ActiveDocument
            if not doc or not doc.ActiveView:
                return

            # 1. スケッチ編集中
            edit_obj = doc.getInEdit()
            if edit_obj and edit_obj.Object.isDerivedFrom("Sketcher::SketchObject"):
                try:
                    FreeCADGui.runCommand("Sketcher_ViewSketch")
                    return
                except Exception:
                    pass

            # 2. 面やパーツを選択している場合 (FreeCAD 1.0+ 標準機能)
            if FreeCADGui.Selection.getSelectionEx():
                try:
                    FreeCADGui.runCommand("Std_AlignToSelection")
                    return
                except Exception:
                    pass

            # 3. 未選択時は全体正面
            FreeCADGui.runCommand("Std_ViewFront")
        except Exception as e:
            FreeCAD.Console.PrintError("[OnshapeWorkflow] N key error: %s\n" % e)

    def register_shortcut(retry=0):
        """メインウィンドウが完全に準備できてから安全にNキーをバインド"""
        try:
            mw = FreeCADGui.getMainWindow()
            if not mw:
                if retry < 50:  # 最大 約5秒リトライ
                    QtCore.QTimer.singleShot(100, lambda: register_shortcut(retry + 1))
                else:
                    FreeCAD.Console.PrintError(
                        "[OnshapeWorkflow] MainWindow not available.\n"
                    )
                return

            # 既存のショートカットがあれば削除 (二重登録防止)
            old_shortcut = mw.findChild(QtGui.QShortcut, SHORTCUT_NAME)
            if old_shortcut:
                old_shortcut.setEnabled(False)
                old_shortcut.deleteLater()

            shortcut = QtGui.QShortcut(QtGui.QKeySequence("N"), mw)
            shortcut.setObjectName(SHORTCUT_NAME)
            shortcut.setContext(QtCore.Qt.ApplicationShortcut)
            shortcut.activated.connect(do_normal_to)

            FreeCAD.Console.PrintMessage(
                ">> [OnshapeWorkflow] 初期化完了: ナビゲーション設定 & Nキー正対が有効化されました。\n"
            )
        except Exception as e:
            FreeCAD.Console.PrintError(
                "[OnshapeWorkflow] register_shortcut error: %s\n" % e
            )

    # 1. 設定を適用
    try:
        setup_navigation()
    except Exception as e:
        FreeCAD.Console.PrintError("[OnshapeWorkflow] setup_navigation error: %s\n" % e)

    # 2. Qtイベントループ開始後にショートカットを登録 (遅延実行)
    QtCore.QTimer.singleShot(200, register_shortcut)


try:
    _onshape_workflow_main()
except Exception as _e:
    import FreeCAD as _FreeCAD

    _FreeCAD.Console.PrintError("[OnshapeWorkflow] init error: %s\n" % _e)
