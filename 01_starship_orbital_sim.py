"""Starship Orbital Flight & Orbital Debris Avoidance Simulator
Keys: Left/Right rotate | Up thrust | Down retro-thrust | R restart
Dotted line = predicted orbit (red X = predicted crash). Dodge the debris, don't hit the planet."""
import tkinter as tk, math, random
W, H = 900, 700
CX, CY = W / 2, H / 2
GM, PR = 600000.0, 55

def accel(x, y):
    dx, dy = CX - x, CY - y
    d = math.hypot(dx, dy) or 1e-6
    a = GM / (d * d)
    return a * dx / d, a * dy / d

class Game:
    def __init__(s, root):
        s.c = tk.Canvas(root, width=W, height=H, bg="black", highlightthickness=0)
        s.c.pack()
        s.keys, s.best = set(), 0.0
        root.bind("<KeyPress>", lambda e: s.keys.add(e.keysym))
        root.bind("<KeyRelease>", lambda e: s.keys.discard(e.keysym))
        root.bind("r", lambda e: s.reset())
        s.stars = [(random.randint(0, W), random.randint(0, H)) for _ in range(90)]
        s.reset()
        s.loop()

    def reset(s):
        r = 260.0
        s.x, s.y = CX + r, CY
        s.vx, s.vy = 0.0, -math.sqrt(GM / r)
        s.ang, s.fuel, s.t, s.alive, s.trail = -math.pi / 2, 100.0, 0.0, True, []
        s.debris = [s.new_debris() for _ in range(16)]

    def new_debris(s):
        while True:
            r, a = random.uniform(130, 340), random.uniform(0, 6.283)
            x, y = CX + r * math.cos(a), CY + r * math.sin(a)
            if math.hypot(x - s.x, y - s.y) > 120:
                break
        v = math.sqrt(GM / r) * random.uniform(0.88, 1.05) * random.choice((1, -1))
        return [x, y, -math.sin(a) * v, math.cos(a) * v]

    def step(s, dt):
        if "Left" in s.keys: s.ang -= 2.8 * dt
        if "Right" in s.keys: s.ang += 2.8 * dt
        ax, ay = accel(s.x, s.y)
        if s.fuel > 0:
            if "Up" in s.keys:
                ax += 70 * math.cos(s.ang); ay += 70 * math.sin(s.ang); s.fuel -= 5 * dt
            if "Down" in s.keys:
                ax -= 70 * math.cos(s.ang); ay -= 70 * math.sin(s.ang); s.fuel -= 5 * dt
        s.vx += ax * dt; s.vy += ay * dt
        s.x += s.vx * dt; s.y += s.vy * dt
        for i, d in enumerate(s.debris):
            gx, gy = accel(d[0], d[1])
            d[2] += gx * dt; d[3] += gy * dt
            d[0] += d[2] * dt; d[1] += d[3] * dt
            if math.hypot(d[0] - CX, d[1] - CY) < PR + 4:
                s.debris[i] = s.new_debris()
            elif math.hypot(d[0] - s.x, d[1] - s.y) < 13:
                s.alive = False
        if math.hypot(s.x - CX, s.y - CY) < PR + 4:
            s.alive = False
        s.t += dt

    def predict(s):
        x, y, vx, vy, pts = s.x, s.y, s.vx, s.vy, []
        for i in range(260):
            ax, ay = accel(x, y)
            vx += ax * 0.06; vy += ay * 0.06
            x += vx * 0.06; y += vy * 0.06
            if math.hypot(x - CX, y - CY) < PR:
                return pts, (x, y)
            if i % 4 == 0: pts.append((x, y))
        return pts, None

    def loop(s):
        if s.alive:
            for _ in range(2): s.step(1 / 60)
            s.trail.append((s.x, s.y)); s.trail = s.trail[-150:]
            s.best = max(s.best, s.t)
        c = s.c; c.delete("all")
        for x, y in s.stars: c.create_rectangle(x, y, x + 1, y + 1, fill="#556")
        c.create_oval(CX - PR, CY - PR, CX + PR, CY + PR, fill="#2a6fb0", outline="#8cf")
        pts, crash = s.predict()
        for x, y in pts: c.create_oval(x - 1, y - 1, x + 1, y + 1, fill="#6f6", outline="")
        if crash:
            c.create_text(crash[0], crash[1], text="X", fill="red", font=("Arial", 14, "bold"))
        for x, y in s.trail: c.create_oval(x - 1, y - 1, x + 1, y + 1, fill="#888", outline="")
        for d in s.debris: c.create_rectangle(d[0] - 4, d[1] - 4, d[0] + 4, d[1] + 4, fill="#e84", outline="")
        a = s.ang; p = []
        for da, r in ((0, 12), (2.5, 9), (-2.5, 9)):
            p += [s.x + r * math.cos(a + da), s.y + r * math.sin(a + da)]
        c.create_polygon(p, fill="white" if s.alive else "red", outline="cyan")
        if s.alive and ("Up" in s.keys or "Down" in s.keys) and s.fuel > 0:
            c.create_oval(s.x - 3, s.y - 3, s.x + 3, s.y + 3, fill="orange", outline="")
        alt = math.hypot(s.x - CX, s.y - CY) - PR
        c.create_text(10, 10, anchor="nw", fill="white", font=("Consolas", 12),
            text=f"ALT {alt:6.0f}   SPD {math.hypot(s.vx, s.vy):5.1f}   FUEL {s.fuel:5.1f}%   TIME {s.t:5.1f}s   BEST {s.best:5.1f}s")
        if not s.alive:
            c.create_text(CX, CY - 100, text="MISSION FAILED - press R", fill="red", font=("Arial", 28, "bold"))
        s.c.after(16, s.loop)

root = tk.Tk(); root.title("Starship Orbital Debris Avoidance"); Game(root); root.mainloop()
