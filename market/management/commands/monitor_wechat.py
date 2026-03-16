import time
import os
import sys
import json
import logging
import requests
import uiautomation as auto
import win32gui
import win32ui
import win32con
from ctypes import windll
from PIL import Image

# Ensure Scripts and CWD are in PATH for OCR model download
scripts_path = os.path.join(os.path.dirname(sys.executable), 'Scripts')
cwd_path = os.getcwd()
new_path = os.environ['PATH']
if scripts_path not in new_path:
    new_path = scripts_path + os.pathsep + new_path
if cwd_path not in new_path:
    new_path = cwd_path + os.pathsep + new_path
os.environ['PATH'] = new_path

from rapidocr_onnxruntime import RapidOCR
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from market.models import ShipListing

# Configure Logging
logger = logging.getLogger(__name__)

User = get_user_model()

class Command(BaseCommand):
    help = 'Monitors a specific WeChat Group for Ship Listing information using UI Automation.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--group',
            type=str,
            default='文件传输助手',  # Default for testing
            help='The name of the WeChat group to monitor (must be open in a separate window or selected).'
        )
        parser.add_argument(
            '--app',
            type=str,
            default='wechat',
            choices=['wechat', 'wecom'],
            help='The application to monitor: "wechat" (Personal) or "wecom" (Enterprise/Work).'
        )
        parser.add_argument(
            '--debug-ui',
            action='store_true',
            help='Print the UI structure of the WeChat window for debugging.'
        )
        parser.add_argument(
            '--history',
            type=int,
            default=0,
            help='Number of pages to scroll up to fetch history messages (Default: 0, only new messages).'
        )

    def handle(self, *args, **options):
        group_name = options['group']
        app_type = options['app']
        debug_ui = options['debug_ui']
        history_pages = options['history']
        
        target_window_name = "微信" if app_type == 'wechat' else "企业微信"
        self.stdout.write(f"Waiting for {target_window_name} Window... (Target Group: {group_name})")
        
        # 1. Connect to Application Window
        if app_type == 'wechat':
            # Personal WeChat
            window = auto.WindowControl(searchDepth=1, Name="微信", ClassName="WeChatMainWndForPC")
        else:
            # Enterprise WeChat (WeCom)
            # WeCom class name varies, easier to search by Name "企业微信"
            # Try exact match first
            window = auto.WindowControl(searchDepth=1, Name="企业微信")
            if not window.Exists(1):
                 # Try partial match or regex if needed, but "企业微信" is standard
                 window = auto.WindowControl(searchDepth=1, SubName="企业微信")
        
        if not window.Exists(3):
            self.stdout.write(self.style.ERROR(f"{target_window_name} is not running or window not found! Please open it."))
            return

        self.stdout.write(self.style.SUCCESS(f"Connected to {target_window_name} Window."))
        window.SetActive()
        
        # If Debug Mode
        if debug_ui:
            self.print_ui_structure(window)
            return

        # 2. Locate the Message List
        # WeCom UI structure is different.
        msg_list = None
        
        if app_type == 'wechat':
            msg_list = window.ListControl(Name="消息")
        else:
            # WeCom: often simpler, just find the ListControl in the main window
            # WeCom message list usually doesn't have a specific Name like "消息"
            # We look for the ListControl that likely contains the messages
            # Heuristic: Find all ListControls, pick the one with the most children or largest area
            pass

        if not msg_list or not msg_list.Exists(1):
            self.stdout.write(self.style.WARNING("Specific Message List not found by name. Searching generic ListControls..."))
            
            # Generic Search Strategy
            # Find all ListControls in the window
            all_lists = window.GetChildren() # Shallow first
            
            # Deep search if needed (but expensive)
            # Let's try direct descendants first
            candidates = []
            
            # Helper to find lists recursively (limited depth)
            def find_lists(control, depth=0):
                if depth > 5: return
                children = control.GetChildren()
                for child in children:
                    if child.ControlTypeName == "ListControl":
                        candidates.append(child)
                    find_lists(child, depth+1)
            
            find_lists(window)
            
            if candidates:
                # Pick the one that looks most like a chat (usually has multiple ListItem children)
                # Or just the largest one?
                # For now, let's pick the last one found (often the chat content is loaded last/deepest)
                # OR, print them for the user to see in debug mode?
                # Let's try to assume it's the one with ListItem children
                best_candidate = None
                max_items = -1
                
                for cand in candidates:
                    # Check children count (lightweight)
                    # Note: GetChildren can be slow if many items.
                    # WeCom list items might be "ListItem" or "Group"
                    # Let's try to just use the one with the most children?
                    try:
                        child_count = len(cand.GetChildren())
                        if child_count > max_items:
                            max_items = child_count
                            best_candidate = cand
                    except:
                        pass
                
                msg_list = best_candidate

        use_generic_scan = False
        if not msg_list or not msg_list.Exists(1):
            self.stdout.write(self.style.WARNING("Message List not reliably found. Falling back to generic scan mode."))
            use_generic_scan = True

        # Check if generic scan works (finds any candidates)
        if use_generic_scan:
            candidates = []
            def test_scan(control, depth=0):
                if depth > 5: return
                try:
                    for child in control.GetChildren():
                        if child.ControlTypeName in ("ListItem", "TextControl"):
                             candidates.append(child)
                        test_scan(child, depth+1)
                except: pass
            test_scan(window)
            if not candidates:
                self.stdout.write(self.style.WARNING("Generic scan found no items. Switching to VISUAL SCAN mode (OCR Whole Window)."))
                use_visual_scan = True
                use_generic_scan = False
            else:
                use_visual_scan = False
        else:
            use_visual_scan = False

        self.stdout.write(f"Monitoring messages in current chat window (Ensure '{group_name}' is selected)...")
        self.stdout.write("Press Ctrl+C to stop.")

        # Initialize OCR
        self.stdout.write("Initializing OCR engine (this may take a few seconds)...")
        try:
            ocr = RapidOCR()
            self.stdout.write(self.style.SUCCESS("OCR Engine Ready."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to init OCR: {e}"))
            ocr = None

        processed_messages = set()
        
        # Admin user to assign listings to
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR("No superuser found. Cannot assign listings."))
            return

        # Helper to process messages
        def scan_messages(scroll_up=False):
            # Focus the list to ensure scrolling works
            if not use_generic_scan and msg_list:
                msg_list.SetFocus()
            
            if scroll_up and not use_generic_scan and msg_list:
                # Scroll up to load history
                # WheelUp parameter is number of steps. 1 step is usually one line or small scroll.
                # We want to scroll a "page".
                msg_list.WheelUp(wheelTimes=10, waitTime=0.5)
                time.sleep(1) # Wait for UI load
            
            # Collect visible messages
            if use_visual_scan and ocr:
                # Visual Scan Strategy
                # 1. Capture whole window
                tmp_file = f"temp_ocr_window_{int(time.time()*1000)}.png"
                try:
                    # Use background capture if possible
                    captured = False
                    try:
                        hwnd = window.NativeWindowHandle
                        captured = self.background_screenshot(hwnd, tmp_file)
                    except:
                        pass
                    
                    if not captured:
                        # Fallback to standard capture
                        window.CaptureToImage(tmp_file)

                    res, _ = ocr(tmp_file)
                    if res:
                        # Extract text blocks
                        # res format: [[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], text, score], ...]
                        # We filter low confidence
                        # We treat each text block as a potential message part
                        # To reduce noise, we can ignore known UI elements (top bar, side bar)
                        # But for now, let's just dump all text that looks like a listing
                        
                        full_text_content = ""
                        for line in res:
                            text = line[1]
                            score = float(line[2])
                            if score > 0.5:
                                full_text_content += text + "\n"
                        
                        # Process the accumulated text
                        # We split by newlines and try to process
                        # However, we need to avoid reprocessing.
                        # We can hash the whole content? No, scrolling changes it.
                        # We can hash each line?
                        
                        lines = full_text_content.split('\n')
                        target_msgs = []
                        for line in lines:
                             if len(line) > 5: # Filter very short noise
                                 # Wrap in a dummy object to match loop structure
                                 class DummyMsg:
                                     Name = line
                                     def CaptureToImage(self, path): pass
                                 target_msgs.append(DummyMsg())
                    else:
                        target_msgs = []
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Visual Scan Error: {e}"))
                    target_msgs = []
                finally:
                     if os.path.exists(tmp_file):
                        try: os.remove(tmp_file)
                        except: pass
            
            elif not use_generic_scan and msg_list:
                msgs = msg_list.GetChildren()
                target_msgs = msgs if scroll_up else (msgs[-10:] if len(msgs) > 10 else msgs)
            else:
                # Generic scan: search for controls that look like message items
                candidates = []
                def find_message_items(control, depth=0):
                    if depth > 12:
                        return
                    try:
                        children = control.GetChildren()
                    except Exception:
                        return
                    for child in children:
                        # Typical message entries are ListItem or TextControl, often with Name containing content
                        if child.ControlTypeName in ("ListItem", "TextControl"):
                            nm = child.Name or ""
                            # Heuristic: skip very short names and UI labels
                            if len(nm) > 6 and not nm.strip() in ("发送", "消息", "企业微信", "微信"):
                                candidates.append(child)
                        # Recurse
                        find_message_items(child, depth + 1)
                find_message_items(window)
                msgs = candidates
            
            if not use_visual_scan and not target_msgs: # If target_msgs already set by visual scan, skip
                 # If scrolling up, we want ALL visible messages, not just recent 10
                 target_msgs = msgs if scroll_up else (msgs[-10:] if len(msgs) > 10 else msgs)
            
            for msg_item in target_msgs:
                full_text = msg_item.Name
                is_image = False
                
                # Check if it needs OCR (Empty text or explicit image placeholder)
                # Only check OCR if NOT using visual scan (visual scan is already OCR)
                if not use_visual_scan and (not full_text or full_text in ["[图片]", "图片", "Image"]):
                    is_image = True
                
                if is_image and ocr:
                    # Capture and OCR
                    tmp_file = f"temp_ocr_{int(time.time()*1000)}_{id(msg_item)}.png"
                    try:
                        msg_item.CaptureToImage(tmp_file)
                        res, _ = ocr(tmp_file)
                        if res:
                            extracted_text = "\n".join([line[1] for line in res if float(line[2]) > 0.4])
                            
                            if extracted_text.strip():
                                full_text = f"[OCR] {extracted_text}"
                    except Exception as e:
                        pass
                    finally:
                        if os.path.exists(tmp_file):
                            try: os.remove(tmp_file)
                            except: pass

                if not full_text: continue
                
                msg_hash = hash(full_text)
                if msg_hash in processed_messages: continue
                
                processed_messages.add(msg_hash)
                
                if '\n' in full_text:
                    parts = full_text.split('\n', 1)
                    sender = parts[0]
                    content = parts[1]
                else:
                    sender = "Unknown"
                    content = full_text

                self.stdout.write(f"[{'History' if scroll_up else 'New'}] Msg from {sender}: {content[:20]}...")
                
                listing_data = self.parse_with_doubao(content)
                if listing_data:
                    self.save_listing(admin_user, listing_data, content, sender)

        try:
            # 1. Fetch History if requested
            if history_pages > 0:
                self.stdout.write(self.style.WARNING(f"Scrolling back {history_pages} pages for history..."))
                for i in range(history_pages):
                    self.stdout.write(f"Scanning history page {i+1}/{history_pages}...")
                    scan_messages(scroll_up=True)
                self.stdout.write(self.style.SUCCESS("History scan completed. Switching to real-time monitor mode."))

            # 2. Real-time Loop
            while True:
                scan_messages(scroll_up=False)
                time.sleep(3)
                
        except KeyboardInterrupt:
            self.stdout.write("Stopping monitor...")

    def print_ui_structure(self, element, depth=0):
        """Recursively prints UI structure."""
        if depth > 10: return
        indent = "  " * depth
        self.stdout.write(f"{indent}{element.ControlTypeName} - Name: '{element.Name}' - Class: '{element.ClassName}'")
        try:
            for child in element.GetChildren():
                self.print_ui_structure(child, depth + 1)
        except Exception:
            pass

    def background_screenshot(self, hwnd, filename):
        """Captures window content even if occluded (but not minimized)."""
        try:
            # Get window dimensions
            left, top, right, bot = win32gui.GetWindowRect(hwnd)
            w = right - left
            h = bot - top
            
            # Create device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
            
            saveDC.SelectObject(saveBitMap)
            
            # PrintWindow is the key for background capture
            # 2 = PW_RENDERFULLCONTENT (available since Win8.1), 0 is default
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2) 
            if result == 0:
                 # Fallback to 0 if 2 fails (e.g. older windows or specific app issues)
                 result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
            
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            
            im.save(filename)
            
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            return True
        except Exception as e:
            # logger.error(f"Screenshot failed: {e}")
            return False

    def parse_with_doubao(self, text):
        """
        Uses Doubao to extract ship listing info.
        """
        endpoint_id = os.getenv('ENDPOINT_ID', '').strip()
        api_key = os.getenv('ARK_API_KEY', '').strip()
        
        if not endpoint_id or not api_key:
            return None

        prompt = (
            "Analyze the following text. If it is a Ship Sale/Lease listing (e.g. 'Sell 5000t barge', 'Charter deck barge'), "
            "extract the details into a JSON object with these keys:\n"
            "- type: 'SELL', 'BUY', 'CHARTER_OFFER', or 'CHARTER_REQUEST'\n"
            "- category: 'SELF_PROPELLED' or 'NON_SELF_PROPELLED' (default SELF_PROPELLED)\n"
            "- dwt: string (e.g. '5000t')\n"
            "- build_year: integer\n"
            "- price: string\n"
            "- contact: string\n"
            "- description: string (summary of the ship)\n"
            "If it is NOT a ship listing, return NULL string only.\n\n"
            f"Text: {text}"
        )

        try:
            url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            payload = {
                "model": endpoint_id,
                "messages": [{"role": "user", "content": prompt}]
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                # Clean code blocks if present
                content = content.replace('```json', '').replace('```', '').strip()
                if content == 'NULL':
                    return None
                return json.loads(content)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API Error: {e}"))
            return None
        return None

    def save_listing(self, user, data, original_text, sender):
        """
        Saves the parsed data to ShipListing.
        """
        try:
            listing = ShipListing(
                user=user,
                listing_type=data.get('type', 'SELL'),
                ship_category=data.get('category', 'SELF_PROPELLED'),
                dwt=data.get('dwt', ''),
                build_year=data.get('build_year'),
                description=data.get('description', original_text),
                contact_info=f"{data.get('contact', '')} (Sender: {sender})",
                status=ShipListing.Status.PENDING,
                admin_notes=f"Auto-imported from WeChat Group. Original: {original_text}"
            )
            listing.save()
            self.stdout.write(self.style.SUCCESS(f"Saved Listing: {listing}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Save Error: {e}"))
