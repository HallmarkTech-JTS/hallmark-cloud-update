from playwright.sync_api import sync_playwright
import random
import time
import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

CDP_URL = "http://localhost:9222"

# ==============================================================
# 🚀 NEW: SMART LAB DATA GENERATOR (DIRECT DB READ + MAX 16 LIMIT)
# ==============================================================
def _get_pending_jobs_from_db():
    try:
        import sqlite3
        conn = sqlite3.connect('jewellery_data.db', timeout=5)
        cursor = conn.cursor()
        
        # 1. DB me saari tables dhoondho
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        
        all_jobs = []
        for t in tables:
            if t in ["lab_results", "sqlite_sequence"]: continue
            try:
                cursor.execute(f"PRAGMA table_info({t})")
                cols = [c[1] for c in cursor.fetchall()]
                # Koi bhi column jiska naam job_id ya job_card ho
                job_col = next((c for c in cols if c in ['job_id', 'job_card', 'job_no', 'id']), None)
                if job_col:
                    cursor.execute(f"SELECT DISTINCT {job_col} FROM {t}")
                    # Valid Job Cards filter karo (> 6 digits)
                    fetched = [str(r[0]).strip() for r in cursor.fetchall() if str(r[0]).strip().isdigit() and len(str(r[0]).strip()) > 6]
                    all_jobs.extend(fetched)
            except: pass
                
        all_jobs = list(set(all_jobs))
        
        # 2. Jo jobs pehle se lab_results mein hain, unhe hata do
        cursor.execute("CREATE TABLE IF NOT EXISTS lab_results (job_id TEXT UNIQUE, sample_drawn_wt REAL, button_wt REAL, s1_m1 REAL, s1_ag REAL, s1_cu REAL, s1_pb REAL, s1_m2 REAL, s2_m1 REAL, s2_ag REAL, s2_cu REAL, s2_pb REAL, s2_m2 REAL, c1_m1 REAL, c1_m2 REAL, c2_m1 REAL, c2_m2 REAL, remarks TEXT)")
        cursor.execute("SELECT job_id FROM lab_results")
        done_jobs = set([str(r[0]).strip() for r in cursor.fetchall()])
        
        conn.close()
        
        pending = sorted([j for j in all_jobs if j not in done_jobs], reverse=True)
        return {"status": "success", "data": pending}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

def launch_lab_generator_popup():
    import tkinter as tk
    from tkinter import ttk, messagebox
    import sqlite3
    
    db_response = _get_pending_jobs_from_db()
    if db_response["status"] == "error":
        return db_response["msg"]
        
    pending_jobs = db_response.get("data", [])
    if not pending_jobs:
        return "⚠️ Badi Badhai! Sabhi Job Cards ka Lab Data pehle se saved hai."
        
    # --- Build Tkinter UI ---
    root = tk.Tk()
    root.title("🧪 SMART LAB DATA GENERATOR")
    root.geometry("850x600")
    root.configure(bg="#f8fafc")
    root.attributes('-topmost', True)
    
    left_frame = tk.Frame(root, width=400, bg="white", highlightbackground="#cbd5e1", highlightthickness=1)
    left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
    
    right_frame = tk.Frame(root, width=400, bg="#f8fafc")
    right_frame.pack(side="right", fill="both", expand=False, padx=15, pady=15)
    
    header_frame = tk.Frame(left_frame, bg="white")
    header_frame.pack(fill="x", padx=10, pady=(10, 0))
    tk.Label(header_frame, text="📌 Pending Database Jobs", font=("Arial", 12, "bold"), bg="white", fg="#0f172a").pack(side="left")
    count_label = tk.Label(header_frame, text="Selected: 0 / 16", font=("Arial", 10, "bold"), bg="white", fg="#b91c1c")
    count_label.pack(side="right")
    
    btn_frame = tk.Frame(left_frame, bg="white")
    btn_frame.pack(fill="x", padx=10, pady=5)
    
    vars_dict = {}
    
    # 🚨 STRICT 16 LIMIT CHECK LOGIC
    def on_check_toggle(jc, var):
        count = sum(1 for v in vars_dict.values() if v.get())
        if count > 16:
            var.set(False) # ❌ Instantly uncheck it
            messagebox.showwarning("Limit Exceeded 🛑", "Aap ek baar mein MAXIMUM 16 Job Card hi select kar sakte hain!")
            return
        count_label.config(text=f"Selected: {count} / 16")
        if count == 16: count_label.config(fg="#10b981") # Green if 16 reached
        else: count_label.config(fg="#b91c1c")
            
    def select_first_16():
        count = 0
        for jc, var in vars_dict.items():
            if count < 16:
                var.set(True)
                count += 1
            else:
                var.set(False)
        count_label.config(text=f"Selected: {count} / 16", fg="#10b981" if count==16 else "#b91c1c")
    
    def deselect_all():
        for var in vars_dict.values(): var.set(False)
        count_label.config(text="Selected: 0 / 16", fg="#b91c1c")
            
    tk.Button(btn_frame, text="☑ Select 16", command=select_first_16, bg="#e2e8f0", font=("Arial", 9, "bold"), cursor="hand2").pack(side="left", expand=True, fill="x", padx=(0, 5))
    tk.Button(btn_frame, text="☐ Deselect All", command=deselect_all, bg="#e2e8f0", font=("Arial", 9, "bold"), cursor="hand2").pack(side="right", expand=True, fill="x", padx=(5, 0))
    
    list_container = tk.Frame(left_frame, bg="white")
    list_container.pack(fill="both", expand=True, padx=10, pady=5)
    canvas = tk.Canvas(list_container, bg="white", highlightthickness=0)
    scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Render Flat List of Job Cards
    for jc in pending_jobs:
        var = tk.BooleanVar(value=False)
        vars_dict[jc] = var
        # Pass variables to lambda safely
        cb = tk.Checkbutton(scrollable_frame, text=f"   Job Card: {jc}", variable=var, font=("Arial", 11, "bold"), bg="white", cursor="hand2", command=lambda j=jc, v=var: on_check_toggle(j, v))
        cb.pack(anchor="w", padx=10, pady=5)
    
    # --- Right Panel Form ---
    tk.Label(right_frame, text="⚙️ Lab Calculation Formula", font=("Arial", 14, "bold"), bg="#f8fafc", fg="#0f172a").pack(pady=(0, 15))
    
    tk.Label(right_frame, text="Declared Purity:", font=("Arial", 10, "bold"), bg="#f8fafc").pack(anchor="w")
    purity_var = tk.StringVar(value="916")
    purity_cb = ttk.Combobox(right_frame, textvariable=purity_var, values=["916", "883", "995", "958", "750", "585", "375"], font=("Arial", 11), state="readonly")
    purity_cb.pack(fill="x", pady=(2, 10))
    
    def create_input(label_text, default_val):
        tk.Label(right_frame, text=label_text, font=("Arial", 10, "bold"), bg="#f8fafc").pack(anchor="w")
        entry = tk.Entry(right_frame, font=("Arial", 11), relief="solid", borderwidth=1)
        entry.insert(0, default_val)
        entry.pack(fill="x", pady=(2, 10))
        return entry
        
    low_entry = create_input("Reading Range LOW (e.g. 916.1):", "916.1")
    high_entry = create_input("Reading Range HIGH (e.g. 916.9):", "916.9")
    c1m2_entry = create_input("Check Gold 1 (C1M2) (e.g. 150):", "150.000")
    c2m2_entry = create_input("Check Gold 2 (C2M2) (e.g. 150):", "150.000")
    
    def on_generate():
        selected_jobs = [jc for jc, var in vars_dict.items() if var.get()]
        if len(selected_jobs) == 0:
            messagebox.showerror("Error", "Please select at least 1 Job Card!")
            return
            
        try:
            p_val = float(purity_var.get()) / 1000.0
            low_r = float(low_entry.get())
            high_r = float(high_entry.get())
            c1m2 = float(c1m2_entry.get())
            c2m2 = float(c2m2_entry.get())
        except Exception:
            messagebox.showerror("Error", "Kripya sabhi boxes mein numbers bharein!")
            return
            
        try:
            conn = sqlite3.connect('jewellery_data.db', timeout=10)
            cursor = conn.cursor()
            
            m1c1_base = c1m2 / 0.9997
            m1c2_base = c2m2 / 0.9999
            
            import random
            for jc in selected_jobs:
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
                
                sample_drawn = round(m1s1 + m1s2 + random.uniform(1.0, 3.0), 3)
                button_wt = round(m1s1 + ag_s1 + 4.0, 3)
                
                cursor.execute('''INSERT OR REPLACE INTO lab_results 
                                  (job_id, sample_drawn_wt, button_wt, s1_m1, s1_ag, s1_cu, s1_pb, s1_m2, 
                                   s2_m1, s2_ag, s2_cu, s2_pb, s2_m2, c1_m1, c1_m2, c2_m1, c2_m2, remarks)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (jc, sample_drawn, button_wt, 
                                m1s1, ag_s1, 0, 4, m2s1,
                                m1s2, ag_s2, 0, 4, m2s2,
                                m1c1, c1m2_final, m1c2, c2m2_final, 'Auto Generated'))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"✅ {len(selected_jobs)} Job Cards ke liye Lab Data successfully save ho gaya!")
            canvas.unbind_all("<MouseWheel>")
            root.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving data: {str(e)}")
            
    tk.Button(right_frame, text="⚡ GENERATE & SAVE LAB DATA", command=on_generate, bg="#10b981", activebackground="#059669", fg="white", font=("Arial", 12, "bold"), cursor="hand2").pack(pady=20, fill="x")
    
    select_first_16() 
    root.mainloop()
    return "✅ Process Completed."


# ==============================================================
# 2. LAB INJECTION (HUMAN-LIKE & AUTO-SAVE)
# ==============================================================
def inject_lab_weight_ghost(lab_data=None):
    
    # 🚨 MAGIC HACK: Bina .exe badle popup kholne ka raaz! 
    # Agar lab_data mein "trigger": "auto_gen" bheja gaya hai, toh Popup khulega!
    if lab_data and lab_data.get("trigger") == "auto_gen":
        print("🚀 Launching Smart Lab Generator Popup...")
        return launch_lab_generator_popup()
        
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

            bis_page.on("dialog", lambda dialog: dialog.accept())

            def human_type_and_save(selector_id, value, save_btn_index, step_name):
                val_str = str(value).strip()
                if val_str and val_str not in ["", "None"]:
                    try:
                        box = bis_page.locator(selector_id).first
                        if box.count() > 0:
                            current_val = str(box.evaluate("node => node.value")).strip()
                            is_match = False
                            try:
                                if float(current_val) == float(val_str): is_match = True
                            except ValueError:
                                if current_val == val_str: is_match = True

                            if is_match:
                                print(f"⏩ SMART SKIP: {step_name} pehle se '{current_val}' bhara hai! ⚡")
                                return 

                            print(f"⏳ Typing {step_name}: {val_str}")
                            box.evaluate("node => { node.removeAttribute('disabled'); node.removeAttribute('readonly'); }")
                            box.clear()
                            
                            bis_page.wait_for_timeout(random.randint(100, 200)) 
                            box.type(val_str, delay=random.randint(50, 100))    
                            bis_page.wait_for_timeout(random.randint(200, 400))
                            
                            save_btns = bis_page.locator("button:has-text('Save')")
                            if save_btns.count() > save_btn_index:
                                save_btns.nth(save_btn_index).click(force=True) 
                                print(f"✅ Clicked Save for {step_name}")
                                bis_page.wait_for_timeout(random.randint(1500, 2000)) 
                        else:
                            print(f"❌ ERROR: {step_name} ka box HTML mein nahi mila!")
                    except Exception as e:
                        print(f"⚠️ {step_name} Error: {e}")

            human_type_and_save("#num_scrap_weight", sample_wt, 0, "Sample Weight")
            human_type_and_save("#buttonweight", button_wt, 1, "Button Weight")

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