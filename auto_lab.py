from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:9222"

# ==============================================================
# 1. LAB INJECTION (FIRE ASSAYING)
# ==============================================================
def inject_lab_weight_ghost(lab_data=None):
    if not lab_data: return "⚠️ इंस्ट्रक्शन: कृपया पहले Excel या Database से डेटा लोड करें!"
    excel_job_card = lab_data.pop("excel_job_card", "UNKNOWN")
    if len(lab_data) == 0: return "⚠️ इंस्ट्रक्शन: इंजेक्ट करने के लिए डेटा नहीं मिला!"

    print(f"👻 Lab Smart Injection Started (JC: {excel_job_card})...")
    try:
        with sync_playwright() as p:
            try: 
                # ⏱️ TIMER 1: Sirf 3 second wait karega (Hang hone se bachayega)
                browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
            except: 
                return "⚠️ सिक्योर ब्राउज़र ओपन नहीं है!"
            
            if len(browser.contexts) == 0: 
                return "⚠️ ब्राउज़र में कोई टैब ओपन नहीं है!"

            # ⏱️ TIMER 2: Page element dhoondhne ke liye bhi sirf 3 second dega
            browser.contexts[0].set_default_timeout(3000)

            # =======================================================
            # 🎯 NAYA STRICT MATCHING LOGIC (Real HTML IDs Ke Sath)
            # =======================================================
            bis_page = None
            
            for page in browser.contexts[0].pages:
                if "SamplingweightingDeatils" in page.url:
                    if excel_job_card != "UNKNOWN":
                        try:
                            site_job_card = ""
                            # HTML ke asli ID se exact Job Card nikalna (100% accurate)
                            if page.locator("#selectedjobcard").count() > 0:
                                site_job_card = page.locator("#selectedjobcard").inner_text().strip()
                            elif page.locator("#str_job_no").count() > 0:
                                site_job_card = page.locator("#str_job_no").input_value().strip()

                            if excel_job_card in site_job_card:
                                bis_page = page
                                break # Sahi page mil gaya
                        except Exception as e:
                            print(f"Tab check error: {e}")
                            continue 
                    else:
                        bis_page = page
                        break
            
            if not bis_page:
                try: browser.disconnect() 
                except: pass
                if excel_job_card != "UNKNOWN":
                    return f"❌ अलर्ट: DB में Job Card '{excel_job_card}' है, पर साइट पर मैच नहीं हुआ! कृपया सही पेज खोलें।"
                else:
                    return "⚠️ Lab का पेज ओपन नहीं है!"
            # =======================================================

            filled_count = 0
            global_phase = 1
            first_strip_name = list(lab_data.keys())[0] 
            first_row = bis_page.locator("tr").filter(has=bis_page.get_by_text(first_strip_name, exact=True))
            
            if first_row.count() > 0:
                m1_box = first_row.locator("input").nth(0)
                m1_target = str(lab_data[first_strip_name].get("M1", "")).strip()
                if str(m1_box.evaluate("node => node.value")).strip() == m1_target and m1_target != "": 
                    global_phase = 2

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
                            if force_fill(0, weights.get("M1")) | force_fill(1, weights.get("SL")) | force_fill(2, weights.get("CU")) | force_fill(3, weights.get("LEAD")): 
                                filled_count += 1
                        elif global_phase == 2:
                            if force_fill(4, weights.get("M2")): 
                                filled_count += 1
                except Exception as e: 
                    print(f"⚠️ Error in row {strip_name}: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ SUCCESS: {filled_count} Rows Injected!"
    except Exception as e: 
        return f"⚠️ Error: {e}"