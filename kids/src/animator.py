import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math
import random
import os

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1920, 1080
FPS  = 24

# ── Color Palettes ────────────────────────────────────────────────────────────
PALETTES = {
    "forest":    {"sky": "#87CEEB", "ground": "#5DBB63", "accent": "#FF6B35"},
    "night":     {"sky": "#1a1a4e", "ground": "#2d5a27", "accent": "#FFD700"},
    "beach":     {"sky": "#00BFFF", "ground": "#F4D03F", "accent": "#FF6B6B"},
    "classroom": {"sky": "#FFF9C4", "ground": "#A5D6A7", "accent": "#7C4DFF"},
    "space":     {"sky": "#0a0a2e", "ground": "#1a1a4e", "accent": "#00FFFF"},
    "village":   {"sky": "#FFB347", "ground": "#7CFC00", "accent": "#FF69B4"},
    "cave":      {"sky": "#4a4a4a", "ground": "#2c2c2c", "accent": "#FFD700"},
    "mountain":  {"sky": "#87CEEB", "ground": "#8B7355", "accent": "#FF4500"},
}

# ── Characters ────────────────────────────────────────────────────────────────
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
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["lion","brave","jungle","wild","king"]):
        return "lion", CHARACTERS["lion"]
    elif any(w in topic_lower for w in ["space","star","planet","rocket","galaxy"]):
        return "robot", CHARACTERS["robot"]
    elif any(w in topic_lower for w in ["magic","fairy","princess","unicorn","rainbow"]):
        return "unicorn", CHARACTERS["unicorn"]
    elif any(w in topic_lower for w in ["fox","clever","smart","trick","cunning"]):
        return "fox", CHARACTERS["fox"]
    elif any(w in topic_lower for w in ["dragon","fire","adventure","quest"]):
        return "dragon", CHARACTERS["dragon"]
    elif any(w in topic_lower for w in ["ocean","sea","fish","water","swim","beach"]):
        return "penguin", CHARACTERS["penguin"]
    elif any(w in topic_lower for w in ["elephant","big","strong","memory","jungle"]):
        return "elephant", CHARACTERS["elephant"]
    else:
        return "rabbit", CHARACTERS["rabbit"]

def pick_scene(scene_number, total_scenes):
    scene_names = list(PALETTES.keys())
    idx = scene_number % len(scene_names)
    return scene_names[idx], PALETTES[scene_names[idx]]

# ── Background Renderers ──────────────────────────────────────────────────────

def draw_background(draw, scene_name, palette, t, frame_w=W, frame_h=H):
    sky_color    = palette["sky"]
    ground_color = palette["ground"]
    sky_rgb = tuple(int(sky_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    for y in range(int(frame_h * 0.65)):
        factor = y / (frame_h * 0.65)
        r = int(sky_rgb[0] * (1 - factor * 0.3))
        g = int(sky_rgb[1] * (1 - factor * 0.1))
        b = int(sky_rgb[2])
        draw.line([(0, y), (frame_w, y)], fill=(r, g, b))
    ground_rgb = tuple(int(ground_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    draw.rectangle([0, int(frame_h*0.65), frame_w, frame_h], fill=ground_rgb)

    if scene_name == "forest":
        draw_forest(draw, t, frame_w, frame_h, palette)
    elif scene_name == "night":
        draw_night(draw, t, frame_w, frame_h, palette)
    elif scene_name == "beach":
        draw_beach(draw, t, frame_w, frame_h, palette)
    elif scene_name == "space":
        draw_space(draw, t, frame_w, frame_h, palette)
    elif scene_name == "classroom":
        draw_classroom(draw, t, frame_w, frame_h, palette)
    elif scene_name == "village":
        draw_village(draw, t, frame_w, frame_h, palette)
    elif scene_name == "mountain":
        draw_mountain(draw, t, frame_w, frame_h, palette)
    else:
        draw_cave(draw, t, frame_w, frame_h, palette)

def draw_forest(draw, t, W, H, palette):
    sun_x = int(W * 0.15)
    sun_y = int(H * 0.15) + int(math.sin(t * 0.5) * 10)
    draw.ellipse([sun_x-60, sun_y-60, sun_x+60, sun_y+60], fill="#FFD700")
    for i in range(8):
        angle = i * 45 + t * 30
        rx = sun_x + int(math.cos(math.radians(angle)) * 80)
        ry = sun_y + int(math.sin(math.radians(angle)) * 80)
        draw.line([sun_x, sun_y, rx, ry], fill="#FFE44D", width=4)
    for i in range(3):
        cx = int((W * 0.2 + i * W * 0.3 + t * 20) % W)
        cy = int(H * 0.1 + i * 40)
        draw_cloud(draw, cx, cy, 100 + i*20)
    tree_positions = [100, 250, W-250, W-100, W//2-200, W//2+200]
    for i, tx in enumerate(tree_positions):
        sway = math.sin(t * 1.5 + i * 0.7) * 8
        draw_tree(draw, tx, int(H * 0.65), sway, i)
    for i in range(12):
        fx = 150 + i * 140
        fy = int(H * 0.72) + int(math.sin(t + i) * 5)
        draw_flower(draw, fx, fy, ["#FF6B6B","#FFD700","#FF69B4","#FF4500"][i%4])

def draw_night(draw, t, W, H, palette):
    rng = random.Random(42)
    for i in range(80):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.6))
        brightness = int(150 + 105 * math.sin(t * 2 + i * 0.5))
        size = rng.randint(2, 6)
        draw.ellipse([sx-size, sy-size, sx+size, sy+size],
                     fill=(brightness, brightness, brightness))
    mx, my = int(W*0.8), int(H*0.15)
    draw.ellipse([mx-50, my-50, mx+50, my+50], fill="#FFFACD")
    draw.ellipse([mx+15, my-45, mx+65, my+35], fill="#1a1a4e")
    for i in range(6):
        gx = 100 + i*300
        gy = int(H*0.65)
        draw_tree(draw, gx, gy, 0, i, dark=True)

def draw_beach(draw, t, W, H, palette):
    for wave in range(5):
        wave_y = int(H * 0.5 + wave * 30 + math.sin(t * 2 + wave) * 15)
        draw.arc([0, wave_y-30, W, wave_y+30], 0, 180,
                 fill=(0, 119+wave*15, 190+wave*10), width=8)
    draw.ellipse([W-150, 50, W-50, 150], fill="#FFD700")
    draw_palm(draw, int(W*0.15), int(H*0.65), t)
    for i in range(4):
        wy = int(H * 0.68 + i * 20)
        draw.arc([50, wy, 400, wy+20], 0, 180, fill="#87CEEB", width=3)

def draw_space(draw, t, W, H, palette):
    rng = random.Random(99)
    for i in range(150):
        sx = rng.randint(0, W)
        sy = rng.randint(0, H)
        bright = int(100 + 155 * abs(math.sin(t + i * 0.3)))
        draw.ellipse([sx-2, sy-2, sx+2, sy+2], fill=(bright, bright, bright))
    planets = [(int(W*0.8), int(H*0.2), 60, "#FF6B35"),
               (int(W*0.15), int(H*0.3), 40, "#DDA0DD")]
    for px, py, pr, pc in planets:
        draw.ellipse([px-pr, py-pr, px+pr, py+pr], fill=pc)
    rx = int((t * 50) % W)
    ry = int(H * 0.15)
    draw_rocket(draw, rx, ry)
    for i in range(5):
        cx2 = rng.randint(100, W-100)
        draw.ellipse([cx2-30, int(H*0.67), cx2+30, int(H*0.72)],
                     fill=(60, 60, 80))

def draw_classroom(draw, t, W, H, palette):
    draw.rectangle([0, 0, W, int(H*0.65)], fill="#FFF9E6")
    draw.rectangle([int(W*0.2), int(H*0.05), int(W*0.8), int(H*0.45)],
                   fill="#2C5F2E")
    draw.rectangle([int(W*0.2)+5, int(H*0.05)+5,
                    int(W*0.8)-5, int(H*0.45)-5], fill="#2E7D32")
    chars = ["A","B","C","1","2","3","★","♥"]
    for i, ch in enumerate(chars):
        cx2 = int(W*0.25 + i * 80)
        cy2 = int(H * 0.2 + math.sin(t*2 + i) * 10)
        draw_text_simple(draw, ch, cx2, cy2, size=50, color="#FFFFFF")
    for wx in [int(W*0.05), int(W*0.85)]:
        draw.rectangle([wx, int(H*0.08), wx+120, int(H*0.35)], fill="#87CEEB")
        draw.line([wx+60, int(H*0.08), wx+60, int(H*0.35)], fill="white", width=4)
        draw.line([wx, int(H*0.215), wx+120, int(H*0.215)], fill="white", width=4)
    for i in range(4):
        dx = 150 + i * 420
        draw.rectangle([dx, int(H*0.72), dx+200, int(H*0.76)], fill="#8B4513")
        draw.rectangle([dx+30, int(H*0.76), dx+60, int(H*0.85)], fill="#6B3410")
        draw.rectangle([dx+140, int(H*0.76), dx+170, int(H*0.85)], fill="#6B3410")

def draw_village(draw, t, W, H, palette):
    for i in range(4):
        cx2 = int((100 + i*400 + t*15) % (W+200)) - 100
        draw_cloud(draw, cx2, 80+i*30, 120)
    houses = [(150, "#FF6B6B"), (450, "#4ECDC4"),
              (W-300, "#FFD93D"), (W-500, "#A8E6CF")]
    for hx, hcolor in houses:
        draw_house(draw, hx, int(H*0.65), hcolor)
    draw.polygon([(W//2-80, H), (W//2+80, H),
                  (W//2+200, int(H*0.65)), (W//2-200, int(H*0.65))],
                 fill="#D4A574")

def draw_mountain(draw, t, W, H, palette):
    mountain_data = [(W//4,"#7B8B6F"),(W//2,"#6B7B5F"),
                     (3*W//4,"#8B9B7F"),(W//8,"#9BAB8F"),(7*W//8,"#6B7B5F")]
    for mx2, mc in mountain_data:
        mh = random.Random(mx2).randint(200, 400)
        draw.polygon([(mx2-200, int(H*0.65)), (mx2, int(H*0.65)-mh),
                      (mx2+200, int(H*0.65))], fill=mc)
        draw.polygon([(mx2-40, int(H*0.65)-mh+40), (mx2, int(H*0.65)-mh),
                      (mx2+40, int(H*0.65)-mh+40)], fill="white")
    for i in range(5):
        bx = int((i*200 + t*40) % W)
        by2 = int(H*0.2 + i*20)
        draw_bird(draw, bx, by2, t+i)

def draw_cave(draw, t, W, H, palette):
    draw.ellipse([-200, -200, W+200, int(H*0.8)], fill="#3a3a3a")
    draw.ellipse([-150, -150, W+150, int(H*0.75)], fill="#1a1a4a")
    crystal_colors = ["#00FFFF","#FF00FF","#FFD700","#00FF00"]
    for i in range(8):
        cx2 = 100 + i * 220
        cy2 = int(H*0.6)
        glow = abs(math.sin(t*2 + i))
        draw_crystal(draw, cx2, cy2, crystal_colors[i%4], glow)
    for tx in [int(W*0.2), int(W*0.8)]:
        draw_torch(draw, tx, int(H*0.35), t)

# ── Scene Detail Helpers ──────────────────────────────────────────────────────

def draw_cloud(draw, cx, cy, size):
    draw.ellipse([cx-size, cy-size//2, cx+size, cy+size//2], fill="white")
    draw.ellipse([cx-size//2, cy-size, cx+size//2, cy], fill="white")
    draw.ellipse([cx, cy-size//2, cx+size*2, cy+size//2], fill="white")

def draw_tree(draw, tx, ty, sway, seed, dark=False):
    rng = random.Random(seed)
    trunk_color = "#5C3317" if not dark else "#2C1A0A"
    leaf_color  = "#228B22" if not dark else "#1A4A1A"
    height = rng.randint(120, 200)
    draw.rectangle([tx-15+int(sway), ty-height+80, tx+15+int(sway), ty],
                   fill=trunk_color)
    for i in range(3):
        lw = 80 - i*15
        ly = ty - height + i*40
        draw.polygon([(tx+int(sway), ly),
                      (tx-lw+int(sway*0.5), ly+60),
                      (tx+lw+int(sway*0.5), ly+60)], fill=leaf_color)

def draw_flower(draw, fx, fy, color):
    for angle in range(0, 360, 60):
        px = fx + int(math.cos(math.radians(angle)) * 15)
        py = fy + int(math.sin(math.radians(angle)) * 15)
        draw.ellipse([px-10, py-10, px+10, py+10], fill=color)
    draw.ellipse([fx-8, fy-8, fx+8, fy+8], fill="#FFD700")

def draw_house(draw, hx, hy, color):
    draw.rectangle([hx, hy-120, hx+180, hy], fill=color)
    draw.polygon([(hx-20, hy-120), (hx+90, hy-200),
                  (hx+200, hy-120)], fill="#CC4444")
    draw.rectangle([hx+65, hy-70, hx+115, hy], fill="#8B4513")
    draw.ellipse([hx+108, hy-40, hx+118, hy-30], fill="#FFD700")
    draw.rectangle([hx+20, hy-100, hx+60, hy-70], fill="#87CEEB")
    draw.rectangle([hx+120, hy-100, hx+160, hy-70], fill="#87CEEB")

def draw_rocket(draw, rx, ry):
    draw.polygon([(rx, ry-40), (rx-20, ry+30), (rx+20, ry+30)], fill="#C0C0C0")
    draw.polygon([(rx, ry-60), (rx-8, ry-40), (rx+8, ry-40)], fill="#FF4444")
    draw.ellipse([rx-25, ry+25, rx-5, ry+45], fill="#FF6600")
    draw.ellipse([rx+5,  ry+25, rx+25, ry+45], fill="#FF6600")

def draw_palm(draw, px, py, t):
    sway = int(math.sin(t*0.8) * 15)
    pts  = [(px, py), (px+sway//2, py-100),
            (px+sway, py-200), (px+sway*2, py-280)]
    for i in range(len(pts)-1):
        draw.line([pts[i], pts[i+1]], fill="#8B6914", width=18)
    lx, ly = px+sway*2, py-280
    for angle in range(0, 360, 60):
        ex2 = lx + int(math.cos(math.radians(angle+t*10)) * 80)
        ey2 = ly + int(math.sin(math.radians(angle+t*10)) * 40)
        draw.line([lx, ly, ex2, ey2], fill="#228B22", width=12)

def draw_crystal(draw, cx, cy, color, glow):
    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    alpha_color = tuple(int(c * (0.5 + glow*0.5)) for c in rgb)
    ch = int(60 + glow * 30)
    draw.polygon([(cx, cy-ch), (cx-20, cy), (cx, cy+20), (cx+20, cy)],
                 fill=alpha_color)

def draw_torch(draw, tx, ty, t):
    draw.rectangle([tx-5, ty, tx+5, ty+40], fill="#8B4513")
    flame_colors = ["#FF4500","#FF6600","#FFD700"]
    for i, fc in enumerate(flame_colors):
        flicker = int(math.sin(t*8+i) * 8)
        size    = 15 - i*3
        draw.ellipse([tx-size+flicker, ty-20-i*10,
                      tx+size+flicker, ty+i*5], fill=fc)

def draw_bird(draw, bx, by, t):
    wing = int(math.sin(t * 5) * 10)
    draw.arc([bx-20, by-wing, bx,    by+wing], 0, 180, fill="#333333", width=3)
    draw.arc([bx,    by-wing, bx+20, by+wing], 0, 180, fill="#333333", width=3)

# ── Character Drawing ─────────────────────────────────────────────────────────

def draw_character(draw, char_name, char_colors, x, y, t,
                   action="idle", expression="happy", scale=1.0):
    s           = scale
    body_color  = char_colors["body"]
    mane_color  = char_colors["mane"]
    eye_color   = char_colors["eyes"]
    ear_color   = char_colors["ears"]

    bob_y = 0; lean_x = 0; arm_angle = 0

    if action == "idle":
        bob_y = int(math.sin(t * 2) * 5 * s)
    elif action == "walk":
        bob_y  = int(math.sin(t * 6) * 10 * s)
        lean_x = int(math.sin(t * 3) * 8 * s)
    elif action == "jump":
        bob_y = -int(((math.sin(t * 4) + 1) / 2) * 80 * s)
    elif action == "wave":
        bob_y     = int(math.sin(t * 2) * 5 * s)
        arm_angle = 45 + int(math.sin(t * 5) * 30)
    elif action == "dance":
        bob_y  = int(math.sin(t * 6) * 20 * s)
        lean_x = int(math.sin(t * 4) * 20 * s)
    elif action == "talk":
        bob_y = int(math.sin(t * 2) * 4 * s)
    elif action == "celebrate":
        bob_y  = -int(abs(math.sin(t * 5)) * 50 * s)
        lean_x = int(math.sin(t * 4) * 15 * s)

    cx     = x + lean_x
    cy     = y + bob_y
    body_w = int(120 * s)
    body_h = int(130 * s)
    head_r = int(70  * s)

    # Body
    draw.ellipse([cx-body_w//2, cy-body_h//2,
                  cx+body_w//2, cy+body_h//2], fill=body_color)

    # Special body features
    if char_name == "robot":
        for gy in range(cy-body_h//2, cy+body_h//2, 20):
            draw.line([cx-body_w//2, gy, cx+body_w//2, gy], fill="#8090A0", width=2)
        blink = int(abs(math.sin(t * 2)) * 255)
        draw.ellipse([cx-15, cy-10, cx+15, cy+20], fill=(0, blink, 0))
    elif char_name == "penguin":
        draw.ellipse([cx-body_w//3, cy-body_h//3,
                      cx+body_w//3, cy+body_h//3], fill="white")
    elif char_name == "unicorn":
        for i in range(5):
            sx2 = cx + random.Random(i+int(t)).randint(-40, 40)
            sy2 = cy + random.Random(i+int(t)+1).randint(-50, 50)
            draw.ellipse([sx2-4, sy2-4, sx2+4, sy2+4], fill="#FFD700")

    # Legs
    leg_swing = int(math.sin(t*6)*20*s) if action in ["walk","dance"] else 0
    leg_color = mane_color
    draw.ellipse([cx-int(40*s)-leg_swing, cy+int(55*s),
                  cx-int(10*s)-leg_swing, cy+int(110*s)], fill=leg_color)
    draw.ellipse([cx+int(10*s)+leg_swing, cy+int(55*s),
                  cx+int(40*s)+leg_swing, cy+int(110*s)], fill=leg_color)
    draw.ellipse([cx-int(50*s)-leg_swing, cy+int(100*s),
                  cx-int(5*s)-leg_swing,  cy+int(120*s)], fill=body_color)
    draw.ellipse([cx+int(5*s)+leg_swing,  cy+int(100*s),
                  cx+int(50*s)+leg_swing, cy+int(120*s)], fill=body_color)

    # Arms
    arm_swing = int(math.sin(t*6+math.pi)*15*s) if action in ["walk","dance"] else 0
    la_end_x = cx - int(80*s)
    la_end_y = cy + int(arm_swing)
    draw.line([cx-int(55*s), cy-int(10*s), la_end_x, la_end_y],
              fill=body_color, width=int(20*s))
    draw.ellipse([la_end_x-int(15*s), la_end_y-int(15*s),
                  la_end_x+int(15*s), la_end_y+int(15*s)], fill=body_color)

    if action == "wave":
        ra_rad   = math.radians(-arm_angle)
        ra_end_x = cx+int(55*s)+int(math.cos(ra_rad)*60*s)
        ra_end_y = cy-int(10*s)+int(math.sin(ra_rad)*60*s)
    else:
        ra_end_x = cx + int(80*s)
        ra_end_y = cy - arm_swing
    draw.line([cx+int(55*s), cy-int(10*s), ra_end_x, ra_end_y],
              fill=body_color, width=int(20*s))
    draw.ellipse([ra_end_x-int(15*s), ra_end_y-int(15*s),
                  ra_end_x+int(15*s), ra_end_y+int(15*s)], fill=body_color)

    # Head
    head_y = cy - body_h//2 - head_r + int(10*s)
    draw.ellipse([cx-head_r, head_y-head_r, cx+head_r, head_y+head_r],
                 fill=body_color)

    # Ears / Special head features
    if char_name == "rabbit":
        for ex_off in [-30, 30]:
            ex_c = cx + int(ex_off*s)
            draw.ellipse([ex_c-int(15*s), head_y-head_r-int(80*s),
                           ex_c+int(15*s), head_y-head_r+int(10*s)], fill=ear_color)
            draw.ellipse([ex_c-int(8*s),  head_y-head_r-int(70*s),
                           ex_c+int(8*s),  head_y-head_r+int(5*s)],  fill="#FFB6C1")
    elif char_name == "lion":
        for angle in range(0, 360, 30):
            mx2 = cx + int(math.cos(math.radians(angle))*(head_r+15)*s)
            my2 = head_y + int(math.sin(math.radians(angle))*(head_r+15)*s)
            draw.ellipse([mx2-int(18*s), my2-int(18*s),
                           mx2+int(18*s), my2+int(18*s)], fill=mane_color)
        draw.ellipse([cx-head_r-int(5*s),  head_y-head_r-int(5*s),
                       cx-head_r+int(25*s), head_y-head_r+int(25*s)], fill=ear_color)
        draw.ellipse([cx+head_r-int(25*s), head_y-head_r-int(5*s),
                       cx+head_r+int(5*s),  head_y-head_r+int(25*s)], fill=ear_color)
    elif char_name == "fox":
        for ex_s in [-1, 1]:
            draw.polygon([(cx+ex_s*int(30*s), head_y-head_r+int(10*s)),
                           (cx+ex_s*int(50*s), head_y-head_r-int(50*s)),
                           (cx+ex_s*int(10*s), head_y-head_r-int(10*s))],
                          fill=ear_color)
    elif char_name == "elephant":
        for ex_s in [-1, 1]:
            draw.ellipse([cx+ex_s*int(50*s)-int(35*s), head_y-int(40*s),
                           cx+ex_s*int(50*s)+int(35*s), head_y+int(40*s)],
                          fill=ear_color)
        trunk_sway = int(math.sin(t*2)*10*s)
        draw.arc([cx-int(20*s), head_y+int(20*s),
                  cx+int(20*s)+trunk_sway, head_y+int(80*s)],
                 0, 270, fill=body_color, width=int(18*s))
    elif char_name == "unicorn":
        draw.polygon([(cx, head_y-head_r-int(60*s)),
                       (cx-int(10*s), head_y-head_r),
                       (cx+int(10*s), head_y-head_r)], fill="#FFD700")
        for i in range(4):
            angle = t*60 + i*90
            sx2 = cx + int(math.cos(math.radians(angle))*int(40*s))
            sy2 = head_y-head_r-int(30*s)+int(math.sin(math.radians(angle))*int(20*s))
            draw.ellipse([sx2-4, sy2-4, sx2+4, sy2+4], fill="#FFD700")
    elif char_name == "robot":
        draw.line([cx, head_y-head_r, cx, head_y-head_r-int(40*s)],
                  fill="#4682B4", width=int(6*s))
        blink2 = int(abs(math.sin(t*3))*255)
        draw.ellipse([cx-int(8*s), head_y-head_r-int(48*s),
                       cx+int(8*s), head_y-head_r-int(32*s)], fill=(255, blink2, 0))
        for ex_s in [-1, 1]:
            draw.rectangle([cx+ex_s*int(70*s)-int(12*s), head_y-int(15*s),
                             cx+ex_s*int(70*s)+int(12*s), head_y+int(15*s)],
                            fill=mane_color)
    elif char_name == "dragon":
        for i, sx_off in enumerate([-40,-15,15,40]):
            draw.polygon([(cx+int(sx_off*s),    head_y-head_r+int(5*s)),
                           (cx+int((sx_off-10)*s), head_y-head_r-int((35+i*5)*s)),
                           (cx+int((sx_off+10)*s), head_y-head_r-int((35+i*5)*s))],
                          fill="#1E8449")
        wing_flap = int(math.sin(t*4)*20*s)
        draw.polygon([(cx-int(60*s),  cy),
                       (cx-int(160*s), cy-int(80*s)-wing_flap),
                       (cx-int(100*s), cy+int(40*s))], fill=mane_color)
        draw.polygon([(cx+int(60*s),  cy),
                       (cx+int(160*s), cy-int(80*s)-wing_flap),
                       (cx+int(100*s), cy+int(40*s))], fill=mane_color)
    elif char_name == "penguin":
        draw.polygon([(cx-int(25*s), cy-int(30*s)),
                       (cx, cy-int(15*s)), (cx-int(25*s), cy)], fill="#FF4444")
        draw.polygon([(cx+int(25*s), cy-int(30*s)),
                       (cx, cy-int(15*s)), (cx+int(25*s), cy)], fill="#FF4444")

    # Eyes
    eye_size = int(18*s)
    for ex2, ey2 in [(cx-int(25*s), head_y-int(10*s)),
                     (cx+int(25*s), head_y-int(10*s))]:
        if expression == "happy":
            draw.ellipse([ex2-eye_size, ey2-eye_size,
                          ex2+eye_size, ey2+eye_size], fill="white")
            draw.ellipse([ex2-int(8*s), ey2-int(8*s),
                          ex2+int(8*s), ey2+int(8*s)], fill=eye_color)
            draw.ellipse([ex2-int(3*s), ey2-int(12*s),
                          ex2+int(3*s), ey2-int(6*s)],  fill="white")
        elif expression == "surprised":
            draw.ellipse([ex2-int(eye_size*1.3), ey2-int(eye_size*1.3),
                          ex2+int(eye_size*1.3), ey2+int(eye_size*1.3)], fill="white")
            draw.ellipse([ex2-int(10*s), ey2-int(10*s),
                          ex2+int(10*s), ey2+int(10*s)], fill=eye_color)
        elif expression == "thinking":
            draw.arc([ex2-eye_size, ey2-int(eye_size*0.5),
                      ex2+eye_size, ey2+eye_size],
                     0, 180, fill=eye_color, width=int(5*s))
        elif expression == "excited":
            for angle in range(0, 360, 72):
                px2 = ex2 + int(math.cos(math.radians(angle)) * eye_size)
                py2 = ey2 + int(math.sin(math.radians(angle)) * eye_size)
                draw.line([ex2, ey2, px2, py2], fill="#FFD700", width=int(4*s))
            draw.ellipse([ex2-int(6*s), ey2-int(6*s),
                          ex2+int(6*s), ey2+int(6*s)], fill="#FFD700")
        elif expression == "sad":
            draw.arc([ex2-eye_size, ey2-eye_size,
                      ex2+eye_size, ey2+int(eye_size*0.5)],
                     180, 360, fill=eye_color, width=int(5*s))

    # Mouth
    mouth_y = head_y + int(25*s)
    if action == "talk":
        open_amount = abs(math.sin(t * 8)) * int(20*s)
        draw.arc([cx-int(25*s), mouth_y, cx+int(25*s), mouth_y+int(25*s)],
                 0, 180, fill="#CC0000", width=int(4*s))
        if open_amount > 5:
            draw.ellipse([cx-int(20*s), mouth_y+int(5*s),
                          cx+int(20*s), mouth_y+int(5*s)+int(open_amount)],
                         fill="#CC0000")
            draw.rectangle([cx-int(15*s), mouth_y+int(5*s),
                             cx+int(15*s), mouth_y+int(10*s)], fill="white")
    elif expression == "happy":
        draw.arc([cx-int(25*s), mouth_y, cx+int(25*s), mouth_y+int(25*s)],
                 0, 180, fill="#CC0000", width=int(5*s))
    elif expression == "surprised":
        draw.ellipse([cx-int(15*s), mouth_y,
                      cx+int(15*s), mouth_y+int(20*s)], fill="#CC0000")
    elif expression == "sad":
        draw.arc([cx-int(25*s), mouth_y, cx+int(25*s), mouth_y+int(25*s)],
                 180, 360, fill="#CC0000", width=int(5*s))

    # Nose
    if char_name == "robot":
        draw.rectangle([cx-int(8*s), head_y+int(5*s),
                        cx+int(8*s), head_y+int(15*s)], fill="#4682B4")
    else:
        draw.ellipse([cx-int(12*s), head_y+int(5*s),
                      cx+int(12*s), head_y+int(20*s)], fill=mane_color)

# ── Particles ─────────────────────────────────────────────────────────────────

def draw_particles(draw, t, effect="stars"):
    rng = random.Random(int(t*10))
    if effect == "stars":
        for i in range(15):
            px2 = rng.randint(0, W)
            py2 = rng.randint(0, int(H*0.6))
            size = rng.randint(5, 20)
            alpha = abs(math.sin(t*3 + i))
            draw_star(draw, px2, py2, size, "#FFD700", alpha)
    elif effect == "hearts":
        for i in range(8):
            px2 = int((i * W//7 + t*30) % W)
            py2 = int(H*0.3 + math.sin(t*2+i)*100)
            draw_heart(draw, px2, py2, 20)
    elif effect == "sparkles":
        for i in range(20):
            px2 = rng.randint(100, W-100)
            py2 = rng.randint(100, int(H*0.8))
            if abs(math.sin(t*4+i)) > 0.7:
                draw_sparkle(draw, px2, py2)
    elif effect == "bubbles":
        for i in range(10):
            bx2  = int((i*200 + t*20) % W)
            by2  = int(H*0.9 - (t*50 + i*60) % H)
            size = 10 + i*5
            draw.ellipse([bx2-size, by2-size, bx2+size, by2+size],
                         outline="#87CEEB", width=3)
    elif effect == "confetti":
        colors = ["#FF6B6B","#FFD700","#4ECDC4","#FF69B4","#7B68EE"]
        for i in range(25):
            cx2   = int((i*77 + t*80) % W)
            cy2   = int((t*60 + i*43) % H)
            color = colors[i % len(colors)]
            draw.rectangle([cx2-6, cy2-6, cx2+6, cy2+6], fill=color)

def draw_star(draw, cx, cy, size, color, alpha=1.0):
    rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    c   = tuple(min(255, int(v*alpha)) for v in rgb)
    for angle in range(0, 360, 72):
        x1 = cx + int(math.cos(math.radians(angle))    * size)
        y1 = cy + int(math.sin(math.radians(angle))    * size)
        x2 = cx + int(math.cos(math.radians(angle+36)) * size//2)
        y2 = cy + int(math.sin(math.radians(angle+36)) * size//2)
        draw.line([cx, cy, x1, y1], fill=c, width=3)
        draw.line([cx, cy, x2, y2], fill=c, width=2)

def draw_heart(draw, cx, cy, size):
    draw.ellipse([cx-size, cy-size//2, cx,      cy+size//2], fill="#FF69B4")
    draw.ellipse([cx,      cy-size//2, cx+size, cy+size//2], fill="#FF69B4")
    draw.polygon([(cx-size, cy), (cx+size, cy), (cx, cy+size)], fill="#FF69B4")

def draw_sparkle(draw, cx, cy):
    for angle in [0, 45, 90, 135]:
        x1 = cx + int(math.cos(math.radians(angle)) * 15)
        y1 = cy + int(math.sin(math.radians(angle)) * 15)
        x2 = cx - int(math.cos(math.radians(angle)) * 15)
        y2 = cy - int(math.sin(math.radians(angle)) * 15)
        draw.line([x1, y1, x2, y2], fill="#FFD700", width=3)
    draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill="white")

# ── Text Overlay ──────────────────────────────────────────────────────────────

def draw_text_simple(draw, text, x, y, size=60, color="#FFFFFF", shadow=True):
    try:
        font = None
        for fp in ["kids/assets/fonts/Fredoka_One/FredokaOne-Regular.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, size)
                break
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    if shadow:
        draw.text((x+3, y+3), text, font=font, fill="#00000088")
    draw.text((x, y), text, font=font, fill=color)

def draw_bouncing_text(draw, text, t, y_base=900, color="#FFD700"):
    words     = text.upper().split()
    total_w   = len(text) * 45
    start_x   = (W - total_w) // 2
    word_w    = total_w // max(len(words), 1)
    for i, word in enumerate(words):
        bounce = int(math.sin(t * 4 + i * 0.8) * 15)
        wx     = start_x + i * word_w
        draw_text_simple(draw, word, wx, y_base + bounce,
                         size=80, color=color, shadow=True)

# ── Scene Action / Particle Maps ──────────────────────────────────────────────

SCENE_ACTIONS = [
    ("idle","happy"),("wave","excited"),("talk","happy"),
    ("jump","excited"),("walk","happy"),("dance","excited"),
    ("talk","surprised"),("celebrate","excited"),("idle","thinking"),
    ("talk","happy"),("jump","surprised"),("wave","excited"),
    ("walk","happy"),("dance","excited"),("talk","surprised"),
    ("celebrate","excited"),("idle","happy"),("wave","excited"),
]

SCENE_PARTICLES = [
    "stars","hearts","sparkles","confetti","bubbles",
    "stars","sparkles","confetti","hearts","stars",
    "bubbles","sparkles","confetti","stars","hearts",
    "sparkles","confetti","stars",
]

# ── Master Frame Generator ────────────────────────────────────────────────────

def generate_frame(t, scene_number, topic, text_overlay="",
                   char_x=None, char_y=None):
    img  = Image.new("RGB", (W, H), "#000000")
    draw = ImageDraw.Draw(img)

    scene_name, palette   = pick_scene(scene_number, 18)
    char_name, char_colors = pick_character(topic)

    draw_background(draw, scene_name, palette, t)

    particle_effect = SCENE_PARTICLES[scene_number % len(SCENE_PARTICLES)]
    draw_particles(draw, t, particle_effect)

    action, expression = SCENE_ACTIONS[scene_number % len(SCENE_ACTIONS)]

    if char_x is None:
        char_x = int(W * 0.1 + (t * 60) % (W * 0.8)) if action == "walk" else W // 2
    if char_y is None:
        char_y = int(H * 0.62)

    draw_character(draw, char_name, char_colors, char_x, char_y,
                   t, action=action, expression=expression, scale=1.0)

    if text_overlay:
        color = ["#FFD700","#FF6B35","#FF1493","#00CED1","#7B68EE"][scene_number%5]
        draw_bouncing_text(draw, text_overlay, t,
                           y_base=int(H*0.88), color=color)

    return np.array(img)
