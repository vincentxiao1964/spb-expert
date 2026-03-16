import uiautomation as auto
import time

def main():
    print("Listing all top-level windows...")
    root = auto.GetRootControl()
    for window in root.GetChildren():
        if window.ControlTypeName == "WindowControl":
             print(f"Window: '{window.Name}' Class: '{window.ClassName}' Handle: {window.NativeWindowHandle}")
             if "WXWork" in str(window.ProcessId): # This might not be directly available as property name, but let's check Name/Class
                 pass

    print("\nDeep search for WXWork windows...")
    # Just checking names
    pass


if __name__ == "__main__":
    main()