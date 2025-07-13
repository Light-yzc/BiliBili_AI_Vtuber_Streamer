#This function not very perfect currently
import win32gui
import win32ui
import win32con # 用于 win32con.SW_SHOWMINIMIZED
from ctypes import windll # 核心改变：导入 windll
from PIL import Image

def capture_background_window_ctypes(window_handle, window_title):
    """
    通过 Windows API (使用 ctypes.windll.user32.PrintWindow) 截取指定句柄的后台窗口。
    即使窗口最小化或被遮挡也能截取。
    """
    try:
        if not window_handle:
            print(f"错误: 无效的窗口句柄。")
            return None

        # 获取窗口尺寸
        # GetWindowRect 返回 (left, top, right, bottom)
        left, top, right, bottom = win32gui.GetWindowRect(window_handle)
        width = right - left
        height = bottom - top

        # 确保窗口尺寸有效，对于最小化的窗口，PrintWindow 也能工作
        if width <= 0 or height <= 0:
            print(f"警告: 窗口 '{window_title}' 的计算尺寸为 ({width}x{height})，可能不准确。但仍尝试截屏...")
            # 尝试获取实际的客户区尺寸作为 fallback，但对于后台窗口可能不准
            _, _, c_width, c_height = win32gui.GetClientRect(window_handle)
            if c_width > 0 and c_height > 0:
                width, height = c_width, c_height
                print(f"已使用客户区尺寸 ({width}x{height})")
            else:
                print(f"警告: 无法获取有效的窗口尺寸，截屏可能不完整或失败。")
                # 继续尝试，有时 PrintWindow 仍能工作
                
        # 获取窗口的设备上下文（DC）
        hwnd_dc = win32gui.GetWindowDC(window_handle)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # 创建一个位图
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)

        # *** 核心改变：使用 ctypes.windll.user32.PrintWindow ***
        # PrintWindow 的参数：句柄，设备上下文句柄，标志 (0表示整个窗口)
        result = windll.user32.PrintWindow(window_handle, save_dc.GetSafeHdc(), 0)

        # PrintWindow 返回 0 表示失败，返回 1 表示成功
        if result != 1:
            print(f"警告: PrintWindow 无法截取 '{window_title}' (错误码: {result})。可能是游戏或视频应用。")
            # 在这里不再尝试 BitBlt，因为它对后台窗口几乎无效。
            # 对于这种特殊情况，通常需要更底层的图形API。
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(window_handle, hwnd_dc)
            return None

        # 将位图保存为 Pillow Image 对象
        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        # 清理
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(window_handle, hwnd_dc)

        return img

    except Exception as e:
        print(f"后台窗口截屏时发生错误: {e}")
        return None

def list_and_capture_background_window_interactive():
    """
    列出所有窗口，让用户选择后进行后台截屏。
    此版本使用 ctypes.windll.user32.PrintWindow。
    """
    try:
        top_level_windows = []

        def callback(hwnd, extra):
            title = win32gui.GetWindowText(hwnd)

            if title and \
               "Program Manager" not in title and \
               "Default IME" not in title and \
               "MSCTFIME UI" not in title and \
               "NVIDIA" not in title and \
               "Cortana" not in title and \
               "DWM" not in title and \
               win32gui.IsWindow(hwnd):
                
                # 获取窗口的显示状态 (是否最小化)
                placement = win32gui.GetWindowPlacement(hwnd)
                is_minimized = (placement[1] == win32con.SW_SHOWMINIMIZED)
                is_visible = win32gui.IsWindowVisible(hwnd)

                top_level_windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'is_visible': is_visible,
                    'is_minimized': is_minimized
                })
            return True

        win32gui.EnumWindows(callback, None)

        if not top_level_windows:
            print("没有找到任何可供截屏的应用程序窗口。请确保有窗口打开。")
            return

        print("--- 可选择的后台窗口列表 ---")
        print("注意：此方法可截取最小化或被遮挡的窗口（部分应用可能截取到黑屏）。")
        window_options = {}
        counter = 1
        for window_info in top_level_windows:
            print(f"{counter}. {window_info['title']} (可见: {window_info['is_visible']}, 最小化: {window_info['is_minimized']})")
            window_options[str(counter)] = window_info
            counter += 1
        print("------------------------")

        if not window_options:
            print("没有找到任何有标题的窗口可以截屏。")
            return

        while True:
            choice = input("请输入您想截屏的窗口编号 (或输入 'q' 退出): ").strip()
            if choice.lower() == 'q':
                print("已退出。")
                return

            if choice in window_options:
                target_window_info = window_options[choice]
                target_hwnd = target_window_info['hwnd']
                target_title = target_window_info['title']
                break
            else:
                print("无效的输入，请重新输入正确的编号。")

        print(f"正在尝试后台截屏窗口: '{target_title}' (句柄: {target_hwnd})")
        # 调用新的截屏函数
        screenshot_image = capture_background_window_ctypes(target_hwnd, target_title)

        if screenshot_image:
            safe_window_title = "".join([c for c in target_title if c.isalnum() or c in (' ', '.', '_')]).strip()
            if len(safe_window_title) > 50:
                safe_window_title = safe_window_title[:50].strip() + "..."
            file_name = f"{safe_window_title}_background_ctypes_screenshot.png"
            screenshot_image.save(file_name)
            print(f"窗口 '{target_title}' 的后台截屏已保存为 {file_name}")
        else:
            print("未成功截屏。")

    except Exception as e:
        print(f"发生意外错误: {e}")

# --- 运行后台截屏程序 ---
if __name__ == "__main__":
    list_and_capture_background_window_interactive()