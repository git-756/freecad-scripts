"""Onshapeスタイルの「N」キー動作マクロ

- 面を選択中: その面に正対 (Normal to face)
- スケッチ編集中: スケッチ平面に正対
- 何も選択していない: 正面 (Front view)
"""

import FreeCAD
import FreeCADGui


def normal_to():
    doc = FreeCADGui.ActiveDocument
    if not doc:
        return

    view = doc.ActiveView
    if not view:
        return

    # 1. スケッチ編集中ならスケッチ平面に正対
    edit_obj = doc.getInEdit()
    if edit_obj and edit_obj.Object.isDerivedFrom("Sketcher::SketchObject"):
        try:
            FreeCADGui.runCommand("Sketcher_ViewSketch")
            return
        except Exception:
            pass

    # 2. 面（Face）が選択されているならその面に正対
    sel_ex = FreeCADGui.Selection.getSelectionEx()
    if sel_ex and len(sel_ex) > 0:
        sub_objs = sel_ex[0].SubObjects
        if sub_objs and len(sub_objs) > 0:
            face = sub_objs[0]
            if hasattr(face, "ShapeType") and face.ShapeType == "Face":
                # 面の中心パラメータから法線ベクトルを取得
                u_mid = (face.ParameterRange[0] + face.ParameterRange[1]) / 2.0
                v_mid = (face.ParameterRange[2] + face.ParameterRange[3]) / 2.0
                normal = face.normalAt(u_mid, v_mid)

                # オブジェクトの絶対配置（回転）を加味
                obj = sel_ex[0].Object
                global_placement = (
                    obj.getGlobalPlacement()
                    if hasattr(obj, "getGlobalPlacement")
                    else obj.Placement
                )
                global_normal = global_placement.Rotation.multVec(normal)

                # カメラの視線ベクトル（法線の逆方向から見つめる）
                view.setViewDirection(
                    FreeCAD.Vector(
                        -global_normal.x, -global_normal.y, -global_normal.z
                    )
                )
                return

    # 3. それ以外（未選択など）は正面（Front）を向く
    FreeCADGui.runCommand("Std_ViewFront")


normal_to()