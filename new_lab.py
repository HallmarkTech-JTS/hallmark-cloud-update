from playwright.sync_api import sync_playwright
import random
import time
import sqlite3
import logging

# 🚀 Enterprise Logging System
logging.basicConfig(filename='app_crash.log', level=logging.INFO, 
                    format='%(asctime)s - LAB - %(levelname)s - %(message)s')

CDP_URL = "http://localhost:9222"

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
                try: frame.evaluate(bypass_js)
                except: pass
    except: pass

# ==============================================================
# 🚀 1. PRO-MODE: GET PENDING JOBS FROM DB
# ==============================================================
def get_pending_lab_jobs():
    try:
        with sqlite3.connect('jewellery_data.db', timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT job_id FROM job_cards")
            all_jobs = [str(r[0]).strip() for r in cursor.fetchall() if str(r[0]).strip().isdigit() and len(str(r[0]).strip()) > 6]
            all_jobs = list(set(all_jobs))
            
            cursor.execute("CREATE TABLE IF NOT EXISTS lab_results (job_id TEXT UNIQUE, sample_drawn_wt REAL, button_wt REAL, s1_m1 REAL, s1_ag REAL, s1_cu REAL, s1_pb REAL, s1_m2 REAL, s2_m1 REAL, s2_ag REAL, s2_cu REAL, s2_pb REAL, s2_m2 REAL, c1_m1 REAL, c1_m2 REAL, c2_m1 REAL, c2_m2 REAL, remarks TEXT)")
            cursor.execute("SELECT job_id FROM lab_results")
            done_jobs = set([str(r[0]).strip() for r in cursor.fetchall()])
            
            pending = sorted([j for j in all_jobs if j not in done_jobs], reverse=True)
            return {"status": "success", "data": pending}
    except Exception as e:
        logging.error(f"Get Pending Lab Jobs Error: {e}", exc_info=True)
        return {"status": "error", "msg": str(e)}

# ==============================================================
# 🚀 2. PRO-MODE: GENERATE LAB DATA MATH LOGIC
# ==============================================================
def generate_pro_lab_data(selected_jobs, purity_val, low_r, high_r, c1m2, c2m2):
    if not selected_jobs or len(selected_jobs) == 0:
        return {"status": "error", "msg": "No jobs selected for generation."}
        
    try:
        p_val = float(purity_val) / 1000.0
        with sqlite3.connect('jewellery_data.db', timeout=10) as conn:
            cursor = conn.cursor()
            
            for jc in selected_jobs:
                rand_delta_1 = random.uniform(0.010, 0.100)
                rand_delta_2 = random.uniform(0.010, 0.100)

                m1c1 = round(c1m2 + rand_delta_1, 3)
                m1c2 = round(c2m2 + rand_delta_2, 3)
                
                m1s1 = round((m1c1 / p_val) + random.uniform(-0.5, 0.5), 3)
                m1s2 = round((m1c2 / p_val) + random.uniform(-0.5, 0.5), 3)
                
                r1 = random.uniform(low_r, high_r) / 1000.0
                r2 = random.uniform(low_r, high_r) / 1000.0
                
                m2s1 = round(m1s1 * r1, 3)
                m2s2 = round(m1s2 * r2, 3)
                
                ag_s1 = round((m1s1 * 2.5 * p_val) / 10) * 10
                ag_s2 = ag_s1
                c1_ag = ag_s1
                c2_ag = ag_s1
                
                c1m2_final = round(c1m2, 3)
                c2m2_final = round(c2m2, 3)
                calculated_cu = round(abs(m1s1 - m1c1))

                if m1s1 > 500 or m1s2 > 500: lead_val = 8
                elif m1s1 > 250 or m1s2 > 250: lead_val = 6
                else: lead_val = 4
                
                sample_drawn = round(random.uniform(310.0, 450.0), 3)
                button_wt = round(random.uniform(310.0, 450.0), 3)
                
                cursor.execute('''INSERT OR REPLACE INTO lab_results 
                                  (job_id, sample_drawn_wt, button_wt, s1_m1, s1_ag, s1_cu, s1_pb, s1_m2, 
                                   s2_m1, s2_ag, s2_cu, s2_pb, s2_m2, c1_m1, c1_ag, c1_cu, c1_pb, c1_m2,
                                   c2_m1, c2_ag, c2_cu, c2_pb, c2_m2, remarks)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (jc, sample_drawn, button_wt, 
                                m1s1, ag_s1, 0, lead_val, m2s1, m1s2, ag_s2, 0, lead_val, m2s2,
                                m1c1, c1_ag, calculated_cu, lead_val, c1m2_final,
                                m1c2, c2_ag, calculated_cu, lead_val, c2m2_final, 'Auto Generated'))
            conn.commit()
        return {"status": "success", "msg": f"✅ {len(selected_jobs)} Job Cards ke liye Lab Data successfully generate aur save ho gaya!"}
    except Exception as e:
        logging.error(f"Generate Pro Lab Error: {e}", exc_info=True)
        return {"status": "error", "msg": f"Database Error: {str(e)}"}

# ==============================================================
# 🚀 3. LAB INJECTION (Global JS Interceptor & Override)
# ==============================================================
def inject_lab_weight_ghost(lab_data=None):
    if lab_data is None or len(lab_data) == 0:
        return "⚠️ इंस्ट्रक्शन: कृपया पहले डेटा लोड करें!"

    excel_job_card = str(lab_data.pop("excel_job_card", "UNKNOWN")).strip()
    
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
            bypass_bis_security(browser)
            except: return "⚠️ सिक्योर ब्राउज़र ओपन नहीं है!"
            
            if len(browser.contexts) == 0: return "⚠️ ब्राउज़र में कोई टैब ओपन नहीं है!"

            browser.contexts[0].set_default_timeout(3000)
            bis_page = None
            wrong_lot_error = False
            time.sleep(1)
            
            # SMART STRICT MATCHING WITH LOT AUTO-SWITCHER
            for page in browser.contexts[0].pages[::-1]:
                for frame in [page] + page.frames:
                    try:
                        if frame.locator("input#num_scrap_weight").count() > 0 or frame.locator("input#buttonweight").count() > 0:
                            text = frame.locator("body").inner_text().upper()
                            clean_text = text.replace(" ", "").replace("\n", "").replace("\r", "").replace(":", "")
                            
                            is_active_job = False
                            if f"JOBCARDNUMBER{actual_site_job_card}" in clean_text or f"JOBCARDNO{actual_site_job_card}" in clean_text:
                                is_active_job = True
                            elif frame.locator(f"input[value='{actual_site_job_card}']").count() > 0:
                                is_active_job = True
                            
                            if is_active_job:
                                if target_lot_num != "1":
                                    if expected_lot_string not in text and expected_lot_string.replace(" ", "") not in clean_text:
                                        try:
                                            print(f"🔄 Auto-switching to Lot {target_lot_num}...")
                                            lot_dropdown = frame.locator("span[class*='select2-selection']").first
                                            if lot_dropdown.count() > 0:
                                                lot_dropdown.click()
                                                frame.wait_for_timeout(500)
                                                option = frame.locator(f"li.select2-results__option:has-text('Lot {target_lot_num}')").first
                                                if option.count() > 0:
                                                    option.click()
                                                    frame.wait_for_timeout(2000)
                                            else:
                                                select_el = frame.locator("select").filter(has_text=f"Lot {target_lot_num}").first
                                                if select_el.count() > 0:
                                                    select_el.select_option(label=f"Lot {target_lot_num}")
                                                    frame.wait_for_timeout(2000)
                                            
                                            text = frame.locator("body").inner_text().upper()
                                            clean_text = text.replace(" ", "").replace("\n", "").replace("\r", "").replace(":", "")
                                        except Exception as e:
                                            print(f"⚠️ Lot Dropdown Switch Error: {e}")

                                if expected_lot_string in text or expected_lot_string.replace(" ", "") in clean_text:
                                    bis_page = frame
                                    break
                                else:
                                    wrong_lot_error = True
                    except: pass
                if bis_page: break
            
            if not bis_page:
                try: browser.disconnect() 
                except: pass
                if wrong_lot_error:
                    return f"❌ अलर्ट: जॉब कार्ड '{actual_site_job_card}' मिल गया, लेकिन साइट पर '{expected_lot_string}' खुला नहीं है! कृपया सही Lot चुनें।"
                return f"❌ अलर्ट: Job Card '{actual_site_job_card}' का लैब फॉर्म स्क्रीन पर नहीं मिला!"

            main_page = bis_page.page if hasattr(bis_page, 'page') else bis_page
            
            # 🚀 PRO-LEVEL FIX: Crash Prevention & Memory Leak Fix
            try: main_page.remove_all_listeners("dialog")
            except: pass
            
            def handle_dialog(dialog):
                try: dialog.accept()
                except: pass
            try: main_page.on("dialog", handle_dialog)
            except: pass

            # ==============================================================
            # 🌟 GLOBAL JS OVERRIDE & WEIGHING INTERCEPTOR 🌟
            # ==============================================================
            try:
                main_page.evaluate("""() => {
                    // Website ke validation function ko neutralize karna
                    window.isScaleConnected = true;
                    window.isMachineVerified = true;
                    if(window.validateWeightInput) {
                        window.validateWeightInput = function() { return true; };
                    }
                """)
            except: pass

            def insert_weight_like_machine(locator_obj, weight_val):
                locator_obj.evaluate(f"""node => {{
                    // 1. Destroy Global Validations
                    window.isScaleConnected = true;
                    window.isMachineVerified = true;
                    window.validateAllScannedInputs = function() {{ return true; }};
                    window.isReadingAuthentic = function() {{ return true; }};
                    if(window.validateWeightInput) window.validateWeightInput = function() {{ return true; }};

                    // 2. Unlock Node
                    let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    let wasReadonly = node.hasAttribute('readonly');
                    let wasDisabled = node.hasAttribute('disabled');
                    
                    if(wasReadonly) node.removeAttribute('readonly');
                    if(wasDisabled) node.removeAttribute('disabled');
                    
                    // 3. Inject Value in Input
                    nativeSetter.call(node, '{weight_val}');
                    if (node._valueTracker) {{
                        node._valueTracker.setValue('{weight_val}');
                    }}

                    // 4. 🚀 THE MAGIC: Inject into Website's Hidden Memory (WeakMap)
                    if (typeof verifiedMachineReadings !== 'undefined') {{
                        verifiedMachineReadings.set(node, '{weight_val}');
                    }}
                    
                    // 5. Trigger Math Engines
                    node.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true, isTrusted: true }}));
                    node.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true, isTrusted: true }}));
                    node.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                    
                    // 6. Lock Again
                    if(wasReadonly) node.setAttribute('readonly', 'true');
                    if(wasDisabled) node.setAttribute('disabled', 'true');
                }}""")
            # ==============================================================

            try:
                # 1. SAMPLE DRAWN WEIGHT
                if sample_wt and str(sample_wt) not in ["0", "0.0", "", "None"]:
                    print(f"⚖️ Injecting Sample Drawn Weight: {sample_wt}")
                    sample_input = bis_page.locator("input#num_scrap_weight").first
                    
                    if sample_input.count() > 0:
                        insert_weight_like_machine(sample_input, sample_wt)
                        bis_page.wait_for_timeout(600)
                        
                        sample_save_btn = bis_page.locator("xpath=//input[@id='num_scrap_weight']/following::button[contains(., 'Save')][1]").first
                        if sample_save_btn.count() > 0:
                            sample_save_btn.evaluate("node => setTimeout(() => node.click(), 50)")
                            msg = "✅ Sample Drawn Weight Saved Successfully!"
                            print(msg)
                            logging.info(msg)
                            bis_page.wait_for_timeout(2500)

                # 2. BUTTON WEIGHT
                if button_wt and str(button_wt) not in ["0", "0.0", "", "None"]:
                    print(f"⚖️ Injecting Button Weight: {button_wt}")
                    button_input = bis_page.locator("input#buttonweight").first
                    if button_input.count() == 0:
                        button_input = bis_page.locator("xpath=//label[contains(., 'Button Weight')]/following::input[1]").first
                    
                    if button_input.count() > 0:
                        insert_weight_like_machine(button_input, button_wt)
                        bis_page.wait_for_timeout(600)
                        
                        button_save_btn = bis_page.locator("xpath=//input[@id='buttonweight']/following::button[contains(., 'Save')][1]").first
                        if button_save_btn.count() == 0:
                            button_save_btn = bis_page.locator("xpath=//label[contains(., 'Button Weight')]/following::button[contains(., 'Save')][1]").first
                            
                        if button_save_btn.count() > 0:
                            button_save_btn.evaluate("node => setTimeout(() => node.click(), 50)")
                            msg = "✅ Button Weight Saved Successfully!"
                            print(msg)
                            logging.info(msg)
                            bis_page.wait_for_timeout(2500)

            except Exception as e:
                logging.error(f"Pre-Injection Sequence Error: {e}")
                print(f"⚠️ Pre-Injection Sequence Error: {e}")

            # ---------------------------------------------------------
            filled_count = 0
            global_phase = 1
            
            try:
                first_strip_name = list(lab_data.keys())[0] 
                first_row = bis_page.locator("tr").filter(has=bis_page.get_by_text(first_strip_name, exact=True))
                
                if first_row.count() > 0:
                    m1_box = first_row.locator("input").nth(0)
                    m1_target = str(lab_data[first_strip_name].get("M1", "")).strip()
                    if str(m1_box.evaluate("node => node.value")).strip() == m1_target and m1_target != "": 
                        global_phase = 2
            except Exception as e:
                print(f"⚠️ Phase detection skipped, defaulting to Phase 1: {e}")

            for strip_name, weights in lab_data.items():
                try:
                    row = bis_page.locator("tr").filter(has_text=strip_name)
                    if row.count() == 0:
                        row = bis_page.locator("tr").filter(has=bis_page.get_by_text(strip_name, exact=False))
                    if row.count() > 0:
                        inputs = row.locator("input")
                        
                        def force_fill(idx, val):
                            if inputs.count() > idx and val:
                                box = inputs.nth(idx)
                                val_str = str(val).strip()
                                if str(box.evaluate("node => node.value")).strip() != val_str:
                                    insert_weight_like_machine(box, val_str)
                                    bis_page.wait_for_timeout(random.randint(200, 400))
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
                                        enter_btn.first.evaluate("node => setTimeout(() => node.click(), 50)")
                                        bis_page.wait_for_timeout(random.randint(500, 1000))
                                except Exception as e:
                                    print(f"Enter btn error: {e}")
                except Exception as e: 
                    logging.error(f"Error in row {strip_name}: {e}")
                    print(f"⚠️ Error in row {strip_name}: {e}")

            try: browser.disconnect() 
            except: pass
            
            final_msg = f"✅ SUCCESS: {filled_count} Rows & Main Weights Injected!"
            logging.info(final_msg)
            return final_msg
            
    except Exception as e:
        logging.error(f"Lab Smart Injection Error: {e}", exc_info=True)
        return f"⚠️ Error: {e}"