from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"

# ==============================================================
# 1. LAB INJECTION (FIRE ASSAYING)
# ==============================================================
def inject_lab_weight_ghost(lab_data=None):
    if not lab_data: return "⚠️ इंस्ट्रक्शन: कृपया पहले Excel फाइल लोड करें!"
    excel_job_card = lab_data.pop("excel_job_card", "UNKNOWN")
    if len(lab_data) == 0: return "⚠️ इंस्ट्रक्शन: Excel में डेटा नहीं मिला!"

    print(f"👻 Lab Smart Injection Started (JC: {excel_job_card})...")
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL)
            except: return "⚠️ सिक्योर ब्राउज़र ओपन नहीं है!"
            if len(browser.contexts) == 0: return "⚠️ टैब नहीं है!"

            bis_page = next((page for page in browser.contexts[0].pages if "SamplingweightingDeatils" in page.url), None)
            if not bis_page: return "⚠️ Lab का पेज ओपन नहीं है!"

            if excel_job_card != "UNKNOWN" and excel_job_card not in bis_page.content():
                try: browser.disconnect() 
                except: pass
                return f"❌ अलर्ट: Excel में Job Card '{excel_job_card}' है, पर साइट पर नहीं मिला!"

            filled_count = 0
            global_phase = 1
            first_strip_name = list(lab_data.keys())[0] 
            first_row = bis_page.locator("tr").filter(has=bis_page.get_by_text(first_strip_name, exact=True))
            
            if first_row.count() > 0:
                m1_box = first_row.locator("input").nth(0)
                m1_target = str(lab_data[first_strip_name].get("M1", "")).strip()
                if str(m1_box.evaluate("node => node.value")).strip() == m1_target and m1_target != "": global_phase = 2

            for strip_name, weights in lab_data.items():
                try:
                    row = bis_page.locator("tr").filter(has=bis_page.get_by_text(strip_name, exact=True))
                    if row.count() > 0:
                        inputs = row.locator("input")
                        def force_fill(idx, val):
                            if inputs.count() > idx and val:
                                box = inputs.nth(idx)
                                val_str = str(val).strip()
                                if str(box.evaluate("node => node.value")).strip() != val_str:
                                    box.evaluate("node => { node.removeAttribute('disabled'); node.removeAttribute('readonly'); }")
                                    box.fill(val_str)
                                    box.evaluate("node => node.dispatchEvent(new Event('input', { bubbles: true }))")
                                    box.evaluate("node => node.dispatchEvent(new Event('change', { bubbles: true }))")
                                    return True
                            return False

                        if global_phase == 1:
                            if force_fill(0, weights.get("M1")) | force_fill(1, weights.get("SL")) | force_fill(2, weights.get("CU")) | force_fill(3, weights.get("LEAD")): filled_count += 1
                        elif global_phase == 2:
                            if force_fill(4, weights.get("M2")): filled_count += 1
                except Exception as e: print(f"⚠️ Error: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ SUCCESS: {filled_count} Rows Injected!"
    except Exception as e: return f"⚠️ Error: {e}"


# ==============================================================
# 2. RECEPTION INJECTION (LIVE STEP-BY-STEP - EXACT MATCH)
# ==============================================================
def inject_single_reception_tag(job_id, tag_id, weight):
    """User button dabayega tab sirf 1 specific Tag me wajan dalega aur Save karega."""
    tag_id, weight = str(tag_id).strip(), str(weight).strip()
    print(f"👻 Live Injecting Tag: {tag_id} | Weight: {weight}g")
    
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL)
            except: return {"status": "error", "msg": "⚠️ Secure BIS Browser open nahi hai!"}
            
            bis_page = next((page for page in browser.contexts[0].pages if "UID_WeighingForm" in page.url), None)
            if not bis_page: return {"status": "error", "msg": "⚠️ Reception wala page open nahi hai!"}
            
            if job_id not in bis_page.content():
                try: browser.disconnect()
                except: pass
                return {"status": "error", "msg": f"❌ Wrong Page! Site par Job Card '{job_id}' nahi hai."}

            # 🎯 STRICT EXACT MATCH (Sirf 2nd column aur editable table me)
            row = bis_page.locator("tr").filter(
                has=bis_page.locator("td:nth-child(2)").get_by_text(tag_id, exact=True)
            ).filter(has=bis_page.locator("input[type='text']"))
            
            if row.count() > 0:
                target_row = row.first
                weight_input = target_row.locator("input[type='text']")
                
                if weight_input.count() > 0:
                    weight_input.evaluate("node => { node.removeAttribute('disabled'); node.removeAttribute('readonly'); }")
                    weight_input.fill(weight)
                    weight_input.evaluate("node => node.dispatchEvent(new Event('input', { bubbles: true }))")
                    weight_input.evaluate("node => node.dispatchEvent(new Event('change', { bubbles: true }))")
                    
                    # 🎯 AUTO SAVE & CONFIRM POPUP
                    save_btn = target_row.locator("text='Save'").first
                    if save_btn.is_visible():
                        bis_page.once("dialog", lambda dialog: dialog.accept())
                        save_btn.click(force=True)
                        bis_page.wait_for_timeout(1000) # 1 sec wait for reload
                        
                    try: browser.disconnect()
                    except: pass
                    return {"status": "success", "msg": f"✅ Tag '{tag_id}' Saved ({weight}g)"}
                else: return {"status": "error", "msg": "⚠️ Input box nahi mila!"}
            else: return {"status": "error", "msg": f"⚠️ Tag '{tag_id}' Editable list me nahi mila."}
    except Exception as e: return {"status": "error", "msg": f"⚠️ Error: {str(e)}"}


# ==============================================================
# 3. RECEPTION AUTO FULL LIST (SPEED CONTROL)
# ==============================================================
def inject_reception_weight_ghost(job_id, job_data, delay_ms=1500):
    if not job_data: return "⚠️ डेटाबेस खाली है।"
    print(f"👻 Auto Injection Started (Speed: {delay_ms}ms)...")

    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL)
            except: return "⚠️ ब्राउज़र ओपन नहीं है!"
            bis_page = next((page for page in browser.contexts[0].pages if "UID_WeighingForm" in page.url), None)
            if not bis_page: return "⚠️ Reception पेज नहीं है!"

            if job_id not in bis_page.content():
                try: browser.disconnect()
                except: pass
                return f"❌ Job Card Mismatch!"

            filled_count = 0
            for item in job_data:
                tag_id, weight = str(item[0]).strip(), str(item[1]).strip()
                try:
                    row = bis_page.locator("tr").filter(
                        has=bis_page.locator("td:nth-child(2)").get_by_text(tag_id, exact=True)
                    ).filter(has=bis_page.locator("input[type='text']"))
                    
                    if row.count() > 0:
                        target_row = row.first
                        weight_input = target_row.locator("input[type='text']")
                        if weight_input.count() > 0 and str(weight_input.evaluate("node => node.value")).strip() != weight:
                            weight_input.evaluate("node => { node.removeAttribute('disabled'); node.removeAttribute('readonly'); }")
                            weight_input.fill(weight)
                            weight_input.evaluate("node => node.dispatchEvent(new Event('input', { bubbles: true }))")
                            weight_input.evaluate("node => node.dispatchEvent(new Event('change', { bubbles: true }))")
                            
                            save_btn = target_row.locator("text='Save'").first
                            if save_btn.is_visible():
                                bis_page.once("dialog", lambda dialog: dialog.accept())
                                save_btn.click(force=True)
                                bis_page.wait_for_timeout(delay_ms) # User ki speed ke hisab se rukega
                            
                            filled_count += 1
                except Exception as e: print(f"⚠️ Error: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ Success! {filled_count} Tags Save kar diye gaye."
    except Exception as e: return f"⚠️ Error: {e}"