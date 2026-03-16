import os
import shutil

source_dir = r"d:\spb-expert11\frontend"
target_dir = r"d:\spb-expert11\frontend\src"

files_to_move = [
    "common",
    "locale",
    "pages",
    "App.vue",
    "main.js",
    "manifest.json",
    "pages.json",
    "uni.scss"
]

if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"Created {target_dir}")

for item in files_to_move:
    src_path = os.path.join(source_dir, item)
    dst_path = os.path.join(target_dir, item)
    
    if os.path.exists(src_path):
        print(f"Moving {item}...")
        try:
            shutil.move(src_path, dst_path)
            print(f"Moved {item}")
        except Exception as e:
            print(f"Error moving {item}: {e}")
    else:
        print(f"Skipping {item} (not found)")
