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
# 4. DATA SCRAPING & 5. WAIT FOR JOB CARD (Unchanged)
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
            
            # 1. Pehle us frame ko dhoondo jisme table hai
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        res = frame.evaluate(js_code)
                        if res and len(res) > 0: 
                            target_frame = frame
                            break
                    except Exception: pass
                if target_frame: break

            # 2. Agar table mil gayi, toh 'Next' button dabane wala Loop chalao
            if target_frame:
                previous_data = [] # Data repeat hone se bachane ke liye
                while True:
                    # Current page ka data nikalo
                    res = target_frame.evaluate(js_code)
                    
                    # Naya data apne main dibbe me dalo (Bina duplicate ke)
                    if res and len(res) > 0 and res != previous_data:
                        for item in res:
                            if item not in all_scraped_items:
                                all_scraped_items.append(item)
                        previous_data = res
                    
                    # Next button check karo
                    next_btn = target_frame.locator("a#tab_logic_next")
                    if next_btn.count() > 0:
                        btn_class = next_btn.get_attribute("class") or ""
                        if "disabled" in btn_class:
                            break # 🚨 Aakhiri page aa gaya, loop khatam!
                        
                        print(f"➡️ Page Load ho raha hai... (Abhi tak {len(all_scraped_items)} items mile)")
                        next_btn.click()
                        time.sleep(1.5) # Naya data aane ka wait (Zaroori hai)
                    else:
                        break # Agar Next button hai hi nahi toh ruk jao
            
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
# 🌟 NAYA FEATURE: BATCH REQUEST SCRAPING & POPUP HANDLING
# ==============================================================

def scrape_all_requests_from_main():
    """Main page ke sabhi pages (Next daba kar) se Request No aur Job Cards nikalna"""
    print("👻 Scraping Requests from Main Dashboard...")
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser connect nahi ho paya!"}

            target_page = browser.contexts[0].pages[0] 

            js_code = """
            () => {
                let results = {};
                let rows = document.querySelectorAll('table tbody tr');
                let headers = Array.from(document.querySelectorAll('table th')).map(th => th.innerText.trim().toUpperCase());
                
                let reqIdx = headers.findIndex(h => h.includes('REQUEST') || h.includes('REQ NO'));
                let jobIdx = headers.findIndex(h => h.includes('JOB CARD') || h.includes('JOB NO') || h.includes('JOB'));

                for(let r of rows) {
                    let cells = r.querySelectorAll('td');
                    let req = "";
                    let job = "";

                    if (reqIdx !== -1 && jobIdx !== -1 && cells.length > Math.max(reqIdx, jobIdx)) {
                        req = cells[reqIdx].innerText.trim();
                        job = cells[jobIdx].innerText.trim();
                    } else {
                        let nums = Array.from(cells).map(c => c.innerText.trim()).filter(t => t.match(/^\\d{8,}$/));
                        if (nums.length >= 2) { req = nums[0]; job = nums[1]; } 
                        else if (nums.length === 1) { job = nums[0]; req = "UNKNOWN"; }
                    }

                    if(req && job && req.match(/\\d+/) && job.match(/\\d+/)) {
                        if(!results[req]) results[req] = [];
                        if(!results[req].includes(job)) results[req].push(job);
                    }
                }
                return results;
            }
            """

            all_data = {}
            while True:
                res = target_page.evaluate(js_code)
                if res:
                    for req, jobs in res.items():
                        if req not in all_data: all_data[req] = []
                        for j in jobs:
                            if j not in all_data[req]: all_data[req].append(j)

                next_btn = target_page.locator("a.paginate_button.next, button.next, a:has-text('Next')").last
                if next_btn.count() > 0 and "disabled" not in (next_btn.get_attribute("class") or ""):
                    print("➡️ Changing page on Main Dashboard...")
                    next_btn.click()
                    time.sleep(1.5)
                else:
                    break 

            try: browser.disconnect()
            except: pass

            if not all_data:
                return {"status": "error", "msg": "⚠️ Main page par koi Request/Job Data nahi mila!"}

            return {"status": "success", "data": all_data}
    except Exception as e: return {"status": "error", "msg": str(e)}


def process_selected_requests(selected_reqs, master_info):
    """User ke select kiye gaye requests ko ek-ek karke open karna aur fetch karna"""
    print(f"👻 Processing Selected Requests: {selected_reqs}")
    from modules import database as db
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            context = browser.contexts[0]
            main_page = context.pages[0]

            total_jobs_saved = 0

            for req in selected_reqs:
                jobs = master_info.get(req, [])
                for job in jobs:
                    print(f"🔍 Fetching Data for Job: {job} (Req: {req})")

                    search_box = main_page.locator("input[type='search']").first
                    if search_box.count() > 0:
                        search_box.fill(job)
                        time.sleep(1) 

                    row = main_page.locator(f"tr", has_text=job).first
                    if row.count() == 0:
                        print(f"⚠️ Job {job} UI me row nahi mila, skipping.")
                        continue

                    view_btn = row.locator("a, button, [title*='QM'], [title*='View'], img[alt*='View']").filter(has_text=re.compile(r'QM|View', re.I)).first
                    if view_btn.count() == 0:
                        view_btn = row.locator("a").last 

                    try:
                        with context.expect_page(timeout=10000) as new_page_info:
                            view_btn.click()
                        new_page = new_page_info.value
                        new_page.wait_for_load_state("networkidle")
                        time.sleep(1)
                    except Exception as e:
                        print(f"⚠️ Failed to open new tab for Job {job}: {e}")
                        continue

                    js_code_tags = """
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

                    print(f"✅ Extracted {len(all_scraped_items)} tags for Job: {job}")

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
            return {"status": "success", "msg": f"✅ Done! Successfully processed and saved {total_jobs_saved} Job Cards."}
            
    except Exception as e: return {"status": "error", "msg": str(e)}