import polib
import os

def compile_po_files():
    locale_dir = os.path.join(os.getcwd(), 'locale')
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                mo_path = os.path.join(root, file.replace('.po', '.mo'))
                print(f'Compiling {po_path} to {mo_path}')
                try:
                    po = polib.pofile(po_path)
                    po.save_as_mofile(mo_path)
                    print(f'Successfully compiled {mo_path}')
                except Exception as e:
                    print(f'Error compiling {po_path}: {e}')

if __name__ == '__main__':
    compile_po_files()
