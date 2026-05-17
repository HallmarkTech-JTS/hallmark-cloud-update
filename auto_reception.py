from playwright.sync_api import sync_playwright
import time
import re
import eel  
import tkinter as tk  # 🚀 NAYA IMPORT POPUP KE LIYE

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
                                js_inject = f"""node => {{
                                    node.removeAttribute('disabled'); node.removeAttribute('readonly'); 
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
# 5. MASTER SCRAPING (Premium Scrollable Popup & Multi-Request)
# ==============================================================
def smart_scrape_with_huid():
    print("🚀 MASTER SCRAPER WITH PREMIUM POPUP TRIGGERED!")
    try:
        from playwright.sync_api import sync_playwright
        import time
        import eel
        import tkinter as tk
        from tkinter import ttk  # Scrollbar ke liye
        
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser connect nahi ho paya!"}
            
            list_page = None
            
            # 🚀 STEP 1: Find Master Table Frame
            for context in browser.contexts:
                for page in context.pages:
                    for frame in [page] + page.frames:
                        try:
                            if frame.locator("a:has-text('QM Job Card View')").count() > 0:
                                list_page = frame; break
                        except: pass
                    if list_page: break
                if list_page: break
            
            if list_page:
                print("🎯 Master Table Detected! Parsing Data...")
                
                # 🚀 STEP 2: Extract ALL Unique Requests and Jobs
                js_find_jobs = """
                () => {
                    let rows = document.querySelectorAll('tr');
                    let uniqueReqs = [];
                    let allData = [];
                    for(let r of rows) {
                        let cells = r.querySelectorAll('td');
                        if(cells.length > 5) {
                            let reqNo = cells[1].innerText.trim();
                            let jobNo = cells[4].innerText.trim();
                            let actionBtn = r.querySelector('a');
                            if (actionBtn && actionBtn.innerText.includes('QM Job Card View')) {
                                if (reqNo && !uniqueReqs.includes(reqNo)) {
                                    uniqueReqs.push(reqNo);
                                }
                                allData.push({req: reqNo, job: jobNo});
                            }
                        }
                    }
                    return { uniqueReqs: uniqueReqs, allData: allData };
                }
                """
                
                master_info = list_page.evaluate(js_find_jobs)
                
                if not master_info or not master_info.get("uniqueReqs"):
                    return {"status": "error", "msg": "⚠️ Table mein Request No. nahi mila!"}
                    
                unique_reqs = master_info["uniqueReqs"]
                all_data = master_info["allData"]
                
                print(f"📌 Found {len(unique_reqs)} Unique Requests.")
                
                # =======================================================
                # 🚀 STEP 3: SHOW PREMIUM WINDOWS POPUP (Scroll + Select All)
                # =======================================================
                selected_requests = []
                
                def show_popup():
                    root = tk.Tk()
                    root.title("SELECT REQUESTS")
                    root.attributes('-topmost', True)
                    root.configure(bg="#f8fafc")
                    
                    # Fix Window Size
                    window_width = 380
                    window_height = 450
                    x = (root.winfo_screenwidth() // 2) - (window_width // 2)
                    y = (root.winfo_screenheight() // 2) - (window_height // 2)
                    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
                    root.resizable(False, False) # Resize lock taaki design na bigde
                    
                    # Title
                    tk.Label(root, text="Select Requests to Fetch:", font=("Arial", 12, "bold"), bg="#f8fafc", fg="#0f172a").pack(pady=(15, 5))
                    
                    # Vars dictionary to track checkboxes
                    vars_dict = {}
                    
                    # --- Select All / Deselect All Buttons ---
                    btn_frame = tk.Frame(root, bg="#f8fafc")
                    btn_frame.pack(fill="x", padx=20, pady=5)
                    
                    def select_all():
                        for v in vars_dict.values(): v.set(True)
                    def deselect_all():
                        for v in vars_dict.values(): v.set(False)
                        
                    tk.Button(btn_frame, text="☑ Select All", command=select_all, bg="#e2e8f0", fg="#334155", font=("Arial", 9, "bold"), relief="flat", cursor="hand2").pack(side="left", expand=True, fill="x", padx=(0, 5))
                    tk.Button(btn_frame, text="☐ Deselect All", command=deselect_all, bg="#e2e8f0", fg="#334155", font=("Arial", 9, "bold"), relief="flat", cursor="hand2").pack(side="right", expand=True, fill="x", padx=(5, 0))
                    
                    # --- Scrollable List Area ---
                    list_container = tk.Frame(root, bg="white", highlightbackground="#cbd5e1", highlightthickness=1)
                    list_container.pack(fill="both", expand=True, padx=20, pady=10)
                    
                    canvas = tk.Canvas(list_container, bg="white", highlightthickness=0)
                    scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
                    scrollable_frame = tk.Frame(canvas, bg="white")
                    
                    scrollable_frame.bind(
                        "<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                    )
                    
                    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                    canvas.configure(yscrollcommand=scrollbar.set)
                    
                    canvas.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")
                    
                    # Mouse wheel scrolling enable
                    def _on_mousewheel(event):
                        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    canvas.bind_all("<MouseWheel>", _on_mousewheel)
                    
                    # Populate checkboxes
                    for req in unique_reqs:
                        var = tk.BooleanVar(value=True) # By default sab par tick
                        vars_dict[req] = var
                        tk.Checkbutton(scrollable_frame, text=f"  Request No:  {req}", variable=var, font=("Arial", 11), bg="white", fg="#334155", activebackground="white", cursor="hand2").pack(anchor="w", padx=10, pady=6)
                        
                    # --- Submit Button ---
                    def on_submit():
                        for r, v in vars_dict.items():
                            if v.get(): selected_requests.append(r)
                        canvas.unbind_all("<MouseWheel>") # Clean up
                        root.destroy()
                        
                    tk.Button(root, text="🚀 FETCH SELECTED DATA", command=on_submit, bg="#10b981", activebackground="#059669", fg="white", activeforeground="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", pady=8).pack(fill="x", padx=20, pady=(0, 20))
                    
                    root.mainloop()

                show_popup() # Call Popup
                
                if not selected_requests:
                    return {"status": "error", "msg": "⚠️ Aapne koi Request No. select nahi kiya!"}
                
                # 🚀 STEP 4: Filter Job Cards based on selection
                job_cards_to_process = [d['job'] for d in all_data if d['req'] in selected_requests]
                print(f"📦 Selected Job Cards to Process: {job_cards_to_process}")
                
                all_jobs_data = []

                # 🚀 STEP 5: Loop and Scrape Each Selected Job Card
                for jc_no in job_cards_to_process:
                    print(f"⏳ Opening Job Card: {jc_no}...")
                    try:
                        row_locator = list_page.locator(f"tr:has-text('{jc_no}')").first
                        action_link = row_locator.locator("a:has-text('QM Job Card View')").first
                        
                        browser_context = list_page.context if hasattr(list_page, 'context') else list_page.page.context
                        
                        with browser_context.expect_page(timeout=15000) as new_page_info:
                            action_link.click(force=True)
                        
                        new_page = new_page_info.value
                        new_page.wait_for_load_state("networkidle")
                        time.sleep(2) 
                        
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
                        for f in [new_page] + new_page.frames:
                            try:
                                res = f.evaluate(js_scrape_inner)
                                if res: items = res; break
                            except: pass
                        
                        if items: 
                            all_jobs_data.append({"job_card": jc_no, "items": items})
                            print(f"✅ Extracted {len(items)} items from {jc_no}")
                        else:
                            print(f"⚠️ Data not found in {jc_no} tab")
                            
                        new_page.close()
                        time.sleep(1) 
                        
                    except Exception as e:
                        print(f"⚠️ Error processing {jc_no}: {e}")

                # 🚀 STEP 6: Secret Internal DB Saving
                if len(all_jobs_data) > 0:
                    try:
                        save_func = eel._exposed_functions.get('wait_for_job_card_and_save')
                        if save_func:
                            for idx in range(1, len(all_jobs_data)):
                                j_data = all_jobs_data[idx]
                                info = {"type": "Job Card", "id": j_data["job_card"]}
                                save_func(j_data["items"], info)
                                print(f"💾 Job {j_data['job_card']} secretly saved to DB!")
                    except Exception as e:
                        print("Silent DB Save Error:", e)

                    first_job = all_jobs_data[0]
                    try: browser.disconnect()
                    except: pass
                    return {
                        "status": "success", 
                        "items": first_job["items"], 
                        "extracted_info": {"type": "Job Card", "id": first_job["job_card"]}
                    }
                else:
                    return {"status": "error", "msg": "⚠️ Selected Requests ke tabs se koi data nahi mila!"}
            
            # =======================================================
            # 🛡️ FALLBACK: SINGLE SCRAPING
            # =======================================================
            print("⚠️ Master page detect nahi hua! Fallback to normal scrape...")
            
            extracted_info = extract_id_from_page(browser)
            js_code_single = """
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
            
            for context in browser.contexts:
                for page in context.pages:
                    for frame in [page] + page.frames:
                        try:
                            res = frame.evaluate(js_code_single)
                            if res and len(res) > 0: 
                                target_frame = frame
                                break
                        except Exception: pass
                    if target_frame: break
                if target_frame: break

            if target_frame:
                previous_data = [] 
                while True:
                    res = target_frame.evaluate(js_code_single)
                    if res and len(res) > 0 and res != previous_data:
                        for item in res:
                            if item not in all_scraped_items:
                                all_scraped_items.append(item)
                        previous_data = res
                    
                    next_btn = target_frame.locator("a#tab_logic_next")
                    if next_btn.count() > 0:
                        btn_class = next_btn.get_attribute("class") or ""
                        if "disabled" in btn_class: break 
                        next_btn.click(force=True)
                        time.sleep(1.5) 
                    else:
                        break 
            
            try: browser.disconnect()
            except: pass
            
            if not all_scraped_items: 
                return {"status": "error", "msg": "⚠️ Data nahi mila! Please BIS portal par theek se page open kijiye."}
            
            return {"status": "success", "items": all_scraped_items, "extracted_info": extracted_info}
            
    except Exception as e: return {"status": "error", "msg": f"Script Error: {str(e)}"}