from playwright.sync_api import sync_playwright
import time
import re
import logging

# 🚀 Enterprise Logging System
logging.basicConfig(filename='app_crash.log', level=logging.ERROR, 
                    format='%(asctime)s - RECEPTION - %(levelname)s - %(message)s')

# Playwright ke liye local browser ka URL
CDP_URL = "http://localhost:9222"

# 🚀 GLOBAL CANCEL SWITCH (Process Rokne ke liye)
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

            # 🚀 THE 100% STRICT MATCH FIX
            row = target_frame.locator("tr").filter(
                has=target_frame.locator("td:nth-child(2), td:nth-child(3)").get_by_text(tag_id, exact=True)
            )
            
            if row.count() > 0:
                target_row = row.first
                weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                
                # 🚀 NAYA FIX: Agar Input box gayab hai, toh Edit button dhoondho
                if weight_input.count() == 0:
                    edit_btn = target_row.locator("[title*='Edit'], [title*='edit'], .fa-edit, .fa-pencil, a.edit, button.edit").first
                    if edit_btn.count() > 0:
                        edit_btn.evaluate("node => node.click()")
                        time.sleep(1.0)
                        weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first

                if weight_input.count() > 0:
                    # 🚀 JABARDASTI LOCK TODNE WALA JS HACK
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
                        time.sleep(1)
                        
                    try: browser.disconnect()
                    except: pass
                    return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                else: 
                    return {"status": "error", "msg": "⚠️ Input box ya Edit button dono nahi mile!"}
            else: 
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' Editable list me nahi mila."}
    except Exception as e:
        logging.error(f"Single Inject Error: {e}", exc_info=True)
        return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}


# ==============================================================
# 2. FAST DROPDOWN INJECTION 
# ==============================================================
def fast_inject_weight(job_id, tag_id, weight):
    # Fast Injector ko bhi same strictly Single wale logic par point kar diya
    return inject_single_reception_tag(job_id, tag_id, weight)


# ==============================================================
# 2. FAST DROPDOWN INJECTION 
# ==============================================================
def fast_inject_weight(job_id, tag_id, weight):
    tag_id, weight = str(tag_id).strip(), str(weight).strip()
    print(f"🚀 Fast Dropdown Inject: Tag: {tag_id} | Wt: {weight}g | Job: {job_id}")
    
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
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
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' list me nahi mila."}

            row = target_frame.locator("tr").filter(has=target_frame.locator("td").get_by_text(tag_id, exact=True))
            
            if row.count() > 0:
                weight_input = row.first.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
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
                    
                    save_btn = row.first.locator("text='Save'").first
                    if save_btn.is_visible():
                        main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                        main_page.once("dialog", lambda dialog: dialog.accept())
                        save_btn.evaluate("node => node.click()") # JS Click lagaya
                        time.sleep(1)
                        
                    try: browser.disconnect()
                    except: pass
                    return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                else: return {"status": "error", "msg": "⚠️ Input box nahi mila!"}
            else: return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' list me nahi mila."}
    except Exception as e:
        logging.error(f"Fast Inject Error: {e}", exc_info=True)
        return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}


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
                # 🚀 ENTERPRISE CANCEL SWITCH CHECK
                if CANCEL_FETCH:
                    print("🛑 User Cancelled Auto Injection!")
                    break

                tag_id, weight = str(item[0]).strip(), str(item[1]).strip()
                
                target_frame = None
                tag_found = False

                # 🚀 SMART PAGINATION LOOP: Tag dhundhne ke liye Next page par jana
                while True:
                    # 1. Pehle current page/frame par tag dhundho
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

                    if tag_found:
                        break # Tag mil gaya, search loop se bahar niklo

                    # 2. Agar tag nahi mila, toh 'Next' button dhundho aur JS Click maaro
                    next_btn_clicked = False
                    for page in browser.contexts[0].pages:
                        frames_to_check = [page] + page.frames
                        for f in frames_to_check:
                            try:
                                # Screenshot ke hisab se exact locators add kiye hain
                                next_btn = f.locator("a.paginate_button.next, a#tabWeight_next, li.next a, a:has-text('Next'), a:has-text('›')").last
                                if next_btn.count() > 0:
                                    btn_class = next_btn.get_attribute("class") or ""
                                    is_disabled = "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true" or next_btn.get_attribute("disabled") is not None
                                    
                                    if not is_disabled:
                                        next_btn.evaluate("node => node.click()") # 🚀 JS Force Click
                                        time.sleep(1.2) # Agla page load hone ka wait (1.2 sec)
                                        next_btn_clicked = True
                                        break
                            except: pass
                        if next_btn_clicked: break

                    # Agar 'Next' button disable hai ya nahi mila (aakhri page aa gaya)
                    if not next_btn_clicked:
                        break

                if not target_frame or not tag_found: 
                    print(f"⚠️ Alert: Tag {tag_id} kisi bhi page par nahi mila, skip kar rahe hain.")
                    continue

                try:
                    # 🚀 THE 100% STRICT MATCH FIX
                    # S.No. (Column 1) ko ignore karega. Sirf Column 2 aur 3 me exact Tag match karega.
                    row = target_frame.locator("tr").filter(
                        has=target_frame.locator("td:nth-child(2), td:nth-child(3)").get_by_text(tag_id, exact=True)
                    )
                    
                    if row.count() > 0:
                        target_row = row.first
                        weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                        
                        if weight_input.count() > 0:
                            # 🚀 CHECK IF ALREADY SAVED (WITH STRICT MATCH)
                            is_disabled = weight_input.evaluate("node => node.disabled || node.readOnly")
                            current_val = str(weight_input.evaluate("node => node.value")).strip()
                            
                            try:
                                already_same = abs(float(current_val) - float(weight)) < 0.001
                            except:
                                already_same = (current_val == weight)

                            if is_disabled and already_same:
                                print(f"⏩ Exact Tag {tag_id} pehle se saved hai, skip kar rahe hain.")
                                continue 
                                
                            if not already_same:
                                js_inject = f"""node => {{
                                    node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                                    node.removeAttribute('onpaste'); node.removeAttribute('oncopy'); 
                                    node.removeAttribute('oncut'); node.removeAttribute('oncontextmenu'); 
                                    node.value = '{weight}'; 
                                    node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                                }}"""
                                weight_input.evaluate(js_inject)
                                
                                save_btn = target_row.locator("text='Save'").first
                                if save_btn.is_visible():
                                    main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                                    main_page.once("dialog", lambda dialog: dialog.accept())
                                    save_btn.evaluate("node => node.click()") 
                                    
                                    # 🚀 NAYA: Save hone par rukega taaki portal overlap na ho
                                    print(f"✅ Tag {tag_id} me {weight}g strict fill kar diya. Waiting...")
                                    time.sleep(1.5) 
                                    try:
                                        main_page.wait_for_load_state("networkidle", timeout=4000)
                                        target_frame.wait_for_selector("table tbody tr", state="visible", timeout=4000)
                                    except: pass
                                    
                                    time.sleep(delay_ms / 1000.0)
                                
                                filled_count += 1
                    else:
                        print(f"⚠️ Tag {tag_id} screen par match nahi hua, skip kar diya.")
                except Exception as e: print(f"⚠️ Error: {e}")
                        
                        if weight_input.count() > 0:
                            current_val = str(weight_input.evaluate("node => node.value")).strip()
                            if current_val != weight:
                                js_inject = f"""node => {{
                                    node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                                    node.removeAttribute('onpaste'); node.removeAttribute('oncopy'); 
                                    node.removeAttribute('oncut'); node.removeAttribute('oncontextmenu'); 
                                    node.value = '{weight}'; 
                                    node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                                }}"""
                                weight_input.evaluate(js_inject)
                                
                                save_btn = target_row.locator("text='Save'").first
                                if save_btn.is_visible():
                                    main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                                    main_page.once("dialog", lambda dialog: dialog.accept())
                                    save_btn.evaluate("node => node.click()") # JS Click lagaya
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
    """Main page par sabhi pages ko (Next click karke) padhna aur Request/Job list banana"""
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
            max_wait = 180 # 3 minute (180 seconds) ka maximum intezaar
            start_time = time.time()
            
            print("⏳ Dashboard table load hone ka wait kar rahe hain (Max 3 minutes)...")
            
            while time.time() - start_time < max_wait:
                if CANCEL_FETCH: break
                
                for page in browser.contexts[0].pages:
                    for frame in [page] + page.frames:
                        try:
                            # 🚀 SMART WAIT: Table load hone ka explicit wait karein pehle
                            #frame.wait_for_selector("table tbody tr", timeout=3000, state="attached")
                            
                            res = frame.evaluate(js_code)
                            if res: 
                                target_frame = frame
                                break
                        except: pass
                    # ✅ FIXED: Properly indented breaks
                    if target_frame:
                        break 
                if target_frame:
                    break
                time.sleep(1) 

            if CANCEL_FETCH:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "🛑 Process Cancelled by User."}

            if not target_frame:
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": "⚠️ Timeout Error: 3 minute me Website par koi Request/Job Data load nahi hua!"}

            all_data = {}
            previous_data_state = None 

            while True:
                # 🚀 ENTERPRISE CANCEL SWITCH
                if CANCEL_FETCH:
                    print("🛑 Fetching loop cancelled by user!")
                    break

                res = target_frame.evaluate(js_code)
                
                if res == previous_data_state:
                    print("🛑 Aakhri page aa gaya (Data repeat ho raha hai). Loop break kar rahe hain.")
                    break
                    
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
                        print("➡️ Website ke agle panne (Next Page) par jaa rahe hain...")
                        # 🚀 ERROR FIX: JS Force Click Lagaya
                        next_btn.evaluate("node => node.click()") 
                        
                        # 🚀 NAYI LINES: Network idle hone ka aur table aane ka pakka wait
                        try:
                            target_frame.page.wait_for_load_state("networkidle", timeout=8000)
                            target_frame.wait_for_selector("table tbody tr", state="visible", timeout=10000)
                        except: pass
                        
                        wait_start = time.time()
                        while time.time() - wait_start < 10:
                            if CANCEL_FETCH: break
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state:
                                    break
                            except: pass
                            time.sleep(0.5)
                    else:
                        break 
                else:
                    break

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH:
                return {"status": "error", "msg": "🛑 Process Stopped. Please try again."}

            return {"status": "success", "data": all_data}
            
    except Exception as e:
        logging.error(f"Dashboard Scrape Error: {e}", exc_info=True)
        return {"status": "error", "msg": str(e)}


def process_selected_requests(selected_reqs, master_info):
    """Website par QM View kholna, Tag/Purity nikalna, aur tab band karna"""
    global CANCEL_FETCH
    CANCEL_FETCH = False
    
    print(f"🌐 Website par selected requests ki scraping shuru: {selected_reqs}")
    from modules import database as db
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            context = browser.contexts[0]

            total_jobs_saved = 0
            max_wait_time = 180 # 3 minutes timeout

            for req in selected_reqs:
                if CANCEL_FETCH: break
                
                jobs = master_info.get(req, [])
                for job in jobs:
                    if CANCEL_FETCH: break
                    
                    print(f"\n🔍 Website par Job dhundh rahe hain: {job}")

                    target_frame = None
                    wait_start_time = time.time()
                    
                    print("⏳ Page frame load hone ka wait kar rahe hain...")
                    
                    while time.time() - wait_start_time < max_wait_time:
                        if CANCEL_FETCH: break
                        for page in context.pages:
                            for frame in [page] + page.frames:
                                try:
                                    # ✅ FIXED: Indentation of JS string improved for clarity
                                    is_target = frame.evaluate("""() => {
                                        let text = document.body.innerText.toUpperCase();
                                        let hasTable = document.querySelectorAll('table tbody tr').length > 0;
                                        return hasTable && (text.includes('JOB CARD') || text.includes('QM JOB') || text.includes('ACTION') || text.includes('XRF') || text.includes('SUBMITTED ARTICLES'));
                                    }""")
                                    if is_target:
                                        target_frame = frame
                                        break
                                except: pass
                            if target_frame: break
                            
                        if target_frame: 
                            break 
                        time.sleep(1) 

                    if CANCEL_FETCH or not target_frame:
                        if not target_frame: print(f"⚠️ Timeout: 3 min wait kiya par Table frame nahi mila.")
                        continue 

                    try:
                        first_btn = target_frame.locator("a.paginate_button.first, li.first a, a:has-text('First'), a:has-text('«'), a.paginate_button:has-text('1')").first
                        if first_btn.count() > 0:
                            f_class = first_btn.get_attribute("class") or ""
                            if "disabled" not in f_class and "current" not in f_class:
                                # 🚀 ERROR FIX: JS Force Click Lagaya
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
                                if target_frame.locator("tr", has_text=job).count() > 0:
                                    break
                                time.sleep(0.5)
                        except: pass

                    job_found = False
                    row = None
                    
                    while True:
                        if CANCEL_FETCH: break
                        row = target_frame.locator("tr", has_text=job).first
                        
                        if row.count() > 0:
                            job_found = True
                            break 
                            
                        next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next'), a:has-text('›'), a[title*='Next']").last
                        
                        if next_btn.count() > 0:
                            btn_class = next_btn.get_attribute("class") or ""
                            if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                                print(f"➡️ Page par nahi mila, agla page scan kar rahe hain...")
                                # 🚀 ERROR FIX: JS Force Click Lagaya
                                next_btn.evaluate("node => node.click()") 
                                
                                p_wait = time.time()
                                while time.time() - p_wait < 10:
                                    if CANCEL_FETCH: break
                                    try:
                                        if target_frame.locator("tr", has_text=job).count() > 0 or target_frame.evaluate("""() => document.readyState === 'complete'"""):
                                            break
                                    except: pass
                                    time.sleep(0.5)
                            else:
                                break
                        else:
                            break
                            
                    if CANCEL_FETCH: continue
                    
                    if not job_found:
                        print(f"⚠️ Alert: Poori website scan ki, par Job {job} nahi mila.")
                        if search_box.count() > 0:
                            try: search_box.fill("")
                            except: pass
                        continue 

                    view_btn = row.locator("a").last 

                    try:
                        with context.expect_page(timeout=10000) as new_page_info:
                            # 🚀 SMART FIX: Force it to open in a NEW TAB every time
                            view_btn.evaluate("node => { node.setAttribute('target', '_blank'); node.click(); }")
                        new_page = new_page_info.value
                    except Exception as e:
                        print(f"⚠️ Naya tab kholne me dikkat: {e}")
                        continue

                    target_new_frame = None
                    tab_wait_start = time.time()
                    
                    print("⏳ Naye tab me Tags load hone ka wait kar rahe hain...")
                    
                    while time.time() - tab_wait_start < max_wait_time:
                        if CANCEL_FETCH: break
                        for page_tab in context.pages:
                            for frame in [page_tab] + page_tab.frames:
                                try:
                                    if "TAG ID" in frame.locator("body").inner_text().upper():
                                        target_new_frame = frame
                                        break
                                except: pass
                            if target_new_frame: break
                        if target_new_frame: 
                            break 
                        time.sleep(1) 
                        
                    if CANCEL_FETCH:
                        try: new_page.close()
                        except: pass
                        continue

                    if not target_new_frame: 
                        target_new_frame = new_page 

                    # 🚀 NAYA FIX: Tags wala table load hone ka wait karega (Aadha data miss nahi hoga)
                    try:
                        target_new_frame.wait_for_load_state("networkidle", timeout=5000)
                        target_new_frame.wait_for_selector("table tbody tr", state="visible", timeout=15000)
                    except:
                        print("⚠️ Tags table aane me internet ki wajah se time lag raha hai...")
                        pass

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
                        
                        if res == previous_page_data:
                            break
                            
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
                                        if target_new_frame.evaluate(js_code_tags) != previous_page_data:
                                            break
                                    except: pass
                                    time.sleep(0.5)
                            else:
                                break
                        else:
                            break 

                    print(f"✅ Website se {len(all_scraped_items)} tags fetch kiye.")

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
            
            if CANCEL_FETCH:
                return {"status": "error", "msg": f"🛑 Cancelled! Lakin pehle ke {total_jobs_saved} Jobs database me save ho chuke hain."}
                
            # 🚀 NAYA CHECK: Agar ek bhi job save nahi hua toh Error dikhaye
            if total_jobs_saved == 0:
                return {"status": "error", "msg": "⚠️ Data Fetch Fail! Ya toh page theek se load nahi hua, ya tags available nahi hain."}
                
            return {"status": "success", "msg": f"✅ Website se Data Fetch ho gaya! {total_jobs_saved} Jobs Database mein save ho gaye."}
            
    except Exception as e:
        logging.error(f"Selected Requests Scrape Error: {e}", exc_info=True)
        return {"status": "error", "msg": str(e)}
# ==============================================================
# 🌟 5. NEW: SCRAPE REQUESTS FROM XRF PAGE (BACKUP FETCH)
# ==============================================================
def scrape_all_requests_from_xrf():
    """XRF page ('Submitted Articles List') se Request aur Job data extract karna"""
    global CANCEL_FETCH
    CANCEL_FETCH = False
    print("🌐 XRF Backup Page se data fetch kar rahe hain...")
    
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

            # 🚀 Exact JS Logic for the XRF "Submitted Articles List" Table
            js_code = """
            () => {
                let results = {};
                let rows = document.querySelectorAll('table tbody tr');
                if(rows.length === 0) return null; 
                
                let hasData = false;
                for(let r of rows) {
                    let rowText = r.innerText || "";
                    // 🚀 FIX: Sirf exact numbers hi filter honge, spaces wagera nahi
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
            max_wait = 180 # 3 mins
            start_time = time.time()
            
            print("⏳ XRF table load hone ka wait kar rahe hain...")
            
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
                return {"status": "error", "msg": "⚠️ Timeout Error: Website par XRF Table Data load nahi hua!"}

            all_data = {}
            previous_data_state = None 

            while True:
                if CANCEL_FETCH:
                    print("🛑 Fetching loop cancelled by user!")
                    break

                res = target_frame.evaluate(js_code)
                if res == previous_data_state:
                    print("🛑 Aakhri page aa gaya. Loop break kar rahe hain.")
                    break
                    
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
                        print("➡️ Agle panne (Next Page) par jaa rahe hain...")
                        next_btn.evaluate("node => node.click()") 
                        wait_start = time.time()
                        while time.time() - wait_start < 10:
                            if CANCEL_FETCH: break
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state:
                                    break
                            except: pass
                            time.sleep(0.5)
                    else:
                        break 
                else:
                    break

            try: browser.disconnect()
            except: pass
            
            if CANCEL_FETCH:
                return {"status": "error", "msg": "🛑 Process Stopped."}

            return {"status": "success", "data": all_data}
            
    except Exception as e:
        logging.error(f"XRF Scrape Error: {e}", exc_info=True)
        return {"status": "error", "msg": str(e)}