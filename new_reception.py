from playwright.sync_api import sync_playwright
import time
import re
import logging
import gc  # 🚀 RAM Cleanup ke liye

# 🚀 Enterprise Logging System
logging.basicConfig(filename='app_crash.log', level=logging.ERROR, 
                    format='%(asctime)s - RECEPTION - %(levelname)s - %(message)s')

# Playwright ke liye local browser ka URL
CDP_URL = "http://localhost:9222"

# 🚀 GLOBAL CANCEL SWITCH (Process Rokne ke liye)
CANCEL_FETCH = False
ACTIVE_BROWSER = None  # 🔥 NAYA: Browser track karne ke liye

def bypass_bis_security(browser):
    """ 🚀 BIS ke naye Anti-Bot aur DevTools security ko bypass karne ka master function """
    bypass_js = """
    () => {
        if (window.__bisSecBypassed) return;
        window.__bisSecBypassed = true;
        
        try {
            Object.defineProperty(window, 'outerWidth', { get: () => window.innerWidth });
            Object.defineProperty(window, 'outerHeight', { get: () => window.innerHeight });
        } catch(e) {}

        try {
            const originalBodySetter = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML').set;
            Object.defineProperty(document.body, 'innerHTML', {
                set: function(val) {
                    if (val === "") {
                        console.log("🔒 Blocked BIS from blanking the screen!");
                        return;
                    }
                    originalBodySetter.call(this, val);
                }
            });
        } catch(e) {}
    }
    """
    try:
        for page in browser.contexts[0].pages:
            for frame in [page] + page.frames:
                try:
                    frame.evaluate(bypass_js)
                except:
                    pass
    except:
        pass

def force_stop_process():
    """Stop button dabne par browser connection ko turant tod dega taaki process ruke"""
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = True
    print("🛑 FORCE KILL ACTIVATED! Disconnecting browser...")
    if ACTIVE_BROWSER:
        try:
            ACTIVE_BROWSER.disconnect()
        except:
            pass

# ==============================================================
# 🌟 LOT SPLITTER HELPER (Rule Book ke hisaab se)
# ==============================================================
def split_tags_into_lots(job_id, tags_list):
    lots = {}
    total = len(tags_list)
    
    if total <= 40:
        if total > 0: 
            lots[f"{job_id}-L1"] = tags_list
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
# 1. SINGLE RECEPTION INJECTION (Auto-Mode jaisa 100% Accurate)
# ==============================================================
def inject_single_reception_tag(job_id, tag_id, weight):
    global CANCEL_FETCH, ACTIVE_BROWSER
    tag_id, weight = str(tag_id).strip(), str(weight).strip()
    search_job_id = str(job_id).split('-L')[0] 
    print(f"👻 Live Single Inject: Tag: {tag_id} | Weight: {weight}g | Job: {search_job_id}")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL)
                ACTIVE_BROWSER = browser
                bypass_bis_security(browser)       
            except: 
                return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
            target_frame = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        if search_job_id in frame.locator("body").inner_text():
                            target_frame = frame
                            break
                    except:
                        pass
                if target_frame: 
                    break
                
            if not target_frame:
                try: 
                    browser.disconnect()
                except: 
                    pass
                return {"status": "error", "msg": f"❌ Wrong Page! Site par ID '{search_job_id}' open nahi hai."}

            try: 
                target_frame.wait_for_selector("table tbody tr", timeout=3000)
            except: 
                pass

            row_count = target_frame.locator("table tbody tr").count()
            tag_found = False

            for i in range(row_count):
                try:
                    row = target_frame.locator("table tbody tr").nth(i)
                    
                    # 🚀 S.No. Fix implemented here
                    tag_cell = row.locator(".tagIdCls").first
                    if tag_cell.count() > 0:
                        current_tag = tag_cell.inner_text().strip()
                    else:
                        current_tag = row.locator("td:nth-child(2)").first.inner_text().strip()
                        if current_tag.isdigit() and len(current_tag) <= 4: 
                            current_tag = row.locator("td:nth-child(3)").first.inner_text().strip()
                    
                    if current_tag == tag_id:
                        tag_found = True
                        weight_input = row.locator("input.weightCls, input.scan-input, input:not([type='hidden']):not([type='checkbox'])").first
                        
                        if weight_input.count() > 0:
                            js_inject = f"""node => {{
                                window.isScaleConnected = true;
                                window.isMachineVerified = true;
                                window.validateAllScannedInputs = function() {{ return true; }};
                                window.isReadingAuthentic = function() {{ return true; }};

                                let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                let wasReadonly = node.hasAttribute('readonly');
                                let wasDisabled = node.hasAttribute('disabled');
                                
                                if(wasReadonly) node.removeAttribute('readonly');
                                if(wasDisabled) node.removeAttribute('disabled');
                                
                                nativeSetter.call(node, '{weight}');

                                if (typeof verifiedMachineReadings !== 'undefined') {{
                                    verifiedMachineReadings.set(node, '{weight}');
                                }}
                                
                                node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                                node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                                node.dispatchEvent(new Event('blur', {{ bubbles: true }})); 
                                
                                if(wasReadonly) node.setAttribute('readonly', 'true');
                                if(wasDisabled) node.setAttribute('disabled', 'true');
                            }}"""
                            weight_input.evaluate(js_inject)
                            
                            save_btn = row.locator(".saveWeight, .btn-primary, button:has-text('Save')").first
                            if save_btn.count() > 0:
                                main_page = target_frame.page if hasattr(target_frame, 'page') else target_frame
                                
                                try: 
                                    main_page.remove_all_listeners("dialog")
                                except: 
                                    pass
                                try: 
                                    main_page.once("dialog", lambda dialog: dialog.accept())
                                except: 
                                    pass
                                
                                save_btn.evaluate("node => setTimeout(() => node.click(), 50)") 
                                
                                start_wait = time.time()
                                processing_started = False
                                
                                while time.time() - start_wait < 3.0:
                                    try:
                                        is_processing = target_frame.evaluate("""() => {
                                            return document.body.innerText.replace(/\\s/g, '').toUpperCase().includes('PROCESSING');
                                        }""")
                                        if is_processing:
                                            processing_started = True
                                            break
                                    except: 
                                        pass
                                    time.sleep(0.2)
                                    
                                if processing_started:
                                    phase2_start = time.time()
                                    while time.time() - phase2_start < 10.0:
                                        try:
                                            is_still_processing = target_frame.evaluate("""() => {
                                                return document.body.innerText.replace(/\\s/g, '').toUpperCase().includes('PROCESSING');
                                            }""")
                                            if not is_still_processing:
                                                break
                                        except: 
                                            break 
                                        time.sleep(0.3)
                                else:
                                    time.sleep(1.0)
                                
                            try: 
                                browser.disconnect()
                            except: 
                                pass
                            return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                        else:
                            try: 
                                browser.disconnect()
                            except: 
                                pass
                            return {"status": "error", "msg": "⚠️ Input box nahi mila!"}
                except:
                    pass
            
            try: 
                browser.disconnect()
            except: 
                pass
            
            if not tag_found:
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' screen par nahi mila! Kripya Next page check karein."}

    except Exception as e:
        logging.error(f"Single Inject Error: {e}", exc_info=True)
        return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}

# ==============================================================
# 2. FAST DROPDOWN INJECTION 
# ==============================================================
def fast_inject_weight(job_id, tag_id, weight):
    global CANCEL_FETCH, ACTIVE_BROWSER
    
    tag_id, weight = str(tag_id).strip(), str(weight).strip()
    print(f"🚀 Fast Dropdown Inject: Tag: {tag_id} | Wt: {weight}g | Job: {job_id}")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL)
                ACTIVE_BROWSER = browser
                bypass_bis_security(browser)
            except: 
                return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
            target_frame = None
            for page in browser.contexts[0].pages:
                try:
                    if page.locator("tr").filter(has=page.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                        target_frame = page
                        break
                except: 
                    pass
                for frame in page.frames:
                    try:
                        if frame.locator("tr").filter(has=frame.locator("td").get_by_text(tag_id, exact=True)).count() > 0:
                            target_frame = frame
                            break
                    except: 
                        pass
                if target_frame: 
                    break

            if not target_frame:
                try: 
                    browser.disconnect()
                except: 
                    pass
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' list me nahi mila."}

            # 🚀 S.No. Fix implemented here
            row = target_frame.locator("tr").filter(has=target_frame.locator(".tagIdCls").get_by_text(tag_id, exact=True))
            if row.count() == 0: 
                row = target_frame.locator("tr").filter(has=target_frame.locator("td:nth-child(2)").get_by_text(tag_id, exact=True))
                if row.count() == 0:
                    row = target_frame.locator("tr").filter(has=target_frame.locator("td:nth-child(3)").get_by_text(tag_id, exact=True))
            
            if row.count() > 0:
                weight_input = row.first.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                
                if weight_input.count() > 0:
                    js_inject = f"""node => {{
                        window.isScaleConnected = true;
                        window.isMachineVerified = true;
                        window.validateAllScannedInputs = function() {{ return true; }};
                        window.isReadingAuthentic = function() {{ return true; }};

                        let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        let wasReadonly = node.hasAttribute('readonly');
                        let wasDisabled = node.hasAttribute('disabled');
                        
                        if(wasReadonly) node.removeAttribute('readonly');
                        if(wasDisabled) node.removeAttribute('disabled');
                        
                        nativeSetter.call(node, '{weight}');

                        if (typeof verifiedMachineReadings !== 'undefined') {{
                            verifiedMachineReadings.set(node, '{weight}');
                        }}
                        
                        node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                        node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                        node.dispatchEvent(new Event('blur', {{ bubbles: true }})); 
                        
                        if(wasReadonly) node.setAttribute('readonly', 'true');
                        if(wasDisabled) node.setAttribute('disabled', 'true');
                    }}"""
                    weight_input.evaluate(js_inject)
                    
                    save_btn = row.first.locator("text='Save'").first
                    if save_btn.is_visible():
                        main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                        main_page.once("dialog", lambda dialog: dialog.accept())
                        save_btn.evaluate("node => node.click()")
                        time.sleep(1)
                        
                    try: 
                        browser.disconnect()
                    except: 
                        pass
                    return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                else: 
                    return {"status": "error", "msg": "⚠️ Input box nahi mila!"}
            else: 
                return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' list me nahi mila."}
                
    except Exception as e:
        logging.error(f"Fast Inject Error: {e}", exc_info=True)
        return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}

# ==============================================================
# 3. FULL AUTO INJECTION (ULTRA FAST & BULLETPROOF RETRY LOGIC)
# ==============================================================
def inject_reception_weight_ghost(job_id, job_data, delay_ms=400): 
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    search_job_id = str(job_id).split('-L')[0] 
    
    if not job_data: 
        return "⚠️ डेटाबेस खाली है।"
    print(f"🚀 Ultra-Fast Auto Injection Started... Job: {search_job_id}")

    tag_map = {str(item[0]).strip(): str(item[1]).strip() for item in job_data if str(item[1]).strip() not in ["0", "0.0", ""]}
    if not tag_map: 
        return "⚠️ Koi valid weight (0.0 ke alawa) nahi mila inject karne ke liye."
    
    filled_count = 0

    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=15000)
                ACTIVE_BROWSER = browser
                bypass_bis_security(browser) 
            except: 
                return "⚠️ ब्राउज़र ओपन नहीं है!"

            target_frame = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        if search_job_id in frame.locator("body").inner_text():
                            target_frame = frame
                            break
                    except: 
                        pass
                if target_frame: 
                    break
                
            if not target_frame:
                try: 
                    browser.disconnect()
                except: 
                    pass
                return f"❌ Wrong Page! Site par ID '{search_job_id}' open nahi hai."

            try:
                first_btn = target_frame.locator("a.paginate_button.first, li.first a, a:has-text('First')").first
                if first_btn.count() > 0 and "disabled" not in (first_btn.get_attribute("class") or ""):
                    first_btn.evaluate("node => node.click()")
                    time.sleep(1)
            except: 
                pass

            empty_table_retries = 0

            while tag_map and not CANCEL_FETCH:
                try:
                    target_frame.locator("body").inner_text()
                except:
                    target_frame = None
                    for page in browser.contexts[0].pages:
                        for frame in [page] + page.frames:
                            try:
                                if search_job_id in frame.locator("body").inner_text():
                                    target_frame = frame
                                    break
                            except: 
                                pass
                        if target_frame: 
                            break
                
                if not target_frame:
                    time.sleep(1)
                    continue

                try: 
                    target_frame.wait_for_selector("table tbody tr", timeout=10000)
                except: 
                    pass
                
                row_count = 0
                try: 
                    row_count = target_frame.locator("table tbody tr").count()
                except: 
                    pass

                if row_count == 0:
                    empty_table_retries += 1
                    if empty_table_retries < 5:
                        time.sleep(1)
                        continue
                    else:
                        break 
                        
                empty_table_retries = 0 
                made_save_on_this_page = False 
                
                for i in range(row_count):
                    if CANCEL_FETCH or not tag_map: 
                        break
                    try:
                        row = target_frame.locator("table tbody tr").nth(i)
                        
                        # 🚀 NAYA S.No. AUR COLUMN LOGIC
                        tag_cell = row.locator(".tagIdCls").first
                        if tag_cell.count() > 0:
                            current_tag = tag_cell.inner_text().strip()
                        else:
                            current_tag = row.locator("td:nth-child(2)").first.inner_text().strip()
                            if current_tag.isdigit() and len(current_tag) <= 4:
                                current_tag = row.locator("td:nth-child(3)").first.inner_text().strip()
                        
                        if current_tag in tag_map:
                            weight = tag_map[current_tag]
                            weight_input = row.locator("input.weightCls, input.scan-input, input:not([type='hidden']):not([type='checkbox'])").first
                            
                            if weight_input.count() > 0:
                                js_inject = f"""node => {{
                                    window.isScaleConnected = true;
                                    window.isMachineVerified = true;
                                    window.validateAllScannedInputs = function() {{ return true; }};
                                    window.isReadingAuthentic = function() {{ return true; }};

                                    let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                    let wasReadonly = node.hasAttribute('readonly');
                                    let wasDisabled = node.hasAttribute('disabled');
                                    
                                    if(wasReadonly) node.removeAttribute('readonly');
                                    if(wasDisabled) node.removeAttribute('disabled');
                                    
                                    nativeSetter.call(node, '{weight}');

                                    if (typeof verifiedMachineReadings !== 'undefined') {{
                                        verifiedMachineReadings.set(node, '{weight}');
                                    }}
                                    
                                    node.dispatchEvent(new Event('input', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('change', {{ bubbles: true }})); 
                                    node.dispatchEvent(new Event('blur', {{ bubbles: true }})); 
                                    
                                    if(wasReadonly) node.setAttribute('readonly', 'true');
                                    if(wasDisabled) node.setAttribute('disabled', 'true');
                                }}"""
                                weight_input.evaluate(js_inject)
                                
                                main_page = target_frame.page if hasattr(target_frame, 'page') else target_frame
                                save_btn = row.locator(".saveWeight, .btn-primary, button:has-text('Save')").first
                                
                                if save_btn.count() > 0:
                                    try: 
                                        main_page.once("dialog", lambda dialog: dialog.accept())
                                    except: 
                                        pass
                                    
                                    save_btn.evaluate("node => setTimeout(() => node.click(), 50)")
                                    
                                    start_wait = time.time()
                                    processing_started = False
                                    
                                    while time.time() - start_wait < 4.0:
                                        try:
                                            is_processing = target_frame.evaluate("""() => {
                                                return document.body.innerText.replace(/\\s/g, '').toUpperCase().includes('PROCESSING');
                                            }""")
                                            if is_processing:
                                                processing_started = True
                                                break 
                                        except: 
                                            pass
                                        time.sleep(0.2) 
                                        
                                    if processing_started:
                                        phase2_start = time.time()
                                        while time.time() - phase2_start < 15.0:
                                            try:
                                                is_still_processing = target_frame.evaluate("""() => {
                                                    return document.body.innerText.replace(/\\s/g, '').toUpperCase().includes('PROCESSING');
                                                }""")
                                                if not is_still_processing:
                                                    break 
                                            except:
                                                break 
                                            time.sleep(0.3)
                                    else:
                                        time.sleep(1.0)
                                        
                                filled_count += 1
                                del tag_map[current_tag]
                                made_save_on_this_page = True
                                
                                break 
                                
                    except Exception as e: 
                        pass

                if not tag_map or CANCEL_FETCH: 
                    break 
                
                if made_save_on_this_page:
                    continue
                
                next_btn = target_frame.locator("a.paginate_button.next, a#tabWeight_next, li.next a").first
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true":
                        break
                        
                    old_first_tag = ""
                    try: 
                        old_first_tag = target_frame.locator("tbody tr td:nth-child(2)").first.inner_text().strip()
                    except: 
                        pass

                    next_btn.evaluate("node => node.click()")
                    
                    t_wait = time.time()
                    while time.time() - t_wait < 5:
                        if CANCEL_FETCH: 
                            break
                        time.sleep(0.2)
                        try:
                            new_first_tag = target_frame.locator("tbody tr td:nth-child(2)").first.inner_text().strip()
                            if new_first_tag != old_first_tag and new_first_tag != "": 
                                break
                        except: 
                            pass
                else: 
                    break

            try: 
                browser.disconnect() 
            except: 
                pass
            
            if CANCEL_FETCH: 
                return f"🛑 STOPPED! {filled_count} Tags Save huye."
            return f"✅ 100% Success! Saare {filled_count} Tags FAST Save kar diye gaye."
            
    except Exception as e: 
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
                if res: 
                    return res
            except: 
                pass
    return None

# ==============================================================
# 4 & 5. SCRAPE REQUESTS (FIXED: HEADER LOGIC + OVERWRITE ISSUE)
# ==============================================================
def scrape_all_requests_from_main():
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    
    try:
        with sync_playwright() as p:
            try: 
                # 🚀 Timeout 5000 se 15000 kiya taaki slow internet par load ho sake
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=15000)
                ACTIVE_BROWSER = browser
                bypass_bis_security(browser)
            except: 
                return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

            js_code = """
            () => {
                let results = {};
                let hasData = false;
                
                let rows = document.querySelectorAll('table tbody tr');
                
                for (let r of rows) {
                    if (r.offsetParent === null) continue;
                    
                    let rowText = r.innerText.toUpperCase();
                    if (rowText.includes("NO DATA") || rowText.includes("LOADING")) continue;
                    
                    let cells = r.querySelectorAll('td');
                    let req = null;
                    let job = null;
                    
                    // 🚀 1. PEHLE HEADER CHECK KAREGA (Isse Request aur Job Card aapas me mix nahi honge)
                    let table = r.closest('table');
                    if (table) {
                        let headers = Array.from(table.querySelectorAll('th, thead td')).map(x => x.innerText.trim().toUpperCase().replace(/\\./g, ''));
                        let reqIdx = headers.findIndex(h => h.includes('REQUEST NO') || h.includes('REQ NO') || h.includes('REQUEST'));
                        let jobIdx = headers.findIndex(h => h.includes('JOB CARD') || h.includes('JOB NO'));
                        
                        if (reqIdx !== -1 && jobIdx !== -1 && cells.length > Math.max(reqIdx, jobIdx)) {
                            let possibleReq = cells[reqIdx].innerText.trim().match(/\\d+/);
                            let possibleJob = cells[jobIdx].innerText.trim().match(/\\d+/);
                            if (possibleReq) req = String(possibleReq[0]).trim();
                            if (possibleJob) job = String(possibleJob[0]).trim();
                        }
                    }

                    // 🚀 2. FALLBACK (Agar Header na mile toh purana logic, lekin overwrite rokne ke lock ke saath)
                    if (!req || !job) {
                        req = null; // Reset taaki double print na ho
                        job = null;
                        for (let c of cells) {
                            let match = c.innerText.trim().match(/\\d{8,}/); 
                            if (match) {
                                if (!req) {
                                    req = String(match[0]);
                                } else if (!job && req !== String(match[0])) {
                                    // 🚀 Ye lock lagaya hai taaki Request ki jagah wapas Job Card na chhap jaye
                                    job = String(match[0]);
                                }
                            }
                        }
                    }

                    if (req && job) {
                        if (!results[req]) results[req] = [];
                        if (!results[req].includes(job)) results[req].push(job);
                        hasData = true;
                    } else if (job) {
                         req = "UNKNOWN";
                         if (!results[req]) results[req] = [];
                         if (!results[req].includes(job)) results[req].push(job);
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
                            if res: 
                                target_frame = frame
                                break
                        except: 
                            pass
                    if target_frame: 
                        break 
                if target_frame: 
                    break
                time.sleep(1) 

            if not target_frame: 
                return {"status": "error", "msg": "⚠️ Timeout Error!"}

            all_data = {}
            previous_data_state = None 

            while True:
                if CANCEL_FETCH: break
                res = target_frame.evaluate(js_code)
                if res == previous_data_state: 
                    break
                    
                if res:
                    for req, jobs in res.items():
                        if req not in all_data: 
                            all_data[req] = []
                        for j in jobs:
                            if j not in all_data[req]: 
                                all_data[req].append(j)

                previous_data_state = res 
                
                next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next')").last
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                        next_btn.evaluate("node => node.click()") 
                        t_wait = time.time()
                        while time.time() - t_wait < 15:
                            if CANCEL_FETCH: 
                                break
                            time.sleep(0.2)
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state: 
                                    break
                            except: 
                                pass
                    else: 
                        break 
                else: 
                    break

            if CANCEL_FETCH: 
                return {"status": "error", "msg": "🛑 Process Stopped."}
            return {"status": "success", "data": all_data}
            
    except Exception as e: 
        return {"status": "error", "msg": str(e)}
    finally:
        ACTIVE_BROWSER = None
        try:
            if 'browser' in locals() and browser:
                browser.disconnect()
        except: 
            pass
# ==============================================================
# 5. PROCESS SELECTED REQUESTS (SINGLE TAB MANAGEMENT + BULLETPROOF)
# ==============================================================
def process_selected_requests(selected_reqs, master_info):
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    from modules import database as db
    
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
                bypass_bis_security(browser)
                context = browser.contexts[0]
            except: 
                return {"status": "error", "msg": "⚠️ Secure Browser open nahi hai!"}
            
            total_jobs_saved = 0

            for req in selected_reqs:
                if CANCEL_FETCH: 
                    break
                
                jobs = master_info.get(req, [])
                for job in jobs:
                    if CANCEL_FETCH: 
                        break
                    
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
                                    if is_target: 
                                        target_frame = frame
                                        break
                                except: 
                                    pass
                            if target_frame: 
                                break
                        if target_frame: 
                            break 
                        time.sleep(1) 

                    if not target_frame: 
                        continue 

                    try:
                        first_btn = target_frame.locator("a.paginate_button.first, li.first a, a:has-text('First')").first
                        if first_btn.count() > 0 and "disabled" not in (first_btn.get_attribute("class") or ""):
                            first_btn.evaluate("node => node.click()") 
                            time.sleep(1.0) 
                    except: 
                        pass

                    search_box = target_frame.locator("input[type='search'], input.form-control.input-sm").first
                    if search_box.count() > 0:
                        try:
                            search_box.fill(job)
                            search_box.press("Enter")
                            s_wait = time.time()
                            while time.time() - s_wait < 10:
                                if target_frame.locator("tr", has_text=job).count() > 0: 
                                    break
                                time.sleep(0.5)
                        except: 
                            pass

                    job_found = False
                    row = None
                    
                    while True:
                        if CANCEL_FETCH: break
                        row = target_frame.locator("tr", has_text=job).first
                        if row.count() > 0:
                            job_found = True
                            break 
                            
                        next_btn = target_frame.locator("a.paginate_button.next, li.next a, a:has-text('Next')").last
                        if next_btn.count() > 0:
                            btn_class = next_btn.get_attribute("class") or ""
                            if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                                next_btn.evaluate("node => node.click()") 
                                p_wait = time.time()
                                while time.time() - p_wait < 10:
                                    if CANCEL_FETCH: 
                                        break
                                    try:
                                        if target_frame.locator("tr", has_text=job).count() > 0: 
                                            break
                                    except: 
                                        pass
                                    time.sleep(0.5)
                            else: 
                                break
                        else: 
                            break
                            
                    if not job_found: 
                        continue 

                    existing_pages = set(context.pages)

                    try:
                        view_btn = row.locator("a.fa-eye, a[title*='View' i], button[title*='View' i], a:has-text('View')").first
                        if view_btn.count() == 0:
                            view_btn = row.locator("td").last.locator("a, button").first
                        
                        view_btn.evaluate("node => { node.scrollIntoView(); node.style.border = '3px solid green'; node.click(); }")
                    except: 
                        continue

                    target_new_frame = None
                    new_opened_page = None
                    tab_wait_start = time.time()
                    
                    while time.time() - tab_wait_start < 45:
                        if CANCEL_FETCH: 
                            break
                        
                        current_pages = set(context.pages)
                        new_pages = current_pages - existing_pages
                        
                        if new_pages:
                            new_opened_page = list(new_pages)[0]
                            target_new_frame = new_opened_page
                        
                        if target_new_frame:
                            try:
                                if target_new_frame.locator("th:has-text('TAG ID'), td:has-text('TAG ID'), th:has-text('AHC TAG')").count() > 0:
                                    break
                            except: 
                                pass
                        else:
                            for frame in [context.pages[0]] + context.pages[0].frames:
                                try:
                                    if frame.locator("th:has-text('TAG ID'), td:has-text('TAG ID'), th:has-text('AHC TAG')").count() > 0:
                                        target_new_frame = frame
                                        break
                                except: 
                                    pass
                            if target_new_frame: 
                                break
                            
                        time.sleep(1) 
                        
                    if not target_new_frame: 
                        continue 

                    try:
                        target_new_frame.wait_for_selector("th:has-text('TAG ID'), td:has-text('TAG ID'), th:has-text('AHC TAG')", timeout=3000)
                    except: 
                        pass
                    
                    time.sleep(0.3) 

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
                        if CANCEL_FETCH: 
                            break
                        try: 
                            res = target_new_frame.evaluate(js_code_tags)
                        except: 
                            res = None
                        
                        if res is None and not all_scraped_items:
                            time.sleep(2)
                            try: 
                                res = target_new_frame.evaluate(js_code_tags)
                            except: 
                                res = None

                        if res == previous_page_data: 
                            break
                            
                        if res:
                            for item in res:
                                if item not in all_scraped_items: 
                                    all_scraped_items.append(item)
                                    
                        previous_page_data = res

                        next_btn = target_new_frame.locator("a#tab_logic_next, a.paginate_button.next, li.next a, a:has-text('Next')").last
                        if next_btn.count() > 0:
                            btn_class = next_btn.get_attribute("class") or ""
                            if "disabled" not in btn_class and next_btn.get_attribute("aria-disabled") != "true":
                                next_btn.evaluate("node => node.click()")
                                
                                t_wait = time.time()
                                while time.time() - t_wait < 10:
                                    if CANCEL_FETCH: 
                                        break
                                    time.sleep(0.1) 
                                    try:
                                        if target_new_frame.evaluate(js_code_tags) != previous_page_data: 
                                            break
                                    except: 
                                        pass
                            else: 
                                break
                        else: 
                            break 

                    if new_opened_page:
                        try: 
                            new_opened_page.close()
                        except: 
                            pass
                    else:
                        try:
                            go_back_btn = target_new_frame.locator("a:has-text('Go Back'), button:has-text('Go Back'), a:has-text('Back')").first
                            if go_back_btn.count() > 0:
                                go_back_btn.evaluate("node => node.click()")
                                time.sleep(0.5) 
                            else:
                                close_js = """() => {
                                    let closeBtn = document.querySelector("button.close, button[data-dismiss='modal'], a.close");
                                    if (closeBtn) { closeBtn.click(); return true; }
                                    return false;
                                }"""
                                target_new_frame.evaluate(close_js)
                        except: 
                            pass
                        
                    time.sleep(1) 

                    if all_scraped_items and not CANCEL_FETCH:
                        lot_dict = split_tags_into_lots(job, all_scraped_items)
                        for lot_job_id, tags_chunk in lot_dict.items():
                            db.save_scraped_job_card(lot_job_id, tags_chunk, request_no=req)
                        total_jobs_saved += 1
                        
                    all_scraped_items.clear() 
                    gc.collect() 
                    
                if target_frame:
                    try:
                        search_box = target_frame.locator("input[type='search'], input.form-control.input-sm").first
                        if search_box.count() > 0:
                            search_box.fill("")
                            search_box.press("Enter")
                            time.sleep(1)
                    except: 
                        pass

                gc.collect() 

            if CANCEL_FETCH: 
                return {"status": "error", "msg": f"🛑 Cancelled! {total_jobs_saved} Jobs database me save huye."}
            if total_jobs_saved == 0: 
                return {"status": "error", "msg": "⚠️ Data Fetch Fail! (Ya toh tags nahi the ya galat button daba)"}
                
            return {"status": "success", "msg": f"✅ {total_jobs_saved} Jobs Database mein Lot-Wise save ho gaye!"}
            
    except Exception as e: 
        return {"status": "error", "msg": str(e)}
    finally:
        ACTIVE_BROWSER = None
        try:
            if 'browser' in locals() and browser:
                browser.disconnect()
        except: 
            pass

# ==============================================================
# 🌟 5. NEW: SCRAPE REQUESTS FROM XRF PAGE (BACKUP FETCH)
# ==============================================================
def scrape_all_requests_from_xrf():
    global CANCEL_FETCH, ACTIVE_BROWSER
    CANCEL_FETCH = False
    print("🌐 XRF Backup Page se data fetch kar rahe hain...")
    
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
                ACTIVE_BROWSER = browser
                bypass_bis_security(browser)
            except: 
                return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

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
            max_wait = 180 
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
                        except: 
                            pass
                    if target_frame: 
                        break
                if target_frame: 
                    break 
                time.sleep(0.2) 

            if CANCEL_FETCH:
                try: 
                    browser.disconnect()
                except: 
                    pass
                return {"status": "error", "msg": "🛑 Process Cancelled by User."}

            if not target_frame:
                try: 
                    browser.disconnect()
                except: 
                    pass
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
                        if req not in all_data: 
                            all_data[req] = []
                        for j in jobs:
                            if j not in all_data[req]: 
                                all_data[req].append(j)

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
                            if CANCEL_FETCH: 
                                break
                            try:
                                if target_frame.evaluate(js_code) != previous_data_state:
                                    break
                            except: 
                                pass
                            time.sleep(0.1) 
                    else:
                        break 
                else:
                    break

            if CANCEL_FETCH:
                return {"status": "error", "msg": "🛑 Process Stopped."}

            return {"status": "success", "data": all_data}
            
    except Exception as e:
        logging.error(f"XRF Scrape Error: {e}", exc_info=True)
        return {"status": "error", "msg": str(e)}
    finally:
        ACTIVE_BROWSER = None   
        try:
            if 'browser' in locals() and browser:
                browser.disconnect()
        except: 
            pass

# ==============================================================
# 7. FETCH HUIDs & DATA FROM WEIGHING DESK PAGE (SMART SYNC + ALL PAGES)
# ==============================================================
def fetch_huids_from_page(job_id):
    global CANCEL_FETCH, ACTIVE_BROWSER
    search_job_id = str(job_id).split('-L')[0] if job_id else ""
    print(f"🔍 Smart Fetching Data for Job: {search_job_id}...")
    
    try:
        with sync_playwright() as p:
            try: 
                # 🚀 Timeout 3000 se 15000 kiya taaki network error na aaye
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=15000)
                ACTIVE_BROWSER = browser
                bypass_bis_security(browser)
            except: 
                return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
            target_frame = None
            actual_job_card = None
            
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        text = frame.locator("body").inner_text()
                        if "Weighing Desk" in text or "tagIdCls" in frame.content():
                            target_frame = frame
                            match = re.search(r'Job Card\s*Number\s*:\s*(\d+)', text, re.IGNORECASE)
                            if match: 
                                actual_job_card = match.group(1).strip()
                            break
                    except: 
                        pass
                if target_frame: 
                    break
                
            if not target_frame:
                return {"status": "error", "msg": "⚠️ Weighing Desk page screen par load nahi hui hai."}

            # 🚀 SMART HEADER DETECTION JAVASCRIPT (Columns idhar-udhar hone par bhi fail nahi hoga)
            js_code = """
            () => {
                let data = [];
                let tables = document.querySelectorAll('table');
                for (let t of tables) {
                    let headers = Array.from(t.querySelectorAll('th, thead td')).map(h => h.innerText.trim().toUpperCase());
                    
                    let tagIdx = headers.findIndex(h => h.includes('TAG'));
                    let matCatIdx = headers.findIndex(h => h.includes('MATERIAL'));
                    let itemCatIdx = headers.findIndex(h => h.includes('ITEM CATEGORY'));
                    let huidIdx = headers.findIndex(h => h.includes('HUID'));
                    let weightIdx = headers.findIndex(h => h.includes('WEIGHT') || h.includes('WT'));

                    if (tagIdx === -1) continue; // Ye sahi table nahi hai

                    let rows = t.querySelectorAll('tbody tr');
                    for (let r of rows) {
                        let cells = r.querySelectorAll('td');
                        if (cells.length > tagIdx) { 
                            let tag = cells[tagIdx].innerText.trim();
                            
                            let matCat = matCatIdx !== -1 && cells.length > matCatIdx ? cells[matCatIdx].innerText.trim() : "-";
                            let itemCat = itemCatIdx !== -1 && cells.length > itemCatIdx ? cells[itemCatIdx].innerText.trim() : "-";
                            let huid = huidIdx !== -1 && cells.length > huidIdx ? cells[huidIdx].innerText.trim() : "-";
                            
                            let weight = "-";
                            if (weightIdx !== -1 && cells.length > weightIdx) {
                                weight = cells[weightIdx].innerText.trim();
                                let wInput = cells[weightIdx].querySelector('input');
                                if(wInput && wInput.value) weight = wInput.value.trim();
                            }
                            
                            if (tag && tag !== "" && !tag.toUpperCase().includes("AHC TAG") && !tag.toUpperCase().includes("NO DATA")) {
                                data.push({
                                    "tag": tag, "category": itemCat,
                                    "purity": matCat, 
                                    "huid": (huid !== "-") ? huid : "",
                                    "weight": (weight !== "-") ? weight : ""
                                });
                            }
                        }
                    }
                }
                return data;
            }
            """
            
            all_data = []
            previous_data_state = None
            
            while True:
                if CANCEL_FETCH: 
                    break
                res = target_frame.evaluate(js_code)
                
                if res == previous_data_state: 
                    break
                    
                if res:
                    for item in res:
                        exists = next((True for x in all_data if x['tag'] == item['tag']), False)
                        if not exists: 
                            all_data.append(item)
                
                previous_data_state = res
                
                next_btn = target_frame.locator("a.paginate_button.next, a#tabWeight_next, li.next a, a:has-text('Next')").first
                
                if next_btn.count() > 0:
                    btn_class = next_btn.get_attribute("class") or ""
                    is_disabled = "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true" or next_btn.get_attribute("disabled") is not None
                    
                    if is_disabled:
                        break
                        
                    next_btn.evaluate("node => node.click()")
                    
                    t_wait = time.time()
                    while time.time() - t_wait < 10:
                        if CANCEL_FETCH: 
                            break
                        time.sleep(0.1) 
                        try:
                            if target_frame.evaluate(js_code) != previous_data_state: 
                                break
                        except: 
                            pass
                else: 
                    break

            if not actual_job_card: 
                actual_job_card = "UNKNOWN_JOB"

            if search_job_id and actual_job_card == search_job_id:
                tags_info = {item['tag']: {"huid": item['huid'], "weight": item.get('weight', '')} for item in all_data}
                if len(tags_info) > 0: 
                    return {"status": "success", "data": tags_info}
                else: 
                    return {"status": "error", "msg": "⚠️ Data khali hai!"}
            else:
                msg_text = f"Job card mismatch! Software: {search_job_id}, Website: {actual_job_card}" if search_job_id else f"Website par Job Card '{actual_job_card}' khula hai."
                return {
                    "status": "mismatch", 
                    "actual_job": actual_job_card, 
                    "tags_data": all_data, 
                    "msg": msg_text
                }
                
    except Exception as e: 
        return {"status": "error", "msg": f"System Error: {str(e)}"}
    finally:
        ACTIVE_BROWSER = None
        try:
            if 'browser' in locals() and browser:
                browser.disconnect()
        except: 
            pass