"""文创合成：把 AI 生成的图套模板（明信片/海报/书签），导出高清成品 PNG。

本质是"生图结果 + Pillow 排版合成"。统一宣纸米白底 #f7f2e9 + 砚墨字色，
标题用楷体（降级雅黑/黑体），落款用朱砂印章式红块。
"""
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

# —— 配色（与前端设计令牌对齐） ——
PAPER = (247, 242, 233)       # 宣纸米白
PAPER_BORDER = (207, 192, 166)  # 纸边线
INK = (36, 27, 21)            # 墨色
INK_SOFT = (138, 116, 98)     # 淡墨
SEAL = (160, 58, 46)          # 朱砂红
GOLD = (197, 123, 58)         # 秋柿金

_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyhbd.ttc",   # 微软雅黑 Bold
    r"C:\Windows\Fonts\msyh.ttc",     # 微软雅黑
    r"C:\Windows\Fonts\simhei.ttf",   # 黑体
    r"C:\Windows\Fonts\simsun.ttc",   # 宋体
    r"C:\Windows\Fonts\STKAITI.TTF",  # 楷体
    "msyhbd.ttc", "msyh.ttc", "simhei.ttf", "simsun.ttc", "STKAITI.TTF",
]


def _load_font(size: int, bold: bool = False):
    """按候选列表加载中文 TTF；都失败则退回默认字体。"""
    cands = list(_FONT_CANDIDATES)
    if bold:
        cands.insert(0, r"C:\Windows\Fonts\msyhbd.ttc")
    for c in cands:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _fit_box(w: int, h: int, box_w: int, box_h: int):
    """返回按比例缩放到 box 内的 (nw, nh)。"""
    scale = min(box_w / w, box_h / h)
    return int(w * scale), int(h * scale)


def _draw_centered(draw, cx, y, text, font, fill, spacing=0):
    """以 cx 为中心横向绘制文字，支持字间距，返回文字底端 y。"""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, fill=fill, font=font)
        x += w + spacing
    return y + font.size


def _seal(draw, cx, cy, size, text="墨蕴徽州"):
    """朱砂印章：红色方框内竖向排字。"""
    draw.rectangle([cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2],
                   outline=SEAL, width=4)
    f = _load_font(int(size * 0.21), bold=True)
    col_w = size * 0.42
    n = len(text)
    rows = (n + 1) // 2
    for i, ch in enumerate(text):
        r = i // 2
        c = i % 2
        x = cx - size / 2 + col_w * (0.32 + c * 0.5)
        y = cy - size / 2 + col_w * (0.32 + r * 0.5)
        draw.text((x, y), ch, fill=SEAL, font=f)


def _frame(draw, x0, y0, x1, y1, color=SEAL, width=3):
    draw.rectangle([x0, y0, x1, y1], outline=color, width=width)


# --------------------------------------------------------------------------
# 一、明信片（竖版 3:4）
# --------------------------------------------------------------------------
def compose_postcard(image_bytes: bytes, title: str = "墨蕴徽州",
                     subtitle: str = "", font_path: str = None) -> bytes:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size

    CARD_W, CARD_H = 1240, 1720
    margin = 52
    card = Image.new("RGB", (CARD_W, CARD_H), PAPER)
    draw = ImageDraw.Draw(card)
    draw.rectangle([2, 2, CARD_W - 3, CARD_H - 3], outline=PAPER_BORDER, width=2)

    # 图画区（顶部）
    box_w = CARD_W - margin * 2 - 14
    box_h = 1080
    nw, nh = _fit_box(w, h, box_w, box_h)
    img_r = img.resize((nw, nh), Image.LANCZOS)
    ix = (CARD_W - nw) // 2
    iy = margin
    card.paste(img_r, (ix, iy))
    _frame(draw, ix - 6, iy - 6, ix + nw + 6, iy + nh + 6, color=GOLD, width=3)

    # 文字区（标题 / 副题 / 印章）
    text_top = iy + nh + 40
    title_font = _load_font(88, bold=True)
    _draw_centered(draw, CARD_W / 2, text_top, title, title_font, INK, spacing=14)
    if subtitle:
        sub_font = _load_font(36)
        _draw_centered(draw, CARD_W / 2, text_top + 120, subtitle, sub_font, INK_SOFT, spacing=4)
    _seal(draw, CARD_W / 2, CARD_H - margin - 92, 116)

    buf = BytesIO()
    card.save(buf, format="PNG")
    return buf.getvalue()


# --------------------------------------------------------------------------
# 二、海报（竖版 2:3）
# --------------------------------------------------------------------------
def compose_poster(image_bytes: bytes, title: str = "墨蕴徽州",
                   subtitle: str = "", font_path: str = None) -> bytes:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size

    P_W, P_H = 1024, 1536
    poster = Image.new("RGB", (P_W, P_H), PAPER)
    draw = ImageDraw.Draw(poster)
    draw.rectangle([2, 2, P_W - 3, P_H - 3], outline=PAPER_BORDER, width=2)

    # 顶部标题
    title_font = _load_font(92, bold=True)
    _draw_centered(draw, P_W / 2, 66, title, title_font, INK, spacing=16)
    if subtitle:
        sub_font = _load_font(38)
        _draw_centered(draw, P_W / 2, 196, subtitle, sub_font, INK_SOFT, spacing=6)
    draw.line([P_W * 0.12, 292, P_W * 0.88, 292], fill=GOLD, width=2)

    # 主图区
    box_w = P_W - 150
    box_h = 980
    nw, nh = _fit_box(w, h, box_w, box_h)
    img_r = img.resize((nw, nh), Image.LANCZOS)
    ix = (P_W - nw) // 2
    iy = 336
    poster.paste(img_r, (ix, iy))
    _frame(draw, ix - 8, iy - 8, ix + nw + 8, iy + nh + 8, color=SEAL, width=4)

    # 底部落款
    foot_font = _load_font(30)
    _draw_centered(draw, P_W / 2, iy + nh + 66, "墨蕴徽州 · AI 文创", foot_font, INK_SOFT, spacing=4)

    buf = BytesIO()
    poster.save(buf, format="PNG")
    return buf.getvalue()


# --------------------------------------------------------------------------
# 三、书签（竖条）
# --------------------------------------------------------------------------
def compose_bookmark(image_bytes: bytes, title: str = "墨蕴徽州",
                     subtitle: str = "", font_path: str = None) -> bytes:
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    w, h = img.size

    B_W, B_H = 480, 1500
    bm = Image.new("RGB", (B_W, B_H), PAPER)
    draw = ImageDraw.Draw(bm)
    draw.rectangle([2, 2, B_W - 3, B_H - 3], outline=PAPER_BORDER, width=2)

    # 顶部朱砂题签
    draw.rectangle([0, 0, B_W, 150], fill=SEAL)
    head_font = _load_font(52, bold=True)
    _draw_centered(draw, B_W / 2, 46, title, head_font, (250, 245, 236), spacing=10)

    # 主图区（居中细框）
    box_w = B_W - 60
    box_h = 700
    nw, nh = _fit_box(w, h, box_w, box_h)
    img_r = img.resize((nw, nh), Image.LANCZOS)
    ix = (B_W - nw) // 2
    iy = 190
    bm.paste(img_r, (ix, iy))
    _frame(draw, ix - 6, iy - 6, ix + nw + 6, iy + nh + 6, color=GOLD, width=3)

    # 副题 + 竖线 + 印章
    if subtitle:
        sub_font = _load_font(32)
        _draw_centered(draw, B_W / 2, iy + nh + 50, subtitle, sub_font, INK_SOFT, spacing=3)
    draw.line([B_W / 2, 1120, B_W / 2, 1240], fill=PAPER_BORDER, width=2)
    _seal(draw, B_W / 2, 1350, 130)

    buf = BytesIO()
    bm.save(buf, format="PNG")
    return buf.getvalue()
