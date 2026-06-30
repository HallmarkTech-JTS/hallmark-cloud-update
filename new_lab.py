from playwright.sync_api import sync_playwright
import random
import time
import sqlite3
import logging

# 🚀 Enterprise Logging System
logging.basicConfig(filename='app_crash.log', level=logging.ERROR, 
                    format='%(asctime)s - LAB - %(levelname)s - %(message)s')

CDP_URL = "http://localhost:9222"

def get_pending_lab_jobs():
    try:
        conn = sqlite3.connect('jewellery_data.db', timeout=5)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT job_id FROM job_cards")
        all_jobs = [str(r[0]).strip() for r in cursor.fetchall() if str(r[0]).strip().isdigit() and len(str(r[0]).strip()) > 6]
        all_jobs = list(set(all_jobs))
        
        cursor.execute("CREATE TABLE IF NOT EXISTS lab_results (job_id TEXT UNIQUE, sample_drawn_wt REAL, button_wt REAL, s1_m1 REAL, s1_ag REAL, s1_cu REAL, s1_pb REAL, s1_m2 REAL, s2_m1 REAL, s2_ag REAL, s2_cu REAL, s2_pb REAL, s2_m2 REAL, c1_m1 REAL, c1_ag REAL, c1_cu REAL, c1_pb REAL, c1_m2 REAL, c2_m1 REAL, c2_ag REAL, c2_cu REAL, c2_pb REAL, c2_m2 REAL, remarks TEXT, s1_delta TEXT, c1_delta TEXT, c2_delta TEXT, s1_fine TEXT, s2_fine TEXT, mean_fineness TEXT)")
        
        cursor.execute("SELECT DISTINCT job_id FROM lab_results")
        completed_jobs = [str(r[0]).strip() for r in cursor.fetchall()]
        
        pending_jobs = [job for job in all_jobs if job not in completed_jobs]
        return sorted(pending_jobs, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
    except Exception as e:
        logging.error(f"get_pending_lab_jobs Error: {e}")
        return []
    finally:
        if 'conn' in locals(): conn.close()

def inject_lab_weight_ghost(formatted_data):
    if not formatted_data: return "⚠️ Error: Data is empty!"
    
    excel_job_card = str(formatted_data.get("excel_job_card", ""))
    # 🚀 Yahan Lot (-L) filter hoga website pe dhoondhne ke liye
    actual_site_job_card = excel_job_card.split('-L')[0].strip()
    
    print(f"👻 Ghost Injecting Lab for Job: {actual_site_job_card} (Original Lot: {excel_job_card})")

    try:
        with sync_playwright() as p:
            try: browser = p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
            except: return "⚠️ Error: Browser open nahi hai!"
            
            bis_page = None
            for page in browser.contexts[0].pages:
                for frame in [page] + page.frames:
                    try:
                        text = frame.locator("body").inner_text()
                        if "Sample Details" in text and "Observation" in text:
                            bis_page = frame
                            break
                    except: pass
                if bis_page: break
            
            if not bis_page:
                try: browser.disconnect() 
                except: pass
                return "❌ अलर्ट: Assaying Observation पेज नहीं मिला!"

            search_box = bis_page.locator("input[type='search']")
            if search_box.count() > 0:
                search_box.fill(actual_site_job_card)
                bis_page.wait_for_timeout(1000)
            else:
                for page in browser.contexts[0].pages:
                    if "Assaying Observation" in page.title():
                        try:
                            site_job_card = page.locator("body").inner_text()
                            if actual_site_job_card in site_job_card:
                                bis_page = page; break 
                        except: continue 
                    else:
                        bis_page = page; break
            
            if not bis_page:
                try: browser.disconnect() 
                except: pass
                return f"❌ अलर्ट: Job Card '{actual_site_job_card}' साइट पर मैच नहीं हुआ!"

            if formatted_data.get("sample_drawn_wt") and formatted_data.get("button_wt"):
                try:
                    sample_drawn_input = bis_page.locator("input[name*='sampleDrawnWt'], input[placeholder*='Sample Drawn']").first
                    if sample_drawn_input.is_visible():
                        sample_drawn_input.fill(str(formatted_data.get("sample_drawn_wt")))
                        bis_page.wait_for_timeout(200)

                    button_wt_input = bis_page.locator("input[name*='buttonWt'], input[placeholder*='Button Weight']").first
                    if button_wt_input.is_visible():
                        button_wt_input.fill(str(formatted_data.get("button_wt")))
                        bis_page.wait_for_timeout(200)
                except Exception as e:
                    print(f"Sample/Button WT Error: {e}")

            filled_count = 0
            strip_mapping = {
                "Sample 1": "Strip 1", "Sample 2": "Strip 2",
                "Check Gold 1": "C1(Check Gold)", "Check Gold 2": "C2(Check Gold)"
            }
            
            global_phase = 1 if (formatted_data.get("Strip 1", {}).get("M2") == "") else 2

            for site_name, dict_name in strip_mapping.items():
                weights = formatted_data.get(dict_name)
                if not weights: continue

                try:
                    row = bis_page.locator(f"tr:has-text('{site_name}')").first
                    if row.is_visible():
                        inputs = row.locator("input[type='text'], input.form-control")
                        input_count = inputs.count()

                        def force_fill(idx, val):
                            if val and str(val).strip() != "" and idx < input_count:
                                try:
                                    field = inputs.nth(idx)
                                    field.evaluate("node => { node.removeAttribute('readonly'); node.removeAttribute('disabled'); }")
                                    field.scroll_into_view_if_needed()
                                    field.click()
                                    bis_page.keyboard.press("Control+A")
                                    bis_page.keyboard.press("Backspace")
                                    bis_page.keyboard.type(str(val), delay=random.randint(30, 80))
                                    field.evaluate("node => { node.dispatchEvent(new Event('change', { bubbles: true })); node.dispatchEvent(new Event('blur', { bubbles: true })); }")
                                    bis_page.wait_for_timeout(random.randint(100, 300))
                                    return True
                                except Exception as e:
                                    print(f"Fill error at index {idx}: {e}")
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
                                except Exception as e: pass
                except Exception as e: print(f"⚠️ Error in row {site_name}: {e}")

            try: browser.disconnect() 
            except: pass
            return f"✅ SUCCESS: {filled_count} Rows & Main Weights Injected!"
    except Exception as e:
        return f"⚠️ System Error: {str(e)}"