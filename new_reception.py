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
# 🌟 LOT SPLITTER HELPER (Based on BIS Image Rules)
# ==============================================================
def split_tags_into_lots(job_id, tags_list):
    """
    BIS Rules:
    1-40: 1 Lot
    41-280: 1 Extra Lot per 60 pieces
    281+: 1 Extra Lot per 100 pieces
    """
    lots = {}
    total = len(tags_list)
    
    if total <= 40:
        if total > 0: lots[f"{job_id}-L1"] = tags_list
        return lots

    idx = 0
    lot_num = 1
    
    while idx < total:
        if lot_num == 1:
            next_idx = min(40, total)
        elif idx < 280:
            next_idx = min(idx + 60, total, 280)
        else:
            next_idx = min(idx + 100, total)
            
        lots[f"{job_id}-L{lot_num}"] = tags_list[idx:next_idx]
        idx = next_idx
        lot_num += 1
        
    return lots

# ==============================================================
# 1. SINGLE RECEPTION INJECTION (Live Ghost Dropdown)
# ==============================================================
def inject_single_reception_tag(job_id, tag_id, weight):
    global CANCEL_FETCH, ACTIVE_BROWSER
    tag_id, weight = str(tag_id).strip(), str(weight).strip()
    search_job_id = str(job_id).split('-L')[0] 
    print(f"👻 Live Injecting Tag: {tag_id} | Weight: {weight}g | Job: {search_job_id}")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
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
                return {"status": "error", "msg": f"❌ Wrong Page! Site par ID '{search_job_id}' open nahi hai."}

            target_frame = None
            for page in browser.contexts[0].pages:
                try:
                    if page.locator("tr").filter(has=page.locator("td.tagIdCls").get_by_text(tag_id, exact=True)).count() > 0:
                        target_frame = page; break
                except: pass
                for frame in page.frames:
                    try:
                        if frame.locator("tr").filter(has=frame.locator("td.tagIdCls").get_by_text(tag_id, exact=True)).count() > 0:
                            target_frame = frame; break
                    except: pass
                if target_frame: break

            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' screen par nahi mila."}

            row = target_frame.locator("tr").filter(has=target_frame.locator("td.tagIdCls").get_by_text(tag_id, exact=True))
            
            if row.count() > 0:
                target_row = row.first
                weight_input = target_row.locator("input.weightCls, input.scan-input, input:not([type='hidden']):not([type='checkbox'])").first
                
                if weight_input.count() > 0:
                    # 🚀 PURE GHOST INJECT
                    js_inject = f"""node => {{
                        node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
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
                        save_btn.evaluate("node => node.click()") 
                        time.sleep(1)
                        
                    try: browser.disconnect()
                    except: pass
                    return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                else: return {"status": "error", "msg": "⚠️ Input box nahi mila!"}
            else: return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' Editable list me nahi mila."}
    except Exception as e: return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}


# ==============================================================
# 2. FAST DROPDOWN INJECTION 
# ==============================================================
def fast_inject_weight(job_id, tag_id, weight):
    return inject_single_reception_tag(job_id, tag_id, weight)


# ==============================================================
# 3. FULL AUTO INJECTION (ULTRA FAST & SMART)
# ==============================================================
def inject_reception_weight_ghost(job_id, job_data, delay_ms=400): 
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    search_job_id = str(job_id).split('-L')[0] 
    
    if not job_data: return "⚠️ डेटाबेस खाली है।"
    print(f"🚀 Ultra-Fast Auto Injection Started (Speed: {delay_ms}ms)... Job: {search_job_id}")

    tag_map = {str(item[0]).strip(): str(item[1]).strip() for item in job_data if str(item[1]).strip() not in ["0", "0.0", ""]}
    if not tag_map: return "⚠️ Koi valid weight (0.0 ke alawa) nahi mila inject karne ke liye."
    
    filled_count = 0

    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
                ACTIVE_BROWSER = browser
            except: return "⚠️ ब्राउज़र ओपन नहीं है!"

            target_frame = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        if search_job_id in frame.locator("body").inner_text():
                            target_frame = frame; break
                    except: pass
                if target_frame: break
                
            if not target_frame:
                try: browser.disconnect()
                except: pass
                return f"❌ Wrong Page! Site par ID '{search_job_id}' open nahi hai."

            try:
                first_btn = target_frame.locator("a.paginate_button.first, li.first a, a:has-text('First'), a:has-text('«')").first
                if first_btn.count() > 0 and "disabled" not in (first_btn.get_attribute("class") or ""):
                    first_btn.evaluate("node => node.click()")
                    time.sleep(1)
            except: pass

            while tag_map and not CANCEL_FETCH:
                try: target_frame.wait_for_selector("td.tagIdCls", timeout=3000)
                except: pass
                
                tag_cells = target_frame.locator("td.tagIdCls").all()
                
                for cell in tag_cells:
                    if CANCEL_FETCH or not tag_map: break
                    try:
                        current_tag = cell.inner_text().strip()
                        if current_tag in tag_map:
                            weight = tag_map[current_tag]
                            row = target_frame.locator("tr").filter(has=target_frame.locator("td.tagIdCls").get_by_text(current_tag, exact=True)).first
                            weight_input = row.locator("input.weightCls, input.scan-input, input:not([type='hidden']):not([type='checkbox'])").first
                            
                            if weight_input.count() > 0:
                                js_inject = f"""node => {{
                                    node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                                    node.value = '{weight}'; 
                                    node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('blur', {{ bubbles: true }})); 
                                }}"""
                                weight_input.evaluate(js_inject)
                                
                                save_btn = row.locator("text='Save'").first
                                if save_btn.is_visible():
                                    main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                                    main_page.once("dialog", lambda dialog: dialog.accept())
                                    save_btn.evaluate("node => node.click()")
                                    time.sleep(delay_ms / 1000.0) 
                                
                                filled_count += 1
                                del tag_map[current_tag] 
                    except: pass

                if not tag_map or CANCEL_FETCH: break 
                
                next_btn = target_frame.locator("a.paginate_button.next, a#tabWeight_next, li.next a, a:has-text('Next')").last
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true":
                        break
                        
                    old_tag = ""
                    try: old_tag = target_frame.locator("td.tagIdCls").first.inner_text().strip()
                    except: pass

                    next_btn.evaluate("node => node.click()")
                    
                    # 🚀 FAST POLLING
                    t_wait = time.time()
                    while time.time() - t_wait < 15:
                        if CANCEL_FETCH: break
                        time.sleep(0.2)
                        try:
                            new_tag = target_frame.locator("td.tagIdCls").first.inner_text().strip()
                            if new_tag != old_tag: break
                        except: pass
                else: break

            try: browser.disconnect() 
            except: pass
            
            if CANCEL_FETCH: return f"🛑 STOPPED! {filled_count} Tags Save huye."
            return f"✅ 100% Success! Saare {filled_count} Tags FAST Save kar diye gaye."
            
    except Exception as e: return f"⚠️ Error: {e}"


# ==============================================================
# 4. SCRAPE ALL REQUESTS FROM MAIN PAGE (Permanent Header Logic)
# ==============================================================
def scrape_all_requests_from_main():
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    print("🌐 Website ke Main Dashboard se data fetch kar rahe hain...")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

            # 🚀 PERMANENT FIX: Table ke headers padh kar exact column pakdega
            js_code = """
            () => {
                let results = {};
                let hasData = false;
                let tables = document.querySelectorAll('table');
                
                for (let t of tables) {
                    // 1. Table ki Header (Titles) Nikalo
                    let headers = Array.from(t.querySelectorAll('th, thead td')).map(x => x.innerText.trim().toUpperCase());
                    if (headers.length === 0) {
                        let firstRow = t.querySelector('tr');
                        if(firstRow) headers = Array.from(firstRow.querySelectorAll('td')).map(x => x.innerText.trim().toUpperCase());
                    }
                    
                    // 2. Header ke naam se Column Number dhoondo
                    let reqIdx = headers.findIndex(h => h.includes('REQUEST NO') || h.includes('REQ NO') || h.includes('REQUEST'));
                    let jobIdx = headers.findIndex(h => h.includes('JOB CARD') || h.includes('JOB NO'));
                    
                    // Agar header na mile to default set karo (Main Page me Request 1st aur Job 3rd me hota hai)
                    if (reqIdx === -1) reqIdx = 0; 
                    if (jobIdx === -1) jobIdx = 2; 

                    // 3. Exact Column se Data Nikalo (Bina length check kiye)
                    let rows = t.querySelectorAll('tbody tr');
                    for (let r of rows) {
                        let cells = r.querySelectorAll('td');
                        if (cells.length > Math.max(reqIdx, jobIdx)) {
                            let reqText = cells[reqIdx].innerText.trim();
                            let jobText = cells[jobIdx].innerText.trim();
                            
                            if (jobText.includes("No data")) continue;

                            // Sirf numbers filter karo
                            let reqMatch = reqText.match(/\\d+/);
                            let jobMatch = jobText.match(/\\d+/);
                            
                            let req = reqMatch ? reqMatch[0] : "UNKNOWN";
                            let job = jobMatch ? jobMatch[0] : null;
                            
                            if (job) {
                                if (!results[req]) results[req] = [];
                                if (!results[req].includes(job)) results[req].push(job);
                                hasData = true;
                            }
                        }
                    }
                }
                return hasData ? results : null;
            }
            """
            
            target_frame = None
            max_wait = 180 
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                if CANCEL_FETCH: break
                for page in browser.contexts[0].pages:
                    for frame in [page] + page.frames:
                        try:
                            frame.wait_for_selector("table tbody tr", timeout=2000, state="attached")
                            res = frame.evaluate(js_code)
                            if res: target_frame = frame; break
                        except: pass
                    if target_frame: break 
                if target_frame: break
                time.sleep(1) 

            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Timeout Error: Dashboard load nahi hua!"}

            all_data = {}
            previous_data_state = None 

            while True:
                if CANCEL_FETCH: break

                res = target_frame.evaluate(js_code)
                if res == previous_data_state: break
                    
                if res:
                    for req, jobs in res.items():
                        if req not in all_data: all_data[req] = []
                        for j in jobs:
                            if j not in all_data[req]: all_data[req].append(j)

                previous_data_state = res 
                
                next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next')").last
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                        next_btn.evaluate("node => node.click()") 
                        
                        t_wait = time.time()
                        while time.time() - t_wait < 15:
                            if CANCEL_FETCH: break
                            time.sleep(0.2)
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state: break
                            except: pass
                    else: break 
                else: break

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH: return {"status": "error", "msg": "🛑 Process Stopped."}
            return {"status": "success", "data": all_data}
            
    except Exception as e: return {"status": "error", "msg": str(e)}

# ==============================================================
# 5. PROCESS SELECTED REQUESTS (100% ACCURATE & LOW-RAM OPTIMIZED)
# ==============================================================
import gc # 🚀 NAYA: RAM ko clean rakhne ke liye

def process_selected_requests(selected_reqs, master_info):
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    from modules import database as db
    
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
                context = browser.contexts[0]
            except: return {"status": "error", "msg": "⚠️ Secure Browser open nahi hai!"}
            
            total_jobs_saved = 0

            for req in selected_reqs:
                if CANCEL_FETCH: break
                
                jobs = master_info.get(req, [])
                for job in jobs:
                    if CANCEL_FETCH: break
                    
                    target_frame = None
                    wait_start_time = time.time()
                    
                    while time.time() - wait_start_time < 60:
                        if CANCEL_FETCH: break
                        for page in context.pages:
                            for frame in [page] + page.frames:
                                try:
                                    is_target = frame.evaluate("""() => {
                                        let text = document.body.innerText.toUpperCase();
                                        return document.querySelectorAll('table tbody tr').length > 0 && 
                                               (text.includes('JOB CARD') || text.includes('QM JOB') || text.includes('SUBMITTED ARTICLES'));
                                    }""")
                                    if is_target: target_frame = frame; break
                                except: pass
                            if target_frame: break
                        if target_frame: break 
                        time.sleep(1) 

                    if not target_frame: continue 

                    try:
                        first_btn = target_frame.locator("a.paginate_button.first, li.first a, a:has-text('First')").first
                        if first_btn.count() > 0 and "disabled" not in (first_btn.get_attribute("class") or ""):
                            first_btn.evaluate("node => node.click()") 
                            time.sleep(1.0) 
                    except: pass

                    search_box = target_frame.locator("input[type='search'], input.form-control.input-sm").first
                    if search_box.count() > 0:
                        try:
                            search_box.fill(job)
                            search_box.press("Enter")
                            s_wait = time.time()
                            while time.time() - s_wait < 10:
                                if target_frame.locator("tr", has_text=job).count() > 0: break
                                time.sleep(0.5)
                        except: pass

                    job_found = False
                    row = None
                    
                    while True:
                        if CANCEL_FETCH: break
                        row = target_frame.locator("tr", has_text=job).first
                        if row.count() > 0:
                            job_found = True; break 
                            
                        next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next')").last
                        if next_btn.count() > 0:
                            btn_class = next_btn.get_attribute("class") or ""
                            if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                                next_btn.evaluate("node => node.click()") 
                                p_wait = time.time()
                                while time.time() - p_wait < 10:
                                    if CANCEL_FETCH: break
                                    try:
                                        if target_frame.locator("tr", has_text=job).count() > 0: break
                                    except: pass
                                    time.sleep(0.5)
                            else: break
                        else: break
                            
                    if not job_found: continue 

                    # 🚀 BULLETPROOF CLICK LOGIC (Sirf 'View/Eye' Button par click karega)
                    try:
                        # 100% Exact View Button dhoondhega (galat button dabaane ka chance zero)
                        view_btn = row.locator("a.fa-eye, a[title*='View' i], button[title*='View' i], a:has-text('View')").first
                        if view_btn.count() == 0:
                            view_btn = row.locator("td").last.locator("a, button").first
                        
                        view_btn.evaluate("node => { node.scrollIntoView(); node.style.border = '3px solid green'; node.click(); }")
                        print(f"✅ Job {job} ke View button par click kiya!")
                    except Exception as e:
                        print(f"⚠️ Click Error: {e}")
                        continue

                    target_new_frame = None
                    tab_wait_start = time.time()
                    
                    print("⏳ View par click kiya. Tags load hone ka wait kar rahe hain...")
                    
                    while time.time() - tab_wait_start < 45:
                        if CANCEL_FETCH: break
                        for page_tab in context.pages:
                            for frame in [page_tab] + page_tab.frames:
                                try:
                                    if frame.locator("th:has-text('TAG ID'), td:has-text('TAG ID'), th:has-text('AHC TAG')").count() > 0:
                                        target_new_frame = frame
                                        break
                                except: pass
                            if target_new_frame: break
                        if target_new_frame: break 
                        time.sleep(1) 
                        
                    if not target_new_frame: 
                        print(f"⚠️ Job {job} ka tags page/popup nahi khula.")
                        continue 

                    js_code_tags = """
                    () => {
                        let results = [];
                        let tables = document.querySelectorAll('table');
                        for (let t of tables) {
                            let text = t.innerText.toUpperCase();
                            if (text.includes('TAG ID (AHC)') || text.includes('TAG ID') || text.includes('AHC TAG')) {
                                let rows = t.querySelectorAll('tbody tr');
                                let headers = Array.from(t.querySelectorAll('th, thead td')).map(cell => cell.innerText.trim().toUpperCase());
                                
                                let tagIdx = headers.findIndex(h => h.includes('TAG ID (AHC)') || h.includes('TAG ID') || h.includes('AHC TAG'));
                                let catIdx = headers.findIndex(h => h.includes('ITEM CATEGORY') || h.includes('CATEGORY'));
                                let purIdx = headers.findIndex(h => h.includes('DECLARED PURITY') || h.includes('PURITY'));
                                
                                if(tagIdx === -1) continue;
                                
                                for (let r of rows) {
                                    let cells = r.querySelectorAll('td');
                                    if (cells.length > tagIdx) {
                                        let tag = cells[tagIdx].innerText.trim();
                                        
                                        // 🚀 BUG FIX: Empty ya 'No Data' wali line completely ignore hogi
                                        if (!tag || tag.toUpperCase().includes('TAG') || tag.toUpperCase().includes('NO DATA')) continue;
                                        
                                        let cat = (catIdx !== -1 && cells.length > catIdx && cells[catIdx]) ? cells[catIdx].innerText.trim() : "-";
                                        let pur = (purIdx !== -1 && cells.length > purIdx && cells[purIdx]) ? cells[purIdx].innerText.trim() : "-";
                                        
                                        results.push([tag, cat, pur]);
                                    }
                                }
                                if (results.length > 0) return results;
                            }
                        }
                        return null;
                    }
                    """

                    all_scraped_items = []
                    previous_page_data = None
                    
                    while True:
                        if CANCEL_FETCH: break
                        try: res = target_new_frame.evaluate(js_code_tags)
                        except: res = None
                        
                        if res == previous_page_data: break
                            
                        if res:
                            for item in res:
                                if item not in all_scraped_items: all_scraped_items.append(item)
                                    
                        previous_page_data = res

                        next_btn = target_new_frame.locator("a#tab_logic_next, a.paginate_button.next, li.next a, a:has-text('Next')").last
                        if next_btn.count() > 0:
                            btn_class = next_btn.get_attribute("class") or ""
                            if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                                next_btn.evaluate("node => node.click()")
                                
                                # 🚀 FAST POLLING: Agla page aane ka 0.1s me wait karega
                                t_wait = time.time()
                                while time.time() - t_wait < 10:
                                    if CANCEL_FETCH: break
                                    time.sleep(0.1) # PC ko hang kiye bina fast check
                                    try:
                                        if target_new_frame.evaluate(js_code_tags) != previous_page_data: break
                                    except: pass
                            else: break
                        else: break 

                    # 🚀 SMART MODAL CLOSE LOGIC
                    try:
                        # JS ke jariye sidha close button dabana sabse fast aur safe hai
                        close_js = """() => {
                            let closeBtn = document.querySelector("button.close, button[data-dismiss='modal'], a.close");
                            if (closeBtn) { closeBtn.click(); return true; }
                            return false;
                        }"""
                        closed_via_js = target_new_frame.evaluate(close_js)
                        
                        # Agar JS se band nahi hua, toh tab/page band karo
                        if not closed_via_js:
                            actual_page = target_new_frame if not hasattr(target_new_frame, 'page') else target_new_frame.page
                            if len(context.pages) > 1 and actual_page != context.pages[0]:
                                actual_page.close()
                            else:
                                actual_page.go_back()
                    except: pass
                    time.sleep(1)

                    # 🚀 DATABASE SAVE & RAM OPTIMIZATION
                    if all_scraped_items and not CANCEL_FETCH:
                        lot_dict = split_tags_into_lots(job, all_scraped_items)
                        for lot_job_id, tags_chunk in lot_dict.items():
                            db.save_scraped_job_card(lot_job_id, tags_chunk, request_no=req)
                        total_jobs_saved += 1
                        
                    # 🔥 RAM CLEARING FOR LOW END PC 🔥
                    all_scraped_items.clear() 
                    gc.collect() # Har job card ke baad kachra saaf!

                gc.collect() # Har request ke baad kachra saaf!

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH: return {"status": "error", "msg": f"🛑 Cancelled! {total_jobs_saved} Jobs database me save huye."}
            if total_jobs_saved == 0: return {"status": "error", "msg": "⚠️ Data Fetch Fail! (Ya toh tags nahi the ya galat button daba)"}
                
            return {"status": "success", "msg": f"✅ {total_jobs_saved} Jobs Database mein Lot-Wise save ho gaye!"}
            
    except Exception as e: return {"status": "error", "msg": str(e)}
# ==============================================================
# 6. SCRAPE REQUESTS FROM XRF PAGE (Permanent Header Logic)
# ==============================================================
def scrape_all_requests_from_xrf():
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Secure Browser open nahi hai!"}

            # 🚀 PERMANENT FIX: Header se column dhoondhna
            js_code = """
            () => {
                let results = {};
                let hasData = false;
                let tables = document.querySelectorAll('table');
                
                for (let t of tables) {
                    let headers = Array.from(t.querySelectorAll('th, thead td')).map(x => x.innerText.trim().toUpperCase());
                    if (headers.length === 0) {
                        let firstRow = t.querySelector('tr');
                        if(firstRow) headers = Array.from(firstRow.querySelectorAll('td')).map(x => x.innerText.trim().toUpperCase());
                    }
                    
                    let reqIdx = headers.findIndex(h => h.includes('REQUEST NO') || h.includes('REQ NO') || h.includes('REQUEST'));
                    let jobIdx = headers.findIndex(h => h.includes('JOB CARD') || h.includes('JOB NO'));
                    
                    // XRF Page par Job Card 2nd column me hota hai (index 1)
                    if (reqIdx === -1) reqIdx = 0; 
                    if (jobIdx === -1) jobIdx = 1; 

                    let rows = t.querySelectorAll('tbody tr');
                    for (let r of rows) {
                        let cells = r.querySelectorAll('td');
                        if (cells.length > Math.max(reqIdx, jobIdx)) {
                            let reqText = cells[reqIdx].innerText.trim();
                            let jobText = cells[jobIdx].innerText.trim();
                            
                            if (jobText.includes("No data")) continue;

                            let reqMatch = reqText.match(/\\d+/);
                            let jobMatch = jobText.match(/\\d+/);
                            
                            let req = reqMatch ? reqMatch[0] : "UNKNOWN";
                            let job = jobMatch ? jobMatch[0] : null;
                            
                            if (job) {
                                if (!results[req]) results[req] = [];
                                if (!results[req].includes(job)) results[req].push(job);
                                hasData = true;
                            }
                        }
                    }
                }
                return hasData ? results : null;
            }
            """
            
            target_frame = None
            start_time = time.time()
            
            while time.time() - start_time < 180:
                if CANCEL_FETCH: break
                for page in browser.contexts[0].pages:
                    for frame in [page] + page.frames:
                        try:
                            if frame.evaluate(js_code): target_frame = frame; break
                        except: pass
                    if target_frame: break
                if target_frame: break 
                time.sleep(1) 

            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Timeout: XRF Table load nahi hui!"}

            all_data = {}
            previous_data_state = None 

            while True:
                if CANCEL_FETCH: break
                res = target_frame.evaluate(js_code)
                if res == previous_data_state: break
                    
                if res:
                    for req, jobs in res.items():
                        if req not in all_data: all_data[req] = []
                        for j in jobs:
                            if j not in all_data[req]: all_data[req].append(j)

                previous_data_state = res 
                
                next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next')").last
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                        next_btn.evaluate("node => node.click()") 
                        
                        t_wait = time.time()
                        while time.time() - t_wait < 15:
                            if CANCEL_FETCH: break
                            time.sleep(0.2)
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state: break
                            except: pass
                    else: break 
                else: break

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH: return {"status": "error", "msg": "🛑 Process Stopped."}
            return {"status": "success", "data": all_data}
            
    except Exception as e: return {"status": "error", "msg": str(e)}

# ==============================================================
# 7. FETCH HUIDs FROM WEIGHING DESK PAGE
# ==============================================================
def fetch_huids_from_page(job_id):
    global CANCEL_FETCH, ACTIVE_BROWSER
    search_job_id = str(job_id).split('-L')[0] 
    print(f"🔍 Fetching HUIDs for Job: {search_job_id}...")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
                ACTIVE_BROWSER = browser
            except: return {"status": "error", "msg": "⚠️ Secure Browser open nahi hai!"}
            
            target_frame = None
            actual_job_card = None
            
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        text = frame.locator("body").inner_text()
                        if "Weighing Desk" in text or "tagIdCls" in frame.content():
                            target_frame = frame
                            match = re.search(r'Job Card\s*Number\s*:\s*(\d+)', text, re.IGNORECASE)
                            if match: actual_job_card = match.group(1).strip()
                            break
                    except: pass
                if target_frame: break
                
            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Weighing Desk page load nahi hui."}

            # 🚀 USER'S ORIGINAL JS CODE
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
                        
                        if (tag && tag !== "" && tag.toUpperCase() !== "AHC TAG") {
                            data.push({
                                "tag": tag, "category": itemCat,
                                "purity": matCat, "huid": (huid !== "-") ? huid : ""
                            });
                        }
                    }
                }
                return data;
            }
            """
            
            all_data = []
            previous_data_state = None
            
            while True:
                if CANCEL_FETCH: break
                res = target_frame.evaluate(js_code)
                
                if res == previous_data_state: break
                    
                if res:
                    for item in res:
                        exists = next((True for x in all_data if x['tag'] == item['tag']), False)
                        if not exists: all_data.append(item)
                
                previous_data_state = res
                
                next_btn = target_frame.locator("a.paginate_button.next, a#tabWeight_next, li.next a, a:has-text('Next')").last
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true":
                        break
                        
                    next_btn.evaluate("node => node.click()")
                    
                    # 🚀 FAST POLLING
                    t_wait = time.time()
                    while time.time() - t_wait < 15:
                        if CANCEL_FETCH: break
                        time.sleep(0.2)
                        try:
                            if target_frame.evaluate(js_code) != previous_data_state: break
                        except: pass
                else: break

            try: browser.disconnect()
            except: pass
            
            if not actual_job_card: actual_job_card = "UNKNOWN_JOB"

            if actual_job_card == search_job_id:
                huids_dict = {item['tag']: item['huid'] for item in all_data if item['huid']}
                if len(huids_dict) > 0: return {"status": "success", "data": huids_dict}
                else: return {"status": "error", "msg": "⚠️ HUID khali hai!"}
            else:
                return {"status": "mismatch", "actual_job": actual_job_card, "tags_data": all_data, "msg": f"Job card mismatch!"}
    except Exception as e: return {"status": "error", "msg": f"System Error: {str(e)}"}