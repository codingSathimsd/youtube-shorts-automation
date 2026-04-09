import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math
import random
import os

# ── Canvas ─────────────────────────────────────────────────────────────────
W, H = 1920, 1080
FPS  = 24

# ── Palettes ────────────────────────────────────────────────────────────────
PALETTES = {
    "forest":    {"sky": "#87CEEB", "ground": "#5DBB63"},
    "night":     {"sky": "#1a1a4e", "ground": "#2d5a27"},
    "beach":     {"sky": "#00BFFF", "ground": "#F4D03F"},
    "classroom": {"sky": "#FFF9C4", "ground": "#A5D6A7"},
    "space":     {"sky": "#0a0a2e", "ground": "#1a1a4e"},
    "village":   {"sky": "#FFB347", "ground": "#7CFC00"},
    "cave":      {"sky": "#4a4a4a", "ground": "#2c2c2c"},
    "mountain":  {"sky": "#87CEEB", "ground": "#8B7355"},
    "jungle":    {"sky": "#228B22", "ground": "#145214"},
    "castle":    {"sky": "#B0C4DE", "ground": "#808080"},
}

CHARACTERS = {
    "lion":     {"body": "#FFB347", "mane": "#FF8C00", "eyes": "#4A235A", "ears": "#FF8C00"},
    "rabbit":   {"body": "#FFB6C1", "mane": "#FF69B4", "eyes": "#4A235A", "ears": "#FF69B4"},
    "robot":    {"body": "#B0C4DE", "mane": "#4682B4", "eyes": "#00FF00", "ears": "#4682B4"},
    "elephant": {"body": "#A9A9A9", "mane": "#808080", "eyes": "#4A235A", "ears": "#808080"},
    "fox":      {"body": "#FF6B35", "mane": "#CC3300", "eyes": "#4A235A", "ears": "#CC3300"},
    "penguin":  {"body": "#2C3E50", "mane": "#ECF0F1", "eyes": "#E74C3C", "ears": "#2C3E50"},
    "dragon":   {"body": "#27AE60", "mane": "#1E8449", "eyes": "#F39C12", "ears": "#1E8449"},
    "unicorn":  {"body": "#DDA0DD", "mane": "#FF1493", "eyes": "#4A235A", "ears": "#FF1493"},
}

def pick_character(topic):
    t = topic.lower()
    if any(w in t for w in ["lion","brave","jungle","wild","king","courage"]):
        return "lion", CHARACTERS["lion"]
    elif any(w in t for w in ["space","star","planet","rocket","galaxy","astronaut"]):
        return "robot", CHARACTERS["robot"]
    elif any(w in t for w in ["magic","fairy","princess","unicorn","rainbow","wish"]):
        return "unicorn", CHARACTERS["unicorn"]
    elif any(w in t for w in ["fox","clever","smart","trick","cunning","sly"]):
        return "fox", CHARACTERS["fox"]
    elif any(w in t for w in ["dragon","fire","adventure","quest","treasure"]):
        return "dragon", CHARACTERS["dragon"]
    elif any(w in t for w in ["ocean","sea","fish","water","swim","beach","island"]):
        return "penguin", CHARACTERS["penguin"]
    elif any(w in t for w in ["elephant","big","strong","memory","forget"]):
        return "elephant", CHARACTERS["elephant"]
    else:
        return "rabbit", CHARACTERS["rabbit"]

def pick_scene(scene_number, total_scenes=30):
    names = list(PALETTES.keys())
    return names[scene_number % len(names)], PALETTES[names[scene_number % len(names)]]

# ── 3D Rendering Helpers ─────────────────────────────────────────────────────

def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"

def shade_color(hex_color, factor):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(int(r*factor), int(g*factor), int(b*factor))

def lighten_color(hex_color, amount=60):
    r, g, b = hex_to_rgb(hex_color)
    return rgb_to_hex(r+amount, g+amount, b+amount)

def draw_sphere_3d(draw, cx, cy, radius, base_color, light_angle=135):
    """True 3D sphere with radial gradient, specular highlight and shadow"""
    if radius < 2:
        return
    base_rgb = hex_to_rgb(base_color)
    lx = cx - int(radius * math.cos(math.radians(light_angle)) * 0.4)
    ly = cy - int(radius * math.sin(math.radians(light_angle)) * 0.4)

    # Draw concentric circles from outside in
    for r in range(radius, 0, -1):
        dist_from_light = math.sqrt((cx-r/radius*lx-lx)**2 +
                                     (cy-r/radius*ly-ly)**2) / radius
        factor = 0.45 + 0.55 * (1 - r/radius)
        shaded = tuple(min(255, int(c * factor)) for c in base_rgb)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=shaded)

    # Specular highlight - bright spot
    hl_r = max(2, int(radius * 0.38))
    hl_x = cx - int(radius * 0.30)
    hl_y = cy - int(radius * 0.30)
    for r in range(hl_r, 0, -1):
        factor    = 1 - (r / hl_r)
        hl_bright = int(220 * factor)
        hl_color  = tuple(min(255, c + hl_bright) for c in base_rgb)
        draw.ellipse([hl_x-r, hl_y-r, hl_x+r, hl_y+r], fill=hl_color)

    # Ground shadow (oval under the sphere)
    sh_y = cy + radius + int(radius * 0.15)
    sh_w = int(radius * 1.4)
    sh_h = int(radius * 0.25)
    for i in range(7):
        alpha = max(0, 55 - i*8)
        sw    = max(0, sh_w - i*8)
        sh    = max(0, sh_h - i*2)
        if sw > 0 and sh > 0:
            draw.ellipse([cx-sw//2, sh_y-sh//2,
                           cx+sw//2, sh_y+sh//2],
                          fill=(alpha, alpha, alpha))

def draw_cylinder_3d(draw, x1, y1, x2, y2, width, base_color):
    """3D cylinder with highlight stripe and shadow stripe"""
    if width < 2:
        return
    base_rgb = hex_to_rgb(base_color)
    dark     = tuple(max(0, int(c * 0.55)) for c in base_rgb)
    light    = tuple(min(255, int(c * 1.35)) for c in base_rgb)
    mid      = base_rgb

    draw.line([x1, y1, x2, y2], fill=mid,   width=width)
    draw.line([x1-width//4, y1, x2-width//4, y2],
              fill=light, width=max(2, width//3))
    draw.line([x1+width//4, y1, x2+width//4, y2],
              fill=dark,  width=max(2, width//3))

def draw_rounded_rect_3d(draw, x1, y1, x2, y2, base_color, radius=15):
    """3D rounded rectangle (for robot parts, desks etc.)"""
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=base_color)
    light = lighten_color(base_color, 50)
    dark  = shade_color(base_color, 0.6)
    # Top highlight edge
    draw.line([x1+radius, y1+2, x2-radius, y1+2], fill=light, width=3)
    # Left highlight edge
    draw.line([x1+2, y1+radius, x1+2, y2-radius], fill=light, width=3)
    # Bottom shadow edge
    draw.line([x1+radius, y2-2, x2-radius, y2-2], fill=dark, width=3)
    # Right shadow edge
    draw.line([x2-2, y1+radius, x2-2, y2-radius], fill=dark, width=3)

# ── Background Scenes ─────────────────────────────────────────────────────────

def draw_background(draw, scene_name, palette, t):
    sky_rgb = hex_to_rgb(palette["sky"])
    # Sky gradient
    for y in range(int(H * 0.68)):
        factor = y / (H * 0.68)
        r = max(0, min(255, int(sky_rgb[0] * (1 - factor*0.35))))
        g = max(0, min(255, int(sky_rgb[1] * (1 - factor*0.12))))
        b = max(0, min(255, int(sky_rgb[2])))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    # Ground
    gr_rgb = hex_to_rgb(palette["ground"])
    for y in range(int(H*0.68), H):
        factor = (y - H*0.68) / (H * 0.32)
        r = max(0, min(255, int(gr_rgb[0] * (1 - factor*0.2))))
        g = max(0, min(255, int(gr_rgb[1] * (1 - factor*0.2))))
        b = max(0, min(255, int(gr_rgb[2] * (1 - factor*0.2))))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    if scene_name == "forest":      draw_forest(draw, t)
    elif scene_name == "night":     draw_night(draw, t)
    elif scene_name == "beach":     draw_beach(draw, t)
    elif scene_name == "space":     draw_space(draw, t)
    elif scene_name == "classroom": draw_classroom(draw, t)
    elif scene_name == "village":   draw_village(draw, t)
    elif scene_name == "mountain":  draw_mountain(draw, t)
    elif scene_name == "jungle":    draw_jungle(draw, t)
    elif scene_name == "castle":    draw_castle(draw, t)
    else:                           draw_cave(draw, t)

def draw_forest(draw, t):
    # Animated sun with rays
    sx, sy = int(W*0.12), int(H*0.12)
    sy += int(math.sin(t*0.4)*8)
    draw_sphere_3d(draw, sx, sy, 55, "#FFD700")
    for i in range(12):
        angle = i*30 + t*20
        rx = sx + int(math.cos(math.radians(angle))*85)
        ry = sy + int(math.sin(math.radians(angle))*85)
        draw.line([sx, sy, rx, ry], fill="#FFE566", width=4)
    # Clouds
    for i in range(4):
        cx2 = int((W*0.1 + i*W*0.28 + t*18) % (W+300)) - 150
        draw_cloud_3d(draw, cx2, int(H*0.08 + i*35), 110+i*20)
    # Background trees (smaller, darker)
    for i, tx in enumerate([80,200,380,W-380,W-200,W-80,W//2-300,W//2+300]):
        sway = math.sin(t*1.2+i*0.9)*6
        draw_tree_3d(draw, tx, int(H*0.68), sway, i, scale=0.75)
    # Foreground trees (bigger)
    for i, tx in enumerate([150, W-150, W//2-180, W//2+180]):
        sway = math.sin(t*1.5+i*0.6)*10
        draw_tree_3d(draw, tx, int(H*0.68), sway, i+10, scale=1.1)
    # Flowers
    for i in range(16):
        fx = 60 + i*118
        fy = int(H*0.71) + int(math.sin(t+i*0.4)*6)
        draw_flower_3d(draw, fx, fy, ["#FF6B6B","#FFD700","#FF69B4","#FF4500","#9B59B6"][i%5])

def draw_night(draw, t):
    rng = random.Random(42)
    for i in range(120):
        sx2 = rng.randint(0, W)
        sy2 = rng.randint(0, int(H*0.62))
        bright = int(130 + 125*math.sin(t*1.8+i*0.4))
        size   = rng.randint(1, 5)
        draw_sphere_3d(draw, sx2, sy2, size, rgb_to_hex(bright, bright, bright))
    # Moon
    draw_sphere_3d(draw, int(W*0.82), int(H*0.14), 52, "#FFFACD")
    draw_sphere_3d(draw, int(W*0.82)+18, int(H*0.14)-12, 42, "#1a1a4e")
    # Fireflies
    for i in range(10):
        fx2 = int((i*193+t*25)%W)
        fy2 = int(H*0.55+math.sin(t*2+i)*80)
        glow = int(abs(math.sin(t*3+i))*255)
        draw_sphere_3d(draw, fx2, fy2, 5, rgb_to_hex(glow, glow, 0))
    for i in range(5):
        draw_tree_3d(draw, 100+i*350, int(H*0.68), 0, i+20, scale=0.9, dark=True)

def draw_beach(draw, t):
    # Ocean waves
    for wave in range(6):
        wy = int(H*0.45 + wave*28 + math.sin(t*1.8+wave*0.7)*18)
        alpha = 130 + wave*15
        draw.arc([0, wy-25, W, wy+25], 0, 180,
                 fill=(0, 100+wave*12, 180+wave*8), width=9)
    # Sun
    draw_sphere_3d(draw, W-130, 80, 58, "#FFD700")
    # Palm trees
    draw_palm_3d(draw, int(W*0.12), int(H*0.68), t)
    draw_palm_3d(draw, int(W*0.88), int(H*0.68), t+1.0)
    # Shells on sand
    for i in range(8):
        shx = 120 + i*220
        shy = int(H*0.74) + int(math.sin(i)*15)
        draw_sphere_3d(draw, shx, shy, 10, ["#FFB6C1","#FFA500","#98FB98"][i%3])

def draw_space(draw, t):
    rng = random.Random(7)
    # Stars
    for i in range(200):
        sx2 = rng.randint(0, W)
        sy2 = rng.randint(0, H)
        bright = int(80 + 175*abs(math.sin(t*0.8+i*0.25)))
        draw_sphere_3d(draw, sx2, sy2, rng.randint(1,4),
                       rgb_to_hex(bright, bright, bright))
    # Planets
    draw_sphere_3d(draw, int(W*0.82), int(H*0.18), 70, "#FF6B35")
    # Planet ring
    draw.arc([int(W*0.82)-95, int(H*0.18)-20,
               int(W*0.82)+95, int(H*0.18)+20],
             0, 180, fill="#CC5522", width=8)
    draw_sphere_3d(draw, int(W*0.15), int(H*0.3), 45, "#DDA0DD")
    # Moving rocket
    rx2 = int((t*55)%W)
    draw_rocket_3d(draw, rx2, int(H*0.12))
    # Nebula effect
    for i in range(5):
        nx = rng.randint(200, W-200)
        ny = rng.randint(100, int(H*0.5))
        nr = rng.randint(30, 80)
        nc = ["#FF69B4","#87CEEB","#9B59B6","#3498DB"][i%4]
        rgb2 = hex_to_rgb(nc)
        draw.ellipse([nx-nr, ny-nr//2, nx+nr, ny+nr//2],
                     fill=(rgb2[0]//4, rgb2[1]//4, rgb2[2]//4))

def draw_classroom(draw, t):
    draw.rectangle([0, 0, W, int(H*0.68)], fill="#FFF8DC")
    # 3D blackboard
    draw_rounded_rect_3d(draw, int(W*0.18), int(H*0.04),
                          int(W*0.82), int(H*0.48), "#2C5F2E", radius=12)
    draw.rounded_rectangle([int(W*0.19), int(H*0.05),
                             int(W*0.81), int(H*0.47)], radius=8, fill="#2E7D32")
    chars = ["A","B","C","1","2","3","★","♥","π","∞"]
    for i, ch in enumerate(chars):
        cx2 = int(W*0.23 + i*95)
        cy2 = int(H*0.18 + math.sin(t*2.5+i)*12)
        draw_text_simple(draw, ch, cx2, cy2, size=55, color="#FFFFFF")
    # Windows with 3D frames
    for wx2 in [int(W*0.03), int(W*0.83)]:
        draw_rounded_rect_3d(draw, wx2, int(H*0.06),
                              wx2+130, int(H*0.38), "#8B6914", radius=8)
        draw.rectangle([wx2+8, int(H*0.07),
                        wx2+122, int(H*0.37)], fill="#87CEEB")
        # Sunlight through window
        draw.line([wx2+10, int(H*0.215), wx2+120, int(H*0.215)],
                  fill="white", width=3)
        draw.line([wx2+65, int(H*0.07), wx2+65, int(H*0.37)],
                  fill="white", width=3)
    # 3D Desks
    for i in range(4):
        dx2 = 110 + i*440
        draw_rounded_rect_3d(draw, dx2, int(H*0.72),
                              dx2+210, int(H*0.76), "#8B4513", radius=5)
        draw.rectangle([dx2+25, int(H*0.76), dx2+60, int(H*0.86)], fill="#6B3410")
        draw.rectangle([dx2+150, int(H*0.76), dx2+185, int(H*0.86)], fill="#6B3410")

def draw_village(draw, t):
    for i in range(5):
        cx2 = int((80+i*380+t*14)%(W+300))-150
        draw_cloud_3d(draw, cx2, 70+i*28, 115)
    houses = [(100,"#FF6B6B"),(340,"#4ECDC4"),(640,"#FFD93D"),
              (W-350,"#A8E6CF"),(W-130,"#FF6B6B")]
    for hx2, hcolor in houses:
        draw_house_3d(draw, hx2, int(H*0.68), hcolor)
    # Road
    draw.polygon([(W//2-100,H),(W//2+100,H),
                  (W//2+220,int(H*0.68)),(W//2-220,int(H*0.68))],
                 fill="#C8B89A")
    # Road markings
    for i in range(5):
        ry2 = int(H*0.72 + i*50)
        draw.line([W//2-5, ry2, W//2+5, ry2+30],
                  fill="#FFFFFF", width=4)

def draw_mountain(draw, t):
    mts = [(W//5,"#7B8B6F",280),(W//2,"#6B7B5F",340),
           (4*W//5,"#8B9B7F",260),(W//8,"#9BAB8F",200),(7*W//8,"#6B7B5F",300)]
    for mx2, mc, mh in mts:
        draw.polygon([(mx2-220,int(H*0.68)),(mx2,int(H*0.68)-mh),
                      (mx2+220,int(H*0.68))], fill=mc)
        draw.polygon([(mx2-50,int(H*0.68)-mh+55),(mx2,int(H*0.68)-mh),
                      (mx2+50,int(H*0.68)-mh+55)], fill="white")
        # Mountain shading
        dark = shade_color(mc, 0.7)
        draw.polygon([(mx2,int(H*0.68)-mh),(mx2+220,int(H*0.68)),
                      (mx2+50,int(H*0.68)-mh+55)], fill=dark)
    for i in range(6):
        bx2 = int((i*310+t*38)%W)
        by2 = int(H*0.18+i*22)
        draw_bird_3d(draw, bx2, by2, t+i*0.4)

def draw_jungle(draw, t):
    # Dense jungle
    for i in range(10):
        tx2 = i*210
        draw_tree_3d(draw, tx2, int(H*0.68), math.sin(t+i)*8, i, scale=1.3)
    # Vines
    for i in range(6):
        vx2 = 100+i*300
        for j in range(8):
            vy2 = j*90
            draw.line([vx2+int(math.sin(t+j)*15), vy2,
                       vx2+int(math.sin(t+j+0.5)*15), vy2+90],
                      fill="#228B22", width=5)
    # Exotic flowers
    for i in range(10):
        fx2 = 80+i*188
        fy2 = int(H*0.7)+int(math.sin(t+i)*8)
        draw_flower_3d(draw, fx2, fy2, ["#FF0066","#FF6600","#FFFF00"][i%3])

def draw_castle(draw, t):
    # Castle structure
    for tx2 in [int(W*0.1), int(W*0.4), int(W*0.6), int(W*0.9)]:
        draw_rounded_rect_3d(draw, tx2-40, int(H*0.25), tx2+40,
                              int(H*0.68), "#808080", radius=4)
        # Battlements
        for bx2 in range(tx2-40, tx2+40, 20):
            draw_rounded_rect_3d(draw, bx2, int(H*0.18), bx2+14,
                                  int(H*0.25), "#707070", radius=3)
    # Main gate
    draw_rounded_rect_3d(draw, int(W*0.4), int(H*0.25),
                          int(W*0.6), int(H*0.68), "#909090", radius=6)
    draw.arc([int(W*0.44), int(H*0.42), int(W*0.56), int(H*0.55)],
             180, 360, fill="#333333", width=4)
    draw.rectangle([int(W*0.44), int(H*0.48), int(W*0.56), int(H*0.68)],
                   fill="#333333")
    # Flags waving
    for fx2 in [int(W*0.1), int(W*0.5), int(W*0.9)]:
        draw.line([fx2, int(H*0.08), fx2, int(H*0.22)],
                  fill="#5C3317", width=4)
        wave = int(math.sin(t*2)*8)
        draw.polygon([(fx2,int(H*0.09)),(fx2+45+wave,int(H*0.12)),
                      (fx2,int(H*0.16))], fill="#FF0000")

def draw_cave(draw, t):
    draw.ellipse([-300,-300,W+300,int(H*0.82)], fill="#3a3a3a")
    draw.ellipse([-200,-200,W+200,int(H*0.76)], fill="#1a1a2a")
    crystal_colors = ["#00FFFF","#FF00FF","#FFD700","#00FF00","#FF6699"]
    for i in range(10):
        cx2 = 80+i*185
        cy2 = int(H*0.6)
        glow = abs(math.sin(t*1.8+i*0.4))
        draw_crystal_3d(draw, cx2, cy2, crystal_colors[i%5], glow)
    for tx2 in [int(W*0.18), int(W*0.82)]:
        draw_torch_3d(draw, tx2, int(H*0.33), t)

# ── Scene Detail Helpers ──────────────────────────────────────────────────────

def draw_cloud_3d(draw, cx, cy, size):
    """3D-style puffy cloud"""
    parts = [(cx,cy,size),(cx-size*0.6,cy+size*0.1,size*0.7),
             (cx+size*0.6,cy+size*0.1,size*0.7),(cx-size*0.3,cy-size*0.3,size*0.6),
             (cx+size*0.3,cy-size*0.3,size*0.6)]
    for px2,py2,pr in parts:
        draw_sphere_3d(draw, int(px2), int(py2), int(pr), "#FFFFFF")

def draw_tree_3d(draw, tx, ty, sway, seed, scale=1.0, dark=False):
    rng    = random.Random(seed)
    trunk  = "#5C3317" if not dark else "#2C1A0A"
    leaf1  = "#228B22" if not dark else "#1A4A1A"
    leaf2  = "#2ECC71" if not dark else "#1A6030"
    height = int(rng.randint(130,210)*scale)
    tw     = int(16*scale)
    # 3D trunk
    draw_cylinder_3d(draw, int(tx+sway//2), ty-height+90,
                     int(tx+sway), ty, tw, trunk)
    # Three leaf layers
    for i in range(3):
        lw2 = int((90-i*18)*scale)
        ly2 = ty-height+i*45
        # Shadow layer
        draw.polygon([(int(tx+sway),ly2+8),
                      (int(tx-lw2+sway*0.4),ly2+65),
                      (int(tx+lw2+sway*0.4),ly2+65)],
                     fill=shade_color(leaf1, 0.7))
        # Main layer
        draw.polygon([(int(tx+sway),ly2),
                      (int(tx-lw2+sway*0.4),ly2+60),
                      (int(tx+lw2+sway*0.4),ly2+60)], fill=leaf1)
        # Highlight
        draw.polygon([(int(tx+sway),ly2),
                      (int(tx-lw2//3+sway*0.4),ly2+35),
                      (int(tx+lw2//3+sway*0.4),ly2+35)], fill=leaf2)

def draw_flower_3d(draw, fx, fy, color):
    for angle in range(0,360,60):
        px2 = fx+int(math.cos(math.radians(angle))*17)
        py2 = fy+int(math.sin(math.radians(angle))*17)
        draw_sphere_3d(draw, px2, py2, 11, color)
    draw_sphere_3d(draw, fx, fy, 9, "#FFD700")

def draw_house_3d(draw, hx, hy, color):
    # 3D box body
    draw_rounded_rect_3d(draw, hx, hy-130, hx+190, hy, color, radius=4)
    # Side face (darker)
    dark_c = shade_color(color, 0.65)
    draw.polygon([(hx+190,hy-130),(hx+220,hy-110),
                  (hx+220,hy+20),(hx+190,hy)], fill=dark_c)
    # 3D roof
    draw.polygon([(hx-25,hy-130),(hx+95,hy-215),(hx+215,hy-130)],
                 fill="#CC4444")
    draw.polygon([(hx+215,hy-130),(hx+95,hy-215),(hx+245,hy-110)],
                 fill=shade_color("#CC4444", 0.7))
    # Door
    draw_rounded_rect_3d(draw, hx+70, hy-75, hx+120, hy, "#8B4513", radius=8)
    draw_sphere_3d(draw, hx+114, hy-35, 6, "#FFD700")
    # Windows
    for wx2 in [hx+15, hx+130]:
        draw_rounded_rect_3d(draw, wx2, hy-105, wx2+50, hy-70, "#87CEEB", radius=4)

def draw_palm_3d(draw, px, py, t):
    sway = int(math.sin(t*0.7)*18)
    pts  = [(px,py),(px+sway//3,py-110),(px+sway*0.7,py-210),(px+sway,py-295)]
    for i in range(len(pts)-1):
        draw_cylinder_3d(draw, pts[i][0], pts[i][1],
                         pts[i+1][0], pts[i+1][1], 20, "#8B6914")
    lx2,ly2 = px+sway, py-295
    for angle in range(0,360,55):
        ex2 = lx2+int(math.cos(math.radians(angle+t*12))*90)
        ey2 = ly2+int(math.sin(math.radians(angle+t*12))*45)
        draw.line([lx2,ly2,ex2,ey2], fill="#228B22", width=14)
        draw.line([lx2,ly2,(lx2+ex2)//2,(ly2+ey2)//2],
                  fill="#2ECC71", width=7)

def draw_rocket_3d(draw, rx, ry):
    draw_cylinder_3d(draw, rx, ry-45, rx, ry+35, 22, "#C0C0C0")
    draw.polygon([(rx,ry-65),(rx-11,ry-45),(rx+11,ry-45)], fill="#FF4444")
    draw_sphere_3d(draw, rx-18, ry+30, 13, "#FF6600")
    draw_sphere_3d(draw, rx+18, ry+30, 13, "#FF6600")

def draw_crystal_3d(draw, cx, cy, color, glow):
    rgb2   = hex_to_rgb(color)
    bright = tuple(min(255, int(c*(0.4+glow*0.7))) for c in rgb2)
    ch2    = int(65+glow*35)
    draw.polygon([(cx,cy-ch2),(cx-22,cy),(cx,cy+22),(cx+22,cy)], fill=bright)
    # Shine
    draw.line([cx-5,cy-ch2+5,cx-8,cy-10], fill="white", width=2)

def draw_torch_3d(draw, tx, ty, t):
    draw_cylinder_3d(draw, tx, ty+5, tx, ty+45, 10, "#8B4513")
    for i, fc in enumerate(["#FF4500","#FF6600","#FFD700"]):
        flicker = int(math.sin(t*9+i)*9)
        size    = 16-i*4
        draw_sphere_3d(draw, tx+flicker, ty-15-i*10, size, fc)

def draw_bird_3d(draw, bx, by, t):
    wing = int(math.sin(t*5)*12)
    draw.arc([bx-22,by-wing,bx,    by+wing], 0, 180, fill="#333", width=4)
    draw.arc([bx,   by-wing,bx+22, by+wing], 0, 180, fill="#333", width=4)

# ── 3D Character Drawing ──────────────────────────────────────────────────────

def draw_character(draw, char_name, char_colors, x, y, t,
                   action="idle", expression="happy", scale=1.0):
    s          = scale
    body_color = char_colors["body"]
    mane_color = char_colors["mane"]
    eye_color  = char_colors["eyes"]
    ear_color  = char_colors["ears"]

    bob_y = 0; lean_x = 0; arm_angle = 0

    if action == "idle":
        bob_y = int(math.sin(t*2.2)*6*s)
    elif action == "walk":
        bob_y  = int(math.sin(t*6)*11*s)
        lean_x = int(math.sin(t*3)*9*s)
    elif action == "jump":
        bob_y = -int(((math.sin(t*4)+1)/2)*85*s)
    elif action == "wave":
        bob_y     = int(math.sin(t*2)*5*s)
        arm_angle = 50+int(math.sin(t*5)*35)
    elif action == "dance":
        bob_y  = int(math.sin(t*6)*22*s)
        lean_x = int(math.sin(t*4)*22*s)
    elif action == "talk":
        bob_y = int(math.sin(t*2.2)*5*s)
    elif action == "celebrate":
        bob_y  = -int(abs(math.sin(t*5))*55*s)
        lean_x = int(math.sin(t*4)*18*s)
    elif action == "spin":
        lean_x = int(math.sin(t*8)*30*s)
        bob_y  = int(math.cos(t*8)*15*s)

    cx = x + lean_x
    cy = y + bob_y

    body_r = int(68*s)
    head_r = int(62*s)
    leg_sw = int(math.sin(t*6)*22*s) if action in ["walk","dance","spin"] else 0

    # Ground shadow
    sh_y = cy + body_r + int(25*s)
    for i in range(9):
        alpha = max(0, 50 - i*6)
        sw2   = max(0, int((body_r*2.3)*(1-i*0.09)))
        sh2   = max(0, int(22*(1-i*0.1)))
        if sw2 > 0 and sh2 > 0:
            draw.ellipse([cx-sw2//2, sh_y-sh2//2,
                           cx+sw2//2, sh_y+sh2//2],
                          fill=(alpha, alpha, alpha))

    # Legs
    for side, swing in [(-1,-leg_sw),(1,leg_sw)]:
        lx2   = cx + side*int(28*s) + swing
        ly_t  = cy + int(52*s)
        ly_b  = cy + int(108*s)
        draw_cylinder_3d(draw, lx2, ly_t, lx2+swing//2, ly_b, int(26*s), mane_color)
        draw_sphere_3d(draw, lx2+swing//2, ly_b, int(17*s), body_color)

    # Body
    draw_sphere_3d(draw, cx, cy, body_r, body_color)

    # Special body details
    if char_name == "robot":
        for gy2 in range(cy-body_r+12, cy+body_r-12, 20):
            draw.line([cx-body_r+14, gy2, cx+body_r-14, gy2],
                      fill="#7090A8", width=2)
        blink3 = int(abs(math.sin(t*2))*255)
        draw_sphere_3d(draw, cx, cy-8, int(11*s), rgb_to_hex(0, blink3, 0))
    elif char_name == "penguin":
        draw_sphere_3d(draw, cx, cy, int(body_r*0.68), "#FFFFFF")
    elif char_name == "unicorn":
        for i in range(7):
            sx4 = cx + random.Random(i+int(t)).randint(-55, 55)
            sy4 = cy + random.Random(i+int(t)+1).randint(-65, 65)
            draw_sphere_3d(draw, sx4, sy4, int(6*s), "#FFD700")

    # Dragon wings
    if char_name == "dragon":
        wf = int(math.sin(t*4)*28*s)
        for side in [-1,1]:
            draw.polygon([
                (cx+side*int(58*s), cy-int(18*s)),
                (cx+side*int(175*s), cy-int(105*s)-wf),
                (cx+side*int(115*s), cy+int(35*s))
            ], fill=mane_color)
            draw.line([cx+side*int(58*s), cy-int(18*s),
                       cx+side*int(175*s), cy-int(105*s)-wf],
                      fill=lighten_color(mane_color, 50), width=3)

    # Arms
    arm_sw = int(math.sin(t*6+math.pi)*16*s) if action in ["walk","dance"] else 0
    la_x2  = cx-int(78*s); la_y2 = cy-int(8*s)+arm_sw
    draw_cylinder_3d(draw, cx-int(52*s), cy-int(8*s), la_x2, la_y2, int(19*s), body_color)
    draw_sphere_3d(draw, la_x2, la_y2, int(13*s), body_color)

    if action == "wave":
        ra_rad2 = math.radians(-arm_angle)
        ra_x2   = cx+int(52*s)+int(math.cos(ra_rad2)*62*s)
        ra_y2   = cy-int(8*s)+int(math.sin(ra_rad2)*62*s)
    else:
        ra_x2 = cx+int(78*s); ra_y2 = cy-int(8*s)-arm_sw
    draw_cylinder_3d(draw, cx+int(52*s), cy-int(8*s), ra_x2, ra_y2, int(19*s), body_color)
    draw_sphere_3d(draw, ra_x2, ra_y2, int(13*s), body_color)

    # Head
    head_y2 = cy - body_r - head_r + int(12*s)

    # Lion mane (behind head)
    if char_name == "lion":
        for angle in range(0,360,22):
            rv = head_r+int(22*s)+int(math.sin(t*1.5+angle*0.05)*6*s)
            mx3 = cx+int(math.cos(math.radians(angle))*rv)
            my3 = head_y2+int(math.sin(math.radians(angle))*rv)
            draw_sphere_3d(draw, mx3, my3, int(15*s), mane_color)

    draw_sphere_3d(draw, cx, head_y2, head_r, body_color)

    # Ears & Special head features
    if char_name == "rabbit":
        for side in [-1,1]:
            ex5 = cx+side*int(33*s)
            draw_cylinder_3d(draw, ex5, head_y2-head_r+5,
                             ex5+side*int(6*s), head_y2-head_r-int(82*s),
                             int(17*s), ear_color)
            draw_cylinder_3d(draw, ex5+side*2, head_y2-head_r+8,
                             ex5+side*int(7*s), head_y2-head_r-int(72*s),
                             int(8*s), "#FFB6C1")
    elif char_name == "lion":
        for side in [-1,1]:
            draw_sphere_3d(draw, cx+side*(head_r+int(5*s)), head_y2-int(18*s),
                           int(19*s), ear_color)
    elif char_name == "fox":
        for side in [-1,1]:
            draw.polygon([(cx+side*int(28*s),head_y2-head_r+int(12*s)),
                           (cx+side*int(58*s),head_y2-head_r-int(58*s)),
                           (cx+side*int(12*s),head_y2-head_r-int(8*s))],
                          fill=ear_color)
            draw.polygon([(cx+side*int(28*s),head_y2-head_r+int(8*s)),
                           (cx+side*int(52*s),head_y2-head_r-int(48*s)),
                           (cx+side*int(18*s),head_y2-head_r)],
                          fill="#FFAAAA")
    elif char_name == "elephant":
        for side in [-1,1]:
            draw_sphere_3d(draw, cx+side*(head_r+int(12*s)), head_y2,
                           int(28*s), ear_color)
        ts = int(math.sin(t*2)*12*s)
        draw.arc([cx-int(18*s), head_y2+int(22*s),
                  cx+int(18*s)+ts, head_y2+int(82*s)],
                 0, 270, fill=body_color, width=int(17*s))
    elif char_name == "unicorn":
        draw.polygon([(cx,head_y2-head_r-int(68*s)),
                       (cx-int(10*s),head_y2-head_r),
                       (cx+int(10*s),head_y2-head_r)], fill="#FFD700")
        draw.line([cx-int(3*s),head_y2-head_r,
                   cx-int(6*s),head_y2-head_r-int(62*s)], fill="white", width=2)
        for i in range(5):
            ang2 = t*65+i*72
            draw_sphere_3d(draw,
                cx+int(math.cos(math.radians(ang2))*int(44*s)),
                head_y2-head_r-int(32*s)+int(math.sin(math.radians(ang2))*int(20*s)),
                int(5*s), "#FFD700")
    elif char_name == "robot":
        draw_cylinder_3d(draw, cx, head_y2-head_r,
                         cx, head_y2-head_r-int(42*s), int(7*s), "#4682B4")
        draw_sphere_3d(draw, cx, head_y2-head_r-int(42*s), int(10*s), "#FF8800")
        for side in [-1,1]:
            draw_rounded_rect_3d(draw,
                cx+side*int(60*s)-int(13*s), head_y2-int(16*s),
                cx+side*int(60*s)+int(13*s), head_y2+int(16*s),
                mane_color, radius=4)
    elif char_name == "dragon":
        for i, sx_off in enumerate([-42,-14,14,42]):
            draw.polygon([
                (cx+int(sx_off*s), head_y2-head_r+int(6*s)),
                (cx+int((sx_off-11)*s), head_y2-head_r-int((38+i*6)*s)),
                (cx+int((sx_off+11)*s), head_y2-head_r-int((38+i*6)*s))
            ], fill=lighten_color(mane_color, 30))
    elif char_name == "penguin":
        for side in [-1,1]:
            draw.polygon([(cx+side*int(24*s),cy-int(28*s)),
                           (cx,cy-int(14*s)),(cx+side*int(24*s),cy+int(2*s))],
                          fill="#FF4444")

    # Eyes (3D)
    eye_r2 = int(15*s)
    for side in [-1,1]:
        ex6 = cx+side*int(21*s)
        ey6 = head_y2-int(7*s)
        if expression in ["happy","walk","idle","celebrate"]:
            draw_sphere_3d(draw, ex6, ey6, eye_r2, "#FFFFFF")
            draw_sphere_3d(draw, ex6+int(3*s), ey6+int(3*s),
                           int(eye_r2*0.56), eye_color)
            draw_sphere_3d(draw, ex6-int(4*s), ey6-int(4*s),
                           int(4*s), "#FFFFFF")
        elif expression == "surprised":
            draw_sphere_3d(draw, ex6, ey6, int(eye_r2*1.35), "#FFFFFF")
            draw_sphere_3d(draw, ex6, ey6, int(eye_r2*0.62), eye_color)
        elif expression == "excited":
            for ang3 in range(0,360,72):
                sx5 = ex6+int(math.cos(math.radians(ang3))*eye_r2)
                sy5 = ey6+int(math.sin(math.radians(ang3))*eye_r2)
                draw.line([ex6,ey6,sx5,sy5], fill="#FFD700", width=int(3*s))
            draw_sphere_3d(draw, ex6, ey6, int(7*s), "#FFD700")
        elif expression == "thinking":
            draw.arc([ex6-eye_r2, ey6-int(eye_r2*0.4),
                      ex6+eye_r2, ey6+eye_r2],
                     0, 180, fill=eye_color, width=int(4*s))
        elif expression == "sad":
            draw.arc([ex6-eye_r2, ey6-eye_r2,
                      ex6+eye_r2, ey6+int(eye_r2*0.4)],
                     180, 360, fill=eye_color, width=int(4*s))
        elif expression == "talk":
            draw_sphere_3d(draw, ex6, ey6, eye_r2, "#FFFFFF")
            draw_sphere_3d(draw, ex6+int(3*s), ey6+int(2*s),
                           int(eye_r2*0.52), eye_color)

    # Mouth
    my2 = head_y2+int(23*s)
    if action == "talk":
        oa = int(abs(math.sin(t*8.5))*int(23*s))
        draw.arc([cx-int(20*s),my2,cx+int(20*s),my2+int(20*s)],
                 0, 180, fill="#CC0000", width=int(4*s))
        if oa > 5:
            draw.ellipse([cx-int(17*s),my2+int(4*s),
                          cx+int(17*s),my2+int(4*s)+oa], fill="#CC0000")
            draw.rectangle([cx-int(13*s),my2+int(4*s),
                             cx+int(13*s),my2+int(9*s)], fill="white")
    elif expression in ["happy","excited","celebrate"]:
        draw.arc([cx-int(22*s),my2,cx+int(22*s),my2+int(22*s)],
                 0, 180, fill="#CC0000", width=int(5*s))
        # Cheek blush
        for side in [-1,1]:
            draw_sphere_3d(draw, cx+side*int(35*s), my2-int(5*s),
                           int(10*s), "#FFB6C1")
    elif expression == "surprised":
        draw_sphere_3d(draw, cx, my2+int(10*s), int(12*s), "#CC0000")
    elif expression == "sad":
        draw.arc([cx-int(22*s),my2,cx+int(22*s),my2+int(22*s)],
                 180, 360, fill="#CC0000", width=int(5*s))

    # Nose
    if char_name == "robot":
        draw_rounded_rect_3d(draw, cx-int(7*s), head_y2+int(7*s),
                              cx+int(7*s), head_y2+int(16*s), "#4682B4", radius=3)
    else:
        draw_sphere_3d(draw, cx, head_y2+int(13*s), int(9*s), mane_color)

# ── Particles ─────────────────────────────────────────────────────────────────

def draw_particles(draw, t, effect="stars"):
    rng = random.Random(int(t*8))
    if effect == "stars":
        for i in range(18):
            px3 = rng.randint(50, W-50)
            py3 = rng.randint(50, int(H*0.55))
            sz2 = rng.randint(6, 22)
            alpha2 = abs(math.sin(t*2.5+i))
            draw_star_3d(draw, px3, py3, sz2, "#FFD700", alpha2)
    elif effect == "hearts":
        for i in range(10):
            px3 = int((i*W//8+t*32)%W)
            py3 = int(H*0.28+math.sin(t*2.2+i)*110)
            draw_heart_3d(draw, px3, py3, 22)
    elif effect == "sparkles":
        for i in range(22):
            px3 = rng.randint(80, W-80)
            py3 = rng.randint(80, int(H*0.78))
            if abs(math.sin(t*4.5+i)) > 0.65:
                draw_sparkle_3d(draw, px3, py3)
    elif effect == "bubbles":
        for i in range(12):
            bx3  = int((i*175+t*22)%W)
            by3  = int(H*0.88-(t*55+i*58)%H)
            sz3  = 12+i*5
            draw.ellipse([bx3-sz3,by3-sz3,bx3+sz3,by3+sz3],
                         outline="#87CEEB", width=3)
            draw.ellipse([bx3-sz3//3,by3-sz3//2,
                          bx3,by3-sz3//3], fill="#FFFFFF")
    elif effect == "confetti":
        cols = ["#FF6B6B","#FFD700","#4ECDC4","#FF69B4","#7B68EE","#FF4500"]
        for i in range(30):
            cx3   = int((i*73+t*88)%W)
            cy3   = int((t*68+i*47)%H)
            color = cols[i%len(cols)]
            angle = (t*90+i*15) % 360
            w3 = 10; h3 = 6
            draw.rectangle([cx3-w3//2, cy3-h3//2, cx3+w3//2, cy3+h3//2], fill=color)
    elif effect == "magic":
        for i in range(15):
            px3 = int((i*128+t*45)%W)
            py3 = int(H*0.4+math.sin(t*3+i*0.6)*180)
            draw_sparkle_3d(draw, px3, py3)
            if i%3 == 0:
                draw_sphere_3d(draw, px3, py3, 7,
                               ["#FFD700","#FF69B4","#00FFFF"][i%3])

def draw_star_3d(draw, cx, cy, size, color, alpha=1.0):
    rgb3 = hex_to_rgb(color)
    c3   = tuple(min(255, int(v*alpha)) for v in rgb3)
    for angle in range(0, 360, 72):
        x3 = cx+int(math.cos(math.radians(angle))*size)
        y3 = cy+int(math.sin(math.radians(angle))*size)
        x4 = cx+int(math.cos(math.radians(angle+36))*size//2)
        y4 = cy+int(math.sin(math.radians(angle+36))*size//2)
        draw.line([cx,cy,x3,y3], fill=c3, width=3)
        draw.line([cx,cy,x4,y4], fill=c3, width=2)

def draw_heart_3d(draw, cx, cy, size):
    draw_sphere_3d(draw, cx-size//2, cy-size//4, size//2, "#FF69B4")
    draw_sphere_3d(draw, cx+size//2, cy-size//4, size//2, "#FF69B4")
    draw.polygon([(cx-size,cy),(cx+size,cy),(cx,cy+size)], fill="#FF69B4")
    draw_sphere_3d(draw, cx-size//3, cy-size//5, size//5, "#FFB6C1")

def draw_sparkle_3d(draw, cx, cy):
    for angle in [0,45,90,135]:
        x5 = cx+int(math.cos(math.radians(angle))*18)
        y5 = cy+int(math.sin(math.radians(angle))*18)
        x6 = cx-int(math.cos(math.radians(angle))*18)
        y6 = cy-int(math.sin(math.radians(angle))*18)
        draw.line([x5,y5,x6,y6], fill="#FFD700", width=3)
    draw_sphere_3d(draw, cx, cy, 5, "#FFFFFF")

# ── Text ─────────────────────────────────────────────────────────────────────

def draw_text_simple(draw, text, x, y, size=60, color="#FFFFFF", shadow=True):
    font = None
    try:
        for fp in ["kids/assets/fonts/Fredoka_One/FredokaOne-Regular.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, size)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    if shadow:
        draw.text((x+3, y+3), text, font=font, fill="#00000099")
    draw.text((x, y), text, font=font, fill=color)

def draw_bouncing_text(draw, text, t, y_base=900, color="#FFD700"):
    words   = text.upper().split()
    total_w = len(text) * 42
    start_x = (W - total_w) // 2
    word_w  = total_w // max(len(words), 1)
    for i, word in enumerate(words):
        bounce = int(math.sin(t*4.5+i*0.9)*16)
        scale2 = 1.0 + abs(math.sin(t*3+i))*0.12
        wx2    = start_x + i*word_w
        draw_text_simple(draw, word, wx2, y_base+bounce,
                         size=int(78*scale2), color=color, shadow=True)

# ── Scene Action Maps ─────────────────────────────────────────────────────────

SCENE_ACTIONS = [
    ("idle","happy"),("wave","excited"),("talk","happy"),
    ("jump","excited"),("walk","happy"),("dance","excited"),
    ("talk","surprised"),("celebrate","excited"),("idle","thinking"),
    ("talk","happy"),("jump","surprised"),("wave","excited"),
    ("walk","happy"),("dance","excited"),("talk","surprised"),
    ("celebrate","excited"),("idle","happy"),("wave","excited"),
    ("talk","excited"),("jump","happy"),("dance","surprised"),
    ("wave","happy"),("celebrate","excited"),("talk","thinking"),
    ("walk","excited"),("idle","surprised"),("jump","excited"),
    ("dance","happy"),("wave","excited"),("celebrate","excited"),
]

SCENE_PARTICLES = [
    "stars","hearts","sparkles","confetti","bubbles","magic",
    "stars","sparkles","confetti","hearts","stars","bubbles",
    "sparkles","confetti","stars","hearts","magic","sparkles",
    "confetti","stars","hearts","bubbles","sparkles","magic",
    "confetti","stars","hearts","sparkles","confetti","stars",
]

# ── Master Frame Generator ────────────────────────────────────────────────────

def generate_frame(t, scene_number, topic, text_overlay="",
                   char_x=None, char_y=None):
    img  = Image.new("RGB", (W, H), "#000000")
    draw = ImageDraw.Draw(img)

    scene_name, palette    = pick_scene(scene_number, 30)
    char_name, char_colors = pick_character(topic)

    draw_background(draw, scene_name, palette, t)

    particle_effect = SCENE_PARTICLES[scene_number % len(SCENE_PARTICLES)]
    draw_particles(draw, t, particle_effect)

    action, expression = SCENE_ACTIONS[scene_number % len(SCENE_ACTIONS)]

    if char_x is None:
        char_x = int(W*0.1+(t*55)%(W*0.8)) if action=="walk" else W//2
    if char_y is None:
        char_y = int(H*0.61)

    draw_character(draw, char_name, char_colors, char_x, char_y,
                   t, action=action, expression=expression, scale=1.0)

    if text_overlay:
        color_opts = ["#FFD700","#FF6B35","#FF1493","#00CED1","#7B68EE","#FF4500"]
        draw_bouncing_text(draw, text_overlay, t,
                           y_base=int(H*0.87),
                           color=color_opts[scene_number % len(color_opts)])

    return np.array(img)
