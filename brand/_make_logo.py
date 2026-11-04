# -*- coding: utf-8 -*-
"""徽脉队标生成（初稿）：马头墙剪影 + 朱砂脉线 + 徽脉二字。"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
INK = (36, 27, 21, 255)          # 砚墨
PAPER = (247, 242, 233, 255)     # 宣纸米白
SEAL = (160, 58, 46, 255)        # 朱砂
MIST = (188, 174, 152, 255)      # 淡墨/远墙
BRICK = (120, 100, 82, 255)      # 砖檐(装饰)

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ---- 底卡：宣纸圆角方 ----
d.rounded_rectangle([24, 24, 1000, 1000], radius=200,
                    fill=PAPER, outline=INK, width=12)

# ---- 右上角小朱砂印章「印」----
sx, sy, ss = 800, 92, 88
d.rectangle([sx, sy, sx + ss, sy + ss], fill=SEAL)
f_seal = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", int(ss * 0.52))
d.text((sx + ss / 2, sy + ss / 2), "印", font=f_seal,
       fill=(250, 245, 236, 255), anchor="mm")

# ---- 后景墙（淡墨，错落一座）----
back = [(336, 548), (336, 404), (448, 404), (448, 322),
        (560, 322), (560, 236), (680, 236), (680, 322),
        (762, 322), (762, 404), (806, 404), (806, 548)]
d.polygon(back, fill=MIST)

# ---- 前景马头墙（浓墨，标志性台阶轮廓）----
front = [(228, 556), (228, 428), (352, 428), (352, 342),
         (466, 342), (466, 244), (612, 244), (612, 342),
         (724, 342), (724, 428), (808, 428), (808, 556)]
d.polygon(front, fill=INK)

# ---- 马头墙顶部小檐线（墨色墙面上的提亮）----
for x0, x1 in [(352, 352), (466, 466), (612, 612), (724, 724)]:
    d.line([x0, 342, x1, 342], fill=BRICK, width=6)
d.line([352, 428, 466, 428], fill=BRICK, width=6)
d.line([612, 428, 724, 428], fill=BRICK, width=6)

# ---- 券门洞（马头墙下的半圆门）----
d.arc([478, 470, 600, 592], 0, 180, fill=(247, 242, 233, 255), width=18)

# ---- 朱砂「脉」线：一条起伏的心跳/水流线，穿过马头墙 ----
pulse = [(246, 512), (332, 474), (424, 546), (512, 462),
         (604, 532), (700, 456), (790, 512)]
d.line(pulse, fill=SEAL, width=22, joint="curve")
# 脉线末端一个朱砂圆点（句读/印章点）
d.ellipse([782, 500, 818, 536], fill=SEAL)

# ---- 主标：徽脉 二字（楷体，居中）----
try:
    f_main = ImageFont.truetype("C:/Windows/Fonts/STKAITI.TTF", 200)
except Exception:
    f_main = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 200)
d.text((512 - 122, 758), "徽", font=f_main, fill=INK, anchor="mm")
d.text((512 + 122, 758), "脉", font=f_main, fill=INK, anchor="mm")

# ---- 徽脉下方朱砂横杠（点睛）----
d.line([392, 888, 632, 888], fill=SEAL, width=14)

img.save("C:/Users/30915/Desktop/mojyun-huizhou/brand/huimai_logo_v1.png")
print("saved huimai_logo_v1.png")
