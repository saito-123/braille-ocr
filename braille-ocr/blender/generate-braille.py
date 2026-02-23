import bpy
import math
import os
import random
import mathutils
from bpy_extras.object_utils import world_to_camera_view

output_dir = "C:\work\sample"
num_images = 100
os.makedirs(output_dir, exist_ok=True)

# --- シーン初期化 ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- 点字セル ---
def create_braille_cell(prefix="dot", radius=0.2):
    positions = [
        (-0.5, 0.5, 0),
        (-0.5, 0.0, 0),
        (-0.5, -0.5, 0),
        (0.5, 0.5, 0),
        (0.5, 0.0, 0),
        (0.5, -0.5, 0),
    ]
    objs = []
    for i, pos in enumerate(positions):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=pos)
        obj = bpy.context.active_object
        obj.name = f"{prefix}_{i+1}"
        objs.append(obj)
    return objs

dots = create_braille_cell()

# --- カメラ ---
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# --- ライト ---
light_data = bpy.data.lights.new(name="Light", type='POINT')
light_obj = bpy.data.objects.new(name="Light", object_data=light_data)
bpy.context.collection.objects.link(light_obj)

# --- レンダリング設定 ---
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
scene.render.resolution_x = 640
scene.render.resolution_y = 640

# --- カメラをターゲットに向ける ---
def look_at(obj, target):
    direction = target.location - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# --- 大量生成 ---
for i in range(num_images):

    # カメラを球面上にランダム配置
    r = 5
    theta = random.uniform(0.3, 1.2)
    phi = random.uniform(0, 2 * math.pi)

    cam_obj.location.x = r * math.sin(theta) * math.cos(phi)
    cam_obj.location.y = r * math.sin(theta) * math.sin(phi)
    cam_obj.location.z = r * math.cos(theta)

    look_at(cam_obj, dots[0])

    # ライトをカメラの近くに配置
    offset = mathutils.Vector((1.5, 0, 1.0))
    light_obj.location = cam_obj.location + cam_obj.matrix_world.to_quaternion() @ offset
    light_data.energy = 1500

    # ★ 行列更新（これが超重要）
    bpy.context.view_layer.update()

    # --- ラベル生成 ---
    label_path = os.path.join(output_dir, f"braille_{i:04d}.txt")
    with open(label_path, "w") as f:
        for class_id, dot in enumerate(dots):

            # ★ ワールド座標で取得（必須）
            world_pos = dot.matrix_world.translation

            # ★ カメラ座標に変換
            uv = world_to_camera_view(scene, cam_obj, world_pos)

            x = uv.x
            y = 1 - uv.y  # Blenderは上下逆なので反転

            # バウンディングボックスの大きさ（仮）
            w = 0.05
            h = 0.05

            f.write(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

    # --- 画像出力 ---
    scene.render.filepath = os.path.join(output_dir, f"braille_{i:04d}.png")
    bpy.ops.render.render(write_still=True)

    print(f"✔ {i+1}/{num_images}")

print("✔ 完了：画像 + 正しいラベル生成が終わりました →", output_dir)