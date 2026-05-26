from playwright.sync_api import sync_playwright
import time
import re

# Playwright ke liye local browser ka URL
CDP_URL = "http://localhost:9222"

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

            row = target_frame.locator("tr").filter(has=target_frame.locator("td").get_by_text(tag_id, exact=True))
            
            if row.count() > 0:
                target_row = row.first
                weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                
                if weight_input.count() > 0:
                    # 🚨 NEW BYPASS: No Click, No Keyboard. Direct Backend Injection!
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
                        save_btn.click(force=True)
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
                    # 🚨 NEW BYPASS
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
                        save_btn.click(force=True)
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
                tag_id, weight = str(item[0]).strip(), str(item[1]).strip()
                
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

                if not target_frame: continue

                try:
                    row = target_frame.locator("tr").filter(has=target_frame.locator("td").get_by_text(tag_id, exact=True))
                    
                    if row.count() > 0:
                        target_row = row.first
                        weight_input = target_row.locator("input.weightCls, input.scan-input, input[name='articlWeight'], input:not([type='hidden']):not([type='checkbox'])").first
                        
                        if weight_input.count() > 0:
                            current_val = str(weight_input.evaluate("node => node.value")).strip()
                            if current_val != weight:
                                # 🚨 NEW BYPASS: Backend Data Injection Only
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
                                    save_btn.click(force=True)
                                    time.sleep(delay_ms / 1000.0)
                                
                                filled_count += 1
                except Exception as e: print(f"⚠️ Error: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ Success! {filled_count} Tags Save kar diye gaye."
    except Exception as e: return f"⚠️ Error: {e}"


# ==============================================================
# 4. DATA SCRAPING & 5. WAIT FOR JOB CARD
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

def smart_scrape_with_huid():
    print("👻 Scraping Table from BIS...")
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser connect nahi ho paya!"}
            
            extracted_info = extract_id_from_page(browser)
            js_code = """
            () => {
                let results = [];
                let tables = document.querySelectorAll('table');
                for (let t of tables) {
                    let text = t.innerText.toUpperCase();
                    if (text.includes('TAG ID') || text.includes('AHC TAG')) {
                        let rows = t.querySelectorAll('tr');
                        let tagIdx = -1, catIdx = -1, huidIdx = -1, purIdx = -1;
                        for(let r of rows) {
                            let headers = Array.from(r.querySelectorAll('th, td')).map(cell => cell.innerText.trim().toUpperCase());
                            tagIdx = headers.findIndex(h => h.includes('TAG ID') || h.includes('AHC TAG'));
                            if(tagIdx !== -1) {
                                catIdx = headers.findIndex(h => h.includes('CATEGORY'));
                                huidIdx = headers.findIndex(h => h.includes('HUID'));
                                purIdx = headers.findIndex(h => h.includes('PURITY'));
                                break;
                            }
                        }
                        if(tagIdx === -1) continue;
                        for (let r of rows) {
                            let cells = r.querySelectorAll('td');
                            if (cells.length > tagIdx) {
                                let tag = cells[tagIdx].innerText.trim();
                                if (!tag || tag.toUpperCase().includes('TAG')) continue;
                                let cat = (catIdx !== -1 && cells.length > catIdx && cells[catIdx]) ? cells[catIdx].innerText.trim() : "-";
                                let huid = (huidIdx !== -1 && cells.length > huidIdx && cells[huidIdx]) ? cells[huidIdx].innerText.trim() : "";
                                let pur = (purIdx !== -1 && cells.length > purIdx && cells[purIdx]) ? cells[purIdx].innerText.trim() : "-";
                                if (huid !== "") { cat = cat + " (HUID: " + huid + ")"; }
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
            target_frame = None
            
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        res = frame.evaluate(js_code)
                        if res and len(res) > 0: 
                            target_frame = frame
                            break
                    except Exception: pass
                if target_frame: break

            if target_frame:
                previous_data = [] 
                while True:
                    res = target_frame.evaluate(js_code)
                    if res and len(res) > 0 and res != previous_data:
                        for item in res:
                            if item not in all_scraped_items:
                                all_scraped_items.append(item)
                        previous_data = res
                    
                    next_btn = target_frame.locator("a#tab_logic_next")
                    
                    # Button ki class check kar rahe hain
                    btn_class = next_btn.get_attribute("class") if next_btn.count() > 0 else ""
                    
                    # Agar button hai aur 'disabled' nahi hai, tabhi click karega
                    if next_btn.count() > 0 and "disabled" not in btn_class:
                        print(f"➡️ Page Load ho raha hai... (Abhi tak {len(all_scraped_items)} items mile)")
                        next_btn.click()
                        time.sleep(1.5) 
                    else:
                        break 
            
            scraped_items = all_scraped_items 
            try: browser.disconnect()
            except: pass
            if not scraped_items: return {"status": "error", "msg": "⚠️ Data nahi mila!"}
            return {"status": "success", "items": scraped_items, "extracted_info": extracted_info}
    except Exception as e: return {"status": "error", "msg": str(e)}

def wait_for_job_card_no():
    print("👻 Waiting for Job Card Generation...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            job_card_no = None
            for _ in range(45): 
                for page in browser.contexts[0].pages:
                    for frame in [page] + page.frames:
                        try:
                            text = frame.locator("body").inner_text()
                            if "Job Card Created" in text:
                                match = re.search(r"Job Card Created\s*[:\-]?\s*(\d{8,})", text, re.IGNORECASE)
                                if match: job_card_no = match.group(1); break
                        except: pass
                    if job_card_no: break
                if job_card_no: break
                time.sleep(1)
            try: browser.disconnect()
            except: pass
            if not job_card_no: return {"status": "error", "msg": "⚠️ Time out!"}
            return {"status": "success", "job_card": job_card_no}
    except Exception as e: return {"status": "error", "msg": str(e)}

# ==============================================================
# 🌟 NAYA FEATURE: 100% LIVE WEB SCRAPING & TAB MANAGEMENT
# ==============================================================
def scrape_all_requests_from_main():
    """Main page par sabhi pages ko (Next click karke) padhna aur Request/Job list banana"""
    print("🌐 Website ke Main Dashboard se data fetch kar rahe hain...")
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

            target_page = browser.contexts[0].pages[0] 

            js_code = """
            () => {
                let results = {};
                let rows = document.querySelectorAll('table tbody tr');
                
                for(let r of rows) {
                    let cells = Array.from(r.querySelectorAll('td')).map(td => td.innerText.trim());
                    let numbers = cells.filter(text => text.match(/^\\d{8,}$/));
                    
                    if (numbers.length >= 2) {
                        let req = numbers[0]; 
                        let job = numbers[1]; 
                        if(!results[req]) results[req] = [];
                        if(!results[req].includes(job)) results[req].push(job);
                    } else if (numbers.length === 1) {
                        let job = numbers[0];
                        let req = "UNKNOWN";
                        if(!results[req]) results[req] = [];
                        if(!results[req].includes(job)) results[req].push(job);
                    }
                }
                return results;
            }
            """

            all_data = {}
            previous_data_state = None # Pichle page ka data yaad rakhne ke liye

            while True:
                res = target_page.evaluate(js_code)
                
                # Check agar data update nahi hua (matlab next page load nahi hua)
                if res == previous_data_state:
                    print("🛑 Aakhri page aa gaya (Data repeat ho raha hai). Loop break kar rahe hain.")
                    break
                    
                if res:
                    for req, jobs in res.items():
                        if req not in all_data: all_data[req] = []
                        for j in jobs:
                            if j not in all_data[req]: all_data[req].append(j)

                previous_data_state = res # Current data ko save kar lo agli checking ke liye

                next_btn = target_page.locator("a.paginate_button.next, button.next, a:has-text('Next')").last
                
                # Naya check: aria-disabled bhi check karega
                btn_class = next_btn.get_attribute("class") or ""
                is_disabled = "disabled" in btn_class or next_btn.get_attribute("aria-disabled") == "true" or next_btn.get_attribute("disabled") is not None

                if next_btn.count() > 0 and not is_disabled:
                    print("➡️ Website ke agle panne (Next Page) par jaa rahe hain...")
                    next_btn.click(force=True)
                    time.sleep(2.0) # Thoda extra time do page load hone ke liye
                else:
                    break 

            try: browser.disconnect()
            except: pass

            if not all_data:
                return {"status": "error", "msg": "⚠️ Website par koi Request/Job Data nahi mila!"}

            return {"status": "success", "data": all_data}
    except Exception as e: return {"status": "error", "msg": str(e)}


def process_selected_requests(selected_reqs, master_info):
    """Website par QM View kholna, Tag/Purity nikalna, aur tab band karna"""
    print(f"🌐 Website par selected requests ki scraping shuru: {selected_reqs}")
    from modules import database as db
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            context = browser.contexts[0]
            main_page = context.pages[0]

            # 🛡️ QA FIX: Reset main dashboard to first page before query loops to prevent offset isolation
            try:
                main_page.evaluate('() => { let f = document.querySelector(".paginate_button.first, a:has-text(\\"First\\")"); if(f) f.click(); }')
                time.sleep(1.0)
            except: pass

            total_jobs_saved = 0

            for req in selected_reqs:
                jobs = master_info.get(req, [])
                for job in jobs:
                    print(f"🔍 Website par Job dhundh rahe hain: {job}")

                    search_box = main_page.locator("input[type='search']").first
                    if search_box.count() > 0:
                        search_box.fill(job)
                        time.sleep(1.5) 

                    row = main_page.locator("tr", has_text=job).first
                    if row.count() == 0:
                        print(f"⚠️ Website par Job {job} nahi mila.")
                        continue

                    view_btn = row.locator("a").last 

                    try:
                        with context.expect_page(timeout=10000) as new_page_info:
                            view_btn.click()
                        new_page = new_page_info.value
                        new_page.wait_for_load_state("networkidle")
                        time.sleep(2) 
                    except Exception as e:
                        print(f"⚠️ Naya tab kholne me dikkat: {e}")
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
                    while True:
                        res = new_page.evaluate(js_code_tags)
                        if res and len(res) > 0:
                            for item in res:
                                if item not in all_scraped_items:
                                    all_scraped_items.append(item)

                        next_btn = new_page.locator("a#tab_logic_next, a.paginate_button.next").last
                        if next_btn.count() > 0 and "disabled" not in (next_btn.get_attribute("class") or ""):
                            next_btn.click()
                            time.sleep(1.5)
                        else:
                            break 

                    print(f"✅ Website se {len(all_scraped_items)} tags fetch kiye.")

                    try: new_page.close()
                    except: pass

                    if all_scraped_items:
                        db.save_scraped_job_card(job, all_scraped_items, request_no=req)
                        total_jobs_saved += 1

                    main_page.bring_to_front()

                    if search_box.count() > 0:
                        search_box.fill("")
                        time.sleep(0.5)

            try: browser.disconnect()
            except: pass
            return {"status": "success", "msg": f"✅ Website se Data Fetch ho gaya! {total_jobs_saved} Jobs Database mein save ho gaye."}
            
    except Exception as e: return {"status": "error", "msg": str(e)}