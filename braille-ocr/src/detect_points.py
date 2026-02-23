from ultralytics import YOLO
import glob
import os


# モデル読み込み(パス指定)
model = YOLO("best.pt")

# 保存先フォルダ(パス指定)
save_dir = "datasets/braille/result"
os.makedirs(save_dir, exist_ok=True)

# val フォルダの PNG を全部取得(パス指定)
image_paths = glob.glob("datasets/braille/images/val/*.png")

for img in image_paths:
    print(f"推論中: {img}")
    results = model(img)

    # YOLO が描画した画像を取得
    plotted = results[0].plot()

    # 保存ファイル名を作成
    filename = os.path.basename(img)
    save_path = os.path.join(save_dir, filename)

    # 保存
    import cv2
    cv2.imwrite(save_path, plotted)

print("保存完了しました。")


