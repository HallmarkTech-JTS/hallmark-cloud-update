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
            # 🚀 Formula Calculations (Divide system khtam, user logic applied)
            rand_delta_1 = random.uniform(0.010, 0.100)
            rand_delta_2 = random.uniform(0.010, 0.100)

            # M1 ki value banegi = User ka M2 + Random Value
            m1c1 = round(c1m2 + rand_delta_1, 3)
            m1c2 = round(c2m2 + rand_delta_2, 3)
            
            m1s1 = round((m1c1 / p_val) + random.uniform(-0.5, 0.5), 3)
            m1s2 = round((m1c2 / p_val) + random.uniform(-0.5, 0.5), 3)
            
            r1 = random.uniform(low_r, high_r) / 1000.0
            r2 = random.uniform(low_r, high_r) / 1000.0
            
            m2s1 = round(m1s1 * r1, 3)
            m2s2 = round(m1s2 * r2, 3)
            
            ag_s1 = round((m1s1 * 2.5 * p_val) / 10) * 10
            
            # 🚀 FIX 1: Silver Sabme Equal
            ag_s2 = ag_s1
            c1_ag = ag_s1
            c2_ag = ag_s1
            
            # 🚀 M2 ki value exact wahi rahegi jo User ne UI se daali hai
            c1m2_final = round(c1m2, 3)
            c2m2_final = round(c2m2, 3)

            # 🚀 FIX 2: Copper (Cu) calculation
            calculated_cu = round(abs(m1s1 - m1c1))

            # 🚀 FIX 3: Lead Calculation
            # 🚀 FIX 3: Lead Calculation (<=250: 4g, 251-500: 6g, >500: 8g)
            if m1s1 > 500 or m1s2 > 500:
                lead_val = 8
            elif m1s1 > 250 or m1s2 > 250:
                lead_val = 6
            else:
                lead_val = 4
            
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
                            m1s1, ag_s1, 0, lead_val, m2s1,
                            m1s2, ag_s2, 0, lead_val, m2s2,
                            m1c1, c1_ag, calculated_cu, lead_val, c1m2_final,
                            m1c2, c2_ag, calculated_cu, lead_val, c2m2_final, 'Auto Generated'))
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
        
    excel_job_card = str(lab_data.pop("excel_job_card", "UNKNOWN")).strip()
    
    # 🚀 SMART LOT DETECTION & EXTRACTION
    if "-L" in excel_job_card:
        actual_site_job_card = excel_job_card.split('-L')[0].strip()
        target_lot_num = excel_job_card.split('-L')[1].strip()
    else:
        actual_site_job_card = excel_job_card.strip()
        target_lot_num = "1"
        
    sample_wt = lab_data.pop("sample_drawn_wt", None)
    button_wt = lab_data.pop("button_wt", None)

    expected_lot_string = f"LOT {target_lot_num}"
    print(f"👻 Lab Smart Injection Started (JC: {actual_site_job_card} | Expected: {expected_lot_string})...")
    
    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=3000)
            except: return "⚠️ सिक्योर ब्राउज़र ओपन नहीं है!"
            
            if len(browser.contexts) == 0: return "⚠️ ब्राउज़र में कोई टैब ओपन नहीं है!"

            browser.contexts[0].set_default_timeout(3000)
            bis_page = None
            wrong_lot_error = False
            time.sleep(1) # Tab load hone ka wait
            
            # 🚀 SMART STRICT MATCHING: Ulta loop (Naya tab pehle check karega)
            for page in browser.contexts[0].pages[::-1]:
                for frame in [page] + page.frames:
                    try:
                        # 🚀 CRITICAL FIX: Pehle check karo ki is frame me Lab inputs hain ya nahi
                        if frame.locator("input#num_scrap_weight").count() > 0 or frame.locator("input#buttonweight").count() > 0:
                            text = frame.locator("body").inner_text().upper()
                            
                            # 🚀 BUG FIX: "Photo Wali Jagah" se Perfect Match (Sidebar Bypass)
                            is_active_job = False
                            
                            # Text ko clean karke label aur value ko ek sath jodd do
                            # Jaise: "Job Card Number : 100166838" ban jayega "JOBCARDNUMBER100166838"
                            clean_text = text.replace(" ", "").replace("\n", "").replace("\r", "").replace(":", "")
                            
                            perfect_match_1 = f"JOBCARDNUMBER{actual_site_job_card}"
                            perfect_match_2 = f"JOBCARDNO{actual_site_job_card}"
                            
                            # Sidebar me sirf number hota hai, label nahi! 
                            # Isliye ye condition SIRF tabhi TRUE hogi jab "Photo wali jagah" par job card hoga!
                            if perfect_match_1 in clean_text or perfect_match_2 in clean_text:
                                is_active_job = True
                            else:
                                # Safety Fallback: Agar job card seedha kisi Input box ke andar ho
                                if frame.locator(f"input[value='{actual_site_job_card}']").count() > 0:
                                    is_active_job = True
                            
                            # Jab 100% PERFECT MATCH hoga, tabhi LOT check karega!
                            if is_active_job:
                                if expected_lot_string in text or expected_lot_string.replace(" ", "") in clean_text:
                                    bis_page = frame
                                    break  # ✅ Sahi tab mil gaya!
                                else:
                                    wrong_lot_error = True
                    except: pass
                if bis_page: break
            
            if not bis_page:
                try: browser.disconnect() 
                except: pass
                
                # 🚀 SMART ERROR: User ko exactly batao ki usne Lot me galti ki hai
                if wrong_lot_error:
                    return f"❌ अलर्ट: जॉब कार्ड '{actual_site_job_card}' मिल गया, लेकिन साइट पर '{expected_lot_string}' खुला नहीं है! कृपया सही Lot चुनें।"
                return f"❌ अलर्ट: Job Card '{actual_site_job_card}' का लैब फॉर्म स्क्रीन पर नहीं मिला!"

            # Handle Popup (Safe way for both Page and Frame)
            main_page = bis_page.page if hasattr(bis_page, 'page') else bis_page
            try: main_page.on("dialog", lambda dialog: dialog.accept())
            except: pass

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
                                    # 🚀 FIX: Key-by-key typing hata di hai, direct JS injection se 100% accuracy aayegi chahe net slow ho
                                    js_fill = f"""node => {{
                                        node.removeAttribute('disabled'); 
                                        node.removeAttribute('readonly');
                                        node.value = '{val_str}';
                                        node.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                        node.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    }}"""
                                    box.evaluate(js_fill)
                                    bis_page.wait_for_timeout(random.randint(100, 300))
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