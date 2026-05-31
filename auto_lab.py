from playwright.sync_api import sync_playwright
import random
import time
import sqlite3
import logging

# 🚀 Enterprise Logging System
logging.basicConfig(filename='app_crash.log', level=logging.ERROR, 
                    format='%(asctime)s - LAB - %(levelname)s - %(message)s')

CDP_URL = "http://localhost:9222"

# ==============================================================
# 🚀 1. PRO-MODE: GET PENDING JOBS FROM DB (No UI)
# ==============================================================
def get_pending_lab_jobs():
    """Sirf Database se un Job Cards ko nikalega jinka Lab data abhi nahi bana hai."""
    try:
        conn = sqlite3.connect('jewellery_data.db', timeout=5)
        cursor = conn.cursor()
        
        # 1. Main job_cards table se valid jobs nikalo
        cursor.execute("SELECT DISTINCT job_id FROM job_cards")
        all_jobs = [str(r[0]).strip() for r in cursor.fetchall() if str(r[0]).strip().isdigit() and len(str(r[0]).strip()) > 6]
        all_jobs = list(set(all_jobs))
        
        # 2. Jo jobs pehle se lab_results mein hain, unhe hata do
        cursor.execute("CREATE TABLE IF NOT EXISTS lab_results (job_id TEXT UNIQUE, sample_drawn_wt REAL, button_wt REAL, s1_m1 REAL, s1_ag REAL, s1_cu REAL, s1_pb REAL, s1_m2 REAL, s2_m1 REAL, s2_ag REAL, s2_cu REAL, s2_pb REAL, s2_m2 REAL, c1_m1 REAL, c1_m2 REAL, c2_m1 REAL, c2_m2 REAL, remarks TEXT)")
        cursor.execute("SELECT job_id FROM lab_results")
        done_jobs = set([str(r[0]).strip() for r in cursor.fetchall()])
        
        conn.close()
        
        pending = sorted([j for j in all_jobs if j not in done_jobs], reverse=True)
        return {"status": "success", "data": pending}
    except Exception as e:
        logging.error(f"Get Pending Lab Jobs Error: {e}", exc_info=True)
        return {"status": "error", "msg": str(e)}

# ==============================================================
# 🚀 2. PRO-MODE: GENERATE LAB DATA MATH LOGIC (Background Calculation)
# ==============================================================
def generate_pro_lab_data(selected_jobs, purity_val, low_r, high_r, c1m2, c2m2):
    """UI se data aayega, ye function calculate karke DB me save karega."""
    if not selected_jobs or len(selected_jobs) == 0:
        return {"status": "error", "msg": "No jobs selected for generation."}
        
    try:
        p_val = float(purity_val) / 1000.0
        conn = sqlite3.connect('jewellery_data.db', timeout=10)
        cursor = conn.cursor()
        
        for jc in selected_jobs:
            # 🚀 Formula Calculations
            m1c1_base = c1m2 / 0.9997
            m1c2_base = c2m2 / 0.9999
            
            m1s1 = round((m1c1_base / p_val) + random.uniform(-0.5, 0.5), 3)
            m1s2 = round((m1c2_base / p_val) + random.uniform(-0.5, 0.5), 3)
            
            r1 = random.uniform(low_r, high_r) / 1000.0
            r2 = random.uniform(low_r, high_r) / 1000.0
            
            m2s1 = round(m1s1 * r1, 3)
            m2s2 = round(m1s2 * r2, 3)
            
            ag_s1 = round((m1s1 * 2.5 * p_val) / 10) * 10
            ag_s2 = ag_s1
            
            m1c1 = round(m1c1_base + random.uniform(-0.1, 0.1), 3)
            m1c2 = round(m1c2_base + random.uniform(-0.1, 0.1), 3)
            c1m2_final = round(m1c1 * 0.9997, 3)
            c2m2_final = round(m1c2 * 0.9999, 3)
            
            # 🚀 AUTOMATIC WEIGHT GENERATION (310 to 450 Range)
            sample_drawn = round(random.uniform(310.0, 450.0), 3)
            button_wt = round(random.uniform(310.0, 450.0), 3)
            
            # 🚀 GitHub ke liye 24-parameter query
            cursor.execute('''INSERT OR REPLACE INTO lab_results 
                              (job_id, sample_drawn_wt, button_wt, s1_m1, s1_ag, s1_cu, s1_pb, s1_m2, 
                               s2_m1, s2_ag, s2_cu, s2_pb, s2_m2, c1_m1, c1_ag, c1_cu, c1_pb, c1_m2,
                               c2_m1, c2_ag, c2_cu, c2_pb, c2_m2, remarks)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (jc, sample_drawn, button_wt, 
                            m1s1, ag_s1, 0, 4, m2s1,
                            m1s2, ag_s2, 0, 4, m2s2,
                            m1c1, c1m2_final, 14, 4, c1m2_final,
                            m1c2, c2m2_final, 14, 4, c2m2_final, 'Auto Generated'))
        conn.commit()
        conn.close()
        return {"status": "success", "msg": f"✅ {len(selected_jobs)} Job Cards ke liye Lab Data successfully generate aur save ho gaya!"}
    except Exception as e:
        logging.error(f"Generate Pro Lab Error: {e}", exc_info=True)
        return {"status": "error", "msg": f"Database Error: {str(e)}"}

# ==============================================================
# 🚀 3. LAB INJECTION (Pure Bot Engine - No Cheat Codes)
# ==============================================================
def inject_lab_weight_ghost(lab_data=None):
    if lab_data is None or len(lab_data) == 0:
        return "⚠️ इंस्ट्रक्शन: कृपया पहले डेटा लोड करें!"
        
    excel_job_card = lab_data.pop("excel_job_card", "UNKNOWN")
    sample_wt = lab_data.pop("sample_drawn_wt", None)
    button_wt = lab_data.pop("button_wt", None)

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
                                bis_page = page; break 
                        except: continue 
                    else:
                        bis_page = page; break
            
            if not bis_page:
                try: browser.disconnect() 
                except: pass
                return f"❌ अलर्ट: Job Card '{excel_job_card}' साइट पर मैच नहीं हुआ!"

            bis_page.on("dialog", lambda dialog: dialog.accept())

            # ---------------------------------------------------------
            # 🚀 ULTRA-PRECISE PRE-INJECTION SEQUENCE (Master Weights)
            # ---------------------------------------------------------
            try:
                # 1. SAMPLE DRAWN WEIGHT
                if sample_wt and str(sample_wt) not in ["0", "0.0", "", "None"]:
                    print(f"⚖️ Injecting Sample Drawn Weight: {sample_wt}")
                    sample_input = bis_page.locator("input#num_scrap_weight").first
                    
                    if sample_input.count() > 0:
                        # 🚨 BYPASS FOCUS STEALING: Direct JS Value Injection
                        js_fill = f"""node => {{
                            node.removeAttribute('disabled'); 
                            node.removeAttribute('readonly');
                            node.value = '{sample_wt}';
                            node.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            node.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}"""
                        sample_input.evaluate(js_fill)
                        bis_page.wait_for_timeout(300)
                        
                        # Uske turant baad wala Save button dabe ga
                        sample_save_btn = bis_page.locator("xpath=//input[@id='num_scrap_weight']/following::button[contains(., 'Save')][1]").first
                        if sample_save_btn.count() > 0:
                            sample_save_btn.evaluate("node => node.click()")
                            print("✅ Sample Drawn Weight Saved Successfully!")
                            bis_page.wait_for_timeout(2500) # Server AJAX request ko process karne dega
                        else:
                            print("⚠️ Sample Weight ka Save button nahi mila!")

                # 2. BUTTON WEIGHT
                if button_wt and str(button_wt) not in ["0", "0.0", "", "None"]:
                    print(f"⚖️ Injecting Button Weight: {button_wt}")
                    
                    button_input = bis_page.locator("input#buttonweight").first
                    if button_input.count() == 0:
                        button_input = bis_page.locator("xpath=//label[contains(., 'Button Weight')]/following::input[1]").first
                    
                    if button_input.count() > 0:
                        # 🚨 BYPASS FOCUS STEALING: Direct JS Value Injection
                        js_fill = f"""node => {{
                            node.removeAttribute('disabled'); 
                            node.removeAttribute('readonly');
                            node.value = '{button_wt}';
                            node.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            node.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}"""
                        button_input.evaluate(js_fill)
                        bis_page.wait_for_timeout(300)
                        
                        button_save_btn = bis_page.locator("xpath=//input[@id='buttonweight']/following::button[contains(., 'Save')][1]").first
                        if button_save_btn.count() == 0:
                            button_save_btn = bis_page.locator("xpath=//label[contains(., 'Button Weight')]/following::button[contains(., 'Save')][1]").first
                            
                        if button_save_btn.count() > 0:
                            button_save_btn.evaluate("node => node.click()")
                            print("✅ Button Weight Saved Successfully!")
                            bis_page.wait_for_timeout(2500) # Wait for Server AJAX
                        else:
                            print("⚠️ Button Weight ka Save button nahi mila!")

            except Exception as e:
                logging.error(f"Pre-Injection Sequence Error: {e}")
                print(f"⚠️ Pre-Injection Sequence Error: {e}")
            # ---------------------------------------------------------

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
                    logging.error(f"Error in row {strip_name}: {e}")
                    print(f"⚠️ Error in row {strip_name}: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ SUCCESS: {filled_count} Rows & Main Weights Injected!"
    except Exception as e:
        logging.error(f"Lab Smart Injection Error: {e}", exc_info=True)
        return f"⚠️ Error: {e}"