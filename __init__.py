import bpy
from bpy.types import Menu, Panel, UIList, Operator, PropertyGroup
from bpy.props import (StringProperty, IntProperty, 
                       CollectionProperty, BoolProperty, EnumProperty)

from . utils import *

bl_info = {
    "name": "custom add driver",
    "author": "pluglug",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "Location": "",
    "description": "custom add driver",
    "warning": "it'll explode",
    "wiki_url": "",
    "category": "Animation",
}


class CUSTOM_OT_add_driver(Operator):
    bl_idname = "custom.add_driver"
    bl_label = "add driver"
    bl_description = "add driver"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.context.property is not None

    def execute(self, context):
        add_driver_from_clipboard()
        return {'FINISHED'}


# IDタイプとそれに関連するbpy.dataの属性をマッピングする辞書を生成
def generate_id_type_dict():
    id_type_dict = {}
    ID = bpy.types.ID

    for attr in dir(bpy.data):
        if attr.startswith("_"):
            continue

        prop = getattr(bpy.data, attr)
        if isinstance(prop, bpy.types.bpy_prop_collection):
            for item in prop:
                if isinstance(item, ID):
                    id_type_dict[attr] = item.rna_type.identifier  #.upper()
                    break

    return id_type_dict


# フルデータパスを解析してIDタイプ、ID名、プロパティパスを抽出
def extract_id_and_path(full_data_path):
    # データパスの解析
    parts = full_data_path.split(".")
    
    # フルデータパスが期待した形式であるか確認
    if len(parts) < 3 or not parts[0] == "bpy" or not parts[1] == "data":
        raise ValueError("Invalid full data path format")
        
    # IDタイプ部分の安全な取得
    id_type_part = parts[2].split("[")[0] if len(parts) > 2 else None
    if not id_type_part:
        raise ValueError("ID type part not found in data path")

    # IDタイプを辞書から取得
    id_type = generate_id_type_dict().get(id_type_part)
    if id_type is None:
        raise ValueError(f"Invalid ID type part: {id_type_part}")

    # ID名とプロパティパスの抽出
    id_name = parts[2].split("[")[1].split("]")[0].replace("\"", "")
    property_path = ".".join(parts[3:]).replace("'", "\"")

    return id_type.upper(), id_name, property_path


def add_driver_from_clipboard():
    # クリップボードからフルデータパスを取得
    full_data_path = bpy.context.window_manager.clipboard

    # データパスからIDタイプとID名を抽出
    id_type, id_name, property_path = extract_id_and_path(full_data_path)

    # マウスオーバーしているプロパティの情報を取得
    hovered_property = bpy.context.property
    if not hovered_property:
        print("No property hovered.")
        return

    datablock, data_path, index = hovered_property

    # ドライバーを追加
    driver = datablock.driver_add(data_path, index).driver
    driver.type = 'SCRIPTED'

    # ドライバー変数の設定
    var = driver.variables.new()
    var.name = 'var'
    var.type = 'SINGLE_PROP'
    target = var.targets[0]
    target.id_type = id_type
    target.id = bpy.data.objects[id_name]
    target.data_path = property_path

    # 式の設定
    driver.expression = "var"
    


def register():
    bpy.utils.register_class(CUSTOM_OT_add_driver)

def unregister():
    bpy.utils.unregister_class(CUSTOM_OT_add_driver)


if __name__ == "__main__":
    register()
