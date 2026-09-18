import os
import win32com.client

def create_shortcuts():
    folder = os.path.dirname(os.path.abspath(__file__))
    shell = win32com.client.Dispatch("WScript.Shell")
    icon_path = os.path.join(folder, "icon.ico") + ",0"
    vbs_path = os.path.join(folder, "launch_silent.vbs")

    # 1. Shortcut brenda folderit te projektit (AppRestaurant)
    lnk_folder = os.path.join(folder, "STRICT LOUNGE & BAR.lnk")
    s1 = shell.CreateShortCut(lnk_folder)
    s1.Targetpath = "wscript.exe"
    s1.Arguments = f'"{vbs_path}"'
    s1.WorkingDirectory = folder
    s1.IconLocation = icon_path
    s1.Description = "STRICT LOUNGE & BAR - Sistemi i Restaurantit"
    s1.save()
    print("Folder shortcut created:", os.path.exists(lnk_folder), lnk_folder)

    # 2. Shortcut ne Desktop te kompjuterit
    desktop_dir = os.path.expanduser("~/Desktop")
    if not os.path.exists(desktop_dir):
        desktop_dir = r"c:\Users\Swisstech\OneDrive\Desktop"
    
    lnk_desktop = os.path.join(desktop_dir, "STRICT LOUNGE & BAR.lnk")
    s2 = shell.CreateShortCut(lnk_desktop)
    s2.Targetpath = "wscript.exe"
    s2.Arguments = f'"{vbs_path}"'
    s2.WorkingDirectory = folder
    s2.IconLocation = icon_path
    s2.Description = "STRICT LOUNGE & BAR - Sistemi i Restaurantit"
    s2.save()
    print("Desktop shortcut created:", os.path.exists(lnk_desktop), lnk_desktop)

if __name__ == "__main__":
    create_shortcuts()
