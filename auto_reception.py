from playwright.sync_api import sync_playwright
import time
import re
import eel  
import random
import queue
import concurrent.futures

# 🌟 NAYA: Web UI ke liye global Queue (Hang hone se bachane ke liye)
ui_queue = queue.Queue()

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
                    js_enable = """node => {
                        node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                    }"""
                    weight_input.evaluate(js_enable)
                    weight_input.focus()
                    weight_input.fill("")
                    time.sleep(random.uniform(0.1, 0.2)) 
                    weight_input.type(weight, delay=random.randint(30, 80)) 
                    
                    weight_input.evaluate("node => { node.dispatchEvent(new Event('input', { bubbles: true })); node.dispatchEvent(new Event('change', { bubbles: true })); }")
                    
                    save_btn = target_row.locator("text='Save'").first
                    if save_btn.is_visible():
                        main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                        main_page.once("dialog", lambda dialog: dialog.accept())
                        time.sleep(random.uniform(0.2, 0.4)) 
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
                    js_enable = """node => {
                        node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                    }"""
                    weight_input.evaluate(js_enable)
                    weight_input.focus()
                    weight_input.fill("")
                    time.sleep(random.uniform(0.1, 0.2)) 
                    weight_input.type(weight, delay=random.randint(30, 80)) 
                    
                    weight_input.evaluate("node => { node.dispatchEvent(new Event('input', { bubbles: true })); node.dispatchEvent(new Event('change', { bubbles: true })); }")
                    
                    save_btn = row.first.locator("text='Save'").first
                    if save_btn.is_visible():
                        main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                        main_page.once("dialog", lambda dialog: dialog.accept())
                        time.sleep(random.uniform(0.2, 0.4))
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
    print(f"👻 Auto Injection Started (Humanized Speed)... Job: {job_id}")
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL)
            except: return "⚠️ ब्राउज़र ओपन नहीं hai!"

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
                                js_enable = """node => {
                                    node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
                                }"""
                                weight_input.evaluate(js_enable)
                                
                                weight_input.focus()
                                weight_input.fill("")
                                time.sleep(random.uniform(0.1, 0.25)) 
                                
                                weight_input.type(weight, delay=random.randint(30, 70))
                                
                                weight_input.evaluate("node => { node.dispatchEvent(new Event('input', { bubbles: true })); node.dispatchEvent(new Event('change', { bubbles: true })); }")
                                
                                save_btn = target_row.locator("text='Save'").first
                                if save_btn.is_visible():
                                    main_page = target_frame if hasattr(target_frame, 'once') else target_frame.page
                                    main_page.once("dialog", lambda dialog: dialog.accept())
                                    
                                    time.sleep(random.uniform(0.2, 0.5)) 
                                    save_btn.click(force=True)
                                    
                                    base_delay = delay_ms / 1000.0
                                    time.sleep(base_delay + random.uniform(0.1, 0.6))
                                filled_count += 1
                except Exception as e: print(f"⚠️ Error: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ Success! {filled_count} Tags Save kar diye gaye."
    except Exception as e: return f"⚠️ Error: {e}"


# ==============================================================
# 4. DATA SCRAPING HELPERS
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
    for context in browser.contexts:
        for page in context.pages:
            for frame in [page] + page.frames:
                try:
                    res = frame.evaluate(js_code)
                    if res: return res
                except: pass
    return {"type": "Manual Scrape", "id": "Scraped_Job"}


# ==============================================================
# 5. MASTER SCRAPING ENGINE (Ultimate JS Detection + QUEUE MODAL)
# ==============================================================

def _smart_scrape_logic():
    try:
        from playwright.sync_api import sync_playwright
        import time
        import eel
        import random
        
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser connect nahi ho paya!"}
            
            master_info = None
            list_page = None
            
            # 🚀 STEP 1: ULTRA SMART DETECTION (JS Injection in all frames)
            js_find_jobs = """
            () => {
                let rows = document.querySelectorAll('tr');
                let reqMap = {};
                let count = 0;
                for(let r of rows) {
                    let cells = r.querySelectorAll('td');
                    if(cells.length >= 8) {
                        let reqNo = cells[1].innerText.trim();
                        let jobNo = cells[4].innerText.trim();
                        let actionBtn = r.querySelector('a');
                        if (actionBtn && actionBtn.innerText.includes('QM Job Card View')) {
                            // Check for valid numbers (length > 5)
                            if (reqNo.length > 5 && jobNo.length > 5 && !isNaN(reqNo)) {
                                if(!reqMap[reqNo]) reqMap[reqNo] = [];
                                reqMap[reqNo].push(jobNo);
                                count++;
                            }
                        }
                    }
                }
                if(count > 0) return reqMap;
                return null;
            }
            """
            
            print("🎯 Scanning all hidden frames for Master Table...")
            for context in browser.contexts:
                for page in context.pages:
                    for frame in [page] + page.frames:
                        try:
                            res = frame.evaluate(js_find_jobs)
                            if res:
                                master_info = res
                                list_page = frame
                                break
                        except: pass
                    if master_info: break
                if master_info: break
            
            if not master_info:
                return {"status": "error", "msg": "⚠️ Master Table Page nahi mila! Kripya BIS portal par List open karein."}
            
            print("🎯 Master Table Detected! Parsing Data...")
            
            # 🚀 SORTING MAGIC
            unique_reqs = sorted(list(master_info.keys()), key=lambda x: int(x) if str(x).isdigit() else 0, reverse=True)
            for req in unique_reqs:
                master_info[req] = sorted(list(set(master_info[req])), key=lambda x: int(x) if str(x).isdigit() else 0)
            
            # ========================================
            # 🌟 NAYA: PROFESSIONAL QUEUE TRIGGER
            # ========================================
            global ui_queue
            ui_queue = queue.Queue() # Purani queue clear
            
            try:
                print("📩 Calling JS Modal...")
                eel.open_reception_selector_modal(unique_reqs, master_info)()
                print("✅ Modal Signal Sent to Browser!")
            except Exception as e:
                return {"status": "error", "msg": f"UI Bridge Error: {e}"}
            
            # 🚨 FIX: Queue se result ka wait karega, block/hang nahi hoga
            print("⏳ Waiting for user input in Modal (Queue Mode)...")
            try:
                selected_requests = ui_queue.get(timeout=300) # 5 minutes time limit
            except queue.Empty:
                return {"status": "error", "msg": "⚠️ Time out! Modal response nahi mila."}
            
            if not selected_requests:
                return {"status": "error", "msg": "⚠️ User ne Cancel button dabaya."}
            # ========================================
            
            # 🌟 NAYA CODE: Request Number aur Job Card ko ek sath map karke list me daalna
            job_cards_to_process = []
            for req in selected_requests:
                for jc in master_info[req]:
                    job_cards_to_process.append({"req_no": req, "job_card": jc})
                
            print(f"📦 Arranged Jobs to Fetch: {[j['job_card'] for j in job_cards_to_process]}")
            all_jobs_data = []

            # =======================================================
            # ⚡ STEP 5: ANTI-BOT HUMANIZED SCRAPING LOOP
            # =======================================================
            for job_info in job_cards_to_process:
                jc_no = job_info["job_card"]
                req_no = job_info["req_no"]
                
                print(f"⚡ Humanized Fetching: {jc_no} (Req: {req_no})...")
                try:
                    row_locator = list_page.locator(f"tr:has-text('{jc_no}')").first
                    action_link = row_locator.locator("a").last # Last action button pakdega
                    
                    time.sleep(random.uniform(0.3, 0.8)) 
                    
                    browser_context = list_page.context if hasattr(list_page, 'context') else list_page.page.context
                    
                    with browser_context.expect_page(timeout=15000) as new_page_info:
                        # 🌟 FIX: Element not visible error ko bypass karne ke liye JAVASCRIPT Click!
                        action_link.evaluate("node => node.click()")
                    
                    new_page = new_page_info.value
                    new_page.wait_for_load_state("domcontentloaded")
                    
                    js_scrape_inner = """
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
                    
                    items = None
                    for _ in range(15):  
                        for f in [new_page] + new_page.frames:
                            try:
                                res = f.evaluate(js_scrape_inner)
                                if res: items = res; break
                            except: pass
                        if items: break
                        time.sleep(0.2)  
                    
                    if items: 
                        # 🌟 NAYA CODE: Req No DB me bhejne ke liye add kiya
                        all_jobs_data.append({"job_card": jc_no, "req_no": req_no, "items": items})
                        print(f"✅ Secure Grab: {len(items)} items from {jc_no}")
                        time.sleep(random.uniform(0.2, 0.5))
                    else:
                        print(f"⚠️ Data not found in {jc_no} tab")
                        
                    new_page.close()
                    
                except Exception as e:
                    print(f"⚠️ Error processing {jc_no}: {e}")

            if len(all_jobs_data) > 0:
                try:
                    # Backend data silent save for idx 1 to N
                    save_func = eel._exposed_functions.get('wait_for_job_card_and_save')
                    if save_func:
                        for idx in range(1, len(all_jobs_data)):
                            j_data = all_jobs_data[idx]
                            info = {"type": "Job Card", "id": j_data["job_card"], "req_no": j_data["req_no"]}
                            save_func(j_data["items"], info)
                except Exception as e:
                    print("Silent DB Save Error:", e)

                first_job = all_jobs_data[0]
                try: browser.disconnect()
                except: pass
                
                # 🌟 NAYA CODE: Frontend ko bhi req_no bheja ja raha hai bundle karne ke liye
                return {
                    "status": "success", 
                    "items": first_job["items"], 
                    "extracted_info": {"type": "Job Card", "id": first_job["job_card"], "req_no": first_job["req_no"]}
                }
            else:
                return {"status": "error", "msg": "⚠️ Selected Requests ke tabs se koi data nahi mila!"}
            
    except Exception as e: return {"status": "error", "msg": f"Script Error: {str(e)}"}

# ==============================================================
# 🚀 NAYA: GUARANTEED EVENT LOOP FIX (THREAD-SAFE WRAPPER)
# ==============================================================

def smart_scrape_with_huid():
    print("🚀 THREAD-SAFE TURBO SCRAPER CALLED!")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_smart_scrape_logic)
            return future.result()
    except Exception as e:
        return {"status": "error", "msg": f"Thread Error: {str(e)}"}

# ==============================================================
# 6. WAIT FOR JOB CARD NO
# ==============================================================
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
# 7. AUTO GENERATE REQUEST & JOB CARDS (Master Automation)
# ==============================================================
def auto_generate_request_and_jobs(jeweller_code, state, items_list):
    print("🚀 Master Automation Started: Request -> Job Cards")
    try:
        with sync_playwright() as p:
            try: 
                browser = p.chromium.connect_over_cdp(CDP_URL)
                page = browser.contexts[0].pages[0] 
            except: 
                return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}

            page.locator("text=Create Hallmarking Request").first.click()
            page.locator("text=PROCESSING").wait_for(state="hidden")

            page.locator("span:has-text('Select State')").first.click()
            page.locator("input[role='textbox']").fill(state)
            page.keyboard.press("Enter")

            page.locator("span:has-text('Select Jeweller Name')").first.click()
            page.locator("input[role='textbox']").fill(jeweller_code)
            time.sleep(1) 
            page.keyboard.press("Enter")

            for item in items_list:
                page.locator("text=Add Items").first.click()
                page.locator("span:has-text('Enter category')").first.click()
                page.keyboard.type(item['category'])
                page.keyboard.press("Enter")
                page.locator("input[placeholder='Enter quantity']").fill(str(item['quantity']))
                page.locator("input[placeholder='Enter weight']").fill(str(item['weight']))
                page.locator("button:has-text('Save')").first.click()
                page.locator("text=PROCESSING").wait_for(state="hidden")

            page.locator("button:has-text('Submit to AHC')").first.click()
            page.locator("text=PROCESSING").wait_for(state="hidden")

            req_text = page.locator("h4:has-text('Request Number is :')").inner_text()
            request_number = req_text.split(":")[-1].strip()

            page.locator("text=Home Page").first.click()
            page.locator("text=PROCESSING").wait_for(state="hidden")
            page.locator("div:has-text('New request')").nth(1).click()
            page.locator("text=PROCESSING").wait_for(state="hidden")

            row = page.locator(f"tr:has-text('{request_number}')")
            row.locator("a[title='Action']").first.click()
            page.locator("text=PROCESSING").wait_for(state="hidden")

            page.locator("input[type='radio'][value='Yes']").first.check()
            rows = page.locator("table tbody tr").all()
            for index, tr in enumerate(rows):
                if index < len(items_list):
                    item = items_list[index]
                    tr.locator("input[title='Observed Item Category Weight(Gms)']").fill(str(item['weight']))
                    cat_prefix = item['category'][:2].lower() 
                    tags = "\n".join([f"{cat_prefix}{i+1}" for i in range(int(item['quantity']))])
                    tr.locator("input[title='Tag Id (AHC)']").fill(tags)
                    tr.locator("input[type='checkbox']").first.check()

            page.locator("input[placeholder='Enter AHC Receiving remarks']").fill("ok")
            page.once("dialog", lambda dialog: dialog.accept()) 
            page.locator("button:has-text('Submit')").first.click()
            page.locator("text=PROCESSING").wait_for(state="hidden")

            job_card_text = page.locator("h4:has-text('Job Card Created')").inner_text()
            job_cards = [x.strip() for x in job_card_text.split("Created")[-1].split(",") if x.strip()]
            
            try: browser.disconnect()
            except: pass

            return {
                "status": "success", 
                "request_number": request_number, 
                "job_cards": job_cards
            }
    except Exception as e: 
        return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}

# ==============================================================
# 🌟 NAYA FEATURE: RECEPTION WEB POPUP BRIDGE
# ==============================================================
@eel.expose
def submit_reception_selection(selected):
    global ui_queue
    ui_queue.put(selected)

@eel.expose
def cancel_reception_selection():
    global ui_queue
    ui_queue.put([]) # Empty list ka matlab cancel