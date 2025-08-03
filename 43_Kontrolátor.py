import tkinter as tk
import json
import os
from datetime import datetime, timedelta
import requests

SETTINGS_FILE = "settings.json"
rows = []
running = False
already_logged = set()

def fetch_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data["price"]) if "price" in data else None
    except Exception as e:
        print(f"⚠️ Chyba při získávání ceny: {e}")
        return None

def save_settings():
    all_data = []
    for idx, (entry_frame, vars, entries, ts_frame, timestamp_labels) in enumerate(rows):
        entry_data = {}
        for key, var in vars.items():
            entry_data[key] = var.get()
            if key in entries:
                try:
                    bg = entries[key].cget("bg")
                    if bg == "lightgreen":
                        entry_data[f"{key}_hit"] = "TP"
                    elif bg == "lightcoral":
                        entry_data[f"{key}_hit"] = "SL"
                except Exception as e:
                    print(f"⚠️ Chyba při čtení barvy pro {key}: {e}")
        for key, label in timestamp_labels.items():
            entry_data[f"{key}_time"] = label.cget("text")
        all_data.append(entry_data)

    data_to_save = {"rows": all_data, "logged_hits": list(already_logged)}

    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        print(f"✅ Soubor byl uložen do: {SETTINGS_FILE}")
    except Exception as e:
        print(f"⚠️ Chyba při ukládání: {e}")

def load_settings():
    global already_logged
    if not os.path.exists(SETTINGS_FILE):
        print("⚠️ Soubor settings.json nebyl nalezen.")
        return []
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print("⚠️ Soubor settings.json je prázdný.")
                return []
            data = json.loads(content)
            if isinstance(data, list):
                already_logged = set()
                return data
            already_logged = set(data.get("logged_hits", []))
            return data.get("rows", [])
    except Exception as e:
        print(f"⚠️ Chyba při načítání settings.json: {e}")
        return []

def log_hit(coin, key, val, hit_type):
    timestamp = datetime.now().strftime("%d.%m %H:%M")
    message = f"[{timestamp}] 🎯 {coin} zasáhl {hit_type} {key} @ {val}\n"
    log_text.insert("end", message)
    log_text.see("end")


def tk_label_row(initial_data=None):
    show_headers = len(rows) == 0
    labels = ["Coin", "Quote", "EP1", "EP2", "Mark Price"] + [f"TP{i}" for i in range(1, 7)] + [f"SL{i}" for i in range(1, 3)]

    row_frame = tk.Frame(root)
    # row_frame.pack(pady=(2 if show_headers else 0), anchor="w", before=log_frame)
    if rows:
        row_frame.pack(pady=(2 if show_headers else 0), anchor="w", before=rows[0][0])
    else:
        row_frame.pack(pady=(2 if show_headers else 0), anchor="w", before=log_frame)


    vars = {}
    entries = {}
    timestamp_labels = {}

    if show_headers:
        tk.Label(row_frame, text="Long/Short", font=("Segoe UI", 9, "bold"), width=10).grid(row=0, column=0, padx=2, pady=(0, 2), sticky="n")
        for col, label in enumerate(labels):
            tk.Label(row_frame, text=label, font=("Segoe UI", 9, "bold"), width=10).grid(row=0, column=col + 1, padx=2, pady=(0, 2), sticky="n")
        tk.Label(row_frame, text="🗑️", font=("Segoe UI", 9, "bold"), width=5).grid(row=0, column=len(labels) + 1, padx=2, pady=(0, 2), sticky="n")

    row_offset = 0 if show_headers else -1

    # Direction field
    direction_var = tk.StringVar(value=initial_data.get("Direction", "") if initial_data else "")
    vars["Direction"] = direction_var
    direction_menu = tk.OptionMenu(row_frame, direction_var, "Short", "Long")
    direction_menu.config(width=8)
    direction_menu.grid(row=1 + row_offset, column=0, padx=2, pady=(0, 2), sticky="n")
    ts_direction = tk.Label(row_frame, text="", font=("Segoe UI", 8), fg="gray", width=10)
    ts_direction.grid(row=2 + row_offset, column=0, padx=2, pady=(0, 2), sticky="n")
    timestamp_labels["Direction"] = ts_direction

    # Main entry fields
    for col, label in enumerate(labels):
        adjusted_col = col + 1
        default_value = "USDT" if label == "Quote" else ""
        var = tk.StringVar(value=default_value)
        if initial_data and label in initial_data:
            var.set(initial_data[label])
        vars[label] = var

        entry = tk.Entry(row_frame, textvariable=var, width=10)
        entry.grid(row=1 + row_offset, column=adjusted_col, padx=2, pady=(0, 2), sticky="n")
        entries[label] = entry

        time_text = initial_data.get(f"{label}_time", "") if initial_data else ""
        ts_label = tk.Label(row_frame, text=time_text, font=("Segoe UI", 8), fg="gray", width=10)
        #ts_label.grid(row=2 + row_offset, column=adjusted_col, padx=2, pady=(0, 2), sticky="n")
        ts_label.grid(row=(1 if show_headers else 0), column=adjusted_col, padx=2, pady=(0, 0), sticky="s")
        ### ts_label.grid(row=(1 if show_headers else 0), column=adjusted_col, padx=2, pady=(6, 0), sticky="n")
        ### ts_label.grid(row=(1 if show_headers else 0), column=adjusted_col, padx=2, pady=(0, 8), sticky="s")
        ##ts_label.grid(row=1, column=adjusted_col, padx=2, pady=(0, 0), sticky="n")

        timestamp_labels[label] = ts_label

    # Apply stored hit colors
    if initial_data:
        for key in labels:
            hit_type = initial_data.get(f"{key}_hit", "")
            if hit_type == "TP":
                entries[key].configure(bg="lightgreen")
            elif hit_type == "SL":
                entries[key].configure(bg="lightcoral")

    # 🗑️ Delete button
    def delete_row():
        row_frame.destroy()
        for idx, (rf, _, _, _, _) in enumerate(rows):
            if rf == row_frame:
                del rows[idx]
                break

    delete_btn = tk.Button(row_frame, text="🗑️", command=delete_row, width=5, fg="red")
    delete_btn.grid(row=1 + row_offset, column=len(labels) + 1, padx=2, pady=(0, 2), sticky="n")

    # rows.append((row_frame, vars, entries, row_frame, timestamp_labels))
    rows.insert(0, (row_frame, vars, entries, row_frame, timestamp_labels))



    ## # # # # # # # # # # #  

def monitor_loop():
    if not running:
        return

    for idx, (entry_frame, vars, entries, ts_frame, timestamp_labels) in enumerate(rows):
        coin = vars["Coin"].get().upper()
        quote = vars["Quote"].get().upper()
        symbol = f"{coin}{quote}"
        current_price = fetch_price(symbol)
        vars["Mark Price"].set(str(current_price))

        direction = vars["Direction"].get().lower()
        is_short = direction == "short"

        # TP logic
        for i in range(1, 7):
            key = f"TP{i}"
            val = vars[key].get()
            if val:
                try:
                    clean_val = val.replace(",", ".").strip()
                    val_float = round(float(clean_val), 4)
                    hit_key = f"{coin}_{key}_{val_float}"
                    tp_hit = (is_short and current_price <= val_float) or (not is_short and current_price >= val_float)

                    print(f"TP Check → {symbol} {key} @ {val_float} | Price: {current_price} | HIT: {tp_hit}")

                    if tp_hit and hit_key not in already_logged:
                        entries[key].configure(bg="lightgreen")
                        log_hit(coin, key, val, "TP")
                        already_logged.add(hit_key)
                        timestamp_labels[key].configure(text=datetime.now().strftime("%d/%m/%y-%H:%M:%S"))
                    elif not tp_hit:
                        # entries[key].configure(bg="white")
                        # ✅ Nová podmínka:
                        if not timestamp_labels[key].cget("text"):
                            entries[key].configure(bg="white")
                except Exception as e:
                    print(f"TP Error → {key}: {e}")
                    entries[key].configure(bg="yellow")

        # SL logic
        for i in range(1, 3):
            key = f"SL{i}"
            val = vars[key].get()
            if val:
                try:
                    clean_val = val.replace(",", ".").strip()
                    val_float = round(float(clean_val), 4)
                    hit_key = f"{coin}_{key}_{val_float}"
                    sl_hit = (is_short and current_price > val_float) or (not is_short and current_price < val_float)

                    print(f"SL Check → {symbol} {key} @ {val_float} | Price: {current_price} | Dir: {direction} | HIT: {sl_hit}")

                    if sl_hit:
                        entries[key].configure(bg="lightcoral")
                        if hit_key not in already_logged:
                            log_hit(coin, key, val, "SL")
                            already_logged.add(hit_key)
                        timestamp_labels[key].configure(text=datetime.now().strftime("%d/%m/%y-%H:%M:%S"))
                    elif not sl_hit:
                        entries[key].configure(bg="white")
                except Exception as e:
                    print(f"SL Error → {key}: {e}")
                    entries[key].configure(bg="yellow")

        # EP1 Logic - automatické razítko při zadání
        ep1_val = vars["EP1"].get()
        if ep1_val and not timestamp_labels["EP1"].cget("text"):
            timestamp_labels["EP1"].configure(text=datetime.now().strftime("%d/%m/%y-%H:%M:%S"))

    now = datetime.now().strftime("%H:%M:%S")
    next_time = (datetime.now() + timedelta(seconds=int(interval_var.get()))).strftime("%H:%M:%S")
    status_text.set(f"🕰 Poslední aktualizace: {now} | ⏳ Příští: {next_time}")

    root.after(int(interval_var.get()) * 1000, monitor_loop)


def start():
    global running
    running = True
    monitor_loop()

def stop():
    global running
    running = False

def add_row(data=None):
    tk_label_row(data)

root = tk.Tk()
root.title("Sledovátor – TP/SL Monitor")

interval_var = tk.StringVar(root)
interval_var.set("30")

status_text = tk.StringVar()
status_text.set("Monitor nezačal…")
tk.Label(root, textvariable=status_text, font=("Segoe UI", 10, "italic")).pack(pady=5)

log_frame = tk.Frame(root)
log_frame.pack(pady=5, fill="both", expand=True)
tk.Label(log_frame, text="📋 Historie zásahů:", font=("Segoe UI", 12, "bold")).pack(anchor="w")
log_text = tk.Text(log_frame, height=10, width=120, bg="#f9f9f9", font=("Segoe UI", 10))
log_text.pack()

control_frame = tk.Frame(root)
control_frame.pack(pady=5)

saved_data = load_settings()
if saved_data:
    for entry in saved_data:
        tk_label_row(entry)
else:
    tk_label_row()

tk.Label(control_frame, text="Refresh interval (sec):").pack(side="left", padx=5)
tk.Entry(control_frame, textvariable=interval_var, width=5).pack(side="left", padx=5)
tk.Button(control_frame, text="+ Přidat řádek", command=lambda: tk_label_row(), bg="lightblue", height=2).pack(side="left", padx=5)
tk.Button(control_frame, text="▶ Start", command=start, bg="lightgreen", height=2).pack(side="left", padx=5)
tk.Button(control_frame, text="■ Stop", command=stop, bg="tomato", height=2).pack(side="left", padx=5)
tk.Button(control_frame, text="💾 Uložit hodnoty", command=save_settings, bg="khaki", height=2).pack(side="left", padx=5)

root.mainloop()
