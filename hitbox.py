import pymem
import pymem.process
import pygame
import win32api
import win32con
import win32gui
import ctypes
import time
import os
import sys

# ==============================================================================
# CONFIGS
# ==============================================================================
PROCESS_NAME = "KingOfFighters2002UM_x64.exe"
WINDOW_TITLE = "King of Fighters 2002 Unlimited Match"

# --- ENDEREÇOS ---
ADDR_BASE_POINTERS = {
    'CAMERA_X': 0x1440C259E,
    'P1_BASE':  0x1440BA21C,
    'P2_BASE':  0x1440BA43C,
    'PROJ_BASE': 0x1440ABC9C,
    'PAUSE_FLAG': 0x1440C38EA
}

# --- PROXIMITY KEYS ---
ADDR_PROXIMITY = {
    'P1_A': 0x1440AB018, 'P1_B': 0x1440AB019, 'P1_C': 0x1440AB01A, 'P1_D': 0x1440AB01B,
    'P2_A': 0x1440AB330, 'P2_B': 0x1440AB331, 'P2_C': 0x1440AB332, 'P2_D': 0x1440AB333
}

# --- OFFSETS ---
OFF = {
    'STATUS': 0x00,
    'ACTION_ID': 0x01,
    'POS_X': 0x1A,
    'POS_Y': 0x22,
    'FACING': 0x38,
    'ANIM_ID': 0x00,
    'BOX_MASK': 0x7C, 
    'BOX_DATA': 0x90,
    'THROW_STATUS': 0x7E, 
    'CMD_THROW_BOX': 0x188,
    'THROWABLE_BOX': 0x18D,
    'NARNIA': 0x1F  # 0=Narnia, 2=Normal
}

VAL_PAUSE_ON    = 153
VAL_PAUSE_OFF   = 27
PROJ_SLOT_SIZE  = 0x220
MAX_PROJECTILES = 42
NEUTRAL_ANIM_IDS = [0, 22, 91, 96, 102, 110, 122]
GHOST_STATUS_LIST = [4, 87, 197, 38, 104]

PROJ_ADDR_LIST = [ADDR_BASE_POINTERS['PROJ_BASE'] + (i * PROJ_SLOT_SIZE) for i in range(MAX_PROJECTILES)]

VISUAL = {
    'LINE_THICKNESS': 2,
    'BOX_SCALE': 2.0,
    'FIX_X': 0.0,
    'FIX_Y': 200.0,
    'ALPHA': 60,
    'WIDTH': 320.0,
    'HEIGHT': 224.0
}

METER_CONFIG = {
    'PIXEL_SIZE': 6,
    'HEIGHT': 20,
    'BAR_LENGTH': 60,
    'SPACING': 1
}

COLORS = {
    'BG_BAR': (10, 10, 10),
    'EMPTY_LED': (60, 60, 60),
    'STARTUP': (0, 255, 255),    # Cian
    'ACTIVE': (255, 50, 50),     # Red
    'RECOVERY': (0, 100, 255),   # Blue
    'HITSTUN': (255, 215, 0),    # Gold
    'NEUTRAL': (128, 128, 128),  # Gray
    'INVISIBLE': None,           
    'TEXT_SHADOW': (0, 0, 0),
    'TEXT_MAIN': (255, 255, 255),
    'ADV_PLUS': (100, 255, 100),
    'ADV_MINUS': (255, 100, 100),
}

TYPE_COLORS = {
    'v': (0, 0, 255),       # Blue
    'c': (173, 169, 252),   # Light Violet
    'a': (255, 0, 0),       # Red
    'g': (128, 128, 128),   # Gray
    'p': (0, 255, 255),     # Magenta
    'push': (0, 255, 0),    # Green
    'Throwable': (255, 255, 255),  # White
    'cmd_idle': (255, 255, 0),      # Yellow
    'cmd_connect': (255, 0, 0)      # Red
}

DRAW_PRIORITY = {
    'push': 0,
    'v': 1,
    'c': 2,
    'a': 3,
    'g': 4,
    'p': 5,
    'throw': 6,
    'cmd': 7
}

BOX_TYPE_MAP = {}
TYPE_SEQUENCE = [
    'v','v','v','c', 'c','v','v','v',
    'v','g','g','a', 'a','a','a','a',
    'a','a','a','a', 'a','a','v','a',
    'a','a','a','a', 'a','a','a','a',
    'a','a','a','a', 'a','a','a','a',
    'a','a','a','a', 'a','a','a','a',
    'a','a','a','a', 'a','a','a','g',
    'g','p','p','p', 'p','p','p'
]
for i, t in enumerate(TYPE_SEQUENCE): BOX_TYPE_MAP[i + 1] = t

STATE = {
    'P1_CYCLE': 0, 'P2_CYCLE': 0,
    'P1_CMD': False, 'P2_CMD': False,
    'P1_COMMON': True, 'P2_COMMON': True,
    'SHOW_METER': False,
    'SHOW_HITBOXES': True,
    'PAUSED': False,
    'FRAME_COUNT': 0,
    'NARNIA_P1': False,
    'NARNIA_P2': False 
}

PROX_MODES_P1 = [
    {'name': 'OFF', 'addr': None, 'color': None},
    {'name': 'A', 'addr': ADDR_PROXIMITY['P1_A'], 'color': (0, 255, 255)},
    {'name': 'B', 'addr': ADDR_PROXIMITY['P1_B'], 'color': (120, 40, 140)},
    {'name': 'C', 'addr': ADDR_PROXIMITY['P1_C'], 'color': (50, 255, 50)},
    {'name': 'D', 'addr': ADDR_PROXIMITY['P1_D'], 'color': (255, 255, 0)}
]

PROX_MODES_P2 = [
    {'name': 'OFF', 'addr': None, 'color': None},
    {'name': 'A', 'addr': ADDR_PROXIMITY['P2_A'], 'color': (0, 255, 255)},
    {'name': 'B', 'addr': ADDR_PROXIMITY['P2_B'], 'color': (120, 40, 140)},
    {'name': 'C', 'addr': ADDR_PROXIMITY['P2_C'], 'color': (50, 255, 50)},
    {'name': 'D', 'addr': ADDR_PROXIMITY['P2_D'], 'color': (255, 255, 0)}
]

# Cache de Fontes
FONTS = {}
def init_fonts():
    if not pygame.font.get_init(): pygame.font.init()
    FONTS['small'] = pygame.font.SysFont('Arial', 9, bold=True)
    FONTS['meter'] = pygame.font.SysFont('Consolas', 14, bold=True)
    FONTS['debug'] = pygame.font.SysFont('Consolas', 20, bold=True)
    FONTS['ui'] = pygame.font.SysFont('Arial', 12, bold=True)
    FONTS['wait'] = pygame.font.SysFont('Arial', 16, bold=True)

# ==============================================================================
# FRAME TRACKER
# ==============================================================================
class FrameDataTracker:
    def __init__(self, name="P1"):
        self.name = name
        self.frames = [] 
        self.reset_stats()

    def reset_stats(self):
        self.cnt_s, self.cnt_a, self.cnt_r = 0, 0, 0
        self.live_s, self.live_a, self.live_r = 0, 0, 0
        self.has_attacked = False
        self.was_hit = False

    def get_total(self):
        return len(self.frames)

    def get_last_active_frame(self):
        for i in range(len(self.frames) - 1, -1, -1):
            if self.frames[i] != COLORS['INVISIBLE']:
                return i + 1
        return 0

    def reset(self):
        self.frames = []
        self.reset_stats()

    def add_frame(self, base_color, is_attacking_frame, is_hit_frame):
        final_color = base_color
        
        # 1. HITSTUN (Dourado)
        if is_hit_frame:
            self.was_hit = True
            final_color = COLORS['HITSTUN']
        
        # 2. ATAQUE JÁ INICIADO (Active ou Recovery)
        elif self.has_attacked and not self.was_hit:
            if is_attacking_frame:
                final_color = COLORS['ACTIVE']
                self.live_a += 1
            else:
                final_color = COLORS['RECOVERY']
                self.live_r += 1
        
        # 3. STARTUP (Antes do primeiro ataque)
        elif is_attacking_frame: 
            self.has_attacked = True
            final_color = COLORS['ACTIVE']
            self.live_a += 1
        elif base_color == COLORS['STARTUP']:
            self.live_s += 1
            final_color = COLORS['STARTUP']
        
        # 4. INVISÍVEL
        elif base_color == COLORS['INVISIBLE']:
            final_color = COLORS['INVISIBLE']

        self.frames.append(final_color)

        if self.was_hit:
            for i in range(len(self.frames)):
                if self.frames[i] != COLORS['INVISIBLE']:
                    self.frames[i] = COLORS['HITSTUN']
            self.live_s, self.live_a, self.live_r = 0, 0, 0

    def finalize_stats(self):
        self.cnt_s, self.cnt_a, self.cnt_r = self.live_s, self.live_a, self.live_r

    def draw_segment_number(self, surface, number, block_index, base_x, base_y):
        if number < 1: return
        txt = str(number)
        ts = FONTS['small'].render(txt, True, COLORS['TEXT_SHADOW'])
        tf = FONTS['small'].render(txt, True, COLORS['TEXT_MAIN'])
        step = METER_CONFIG['PIXEL_SIZE'] + METER_CONFIG['SPACING']
        bx = int(base_x + (block_index * step))
        cx = bx + (METER_CONFIG['PIXEL_SIZE'] // 2)
        cy = base_y + (METER_CONFIG['HEIGHT'] // 2)
        tx = cx - (tf.get_width() // 2)
        ty = cy - (tf.get_height() // 2)
        surface.blit(ts, (tx + 1, ty + 1))
        surface.blit(tf, (tx, ty))

    def draw(self, surface, x, y, is_recording, advantage_val=None):
        try:
            s = self.live_s if is_recording else self.cnt_s
            tot = self.get_total() 
            adv_str = "--"
            adv_col = COLORS['TEXT_MAIN']
            if tot > 0 and advantage_val is not None and not is_recording:
                if advantage_val > 0:
                    adv_str = f"+{advantage_val}F"
                    adv_col = COLORS['ADV_PLUS']
                elif advantage_val < 0:
                    adv_str = f"{advantage_val}F"
                    adv_col = COLORS['ADV_MINUS']
                else:
                    adv_str = "0F"
            
            info_txt = f"Startup {s:02d}F / Total {tot:02d}F / Advantage "
            t1 = FONTS['meter'].render(info_txt, True, COLORS['TEXT_MAIN'])
            t1_s = FONTS['meter'].render(info_txt, True, COLORS['TEXT_SHADOW'])
            t2 = FONTS['meter'].render(adv_str, True, adv_col)
            t2_s = FONTS['meter'].render(adv_str, True, COLORS['TEXT_SHADOW'])
            
            surface.blit(t1_s, (int(x+1), int(y-20)))
            surface.blit(t1, (int(x), int(y-21)))
            surface.blit(t2_s, (int(x + t1.get_width() + 1), int(y-20)))
            surface.blit(t2, (int(x + t1.get_width()), int(y-21)))

            bar_w = (METER_CONFIG['PIXEL_SIZE'] + METER_CONFIG['SPACING']) * METER_CONFIG['BAR_LENGTH']
            pygame.draw.rect(surface, COLORS['BG_BAR'], (x, y, bar_w + 4, METER_CONFIG['HEIGHT'] + 4))

            step = METER_CONFIG['PIXEL_SIZE'] + METER_CONFIG['SPACING']
            for i in range(METER_CONFIG['BAR_LENGTH']):
                bx = x + 2 + (i * step)
                pygame.draw.rect(surface, COLORS['EMPTY_LED'], (bx, y + 2, METER_CONFIG['PIXEL_SIZE'], METER_CONFIG['HEIGHT']))

            if not self.frames: return

            current_color = None
            segment_len = 0

            for i, col in enumerate(self.frames):
                if i >= METER_CONFIG['BAR_LENGTH']: break
                if col == COLORS['INVISIBLE']:
                    if current_color is not None:
                        self.draw_segment_number(surface, segment_len, i - 1, x + 2, y + 2)
                        current_color = None
                        segment_len = 0
                    continue
                bx = x + 2 + (i * step)
                draw_col = col if col != COLORS['INVISIBLE'] else COLORS['EMPTY_LED']
                pygame.draw.rect(surface, draw_col, (bx, y + 2, METER_CONFIG['PIXEL_SIZE'], METER_CONFIG['HEIGHT']))
                
                if col == current_color:
                    segment_len += 1
                else:
                    if current_color is not None:
                        self.draw_segment_number(surface, segment_len, i - 1, x + 2, y + 2)
                    current_color = col
                    segment_len = 1
            if current_color is not None:
                final_idx = min(len(self.frames), METER_CONFIG['BAR_LENGTH']) - 1
                self.draw_segment_number(surface, segment_len, final_idx, x + 2, y + 2)
        except: pass

p1_tracker = FrameDataTracker("P1")
p2_tracker = FrameDataTracker("P2")

# ==============================================================================
# SISTEMA
# ==============================================================================
def set_dwm_transparency(hwnd):
    class MARGINS(ctypes.Structure):
        _fields_ = [("cxLeftWidth", ctypes.c_int), ("cxRightWidth", ctypes.c_int), 
                    ("cyTopHeight", ctypes.c_int), ("cyBottomHeight", ctypes.c_int)]
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    margins = MARGINS(-1, -1, -1, -1)
    ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

def get_game_window_info():
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if not hwnd: return None
    try:
        rect = win32gui.GetClientRect(hwnd)
        point = win32gui.ClientToScreen(hwnd, (0,0))
        if rect[2] <= 0 or rect[3] <= 0: return None

        win_w, win_h = rect[2], rect[3]
        native_w, native_h = VISUAL['WIDTH'], VISUAL['HEIGHT']

        scale = win_h / native_h
        actual_game_width = native_w * scale
        offset_x = (win_w - actual_game_width) /2

        return {
            "hwnd": hwnd, "x": point[0], "y": point[1], 
            "w": rect[2], "h": rect[3], 
            "scale": scale, "off_x": offset_x
        }
    except: return None

class GameMemory:
    def __init__(self): self.pm = None; self.attached = False
    def attach(self):
        try: self.pm = pymem.Pymem(PROCESS_NAME); self.attached = True
        except: self.attached = False
    def read_short(self, addr): 
        try: return self.pm.read_short(addr) if self.attached else 0
        except: return 0
    def read_ubyte(self, addr): 
        try: return self.pm.read_uchar(addr) if self.attached else 0
        except: return 0
    def read_int(self, addr): 
        try: return self.pm.read_int(addr) if self.attached else 0
        except: return 0
    def read_bytes(self, addr, size):
        try: return self.pm.read_bytes(addr, size) if self.attached else None
        except: return None
    def write_ubyte(self, addr, val):
        if self.attached:
            try: self.pm.write_uchar(addr, val)
            except: pass
    def write_int(self, addr, val): 
        if self.attached:
            try: self.pm.write_int(addr, val)
            except: pass

# ==============================================================================
# LÓGICA AUXILIAR
# ==============================================================================
def toggle_pause(mem):
    STATE['PAUSED'] = not STATE['PAUSED']
    if not STATE['PAUSED']: STATE['FRAME_COUNT'] = 0
    val = VAL_PAUSE_ON if STATE['PAUSED'] else VAL_PAUSE_OFF
    mem.write_ubyte(ADDR_BASE_POINTERS['PAUSE_FLAG'], val)

def advance_frame(mem):
    if not STATE['PAUSED']: return False
    try:
        mem.write_ubyte(ADDR_BASE_POINTERS['PAUSE_FLAG'], VAL_PAUSE_OFF)
        time.sleep(0.017) 
        mem.write_ubyte(ADDR_BASE_POINTERS['PAUSE_FLAG'], VAL_PAUSE_ON)
        STATE['FRAME_COUNT'] += 1
        return True
    except: return False

def toggle_narnia(mem, player):
    if player == 1:
        STATE['NARNIA_P1'] = not STATE['NARNIA_P1']
        target_val = 0 if STATE['NARNIA_P1'] else 2
        mem.write_ubyte(ADDR_BASE_POINTERS['P1_BASE'] + OFF['NARNIA'], target_val)
    elif player == 2:
        STATE['NARNIA_P2'] = not STATE['NARNIA_P2']
        target_val = 0 if STATE['NARNIA_P2'] else 2
        mem.write_ubyte(ADDR_BASE_POINTERS['P2_BASE'] + OFF['NARNIA'], target_val)

def get_status(mem, base_addr): return mem.read_ubyte(base_addr + OFF['STATUS'])
def get_anim_id(mem, base_addr): return mem.read_ubyte(base_addr + OFF['ANIM_ID'])
def get_stun_memory(mem, base_addr): return mem.read_ubyte(base_addr + OFF['THROW_STATUS'])

def clear_projectiles_optimized(mem):
    for addr in PROJ_ADDR_LIST:
        mem.write_int(addr + OFF['BOX_MASK'], 0)

def get_world_rect(mem, base_addr, box_offset):
    if box_offset == OFF['THROWABLE_BOX']:
        raw = mem.read_bytes(base_addr + OFF['THROWABLE_BOX'], 5)
        if not raw: return None
        bx, by, bw, bh = (raw[1] if raw[1]<=127 else raw[1]-256), (raw[2] if raw[2]<=127 else raw[2]-256), raw[3], raw[4]
        if bw <= 0: return None
    else:
        box_mask = mem.read_ubyte(base_addr + OFF['BOX_MASK'])
        if box_mask is None or box_mask == 0: return None
        found = False
        for i in range(4):
            if (box_mask >> i) & 1:
                raw = mem.read_bytes(base_addr + OFF['BOX_DATA'] + (i * 5), 5)
                if not raw: continue
                b_id = raw[0]
                if BOX_TYPE_MAP.get(b_id) == 'a':
                    bx, by, bw, bh = (raw[1] if raw[1]<=127 else raw[1]-256), (raw[2] if raw[2]<=127 else raw[2]-256), raw[3], raw[4]
                    if i == 1: continue 
                    found = True
                    break
        if not found: return None

    px = mem.read_short(base_addr + OFF['POS_X'])
    py = mem.read_short(base_addr + OFF['POS_Y'])
    facing = mem.read_ubyte(base_addr + OFF['FACING'])
    if px is None: return None

    real_bx = -bx if facing != 0 else bx
    cx, cy = px + real_bx, py + by
    sw, sh = bw * VISUAL['BOX_SCALE'], bh * VISUAL['BOX_SCALE']
    return (cx - sw/2, cx + sw/2, cy - sh/2, cy + sh/2)

def check_overlap_rect(r1, r2):
    if not r1 or not r2: return False
    if r1[1] < r2[0] or r1[0] > r2[1]: return False
    if r1[3] < r2[2] or r1[2] > r2[3]: return False
    return True

def determine_base_color(anim_id):
    if anim_id not in NEUTRAL_ANIM_IDS:
        return COLORS['STARTUP']
    else:
        return COLORS['INVISIBLE']

# ==============================================================================
# DESENHO
# ==============================================================================
def draw_glass_box(surface, color, rect, thickness=2, filled=True):
    try:
        x, y, w, h = int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])
        if w <= 0 or h <= 0: return
        if filled:
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((*color, VISUAL['ALPHA']))
            surface.blit(s, (x, y))
        pygame.draw.rect(surface, color[:3], (x, y, w, h), thickness)
    except: pass

def draw_pivot(surface, x, y, size=6, color=(255, 255, 255)):
    ix, iy = int(x), int(y)
    pygame.draw.line(surface, color, (ix - size, iy), (ix + size, iy), 2)
    pygame.draw.line(surface, color, (ix, iy - size), (ix, iy + size), 2)

def draw_box_from_data(screen, win_info, piv_sx, piv_sy, facing, b_x, b_y, b_w, b_h, color, filled=True):
    vis_w = b_w * VISUAL['BOX_SCALE'] * win_info['scale']
    vis_h = b_h * VISUAL['BOX_SCALE'] * win_info['scale']

    final_rx = -b_x if facing != 0 else b_x

    scr_x = piv_sx + ((final_rx * win_info['scale']) - (vis_w/2))
    scr_y = piv_sy + ((b_y * win_info['scale']) - (vis_h/2))
    
    rect_tuple = (scr_x, scr_y, vis_w, vis_h)
    draw_glass_box(screen, color, rect_tuple, VISUAL['LINE_THICKNESS'], filled)

def draw_text(surface, x, y, text, color):
    font = FONTS['ui']
    render = font.render(text, True, color)
    bg = pygame.Surface((render.get_width()+4, render.get_height()+4))
    bg.fill((0,0,0))
    surface.blit(bg, (int(x), int(y)))
    surface.blit(render, (int(x+2), int(y+2)))

def draw_proximity_wall(screen, color, piv_x, piv_y, range_val, facing, win_info):
    line_col = color[:3]
    screen_range = range_val * win_info['sx']
    wall_x = piv_x - screen_range if facing == 0 else piv_x + screen_range 
    ix, iy, iwx = int(piv_x), int(piv_y), int(wall_x)
    pygame.draw.line(screen, line_col, (ix, iy), (iwx, iy), 2)
    pygame.draw.line(screen, line_col, (iwx, 0), (iwx, iy), 2)

def draw_frame_counter(screen, win_w):
    if not STATE['PAUSED']: return
    text = f"Frames: {STATE['FRAME_COUNT']}"
    render = FONTS['debug'].render(text, True, (0, 255, 0))
    bg = pygame.Surface((render.get_width()+10, render.get_height()+5))
    bg.fill((0, 0, 0))
    x = (win_w / 2) - (render.get_width() / 2)
    y = 10
    screen.blit(bg, (int(x-5), int(y-5)))
    screen.blit(render, (int(x), int(y)))

def draw_standard_boxes(screen, mem, base_addr, win_info, cam_x, opponent_base=None, is_projectile=False, is_p2=False, draw=True):
    visibility = mem.read_ubyte(base_addr + OFF['NARNIA'])
    if visibility == 0: return STATE['SHOW_HITBOXES']

    boxes_to_draw = []
    
    status = mem.read_ubyte(base_addr + OFF['STATUS'])
    if is_projectile and status in GHOST_STATUS_LIST:
        if mem.read_ubyte(base_addr + OFF['THROW_STATUS']) > 1: return None
    try:
        px = mem.read_short(base_addr + OFF['POS_X'])
        py = mem.read_short(base_addr + OFF['POS_Y'])
        facing = mem.read_ubyte(base_addr + OFF['FACING'])
    except: return None
    
    if px == 0 and py == 0: return None
    piv_sx = win_info['off_x'] + ((px - cam_x + VISUAL['FIX_X']) * win_info['scale'])
    piv_sy = ((VISUAL['FIX_Y'] - py) * win_info['scale'])
    
    if not is_projectile and draw: draw_pivot(screen, piv_sx, piv_sy)
    
    has_attack_box = False 

    # 1. PUSH BOX
    if not is_projectile:
        pb_data = mem.read_bytes(base_addr + 0xA4 + 1, 4)
        if pb_data:
            pb_x, pb_y = (pb_data[0] if pb_data[0]<=127 else pb_data[0]-256), (pb_data[1] if pb_data[1]<=127 else pb_data[1]-256)
            pb_w, pb_h = pb_data[2], pb_data[3]
            if pb_w > 0:
                boxes_to_draw.append({
                    'type': 'push',
                    'bx': pb_x, 'by': pb_y, 'bw': pb_w, 'bh': pb_h,
                    'color': TYPE_COLORS['push'],
                    'filled': False 
                })
    
    show_cmd = STATE['P2_CMD'] if is_p2 else STATE['P1_CMD']
    show_common = STATE['P2_COMMON'] if is_p2 else STATE['P1_COMMON']

    opp_throwable_rect = None
    if opponent_base:
        opp_throwable_rect = get_world_rect(mem, opponent_base, OFF['THROWABLE_BOX'])

    if not is_projectile:
        # 2. NORMAL THROW
        if show_common:
            val_th = mem.read_ubyte(base_addr + OFF['THROW_STATUS'])
            if val_th is not None and (val_th & 1) == 0:
                raw_th = mem.read_bytes(base_addr + OFF['THROWABLE_BOX'], 5)
                if raw_th:
                    tb_x, tb_y = (raw_th[1] if raw_th[1]<=127 else raw_th[1]-256), (raw_th[2] if raw_th[2]<=127 else raw_th[2]-256)
                    tb_w, tb_h = raw_th[3], raw_th[4]
                    if tb_w > 0: 
                        col = TYPE_COLORS['Throwable']
                        boxes_to_draw.append({
                            'type': 'throw',
                            'bx': tb_x, 'by': tb_y, 'bw': tb_w, 'bh': tb_h,
                            'color': col,
                            'filled': False
                        })
        # 3. COMMAND THROW
        if show_cmd:
            raw_cmd = mem.read_bytes(base_addr + OFF['CMD_THROW_BOX'], 5)
            if raw_cmd:
                ct_x = raw_cmd[1] if raw_cmd[1] <= 127 else raw_cmd[1] - 256
                ct_y = raw_cmd[2] if raw_cmd[2] <= 127 else raw_cmd[2] - 256
                ct_w, ct_h = raw_cmd[3], raw_cmd[4]
                if ct_w > 0: 
                    sw = ct_w * VISUAL['BOX_SCALE']
                    sh = ct_h * VISUAL['BOX_SCALE']
                    real_cx = -ct_x if facing != 0 else ct_x
                    center_x = px + real_cx
                    min_x, max_x = center_x - (sw / 2), center_x + (sw / 2)
                    center_y = py + ct_y
                    min_y, max_y = center_y - (sh / 2), center_y + (sh / 2)
                    
                    col = TYPE_COLORS['cmd_idle']
                    if check_overlap_rect((min_x, max_x, min_y, max_y), opp_throwable_rect):
                        col = TYPE_COLORS['cmd_connect']
                    
                    boxes_to_draw.append({
                        'type': 'cmd',
                        'bx': ct_x, 'by': ct_y, 'bw': ct_w, 'bh': ct_h,
                        'color': col,
                        'filled': True
                    })

    # 4. HITBOXES / HURTBOXES
    box_mask = mem.read_ubyte(base_addr + OFF['BOX_MASK'])
    if box_mask and box_mask != 0:
        for i in range(4): 
            if (box_mask >> i) & 1:
                raw = mem.read_bytes(base_addr + OFF['BOX_DATA'] + (i * 5), 5)
                if not raw: continue
                b_id, b_x, b_y, b_w, b_h = raw[0], raw[1], raw[2], raw[3], raw[4]
                if b_w >= 250 or b_h >= 250 or b_w <= 0: continue
                if b_x > 127: b_x -= 256
                if b_y > 127: b_y -= 256
                type_code = BOX_TYPE_MAP.get(b_id)
                
                if type_code == 'a': has_attack_box = True

                if type_code == 'a' and i == 1: continue 
                if type_code and TYPE_COLORS.get(type_code):
                    boxes_to_draw.append({
                        'type': type_code,
                        'bx': b_x, 'by': b_y, 'bw': b_w, 'bh': b_h,
                        'color': TYPE_COLORS.get(type_code),
                        'filled': True
                    })
    
    # 5. SORT AND DRAW
    if draw:
        boxes_to_draw.sort(key=lambda item: DRAW_PRIORITY.get(item['type'], 0))
        for box in boxes_to_draw:
            is_filled = box.get('filled', True)
            draw_box_from_data(
                screen, win_info, piv_sx, piv_sy, facing, 
                box['bx'], box['by'], box['bw'], box['bh'], 
                box['color'], is_filled
            )

    return {'raw_x': px, 'raw_y': py, 'facing': facing, 'scr_x': piv_sx, 'scr_y': piv_sy, 'has_atk': has_attack_box}

def process_proximity_cycle(screen, mem, p1_data, p2_data, win_info, is_p2=False):
    idx = STATE['P2_CYCLE'] if is_p2 else STATE['P1_CYCLE']
    modes = PROX_MODES_P2 if is_p2 else PROX_MODES_P1
    if idx == 0: return

    config = modes[idx]
    if config['addr']:
        val = mem.read_ubyte(config['addr'])
        if val is not None:
            dist = abs(p1_data['raw_x'] - p2_data['raw_x'])
            draw_color = config['color']
            if dist <= val:
                draw_color = (255, 50, 50)
            
            target = p2_data if is_p2 else p1_data
            draw_proximity_wall(screen, draw_color, target['scr_x'], target['scr_y'], val, target['facing'], win_info)
            render = FONTS['ui'].render(f"[{config['name']}]", True, draw_color)
            screen.blit(render, (int(target['scr_x'] - 10), int(target['scr_y'] - 60)))

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    print("--- KOF 2002 UM HITBOXES V1.0 ---")
    
    pygame.init()
    try:
        icone_img = pygame.image.load('kof.png')
        pygame.display.set_icon(icone_img)
    except: pass
    
    init_fonts()

    # --- TELA DE AGUARDE ---
    screen = pygame.display.set_mode((400, 150))
    pygame.display.set_caption("KOF HitBoxes by Slipcar - Aguardando")
    
    game_info = None
    while not game_info:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        game_info = get_game_window_info()

        if not game_info:
            screen.fill((20, 20, 20))
            txt = FONTS['wait'].render("Aguardando King of Fighters 2002 UM...", True, (255, 255, 0))
            rect = txt.get_rect(center=(200, 75))
            screen.blit(txt, rect)
            pygame.display.flip()
            time.sleep(0.5)
    
    # --- INICIA OVERLAY ---
    pygame.display.set_caption("KOF HitBox By Slipcar")
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (game_info['x'], game_info['y'])
    screen = pygame.display.set_mode((game_info['w'], game_info['h']), pygame.NOFRAME)
    hwnd_py = pygame.display.get_wm_info()["window"]
    set_dwm_transparency(hwnd_py)
    win32gui.SetWindowPos(hwnd_py, win32con.HWND_TOPMOST, game_info['x'], game_info['y'], 0, 0, win32con.SWP_NOSIZE)
    
    mem = GameMemory()
    mem.attach()
    clock = pygame.time.Clock()
    keys_state = {}

    prev_anim_p1 = 0
    prev_anim_p2 = 0
    
    recording = False
    cooldown = 0

    hit_buffer_p1 = 0
    hit_buffer_p2 = 0

    while True:
        if not mem.attached: mem.attach()
        screen.fill((0, 0, 0)) 
        for e in pygame.event.get(): 
            if e.type == pygame.QUIT: 
                if STATE['PAUSED']: toggle_pause(mem)
                return

        # EXIT HOTKEY (CTRL + ESC)
        if (win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000) and (win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000):
            if STATE['PAUSED']: toggle_pause(mem)
            return

        def check_key(vk): return win32api.GetAsyncKeyState(vk) & 0x8000
        
        # ATIVAÇÃO DO BOTÕES DE PERTO (A, B, C, D) DO PLAYER1
        if check_key(win32con.VK_F1):
            if not keys_state.get('F1'): STATE['P1_CYCLE'] = (STATE['P1_CYCLE']+1)%len(PROX_MODES_P1); keys_state['F1']=True
        else: keys_state['F1']=False

        # ATIVAÇÃO DAS BOXES DE NORMAL E COMMAND GRAB DO PLAYER1
        if check_key(win32con.VK_F2):
            if not keys_state.get('F2'): STATE['P1_CMD'] = not STATE['P1_CMD']; keys_state['F2']=True
        else: keys_state['F2']=False
        
        # ATIVAÇÃO DA BOX ONDE O PLAYER1 PODE SER AGARRADO
        if check_key(win32con.VK_F3):
            if not keys_state.get('F3'): STATE['P1_COMMON'] = not STATE['P1_COMMON']; keys_state['F3']=True
        else: keys_state['F3']=False

        # ATIVAÇÃO DO BOTÕES DE PERTO (A, B, C, D) DO PLAYER2
        if check_key(win32con.VK_F4):
            if not keys_state.get('F4'): STATE['P2_CYCLE'] = (STATE['P2_CYCLE']+1)%len(PROX_MODES_P2); keys_state['F4']=True
        else: keys_state['F4']=False
        
        # ATIVAÇÃO DAS BOXES DE NORMAL E COMMAND GRAB DO PLAYER2
        if check_key(win32con.VK_F5):
            if not keys_state.get('F5'): STATE['P2_CMD'] = not STATE['P2_CMD']; keys_state['F5']=True
        else: keys_state['F5']=False

        # ATIVAÇÃO DA BOX ONDE O PLAYER2 PODE SER AGARRADO
        if check_key(win32con.VK_F6):
            if not keys_state.get('F6'): STATE['P2_COMMON'] = not STATE['P2_COMMON']; keys_state['F6']=True
        else: keys_state['F6']=False

        # ATIVA O PAUSE INTERNO DO JOGO
        if check_key(win32con.VK_F7):
            if not keys_state.get('F7'): toggle_pause(mem); keys_state['F7'] = True
        else: keys_state['F7'] = False
        
        # AVANÇA 1 FRAME
        did_step = False
        if check_key(win32con.VK_F8):
            if not keys_state.get('F8'): 
                did_step = advance_frame(mem)
                keys_state['F8'] = True
        else: keys_state['F8'] = False
        
        # ATIVA OU DESATIVA A BARRA DE CONTAGEM DE FRAMES
        if check_key(win32con.VK_F9):
            if not keys_state.get('F9'): STATE['SHOW_METER'] = not STATE['SHOW_METER']; keys_state['F9']=True
        else: keys_state['F9']=False

        # ATIVA OU DESATIVA AS HITBOXES
        if check_key(win32con.VK_F10):
            if not keys_state.get('F10'): 
                STATE['SHOW_HITBOXES'] = not STATE['SHOW_HITBOXES']
                keys_state['F10'] = True
        else: keys_state['F10'] = False

        # (P1 NARNIA)
        if check_key(win32con.VK_NUMPAD1):
            if not keys_state.get('NUMPAD1'): 
                toggle_narnia(mem, 1)
                keys_state['NUMPAD1'] = True
        else: keys_state['NUMPAD1'] = False

        # (P2 NARNIA)
        if check_key(win32con.VK_NUMPAD2):
            if not keys_state.get('VK_NUMPAD2'): 
                toggle_narnia(mem, 2)
                keys_state['VK_NUMPAD2'] = True
        else: keys_state['VK_NUMPAD2'] = False

        current_info = get_game_window_info()
        if current_info:
            if current_info['w'] != game_info['w'] or current_info['h'] != game_info['h'] or current_info['x'] != game_info['x']:
                game_info = current_info
                win32gui.SetWindowPos(hwnd_py, win32con.HWND_TOPMOST, game_info['x'], game_info['y'], 0, 0, win32con.SWP_NOSIZE)
                screen = pygame.display.set_mode((game_info['w'], game_info['h']), pygame.NOFRAME)

            # Verifica se a janela do jogo está em Foco/Ativa
            fg_window = win32gui.GetForegroundWindow()
            should_draw = (fg_window == current_info['hwnd'])

            if should_draw and mem.attached:
                cam_x = mem.read_int(ADDR_BASE_POINTERS['CAMERA_X'])
                if cam_x is None: cam_x = 0

                p1_data = draw_standard_boxes(screen, mem, ADDR_BASE_POINTERS['P1_BASE'], game_info, cam_x, ADDR_BASE_POINTERS['P2_BASE'], False, False, draw=STATE['SHOW_HITBOXES'])
                p2_data = draw_standard_boxes(screen, mem, ADDR_BASE_POINTERS['P2_BASE'], game_info, cam_x, ADDR_BASE_POINTERS['P1_BASE'], False, True, draw=STATE['SHOW_HITBOXES'])
                
                if p1_data and p2_data and STATE['SHOW_HITBOXES']:
                    try:
                        process_proximity_cycle(screen, mem, p1_data, p2_data, game_info, False)
                        process_proximity_cycle(screen, mem, p1_data, p2_data, game_info, True)
                    except: pass
                
                if (not STATE['PAUSED']) or did_step:
                    if p1_data and p2_data:
                        anim_p1 = get_anim_id(mem, ADDR_BASE_POINTERS['P1_BASE'])
                        anim_p2 = get_anim_id(mem, ADDR_BASE_POINTERS['P2_BASE'])
                        stun_p1 = get_stun_memory(mem, ADDR_BASE_POINTERS['P1_BASE'])
                        stun_p2 = get_stun_memory(mem, ADDR_BASE_POINTERS['P2_BASE'])

                        p1_ret_neutral = (anim_p1 in NEUTRAL_ANIM_IDS) and (prev_anim_p1 not in NEUTRAL_ANIM_IDS)
                        p2_ret_neutral = (anim_p2 in NEUTRAL_ANIM_IDS) and (prev_anim_p2 not in NEUTRAL_ANIM_IDS)
                        if p1_ret_neutral or p2_ret_neutral:
                            clear_projectiles_optimized(mem)
                        
                        prev_anim_p1 = anim_p1
                        prev_anim_p2 = anim_p2

                        rect_hit_p1 = get_world_rect(mem, ADDR_BASE_POINTERS['P1_BASE'], OFF['BOX_DATA'])
                        rect_hit_p2 = get_world_rect(mem, ADDR_BASE_POINTERS['P2_BASE'], OFF['BOX_DATA'])
                        has_hitbox_p1 = (rect_hit_p1 is not None)
                        has_hitbox_p2 = (rect_hit_p2 is not None)

                        p1_busy = (anim_p1 not in NEUTRAL_ANIM_IDS) or (stun_p1 != 0)
                        p2_busy = (anim_p2 not in NEUTRAL_ANIM_IDS) or (stun_p2 != 0)
                        
                        global_active = p1_busy or p2_busy

                        if global_active:
                            if not recording:
                                recording = True
                                p1_tracker.reset()
                                p2_tracker.reset()
                                cooldown = 0
                                hit_buffer_p1 = 0
                                hit_buffer_p2 = 0
                            
                            base_col_p1 = determine_base_color(anim_p1)
                            base_col_p2 = determine_base_color(anim_p2)

                            # P1
                            if stun_p1 == 2: 
                                hit_buffer_p1 += 1
                                is_hit_p1 = (hit_buffer_p1 > 2)
                            else: 
                                hit_buffer_p1 = 0
                                is_hit_p1 = False

                            # P2
                            if stun_p2 == 2: 
                                hit_buffer_p2 += 1
                                is_hit_p2 = (hit_buffer_p2 > 2)
                            else: 
                                hit_buffer_p2 = 0
                                is_hit_p2 = False

                            p1_tracker.add_frame(base_col_p1, has_hitbox_p1, is_hit_p1)
                            p2_tracker.add_frame(base_col_p2, has_hitbox_p2, is_hit_p2)
                            
                        elif recording:
                            cooldown += 1
                            if cooldown > 5: 
                                recording = False
                                p1_tracker.finalize_stats()
                                p2_tracker.finalize_stats()

                try:
                    for i in range(MAX_PROJECTILES):
                        draw_standard_boxes(screen, mem, PROJ_ADDR_LIST[i], game_info, cam_x, None, True, draw=STATE['SHOW_HITBOXES'])
                except: pass

                if STATE['SHOW_METER']:
                    last_idx_p1 = p1_tracker.get_last_active_frame()
                    last_idx_p2 = p2_tracker.get_last_active_frame()
                    adv_p1 = last_idx_p2 - last_idx_p1
                    adv_p2 = last_idx_p1 - last_idx_p2

                    # --- CENTRALIZAÇÃO ---
                    bar_width = ((METER_CONFIG['PIXEL_SIZE'] + METER_CONFIG['SPACING']) * METER_CONFIG['BAR_LENGTH']) + 4
                    mx = (game_info['w'] // 2) - (bar_width // 2)
                    my = game_info['h'] - 140

                    p1_tracker.draw(screen, mx, my, recording, advantage_val=adv_p1)
                    p2_tracker.draw(screen, mx, my + 50, recording, advantage_val=adv_p2)
        
        draw_frame_counter(screen, game_info['w'])
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
