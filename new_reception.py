from playwright.sync_api import sync_playwright
import time
import re
import logging

# 🚀 Enterprise Logging System
logging.basicConfig(filename='app_crash.log', level=logging.ERROR, 
                    format='%(asctime)s - RECEPTION - %(levelname)s - %(message)s')

CDP_URL = "http://localhost:9222"
CANCEL_FETCH = False
ACTIVE_BROWSER = None

def force_stop_process():
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = True
    print("🛑 FORCE KILL ACTIVATED! Disconnecting browser...")
    if ACTIVE_BROWSER:
        try: ACTIVE_BROWSER.disconnect()
        except: pass

# ==============================================================
# 1. SINGLE RECEPTION INJECTION (Live Dropdown & Fast Inject)
# ==============================================================
def inject_single_reception_tag(job_id, tag_id, weight):
    global CANCEL_FETCH, ACTIVE_BROWSER
    tag_id, weight = str(tag_id).strip(), str(weight).strip()
    search_job_id = str(job_id).split('-L')[0] 
    print(f"👻 Live Ghost Injecting Tag: {tag_id} | Weight: {weight}g | Job: {search_job_id}")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Browser connect nahi ho paya!"}
            
            target_frame = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        if search_job_id in frame.locator("body").inner_text() and "Save" in frame.locator("body").inner_text():
                            target_frame = frame
                            break
                    except: pass
                if target_frame: break
                
            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": f"⚠️ Job Card '{search_job_id}' screen par nahi mila."}
            
            # Row dhoondho
            row = target_frame.locator(f"tr:has-text('{tag_id}')")
            if row.count() > 0:
                weight_input = row.first.locator("input[type='text'], input.form-control, input.scan-input, input.weightCls").first
                if weight_input.is_visible():
                    
                    # 🚀 CRITICAL FIX: PURE GHOST INJECT (Bina Keyboard Typing Ke)
                    js_inject = f"""node => {{
                        node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                        node.removeAttribute('onpaste'); node.removeAttribute('oncopy'); 
                        node.removeAttribute('oncut'); node.removeAttribute('oncontextmenu'); 
                        node.value = '{weight}'; 
                        node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                        node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                        node.dispatchEvent(new Event('blur', {{ bubbles: true }})); 
                    }}"""
                    weight_input.evaluate(js_inject)
                    
                    # Save Button ko Ghost Click karna
                    save_btn = row.first.locator("text='Save'").first
                    if save_btn.is_visible():
                        main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                        main_page.once("dialog", lambda dialog: dialog.accept())
                        save_btn.evaluate("node => node.click()") # 🚀 JS Force Click
                        time.sleep(1)
                        
                    try: browser.disconnect()
                    except: pass
                    return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                else: return {"status": "error", "msg": "⚠️ Input box nahi mila!"}
            else: return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' list me nahi mila."}
    except Exception as e: return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}

# ==============================================================
# 3. FULL AUTO INJECTION (Poori list ek sath)
# ==============================================================
def inject_reception_weight_ghost(job_id, job_data, delay_ms=1500):
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    search_job_id = str(job_id).split('-L')[0] 
    
    print(f"👻 Ghost Injecting Reception for: {search_job_id} (Original: {job_id})")
    if not job_data: return "⚠️ डेटाबेस खाली है।"
    print(f"👻 Auto Injection Started (Speed: {delay_ms}ms)... Job: {job_id}")

    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL)
                ACTIVE_BROWSER = browser
            except: return "⚠️ ब्राउज़र ओपन नहीं है!"

            job_matched = False
            for page in browser.contexts[0].pages:
                try:
                    if search_job_id in page.locator("body").inner_text(): job_matched = True; break
                except: pass
                for frame in page.frames:
                    try:
                        if search_job_id in frame.locator("body").inner_text(): job_matched = True; break
                    except: pass
                if job_matched: break
                
            if not job_matched:
                try: browser.disconnect()
                except: pass
                return f"❌ Wrong Page! Site par ID '{search_job_id}' open nahi hai."

            filled_count = 0
            for item in job_data:
                if CANCEL_FETCH:
                    print("🛑 User Cancelled Auto Injection!")
                    break

                tag_id, weight = str(item[0]).strip(), str(item[1]).strip()
                
                # 🚀 CRITICAL FIX 1: 0.0 weight wale tags ko skip karna zaroori hai!
                if not weight or weight == "0" or weight == "0.0": 
                    continue
                
                target_frame = None
                tag_found = False

                while True:
                    for page in browser.contexts[0].pages:
                        try:
                            if page.locator("tr").filter(has=page.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                                target_frame = page
                                tag_found = True
                                break
                        except: pass
                        
                        if not tag_found:
                            for frame in page.frames:
                                try:
                                    if frame.locator("tr").filter(has=frame.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                                        target_frame = frame
                                        tag_found = True
                                        break
                                except: pass
                        if tag_found: break

                    if tag_found: break

                    next_btn_clicked = False
                    for page in browser.contexts[0].pages:
                        frames_to_check = [page] + page.frames
                        for f in frames_to_check:
                            try:
                                next_btn = f.locator("a.paginate_button.next, a#tabWeight_next, li.next a, a:has-text('Next'), a:has-text('›')").last
                                if next_btn.count() > 0:
                                    btn_class = next_btn.get_attribute("class") or ""
                                    is_disabled = "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true" or next_btn.get_attribute("disabled") is not None
                                    
                                    if not is_disabled:
                                        next_btn.evaluate("node => node.click()") 
                                        time.sleep(1.2) 
                                        next_btn_clicked = True
                                        break
                            except: pass
                        if next_btn_clicked: break

                    if not next_btn_clicked: break

                if not target_frame or not tag_found: 
                    print(f"⚠️ Alert: Tag {tag_id} kisi bhi page par nahi mila, skip kar rahe hain.")
                    continue

                try:
                    row = target_frame.locator("tr").filter(has=target_frame.locator("td:nth-child(2), td:nth-child(3)").get_by_text(tag_id, exact=True))
                    
                    if row.count() > 0:
                        target_row = row.first
                        weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                        
                        if weight_input.count() > 0:
                            current_val = str(weight_input.evaluate("node => node.value")).strip()
                            if current_val != weight:
                                
                                # 🚀 CRITICAL FIX 2: 100% Pure Ghost Inject (With 'blur' event)
                                js_inject = f"""node => {{
                                    node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                                    node.removeAttribute('onpaste'); node.removeAttribute('oncopy'); 
                                    node.removeAttribute('oncut'); node.removeAttribute('oncontextmenu'); 
                                    node.value = '{weight}'; 
                                    node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('blur', {{ bubbles: true }})); 
                                }}"""
                                weight_input.evaluate(js_inject)
                                
                                save_btn = target_row.locator("text='Save'").first
                                if save_btn.is_visible():
                                    main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                                    main_page.once("dialog", lambda dialog: dialog.accept())
                                    
                                    # Ghost Click
                                    save_btn.evaluate("node => node.click()") 
                                    
                                    print(f"⏳ Tag {tag_id} saved. Waiting for BIS portal to stabilize...")
                                    time.sleep(1.5) 
                                    try:
                                        main_page.wait_for_load_state("networkidle", timeout=5000)
                                        target_frame.wait_for_selector("table tbody tr", state="visible", timeout=5000)
                                    except: pass
                                    
                                    time.sleep(delay_ms / 1000.0) 
                                
                                filled_count += 1
                except Exception as e: print(f"⚠️ Error: {e}")

            try: browser.disconnect() 
            except: pass
            
            if CANCEL_FETCH:
                return f"🛑 STOPPED! {filled_count} Tags Save hone ke baad process rok di gayi."
            return f"✅ Success! {filled_count} Tags Save kar diye gaye."
    except Exception as e:
        logging.error(f"Auto Inject Error: {e}", exc_info=True)
        return f"⚠️ Error: {e}"
# ==============================================================
# 3. SCRAPE ALL REQUESTS FROM MAIN PAGE
# ==============================================================
def scrape_all_requests_from_main():
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    print("👻 Scanning Request Batches (Main Dashboard)...")
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Browser connect nahi ho paya!"}
            
            target_frame = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        if "Jewellery/Artefacts Received" in frame.locator("body").inner_text():
                            target_frame = frame; break
                    except: pass
                if target_frame: break
                
            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Main Dashboard 'Jewellery/Artefacts Received' wali table nahi mili!"}

            js_code = """
            () => {
                let req_data = {};
                let rows = document.querySelectorAll('table tbody tr');
                for (let r of rows) {
                    let reqNo = r.querySelector('td:nth-child(1)')?.innerText.trim();
                    let jobCard = r.querySelector('td:nth-child(3)')?.innerText.trim();
                    if (reqNo && jobCard && jobCard !== "No data available in table") {
                        if (!req_data[reqNo]) req_data[reqNo] = [];
                        if (!req_data[reqNo].includes(jobCard)) req_data[reqNo].push(jobCard);
                    }
                }
                return req_data;
            }
            """
            
            master_data = {}
            while True:
                if CANCEL_FETCH: break
                current_page_data = target_frame.evaluate(js_code)
                
                if current_page_data:
                    for req, jobs in current_page_data.items():
                        if req not in master_data: master_data[req] = []
                        for j in jobs:
                            if j not in master_data[req]: master_data[req].append(j)
                            
                next_btn = target_frame.locator("a.paginate_button.next").last
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true":
                        break
                        
                    old_keys = list(current_page_data.keys())
                    old_first_req = old_keys[0] if old_keys else ""
                    
                    try: next_btn.click(force=True)
                    except: next_btn.evaluate("node => node.click()")
                    
                    t_wait = time.time()
                    while time.time() - t_wait < 6:
                        if CANCEL_FETCH: break
                        time.sleep(0.2)
                        try:
                            chk_data = target_frame.evaluate(js_code)
                            chk_keys = list(chk_data.keys())
                            if chk_keys and chk_keys[0] != old_first_req: break
                        except: pass
                else: break

            try: browser.disconnect()
            except: pass
            
            if not master_data: return {"status": "error", "msg": "⚠️ Koi data nahi mila!"}
            return {"status": "success", "data": master_data}
    except Exception as e: return {"status": "error", "msg": str(e)}

# ==============================================================
# 4. SCRAPE ALL REQUESTS FROM XRF PAGE
# ==============================================================
def scrape_all_requests_from_xrf():
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    print("👻 Scanning Request Batches (XRF Page)...")
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Browser connect nahi ho paya!"}
            
            target_frame = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        text = frame.locator("body").inner_text()
                        if "List of Jewellery /Artefacts" in text or "Submitted Articles List" in text:
                            target_frame = frame; break
                    except: pass
                if target_frame: break
                
            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ XRF Dashboard nahi mila! Kripya 'XRF' menu kholen."}

            js_code = """
            () => {
                let req_data = {};
                let rows = document.querySelectorAll('table tbody tr');
                for (let r of rows) {
                    let reqNo = r.querySelector('td:nth-child(1)')?.innerText.trim();
                    let jobCard = r.querySelector('td:nth-child(2)')?.innerText.trim();
                    if (reqNo && jobCard && jobCard !== "No data available in table") {
                        if (!req_data[reqNo]) req_data[reqNo] = [];
                        if (!req_data[reqNo].includes(jobCard)) req_data[reqNo].push(jobCard);
                    }
                }
                return req_data;
            }
            """
            master_data = {}
            while True:
                if CANCEL_FETCH: break
                current_page_data = target_frame.evaluate(js_code)
                
                if current_page_data:
                    for req, jobs in current_page_data.items():
                        if req not in master_data: master_data[req] = []
                        for j in jobs:
                            if j not in master_data[req]: master_data[req].append(j)
                            
                next_btn = target_frame.locator("a.paginate_button.next").last
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true":
                        break
                        
                    old_keys = list(current_page_data.keys())
                    old_first_req = old_keys[0] if old_keys else ""
                    
                    try: next_btn.click(force=True)
                    except: next_btn.evaluate("node => node.click()")
                    
                    t_wait = time.time()
                    while time.time() - t_wait < 6:
                        if CANCEL_FETCH: break
                        time.sleep(0.2)
                        try:
                            chk_data = target_frame.evaluate(js_code)
                            chk_keys = list(chk_data.keys())
                            if chk_keys and chk_keys[0] != old_first_req: break
                        except: pass
                else: break

            try: browser.disconnect()
            except: pass
            
            if not master_data: return {"status": "error", "msg": "⚠️ Koi data nahi mila!"}
            return {"status": "success", "data": master_data}
    except Exception as e: return {"status": "error", "msg": str(e)}

# ==============================================================
# 5. PROCESS SELECTED REQUESTS
# ==============================================================
def process_selected_requests(selected_reqs, master_info):
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    import database as db
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Browser connect nahi ho paya!"}
            
            target_frame = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        if "Jewellery/Artefacts Received" in frame.locator("body").inner_text() or "Submitted Articles List" in frame.locator("body").inner_text():
                            target_frame = frame; break
                    except: pass
                if target_frame: break
                
            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Dashboard table nahi mili!"}

            for req in selected_reqs:
                if CANCEL_FETCH: break
                
                search_box = target_frame.locator("input[type='search']").last
                if search_box.count() > 0:
                    search_box.fill("")
                    time.sleep(0.5)
                    search_box.fill(req)
                    time.sleep(1)
                
                view_btn = target_frame.locator(f"tr:has-text('{req}')").locator("a.fa-eye, a.fa-list, a:has-text('View'), button:has-text('View')").first
                if view_btn.count() > 0:
                    try: view_btn.click(force=True)
                    except: view_btn.evaluate("node => node.click()")
                    time.sleep(2)
                    
                    target_new_frame = None
                    wait_count = 0
                    while wait_count < 10 and not target_new_frame:
                        if CANCEL_FETCH: break
                        for page in browser.contexts[0].pages:
                            for frame in [page] + page.frames:
                                try:
                                    if "Total Tag List" in frame.locator("body").inner_text() or "AHC TAG" in frame.locator("body").inner_text():
                                        target_new_frame = frame; break
                                except: pass
                            if target_new_frame: break
                        time.sleep(0.5)
                        wait_count += 1
                        
                    if target_new_frame:
                        js_code_tags = """
                        () => {
                            let tags = [];
                            let rows = document.querySelectorAll('table tbody tr');
                            for (let r of rows) {
                                let tag = r.querySelector('td:nth-child(2)')?.innerText.trim() || r.querySelector('td:nth-child(1)')?.innerText.trim();
                                let purity = r.querySelector('td:nth-child(5)')?.innerText.trim() || r.querySelector('td:nth-child(3)')?.innerText.trim();
                                let cat = r.querySelector('td:nth-child(4)')?.innerText.trim() || "";
                                if (tag && tag !== "No data available in table" && !tag.includes("Showing")) {
                                    tags.push([tag, cat, purity]);
                                }
                            }
                            return tags;
                        }
                        """
                        
                        all_tags = []
                        while True:
                            if CANCEL_FETCH: break
                            current_page_tags = target_new_frame.evaluate(js_code_tags)
                            
                            if current_page_tags:
                                for t in current_page_tags:
                                    exists = False
                                    for ext in all_tags:
                                        if ext[0] == t[0]: exists = True; break
                                    if not exists: all_tags.append(t)
                                        
                            next_btn = target_new_frame.locator("a.next, a.paginate_button.next").last
                            if next_btn.count() > 0:
                                btn_class = next_btn.get_attribute("class") or ""
                                if "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true":
                                    break
                                
                                old_first_tag = current_page_tags[0][0] if current_page_tags else ""
                                try: next_btn.click(force=True)
                                except: next_btn.evaluate("node => node.click()")
                                
                                t_wait = time.time()
                                while time.time() - t_wait < 6:
                                    if CANCEL_FETCH: break
                                    time.sleep(0.2)
                                    try:
                                        chk_data = target_new_frame.evaluate(js_code_tags)
                                        if chk_data and chk_data[0][0] != old_first_tag: break
                                    except: pass
                            else: break
                            
                        job_groups = {}
                        for tag_data in all_tags:
                            tag_str = tag_data[0]
                            possible_job = tag_str.split('-')[0]
                            if len(possible_job) >= 5 and possible_job.isdigit():
                                if possible_job not in job_groups: job_groups[possible_job] = []
                                job_groups[possible_job].append(tag_data)
                                
                        for j_id, t_list in job_groups.items():
                            db.save_scraped_job_card(j_id, t_list, request_no=req)
                            
                        close_btn = target_new_frame.locator("button.close, button:has-text('Close'), a.close").first
                        if close_btn.count() > 0:
                            try: close_btn.click(force=True)
                            except: close_btn.evaluate("node => node.click()")
                            time.sleep(1)
                        else:
                            try: target_new_frame.page.go_back()
                            except: pass
                            time.sleep(2)
                            
            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH: return {"status": "error", "msg": "Process Cancelled by User."}
            return {"status": "success", "msg": "Data successfully fetched."}
    except Exception as e: return {"status": "error", "msg": str(e)}

# ==============================================================
# 🌟 6. NEW: FETCH HUIDs FROM WEIGHING DESK PAGE (100% FIXED)
# ==============================================================
def fetch_huids_from_page(job_id):
    global CANCEL_FETCH, ACTIVE_BROWSER
    search_job_id = str(job_id).split('-L')[0] 
    print(f"🔍 Smart Fetching HUIDs/Data for Job: {search_job_id}...")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
            target_frame = None
            actual_job_card = None
            
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        text = frame.locator("body").inner_text()
                        if "Weighing Desk" in text or "tabWeight_next" in frame.content():
                            target_frame = frame
                            import re
                            match = re.search(r'Job Card\s*Number\s*:\s*(\d+)', text, re.IGNORECASE)
                            if match: actual_job_card = match.group(1).strip()
                            break
                    except: pass
                if target_frame: break
                
            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Weighing Desk page screen par load nahi hui hai."}

            js_code = """
            () => {
                let data = [];
                let rows = document.querySelectorAll('table tbody tr');
                for (let r of rows) {
                    let cells = r.querySelectorAll('td');
                    if (cells.length >= 5) {
                        let tag = cells[1].innerText.trim();
                        let matCat = cells[2].innerText.trim();
                        let itemCat = cells[3].innerText.trim();
                        let huid = cells[4].innerText.trim();
                        if (tag && tag !== "" && tag.toUpperCase() !== "AHC TAG" && !tag.includes("No data available")) {
                            data.push({ "tag": tag, "category": itemCat, "purity": matCat, "huid": (huid !== "-") ? huid : "" });
                        }
                    }
                }
                return data;
            }
            """
            
            import time
            all_data = []
            max_pages = 50 # 🔥 CRASH-PROOF: 50 page se zyada nahi jayega (Loop me atakne se bachane ke liye)
            page_count = 0
            
            while page_count < max_pages:
                if CANCEL_FETCH: break
                page_count += 1
                
                # 1. Current page ka data nikalo
                current_data = target_frame.evaluate(js_code)
                if current_data and len(current_data) > 0:
                    for item in current_data:
                        exists = False
                        for existing_item in all_data:
                            if existing_item['tag'] == item['tag']: exists = True; break
                        if not exists: all_data.append(item)
                            
                # 🚀 BUG FIX: DataTables me ID <li> par hoti hai, <a> par nahi!
                next_li = target_frame.locator("#tabWeight_next, li.paginate_button.next").first
                
                if next_li.count() > 0:
                    btn_class = next_li.get_attribute("class") or ""
                    
                    # 2. Check agar next button disabled hai (Aakhri page)
                    if "disabled" in btn_class or "disabled" in next_li.inner_html():
                        break
                        
                    # 3. Asli click karne wala link (anchor tag) dhoondo
                    next_btn = next_li.locator("a").first
                    if next_btn.count() == 0:
                        next_btn = next_li # Fallback
                        
                    old_first_tag = current_data[0]['tag'] if current_data else ""
                    
                    try: next_btn.click(force=True)
                    except: next_btn.evaluate("node => node.click()")
                    
                    # 4. Smart Wait: Tab tak wait karo jab tak naya tag na aa jaye
                    wait_start = time.time()
                    data_changed = False
                    
                    while time.time() - wait_start < 6:
                        if CANCEL_FETCH: break
                        time.sleep(0.2)
                        try:
                            check_data = target_frame.evaluate(js_code)
                            if check_data and len(check_data) > 0:
                                if check_data[0]['tag'] != old_first_tag: 
                                    data_changed = True
                                    break
                        except: pass
                    
                    # Agar 6 sec wait ke baad bhi page nahi badla (Internet band ho gaya), to loop tod do (CRASH SE BACHAO)
                    if not data_changed:
                        break
                else:
                    break # Next button hi nahi hai

            try: browser.disconnect()
            except: pass
            
            if not all_data or len(all_data) == 0: return {"status": "error", "msg": "⚠️ Table me koi Tags nahi mile!"}
            if not actual_job_card: actual_job_card = "UNKNOWN_JOB"

            if actual_job_card == search_job_id:
                huids_dict = {item['tag']: item['huid'] for item in all_data if item['huid']}
                if len(huids_dict) > 0: return {"status": "success", "data": huids_dict, "msg": f"✅ {len(huids_dict)} HUIDs fetched from {page_count} pages!"}
                else: return {"status": "error", "msg": "⚠️ HUID column khali hai!"}
            else:
                return {"status": "mismatch", "actual_job": actual_job_card, "tags_data": all_data, "msg": f"Job card mismatch!"}
    except Exception as e: return {"status": "error", "msg": f"System Error: {str(e)}"}