import tkinter as tk
from tkinter import ttk
import random
import math
from datetime import datetime

class EonSentinelV65_Ultimate:
    def __init__(self, root):
        self.root = root
        self.root.title("EON-SENTINEL V65.0 // MOLECULAR COMMAND CENTER")
        self.root.geometry("1700x950")
        self.root.configure(background="#000000")

        self.idx = 0
        self.shield_active = False
        
        # --- PROFESYONEL METRİKLER VE BİRİMLER ---
        self.metrics = {
            # SOL PANEL: RESOURCE & BIO GROUP
            "PWR_BAT":      {"curr": 98.42, "unit": "Vdc",  "max": 100, "color": "#00FF88", "label": "MAIN BATTERY UNIT"},
            "PWR_CAP":      {"curr": 100.0, "unit": "kJ",   "max": 100, "color": "#00D4FF", "label": "SUPER-CAPACITOR ARRAY"},
            "MOF_RECOVERY": {"curr": 99.85, "unit": "L/h",  "max": 100, "color": "#00D4FF", "label": "MOF-MATRIX WATER RECOVERY"},
            "UiO_STABILITY":{"curr": 100.0, "unit": "Å",    "max": 100, "color": "#FFBD03", "label": "UiO-66 CRYSTAL INTEGRITY"},
            "BIO_OXY":      {"curr": 21.35, "unit": "%",    "max": 100, "color": "#00FF88", "label": "OXYGEN DENSITY"},
            "BIO_HUM":      {"curr": 76.50, "unit": "%RH",  "max": 100, "color": "#00D4FF", "label": "RELATIVE HUMIDITY"},
            "BIO_CO2_PCT":  {"curr": 442.0, "unit": "ppm",  "max": 100, "color": "#FFBD03", "label": "CO2 SATURATION"},
            "BIO_CHL":      {"curr": 88.42, "unit": "idx",  "max": 100, "color": "#39FF14", "label": "CHLOROPHYLL INDEX"}, # Sol alt yerleşim
            
            # ORTA PANEL: GRAPH DATA (SAYISAL VERİ SETLERİ)
            "TEMP":   {"curr": 24.15, "max": 45.0,   "color": "#FFBD03", "glow": "#332200", "unit": "°C"},
            "HUM_G":  {"curr": 76.20, "max": 100.0,  "color": "#00D4FF", "glow": "#001133", "unit": "%RH"},
            "OXY_G":  {"curr": 21.05, "max": 25.0,   "color": "#00FF88", "glow": "#002200", "unit": "%O2"},
            "CO2_G":  {"curr": 442.1, "max": 1000.0, "color": "#FF5500", "glow": "#331100", "unit": "PPM"}
        }

        self.history = {k: [0]*220 for k in ["TEMP", "HUM_G", "OXY_G", "CO2_G"]}
        self.setup_ui()
        self.add_log("SYSTEM_BOOT: KERNEL V65.0 STABLE.", "SYS")
        self.add_log("ENERGY_CELLS: NOMINAL. CAPACITOR AT FULL CHARGE.", "SYS")
        self.kernel_loop()

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, background="#030303", height=80, highlightbackground="#1A1A1A", highlightthickness=1)
        header.pack(fill="x", padx=15, pady=10)
        tk.Label(header, text="EON-SENTINEL V65.0", font=("Courier", 24, "bold"), foreground="#00D4FF", background="#030303").pack(side="left", padx=25)
        self.lbl_clock = tk.Label(header, text="", font=("Consolas", 12), foreground="#555", background="#030303")
        self.lbl_clock.pack(side="right", padx=25)

        main_frame = tk.Frame(self.root, background="#000000")
        main_frame.pack(fill="both", expand=True, padx=10)

        # SOL PANEL: VERİ BARLARI
        left = tk.Frame(main_frame, background="#000000", width=400)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        self.ui_bars = {}

        # Grup 1: ENERGY & RECOVERY
        f1 = tk.LabelFrame(left, text=" POWER & RECOVERY ", font=("Consolas", 10, "bold"), foreground="#00A8FF", background="#000", padx=15, pady=10)
        f1.pack(fill="x", pady=5)
        for k in ["PWR_BAT", "PWR_CAP", "MOF_RECOVERY", "UiO_STABILITY"]:
            self._create_bar_item(f1, k)

        # Grup 2: BIOLOGICAL CONTROL (Klorofili Buraya Sabitledik)
        f2 = tk.LabelFrame(left, text=" BIO-ATMOSPHERE CONTROL ", font=("Consolas", 10, "bold"), foreground="#00FF88", background="#000", padx=15, pady=10)
        f2.pack(fill="x", pady=5)
        for k in ["BIO_OXY", "BIO_HUM", "BIO_CO2_PCT", "BIO_CHL"]:
            self._create_bar_item(f2, k)

        # SAĞ PANEL: RAD & LOG
        right = tk.Frame(main_frame, background="#000000", width=380)
        right.pack(side="right", fill="y", padx=10)
        right.pack_propagate(False)

        rad_f = tk.LabelFrame(right, text=" SENSOR: RADIATION ", font=("Consolas", 10, "bold"), foreground="#FF3131", background="#000", pady=15)
        rad_f.pack(fill="x")
        self.lbl_rad = tk.Label(rad_f, text="42.0", font=("Consolas", 52, "bold"), foreground="#FF3131", background="#000")
        self.lbl_rad.pack()
        tk.Label(rad_f, text="COUNTS PER SECOND (c/s)", font=("Consolas", 8), foreground="#444", background="#000").pack()

        log_f = tk.LabelFrame(right, text=" MISSION LOGS ", font=("Consolas", 10, "bold"), foreground="#00D4FF", background="#000")
        log_f.pack(fill="both", expand=True, pady=15)
        self.log_w = tk.Text(log_f, background="#020202", foreground="#EEE", font=("Consolas", 9), bd=0, padx=10, pady=10, state="disabled")
        self.log_w.pack(fill="both", expand=True)
        self.log_w.tag_config("SYS", foreground="#00D4FF")
        self.log_w.tag_config("BIO", foreground="#39FF14")

        # ORTA PANEL: GRAFİKLER
        center = tk.Frame(main_frame, background="#000000")
        center.pack(fill="both", expand=True, padx=10)
        self.canvases, self.readouts = {}, {}
        grid = tk.Frame(center, background="#000")
        grid.pack(fill="both", expand=True)

        configs = [("TEMPERATURE (°C)", 0, 0, "TEMP"), ("HUMIDITY (%RH)", 0, 1, "HUM_G"), 
                   ("OXYGEN FLOW (%O2)", 1, 0, "OXY_G"), ("CARBON DENSITY (PPM)", 1, 1, "CO2_G")]
        
        for title, r, c, k in configs:
            f = tk.Frame(grid, background="#050505", highlightbackground="#1A1A1A", highlightthickness=1)
            f.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
            grid.grid_rowconfigure(r, weight=1); grid.grid_columnconfigure(c, weight=1)
            
            lbl_f = tk.Frame(f, background="#050505")
            lbl_f.pack(fill="x", padx=15, pady=8)
            tk.Label(lbl_f, text=f"SIGNAL_{k}", font=("Consolas", 9), foreground="#666", background="#050505").pack(side="left")
            
            rd = tk.Label(lbl_f, text="0.00", font=("Consolas", 16, "bold"), foreground=self.metrics[k]["color"], background="#050505")
            rd.pack(side="right")
            self.readouts[k] = rd
            
            cv = tk.Canvas(f, background="#000", highlightthickness=0)
            cv.pack(fill="both", expand=True)
            self.canvases[k] = cv

    def _create_bar_item(self, parent, k):
        tk.Label(parent, text=self.metrics[k]["label"], font=("Consolas", 8), foreground="#777", background="#000").pack(anchor="w")
        pb = ttk.Progressbar(parent, length=340, mode="determinate")
        pb.pack(fill="x", pady=4)
        lbl = tk.Label(parent, text="---", font=("Consolas", 10, "bold"), foreground=self.metrics[k]["color"], background="#000")
        lbl.pack(anchor="e")
        self.ui_bars[k] = (pb, lbl)

    def kernel_loop(self):
        # GERÇEKÇİ VERİ SETİ SİMÜLASYONU
        rad = 41.5 + random.uniform(-0.8, 0.8)
        self.lbl_rad.config(text=f"{rad:.1f}")
        
        # Grafik Verilerini Güncelle (Yüzdelik Değil, Birim Değerler)
        self.metrics["TEMP"]["curr"] = 24.1 + 2 * math.sin(self.idx * 0.05) + random.uniform(-0.1, 0.1)
        self.metrics["HUM_G"]["curr"] = 76.2 + random.uniform(-0.3, 0.3)
        self.metrics["OXY_G"]["curr"] = 21.0 + random.uniform(-0.05, 0.05)
        self.metrics["CO2_G"]["curr"] = 442.0 + random.uniform(-2, 5)

        # Bar Verilerini Güncelle
        self.metrics["BIO_CHL"]["curr"] = 88.4 + random.uniform(-0.1, 0.1)
        self.metrics["PWR_BAT"]["curr"] -= 0.001 # Deşarj simülasyonu
        
        if self.idx % 50 == 0:
            self.add_log(f"TELEMETRY: CHL_INDEX AT {self.metrics['BIO_CHL']['curr']:.2f} NOMINAL", "BIO")

        self.refresh_ui()
        self.idx += 1
        self.root.after(100, self.kernel_loop)

    def refresh_ui(self):
        self.lbl_clock.config(text=datetime.now().strftime("%H:%M:%S"))
        
        # Barlar (Sol Panel) - Sayısal Birimlerle
        for k, (pb, lbl) in self.ui_bars.items():
            m = self.metrics[k]
            pb["value"] = (m["curr"] / m["max"]) * 100
            lbl.config(text=f"{m['curr']:.2f} {m['unit']}")

        # Grafikler (Orta Panel)
        for k, cv in self.canvases.items():
            m = self.metrics[k]
            self.history[k].append(m["curr"])
            if len(self.history[k]) > 220: self.history[k].pop(0)
            

            self.readouts[k].config(text=f"{m['curr']:.2f} {m['unit']}")
            self.draw_graph(cv, self.history[k], m["color"], m["glow"], m["max"])

    def draw_graph(self, cv, data, color, glow, mx):
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 10: return
        

        for i in range(0, h, 40): cv.create_line(0, i, w, i, fill="#0A0A0A")
        
        pts = []
        for i, v in enumerate(data):
            x = i * (w / 219)
            y = h - (v / mx * h * 0.8) - 20 # Grafiklerin tavana vurmaması için 0.8 ile çarptık
            pts.append((x, y))
            
        if len(pts) > 1:
            cv.create_polygon([(0, h)] + pts + [(w, h)], fill=glow, stipple="gray50")
            cv.create_line(pts, fill=color, width=2.5)

    def add_log(self, msg, tag="SYS"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_w.config(state="normal")
        self.log_w.insert("end", f"[{ts}] {msg}\n", tag)
        self.log_w.see("end"); self.log_w.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TProgressbar", thickness=10, troughcolor="#080808", background="#00D4FF", bordercolor="#000")
    EonSentinelV65_Ultimate(root)
    root.mainloop()