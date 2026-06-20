from playwright.sync_api import sync_playwright
import time
import re
import logging

# 🚀 Enterprise Logging System
logging.basicConfig(filename='app_crash.log', level=logging.ERROR, 
                    format='%(asctime)s - RECEPTION - %(levelname)s - %(message)s')

CDP_URL = "http://localhost:9222"
CANCEL_FETCH = False

# ==============================================================
# 1. SINGLE RECEPTION INJECTION (Manual Table Button Se)
# ==============================================================
def inject_single_reception_tag(job_id, tag_id, weight):
    tag_id, weight = str(tag_id).strip(), str(weight).strip()
    print(f"👻 Live Injecting Tag: {tag_id} | Weight: {weight}g | Job: {job_id}")
    
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
            job_matched = False
            for page in browser.contexts[0].pages:
                try:
                    text = page.locator("body").inner_text()
                    if job_id in text: job_matched = True; break
                except: pass
                for frame in page.frames:
                    try:
                        if job_id in frame.locator("body").inner_text(): job_matched = True; break
                    except: pass
                if job_matched: break
                
            if not job_matched:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": f"❌ Wrong Page! Site par ID '{job_id}' open nahi hai."}

            target_frame = None
            for page in browser.contexts[0].pages:
                try:
                    if page.locator("tr").filter(has=page.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                        target_frame = page; break
                except: pass
                for frame in page.frames:
                    try:
                        if frame.locator("tr").filter(has=frame.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                            target_frame = frame; break
                    except: pass
                if target_frame: break

            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' nahi mila."}

            # 🚀 STRICT MATCH FIX
            row = target_frame.locator("tr").filter(
                has=target_frame.locator("td:nth-child(2), td:nth-child(3)").get_by_text(tag_id, exact=True)
            )
            
            if row.count() > 0:
                target_row = row.first
                weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                
                if weight_input.count() == 0:
                    edit_btn = target_row.locator("[title*='Edit'], [title*='edit'], .fa-edit, .fa-pencil, a.edit, button.edit").first
                    if edit_btn.count() > 0:
                        edit_btn.evaluate("node => node.click()")
                        time.sleep(1.0)
                        weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first

                if weight_input.count() > 0:
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
                    
                    save_btn = target_row.locator("text='Save', text='Update', [title*='Save'], [title*='Update'], .fa-save").first
                    if save_btn.is_visible():
                        main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                        main_page.once("dialog", lambda dialog: dialog.accept())
                        save_btn.evaluate("node => node.click()") 
                        
                        # 🚀 SMART INTERNET WAIT
                        time.sleep(1)
                        try:
                            main_page.wait_for_load_state("networkidle", timeout=5000)
                            target_frame.wait_for_selector("table tbody tr", state="visible", timeout=5000)
                        except: pass
                        
                    try: browser.disconnect()
                    except: pass
                    return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                else: 
                    return {"status": "warning", "msg": f"🔒 Tag '{tag_id}' BIS dwara permanently lock hai."}
            else: 
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' Editable list me nahi mila."}
    except Exception as e:
        logging.error(f"Single Inject Error: {e}", exc_info=True)
        return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}


# ==============================================================
# 2. FAST DROPDOWN INJECTION 
# ==============================================================
def fast_inject_weight(job_id, tag_id, weight):
    return inject_single_reception_tag(job_id, tag_id, weight)


# ==============================================================
# 3. FULL AUTO INJECTION (Poori list ek sath)
# ==============================================================
def inject_reception_weight_ghost(job_id, job_data, delay_ms=1500):
    global CANCEL_FETCH
    CANCEL_FETCH = False
    
    if not job_data: return "⚠️ डेटाबेस खाली है।"
    print(f"👻 Auto Injection Started (Speed: {delay_ms}ms)... Job: {job_id}")

    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL)
            except: return "⚠️ ब्राउज़र ओपन नहीं है!"

            job_matched = False
            for page in browser.contexts[0].pages:
                try:
                    if job_id in page.locator("body").inner_text(): job_matched = True; break
                except: pass
                for frame in page.frames:
                    try:
                        if job_id in frame.locator("body").inner_text(): job_matched = True; break
                    except: pass
                if job_matched: break
                
            if not job_matched:
                try: browser.disconnect()
                except: pass
                return f"❌ Wrong Page! Site par ID '{job_id}' open nahi hai."

            filled_count = 0
            for item in job_data:
                if CANCEL_FETCH:
                    print("🛑 User Cancelled Auto Injection!")
                    break

                tag_id, weight = str(item[0]).strip(), str(item[1]).strip()
                
                target_frame = None
                tag_found = False

                while True:
                    for page in browser.contexts[0].pages:
                        try:
                            if page.locator("tr").filter(has=page.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                                target_frame = page; tag_found = True; break
                        except: pass
                        if not tag_found:
                            for frame in page.frames:
                                try:
                                    if frame.locator("tr").filter(has=frame.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                                        target_frame = frame; tag_found = True; break
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
                    # 🚀 STRICT MATCH FIX
                    row = target_frame.locator("tr").filter(
                        has=target_frame.locator("td:nth-child(2), td:nth-child(3)").get_by_text(tag_id, exact=True)
                    )
                    
                    if row.count() > 0:
                        target_row = row.first
                        weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                        
                        if weight_input.count() == 0:
                            edit_btn = target_row.locator("[title*='Edit'], [title*='edit'], .fa-edit, .fa-pencil, a.edit, button.edit").first
                            if edit_btn.count() > 0:
                                edit_btn.evaluate("node => node.click()")
                                time.sleep(1.0)
                                weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first

                        if weight_input.count() > 0:
                            is_disabled = weight_input.evaluate("node => node.disabled || node.readOnly")
                            current_val = str(weight_input.evaluate("node => node.value")).strip()
                            
                            try:
                                already_same = abs(float(current_val) - float(weight)) < 0.001
                            except:
                                already_same = (current_val == weight)

                            if is_disabled and already_same:
                                print(f"⏩ Exact Tag {tag_id} pehle se saved hai, skip kar rahe hain.")
                                continue 
                                
                            js_inject = f"""node => {{
                                node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                                node.removeAttribute('onpaste'); node.removeAttribute('oncopy'); 
                                node.removeAttribute('oncut'); node.removeAttribute('oncontextmenu'); 
                                node.value = '{weight}'; 
                                node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                                node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                            }}"""
                            weight_input.evaluate(js_inject)
                            
                            save_btn = target_row.locator("text='Save', text='Update', [title*='Save'], [title*='Update'], .fa-save").first
                            if save_btn.is_visible():
                                main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                                main_page.once("dialog", lambda dialog: dialog.accept())
                                save_btn.evaluate("node => node.click()") 
                                
                                # 🚀 SMART INTERNET WAIT
                                time.sleep(1.5) 
                                try:
                                    main_page.wait_for_load_state("networkidle", timeout=5000)
                                    target_frame.wait_for_selector("table tbody tr", state="visible", timeout=5000)
                                except: pass
                                
                                time.sleep(delay_ms / 1000.0)
                            
                            filled_count += 1
                        else:
                            print(f"🔒 Tag {tag_id} BIS portal par permanently lock ho chuka hai. Skipping...")
                            continue
                    else:
                        print(f"⚠️ Tag {tag_id} screen par match nahi hua, skip kar diya.")
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
# 4. DATA SCRAPING & WAIT FOR JOB CARD
# ==============================================================
def extract_id_from_page(browser):
    js_code = """
    () => {
        let text = document.body.innerText;
        let jobMatch = text.match(/Job Card No[\\s:]*(\\d+)/i);
        if (jobMatch && jobMatch[1]) { return { type: 'Job Card', id: jobMatch[1] }; }
        let reqMatch = text.match(/Request No[\\s:]*(\\d+)/i);
        if (reqMatch && reqMatch[1]) { return { type: 'Request No', id: reqMatch[1] }; }
        return null;
    }
    """
    for page in browser.contexts[0].pages:
        for frame in [page] + page.frames:
            try:
                res = frame.evaluate(js_code)
                if res: return res
            except: pass
    return None

# ==============================================================
# 🌟 100% LIVE WEB SCRAPING WITH DYNAMIC WAIT (3-MIN TIMEOUT)
# ==============================================================
def scrape_all_requests_from_main():
    global CANCEL_FETCH
    CANCEL_FETCH = False
    print("🌐 Website ke Main Dashboard se data fetch kar rahe hain...")
    
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

            js_code = """
            () => {
                let results = {};
                let rows = document.querySelectorAll('table tbody tr');
                if(rows.length === 0) return null; 
                
                let hasData = false;
                for(let r of rows) {
                    let rowText = r.innerText || "";
                    let numbers = rowText.match(/\\b\\d{8,}\\b/g);
                    
                    if (numbers && numbers.length >= 2) {
                        let req = numbers[0]; 
                        let job = numbers[1]; 
                        if(!results[req]) results[req] = [];
                        if(!results[req].includes(job)) results[req].push(job);
                        hasData = true;
                    } else if (numbers && numbers.length === 1) {
                        let job = numbers[0];
                        let req = "UNKNOWN";
                        if(!results[req]) results[req] = [];
                        if(!results[req].includes(job)) results[req].push(job);
                        hasData = true;
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
                            res = frame.evaluate(js_code)
                            if res: 
                                target_frame = frame
                                break
                        except: pass
                    if target_frame: break 
                if target_frame: break
                time.sleep(1) 

            if CANCEL_FETCH:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "🛑 Process Cancelled by User."}

            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Timeout Error!"}

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
                next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next'), a:has-text('›'), a[title*='Next']").last
                
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    is_disabled = "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true" or next_btn.get_attribute("disabled") is not None
                    
                    if not is_disabled:
                        next_btn.evaluate("node => node.click()") 
                        try:
                            target_frame.page.wait_for_load_state("networkidle", timeout=8000)
                            target_frame.wait_for_selector("table tbody tr", state="visible", timeout=10000)
                        except: pass
                        
                        wait_start = time.time()
                        while time.time() - wait_start < 10:
                            if CANCEL_FETCH: break
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state: break
                            except: pass
                            time.sleep(0.5)
                    else: break 
                else: break

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH: return {"status": "error", "msg": "🛑 Process Stopped."}
            return {"status": "success", "data": all_data}
            
    except Exception as e:
        return {"status": "error", "msg": str(e)}

def process_selected_requests(selected_reqs, master_info):
    global CANCEL_FETCH
    CANCEL_FETCH = False
    from modules import database as db
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            context = browser.contexts[0]
            total_jobs_saved = 0

            for req in selected_reqs:
                if CANCEL_FETCH: break
                jobs = master_info.get(req, [])
                for job in jobs:
                    if CANCEL_FETCH: break
                    
                    target_frame = None
                    wait_start_time = time.time()
                    
                    while time.time() - wait_start_time < 180:
                        if CANCEL_FETCH: break
                        for page in context.pages:
                            for frame in [page] + page.frames:
                                try:
                                    is_target = frame.evaluate("""() => {
                                        let text = document.body.innerText.toUpperCase();
                                        let hasTable = document.querySelectorAll('table tbody tr').length > 0;
                                        return hasTable && (text.includes('JOB CARD') || text.includes('QM JOB') || text.includes('ACTION') || text.includes('XRF') || text.includes('SUBMITTED ARTICLES'));
                                    }""")
                                    if is_target: target_frame = frame; break
                                except: pass
                            if target_frame: break
                        if target_frame: break 
                        time.sleep(1) 

                    if CANCEL_FETCH or not target_frame: continue 

                    try:
                        first_btn = target_frame.locator("a.paginate_button.first, li.first a, a:has-text('First'), a:has-text('«'), a.paginate_button:has-text('1')").first
                        if first_btn.count() > 0:
                            f_class = first_btn.get_attribute("class") or ""
                            if "disabled" not in f_class and "current" not in f_class:
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
                                if CANCEL_FETCH: break
                                if target_frame.locator("tr", has_text=job).count() > 0: break
                                time.sleep(0.5)
                        except: pass

                    job_found = False
                    row = None
                    
                    while True:
                        if CANCEL_FETCH: break
                        row = target_frame.locator("tr", has_text=job).first
                        if row.count() > 0: job_found = True; break 
                            
                        next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next'), a:has-text('›'), a[title*='Next']").last
                        if next_btn.count() > 0:
                            btn_class = next_btn.get_attribute("class") or ""
                            if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                                next_btn.evaluate("node => node.click()") 
                                p_wait = time.time()
                                while time.time() - p_wait < 10:
                                    if CANCEL_FETCH: break
                                    try:
                                        if target_frame.locator("tr", has_text=job).count() > 0 or target_frame.evaluate("""() => document.readyState === 'complete'"""): break
                                    except: pass
                                    time.sleep(0.5)
                            else: break
                        else: break
                            
                    if CANCEL_FETCH or not job_found:
                        if search_box.count() > 0:
                            try: search_box.fill("")
                            except: pass
                        continue 

                    view_btn = row.locator("a").last 

                    try:
                        with context.expect_page(timeout=10000) as new_page_info:
                            view_btn.evaluate("node => { node.setAttribute('target', '_blank'); node.click(); }")
                        new_page = new_page_info.value
                    except Exception as e: continue

                    target_new_frame = None
                    tab_wait_start = time.time()
                    
                    while time.time() - tab_wait_start < 180:
                        if CANCEL_FETCH: break
                        for page_tab in context.pages:
                            for frame in [page_tab] + page_tab.frames:
                                try:
                                    if "TAG ID" in frame.locator("body").inner_text().upper():
                                        target_new_frame = frame; break
                                except: pass
                            if target_new_frame: break
                        if target_new_frame: break 
                        time.sleep(1) 
                        
                    if CANCEL_FETCH:
                        try: new_page.close()
                        except: pass
                        continue

                    if not target_new_frame: target_new_frame = new_page 

                    try:
                        target_new_frame.wait_for_load_state("networkidle", timeout=5000)
                        target_new_frame.wait_for_selector("table tbody tr", state="visible", timeout=15000)
                    except: pass

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
                                let catIdx = headers.findIndex(h => h.includes('ITEM CATEGORY'));
                                let purIdx = headers.findIndex(h => h.includes('DECLARED PURITY'));
                                
                                if(tagIdx === -1) continue;
                                
                                for (let r of rows) {
                                    let cells = r.querySelectorAll('td');
                                    if (cells.length > tagIdx) {
                                        let tag = cells[tagIdx].innerText.trim();
                                        if (!tag || tag.toUpperCase().includes('TAG')) continue;
                                        
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
                        res = target_new_frame.evaluate(js_code_tags)
                        if res == previous_page_data: break
                            
                        if res and len(res) > 0:
                            for item in res:
                                if item not in all_scraped_items:
                                    all_scraped_items.append(item)
                                    
                        previous_page_data = res

                        next_btn = target_new_frame.locator("a#tab_logic_next, a.paginate_button.next, li.next a, a:has-text('Next'), a:has-text('›'), a[title*='Next']").last
                        if next_btn.count() > 0:
                            btn_class = next_btn.get_attribute("class") or ""
                            if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                                next_btn.evaluate("node => node.click()")
                                t_wait = time.time()
                                while time.time() - t_wait < 10:
                                    if CANCEL_FETCH: break
                                    try:
                                        if target_new_frame.evaluate(js_code_tags) != previous_page_data: break
                                    except: pass
                                    time.sleep(0.5)
                            else: break
                        else: break 

                    try: new_page.close()
                    except: pass

                    if all_scraped_items and not CANCEL_FETCH:
                        db.save_scraped_job_card(job, all_scraped_items, request_no=req)
                        total_jobs_saved += 1

                    if target_frame and search_box.count() > 0:
                        try: search_box.fill("")
                        except: pass
                        time.sleep(0.5)
                        
                    try: context.pages[0].bring_to_front()
                    except: pass

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH: return {"status": "error", "msg": f"🛑 Cancelled! Lakin pehle ke {total_jobs_saved} Jobs database me save ho chuke hain."}
            if total_jobs_saved == 0: return {"status": "error", "msg": "⚠️ Data Fetch Fail! Ya toh page theek se load nahi hua, ya tags available nahi hain."}
                
            return {"status": "success", "msg": f"✅ Website se Data Fetch ho gaya! {total_jobs_saved} Jobs Database mein save ho gaye."}
            
    except Exception as e:
        return {"status": "error", "msg": str(e)}

# ==============================================================
# 🌟 5. NEW: SCRAPE REQUESTS FROM XRF PAGE (BACKUP FETCH)
# ==============================================================
def scrape_all_requests_from_xrf():
    global CANCEL_FETCH
    CANCEL_FETCH = False
    print("🌐 XRF Backup Page se data fetch kar rahe hain...")
    
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

            js_code = """
            () => {
                let results = {};
                let rows = document.querySelectorAll('table tbody tr');
                if(rows.length === 0) return null; 
                
                let hasData = false;
                for(let r of rows) {
                    let rowText = r.innerText || "";
                    let numbers = rowText.match(/\\b\\d{8,}\\b/g) || [];
                    
                    if (numbers.length >= 2) {
                        let req = String(numbers[0]).trim(); 
                        let job = String(numbers[1]).trim(); 
                        if(!results[req]) results[req] = [];
                        if(!results[req].includes(job)) results[req].push(job);
                        hasData = true;
                    } else if (numbers.length === 1) {
                        let job = String(numbers[0]).trim();
                        let req = "UNKNOWN";
                        if(!results[req]) results[req] = [];
                        if(!results[req].includes(job)) results[req].push(job);
                        hasData = true;
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
                            res = frame.evaluate(js_code)
                            if res: target_frame = frame; break
                        except: pass
                    if target_frame: break
                if target_frame: break 
                time.sleep(1) 

            if CANCEL_FETCH:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "🛑 Process Cancelled by User."}

            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Timeout Error: Website par XRF Table Data load nahi hua!"}

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
                next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next'), a:has-text('›'), a[title*='Next']").last
                
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    is_disabled = "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true" or next_btn.get_attribute("disabled") is not None
                    
                    if not is_disabled:
                        next_btn.evaluate("node => node.click()") 
                        wait_start = time.time()
                        while time.time() - wait_start < 10:
                            if CANCEL_FETCH: break
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state: break
                            except: pass
                            time.sleep(0.5)
                    else: break 
                else: break

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH: return {"status": "error", "msg": "🛑 Process Stopped."}
            return {"status": "success", "data": all_data}
            
    except Exception as e:
        return {"status": "error", "msg": str(e)}