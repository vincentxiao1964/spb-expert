import shutil
import os

path = r"d:\spb-expert11\frontend\node_modules\@vue\cli-service\node_modules\postcss-loader"

if os.path.exists(path):
    print(f"Deleting {path}...")
    try:
        shutil.rmtree(path)
        print("Deleted.")
    except Exception as e:
        print(f"Error: {e}")
else:
    print(f"Path not found: {path}")
