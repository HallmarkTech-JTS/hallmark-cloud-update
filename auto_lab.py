from playwright.sync_api import sync_playwright
import random

CDP_URL = "http://localhost:9222"

# ==============================================================
# 1. LAB INJECTION (HUMAN-LIKE & AUTO-SAVE)
# ==============================================================
def inject_lab_weight_ghost(lab_data=None):
    if not lab_data: return "⚠️ इंस्ट्रक्शन: कृपया पहले Excel या Database से डेटा लोड करें!"
    excel_job_card = lab_data.pop("excel_job_card", "UNKNOWN")
    
    sample_wt = lab_data.pop("sample_drawn_wt", None)
    button_wt = lab_data.pop("button_wt", None)

    if len(lab_data) == 0: return "⚠️ इंस्ट्रक्शन: इंजेक्ट करने के लिए डेटा नहीं मिला!"

    print(f"👻 Lab Smart Injection Started (JC: {excel_job_card})...")
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
            except: return "⚠️ सिक्योर ब्राउज़र ओपन नहीं है!"
            
            if len(browser.contexts) == 0: return "⚠️ ब्राउज़र में कोई टैब ओपन नहीं है!"

            browser.contexts[0].set_default_timeout(3000)
            bis_page = None
            
            for page in browser.contexts[0].pages:
                if "SamplingweightingDeatils" in page.url:
                    if excel_job_card != "UNKNOWN":
                        try:
                            site_job_card = ""
                            if page.locator("#selectedjobcard").count() > 0:
                                site_job_card = page.locator("#selectedjobcard").inner_text().strip()
                            elif page.locator("#str_job_no").count() > 0:
                                site_job_card = page.locator("#str_job_no").input_value().strip()

                            if excel_job_card in site_job_card:
                                bis_page = page
                                break 
                        except: continue 
                    else:
                        bis_page = page
                        break
            
            if not bis_page:
                try: browser.disconnect() 
                except: pass
                return f"❌ अलर्ट: Job Card '{excel_job_card}' साइट पर मैच नहीं हुआ!"

            # =======================================================
            # 🚨 MAGIC 1: POP-UP AUTO HANDLER (Never Sleeps!)
            # =======================================================
            bis_page.on("dialog", lambda dialog: dialog.accept())

            # =======================================================
            # 🚨 MAGIC 2: STRICT SEQUENTIAL FLOW 
            # =======================================================
            def human_type_and_save(selector_id, value, save_btn_index, step_name):
                val_str = str(value).strip()
                if val_str and val_str not in ["", "None"]:
                    try:
                        box = bis_page.locator(selector_id).first
                        if box.count() > 0:
                            print(f"⏳ Typing {step_name}: {val_str}")
                            box.evaluate("node => { node.removeAttribute('disabled'); node.removeAttribute('readonly'); }")
                            box.clear()
                            
                            # 🚨 FIX: wait_for_timeout ka use kiya taaki Pop-ups catch ho sakein
                            bis_page.wait_for_timeout(random.randint(200, 400))
                            box.type(val_str, delay=random.randint(80, 150))
                            bis_page.wait_for_timeout(random.randint(400, 600))
                            
                            save_btns = bis_page.locator("button:has-text('Save')")
                            if save_btns.count() > save_btn_index:
                                # force=True lagaya taaki click 100% ho
                                save_btns.nth(save_btn_index).click(force=True) 
                                print(f"✅ Clicked Save for {step_name}")
                                # Server processing ka wait
                                bis_page.wait_for_timeout(random.randint(2000, 2500)) 
                    except Exception as e:
                        print(f"⚠️ {step_name} Error: {e}")

           # 🛑 STEP 1: Sample Weight (Exact ID from site)
            human_type_and_save("#num_scrap_weight", sample_wt, 0, "Sample Weight")

            # 🛑 STEP 2: Button Weight
            human_type_and_save("#buttonweight", button_wt, 1, "Button Weight")

            # =======================================================
            # 🚨 MAGIC 3: TABLE M1/M2 INJECTION
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
                                    box.clear()
                                    bis_page.wait_for_timeout(random.randint(100, 300))
                                    box.type(val_str, delay=random.randint(80, 150))
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
                                try:
                                    enter_btn = row.locator("button:has-text('Enter')")
                                    if enter_btn.count() > 0:
                                        bis_page.wait_for_timeout(random.randint(300, 600))
                                        enter_btn.first.click(force=True)
                                        bis_page.wait_for_timeout(random.randint(500, 1000))
                                except Exception as e:
                                    print(f"Enter btn error: {e}")
                except Exception as e: 
                    print(f"⚠️ Error in row {strip_name}: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ SUCCESS: {filled_count} Rows & Main Weights Injected!"
    except Exception as e: 
        return f"⚠️ Error: {e}"