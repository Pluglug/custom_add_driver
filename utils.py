import bpy

# マウスオーバーしているプロパティの情報を取得
def print_hovered_property_info():
    hovered_property = bpy.context.property
    if hovered_property:
        datablock, data_path, index = hovered_property
        print("")
        print("Datablock:", datablock)
        print("Data Path:", data_path)
        print("Index:", index)