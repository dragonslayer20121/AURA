import tkinter as tk
from tkinter import colorchooser, messagebox
from datetime import datetime
import math, random

# AURA v2 — personal desktop clock + neon ring
# Standard-library-only prototype. Right-click for options.

BG = "#090611"
PINK = "#ff2d87"
ORANGE = "#ff8b31"
WHITE = "#f7f1ff"
MUTED = "#d48bb4"

class Aura:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AURA")
        self.root.geometry("560x310+80+70")
        self.root.configure(bg=BG)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.91)

        self.accent = PINK
        self.ring_on = True
        self.clock_on = True
        self.phase = 0.0
        self.drag = (0,0)
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.menu = tk.Menu(self.root, tearoff=0, bg="#17111f", fg=WHITE,
                            activebackground="#54203e", activeforeground=WHITE)
        self.menu.add_command(label="Toggle clock", command=self.toggle_clock)
        self.menu.add_command(label="Toggle visualizer", command=self.toggle_ring)
        self.menu.add_command(label="Change accent color", command=self.pick_color)
        self.menu.add_separator()
        self.menu.add_command(label="Reset position", command=lambda: self.root.geometry("560x310+80+70"))
        self.menu.add_command(label="Hide AURA", command=self.root.withdraw)
        self.menu.add_command(label="Show AURA", command=self.root.deiconify)
        self.menu.add_command(label="Quit", command=self.root.destroy)

        for w in (self.root, self.canvas):
            w.bind("<Button-1>", self.start_drag)
            w.bind("<B1-Motion>", self.move_drag)
            w.bind("<Button-3>", self.popup)
            w.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Map>", lambda e: self.root.attributes("-topmost", True))
        self.draw()

    def start_drag(self, e):
        self.drag = (e.x_root-self.root.winfo_x(), e.y_root-self.root.winfo_y())

    def move_drag(self, e):
        self.root.geometry(f"+{e.x_root-self.drag[0]}+{e.y_root-self.drag[1]}")

    def popup(self, e):
        self.menu.tk_popup(e.x_root, e.y_root)

    def toggle_clock(self):
        self.clock_on = not self.clock_on

    def toggle_ring(self):
        self.ring_on = not self.ring_on

    def pick_color(self):
        picked = colorchooser.askcolor(color=self.accent, title="AURA accent color")[1]
        if picked:
            self.accent = picked

    def draw(self):
        self.canvas.delete("all")
        w, h = 560, 310
        now = datetime.now()

        # Soft visual accents
        self.canvas.create_oval(-170,-190,300,250, fill="#1a0b2b", outline="")
        self.canvas.create_oval(350,150,750,520, fill="#101c35", outline="")

        # Header
        self.canvas.create_text(25,22,text="A U R A",fill=self.accent,
                               font=("Segoe UI Semibold",10),anchor="w")
        self.canvas.create_text(w-24,22,text="⋯",fill="#8f789d",
                               font=("Segoe UI",17),anchor="e")

        if self.clock_on:
            time_text = now.strftime("%I:%M").lstrip("0")
            ampm = now.strftime("%p")
            self.canvas.create_text(330,115,text=time_text,fill=WHITE,
                                   font=("Segoe UI Light",64),anchor="center")
            self.canvas.create_text(465,133,text=ampm,fill=MUTED,
                                   font=("Segoe UI",17),anchor="center")
            self.canvas.create_text(330,164,text=now.strftime("%A, %B %d").upper(),
                                   fill=MUTED,font=("Segoe UI Semibold",11),
                                   anchor="center")

        if self.ring_on:
            cx, cy = 88, 218
            self.phase += 0.10
            for i in range(72):
                a = 2*math.pi*i/72 + self.phase
                # visual ambient pulse; audio-reactive mode can be added later
                pulse = 3.5*math.sin(self.phase*2.2+i*0.38)+random.uniform(0,1.8)
                r1, r2 = 54, 61+pulse
                x1,y1 = cx+math.cos(a)*r1,cy+math.sin(a)*r1
                x2,y2 = cx+math.cos(a)*r2,cy+math.sin(a)*r2
                color = self.accent if i < 52 else ORANGE
                self.canvas.create_line(x1,y1,x2,y2,fill=color,width=2.5,capstyle="round")
            self.canvas.create_oval(cx-44,cy-44,cx+44,cy+44,
                                   fill="#160c23",outline="#4a1b52",width=2)
            self.canvas.create_oval(cx-29,cy-29,cx+29,cy+29,
                                   fill="#24112e",outline="#68265f",width=1)
            self.canvas.create_oval(cx-10,cy-10,cx+10,cy+10,
                                   fill="#a84a24",outline="#ff754e",width=1)

        self.canvas.create_text(w/2,h-22,text="DRAG TO MOVE  •  RIGHT-CLICK FOR SETTINGS",
                               fill="#826b8d",font=("Segoe UI",8),anchor="center")
        self.root.after(50,self.draw)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    Aura().run()
