"""Reels "Feirão Black" — carros em estoque como cartas de jogo, deslizando para o lado.

Uso: python3 cartas.py <pasta_fotos> <pasta_saida>
Fotos: 1.webp ... 6.webp na ordem de CARROS.
Gera: cartas/carta-XX.png, frames brutos para o ffmpeg (via stdout) e capa.png.
"""
import math, os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps

FOTOS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(f"{OUT}/cartas", exist_ok=True)
W, H, FPS = 1080, 1920, 30
FD = "/usr/share/fonts/opentype/inter/"
def F(s, w="ExtraBold"): return ImageFont.truetype(f"{FD}Inter-{w}.otf", s)

RED, RED2, GOLD, GOLD2 = (225, 30, 55), (140, 10, 30), (247, 200, 80), (190, 120, 30)

CARROS = [
    dict(marca="CITROËN", modelo="C4 CACTUS", versao="Feel 1.6 16V Flex Aut.",
         stats=[("ANO", "2022/2022"), ("KM", "62.108"), ("CÂMBIO", "Automático"), ("COMBUSTÍVEL", "Flex")], extras=[]),
    dict(marca="VOLKSWAGEN", modelo="NIVUS", versao="Comfortline 1.0 200 TSI Flex Aut.",
         stats=[("ANO", "2025/2026"), ("KM", "12.000"), ("CÂMBIO", "Automático"), ("COMBUSTÍVEL", "Flex")], extras=[]),
    dict(marca="CITROËN", modelo="AIRCROSS", versao="Aircross7 Feel 1.0 Flex Tb. 200 Aut.",
         stats=[("ANO", "2024/2025"), ("KM", "41.459"), ("CÂMBIO", "Automático"), ("COMBUSTÍVEL", "Flex")],
         extras=["7 lugares", "Central multimídia", "CarPlay · Android Auto"]),
    dict(marca="RENAULT", modelo="DUSTER", versao="Iconic 1.6 16V Flex Aut.",
         stats=[("ANO", "2021/2022"), ("KM", "62.154"), ("CÂMBIO", "Automático"), ("COMBUSTÍVEL", "Flex")],
         extras=["Bancos de couro", "Câmera de ré", "Central multimídia", "Ar digital"]),
    dict(marca="RENAULT", modelo="OROCH", versao="Pro 1.6 Flex 16V Mec.",
         stats=[("ANO", "2023/2024"), ("KM", "95.202"), ("CÂMBIO", "Manual"), ("COMBUSTÍVEL", "Flex")],
         extras=["Carroceria"]),
    dict(marca="HYUNDAI", modelo="ELANTRA", versao="Special Edition 2.0 16V Flex Aut.",
         stats=[("ANO", "2016/2017"), ("MOTOR", "2.0 16V"), ("CÂMBIO", "Automático"), ("COMBUSTÍVEL", "Flex")],
         extras=["Bancos de couro", "Câmera de ré", "Piloto automático"]),
]
N = len(CARROS)

def grad(w, h, c1, c2, horizontal=False):
    g = Image.linear_gradient("L").resize((w, h))
    if horizontal: g = g.rotate(90, expand=True).resize((w, h))
    return Image.composite(Image.new("RGB", (w, h), c2), Image.new("RGB", (w, h), c1), g)

def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

def ctext(d, cx, y, txt, font, fill="white", **kw):
    d.text((cx - d.textlength(txt, font=font) / 2, y), txt, font=font, fill=fill, **kw)

def fit(d, txt, w, size, weight="Black"):
    while d.textlength(txt, font=F(size, weight)) > w: size -= 4
    return F(size, weight)

# ---------- carta ----------
CW, CH = 780, 1200
def carta(i, c):
    card = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    borda = grad(CW, CH, GOLD, RED)  # moldura dourado -> vermelho
    card.paste(borda, (0, 0), rmask(CW, CH, 48))
    b = 14; iw, ih = CW - 2 * b, CH - 2 * b
    inner = grad(iw, ih, (48, 8, 16), (12, 12, 16))
    d = ImageDraw.Draw(inner, "RGBA")
    # textura de linhas finas
    for y in range(0, ih, 6): d.line((0, y, iw, y), fill=(255, 255, 255, 5))
    # topo: número e selo
    d.rounded_rectangle((28, 28, 178, 82), 27, fill=RED)
    ctext(d, 103, 37, f"Nº {i+1:02d}/{N:02d}", F(28))
    selo = "FEIRÃO BLACK"
    sw = d.textlength(selo, font=F(28)) + 44
    d.rounded_rectangle((iw - 28 - sw, 28, iw - 28, 82), 27, outline=GOLD, width=3)
    ctext(d, iw - 28 - sw / 2, 37, selo, F(28), fill=GOLD)
    # nome
    ctext(d, iw / 2, 108, c["marca"], F(34, "Bold"), fill=(200, 200, 205))
    ctext(d, iw / 2, 146, c["modelo"], fit(d, c["modelo"], iw - 80, 110))
    ctext(d, iw / 2, 268, c["versao"], fit(d, c["versao"], iw - 70, 34, "SemiBold"), fill=(215, 215, 220))
    # foto
    foto = Image.open(f"{FOTOS}/{i+1}.webp").convert("RGB")
    foto = foto.crop((110, 318, 1100, 888)).resize((iw - 56, 360), Image.LANCZOS)
    fx, fy = 28, 322
    sombra = Image.new("L", inner.size, 0); ImageDraw.Draw(sombra).rounded_rectangle((fx - 4, fy - 4, fx + foto.width + 4, fy + foto.height + 4), 30, fill=255)
    inner.paste(grad(foto.width + 8, foto.height + 8, GOLD, GOLD2), (fx - 4, fy - 4), rmask(foto.width + 8, foto.height + 8, 30))
    inner.paste(foto, (fx, fy), rmask(foto.width, foto.height, 26))
    # atributos (2x2)
    gy = fy + foto.height + 20; gw = (iw - 56 - 20) // 2; gh = 98
    for k, (lab, val) in enumerate(c["stats"]):
        x = 28 + (k % 2) * (gw + 20); y = gy + (k // 2) * (gh + 12)
        d.rounded_rectangle((x, y, x + gw, y + gh), 22, fill=(255, 255, 255, 14), outline=(255, 255, 255, 40), width=2)
        d.rounded_rectangle((x, y, x + 10, y + gh), 5, fill=RED)
        d.text((x + 30, y + 12), lab, font=F(26, "Bold"), fill=GOLD)
        d.text((x + 30, y + 42), val, font=fit(d, val, gw - 50, 46, "ExtraBold"), fill="white")
    # habilidades
    ey = gy + 2 * gh + 12 + 20
    if c["extras"]:
        xs = 28; row = 0
        for e in c["extras"]:
            t = "★ " + e; fnt = F(28, "SemiBold"); tw = d.textlength(t, font=fnt) + 40
            if xs + tw > iw - 28: row += 1; xs = 28
            y = ey + row * 60
            d.rounded_rectangle((xs, y, xs + tw, y + 50), 25, fill=(225, 30, 55, 60), outline=RED, width=2)
            d.text((xs + 20, y + 9), t, font=fnt, fill="white")
            xs += tw + 12
    else:
        ctext(d, iw / 2, ey + 22, "MARIO CAR", F(54, "Black"), fill=(255, 255, 255, 40))
    # faixa final
    fy2 = ih - 96
    inner.paste(grad(iw, 96, RED, RED2, True), (0, fy2), rmask(iw, 96, 0))
    ctext(d, iw / 2, fy2 + 18, "IPVA 2027 PAGO", F(52, "Black"))
    card.paste(inner, (b, b), rmask(iw, ih, 38))
    return card

cartas = [carta(i, c) for i, c in enumerate(CARROS)]
for i, c in enumerate(cartas): c.save(f"{OUT}/cartas/carta-{i+1:02d}.png")
if "--so-cartas" in sys.argv: sys.exit()

# ---------- fundo ----------
def fundo():
    img = Image.new("RGB", (W, H), (8, 8, 10))
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((-350, 520, W + 350, 1650), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(230))
    img = Image.composite(Image.new("RGB", (W, H), (170, 10, 35)), img, glow.point(lambda v: int(v * .7)))
    st = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(st)
    for k in range(-6, 14):
        x = k * 150; sd.polygon([(x, 0), (x + 36, 0), (x + 36 - 800, 800), (x - 800, 800)], fill=255)
    fm = Image.new("L", (W, H), 0); fm.paste(Image.linear_gradient("L").resize((W, 800)).point(lambda v: (255 - v) // 4), (0, 0))
    img = Image.composite(Image.new("RGB", (W, H), (30, 30, 36)), img, ImageChops.multiply(st, fm))
    return img
BG = fundo()

def cabecalho():
    lay = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((330, 70, 750, 130), 30, fill=RED); ctext(d, 540, 80, "ÚLTIMA SEMANA", F(38))
    ctext(d, 540, 140, "FEIRÃO", F(150, "Black"))
    ctext(d, 540, 280, "BLACK", F(110, "Black"), fill=RED)
    # brilho dourado sob o título
    d.rectangle((390, 400 - 8, 690, 400 - 4), fill=GOLD)
    return lay
HEAD = cabecalho()

def rodape(idx):
    lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ctext(d, 540, 20, "Escolha a sua carta", F(46, "Bold"), fill=(235, 235, 240))
    for k in range(N):
        x = 540 + (k - (N - 1) / 2) * 44
        if k == idx: d.rounded_rectangle((x - 22, 100, x + 22, 116), 8, fill=GOLD)
        else: d.ellipse((x - 8, 100, x + 8, 116), fill=(255, 255, 255, 90))
    return lay
RODAPES = [rodape(k) for k in range(N)]

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def eob(x):  # ease out back (pulinho)
    x = max(0, min(1, x)); c1 = 1.5; return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2

BEAT = 60 / 124
T0 = 4 * BEAT           # baralho chega
STEP = 6 * BEAT         # tempo por carta
TR = 0.6                # duração do deslize
TEND = T0 + N * STEP    # tela final
DUR = TEND + 5.6

def pos(t):
    if t < T0: return -2.6 * (1 - ease((t - 0.35) / (T0 - 0.35)))
    k = int((t - T0) // STEP); r = (t - T0) - k * STEP
    if k >= N: return N + 0.6
    return k + ease((r - (STEP - TR)) / TR) * (1 if k < N - 1 else 1.6)

def escuro(im, f):
    a = im.getchannel("A"); rgb = im.convert("RGB").point(lambda v: int(v * f)); rgb.putalpha(a); return rgb

def brilho(card, u):
    """faixa holográfica atravessando a carta (u de 0 a 1)."""
    if not 0 < u < 1: return card
    band = Image.new("L", (CW * 2, CH * 2), 0); bd = ImageDraw.Draw(band)
    x = int(-400 + u * (CW * 2 + 400))
    bd.polygon([(x, 0), (x + 140, 0), (x + 140 - 900, CH * 2), (x - 900, CH * 2)], fill=110)
    band = band.filter(ImageFilter.GaussianBlur(30)).crop((CW // 2, CH // 2, CW // 2 + CW, CH // 2 + CH))
    band = ImageChops.multiply(band, card.getchannel("A"))
    out = card.copy(); out.alpha_composite(Image.merge("RGBA", (band.point(lambda v: 255),) * 3 + (band,)))
    return out

def desenha_carta(frame, im, cx, cy, s, ang, sombra=True):
    w, h = int(CW * s), int(CH * s)
    c = im.resize((w, h), Image.BILINEAR).rotate(ang, Image.BICUBIC, expand=True)
    if sombra:
        sh = c.getchannel("A").point(lambda v: v * 0.6).filter(ImageFilter.BoxBlur(18))
        frame.paste((0, 0, 0), (int(cx - sh.width / 2 + 14), int(cy - sh.height / 2 + 30)), sh)
    frame.paste(c, (int(cx - c.width / 2), int(cy - c.height / 2)), c)

def dedo(frame, x, y, a):
    if a <= 0: return
    lay = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((40, 40, 180, 180), fill=(255, 255, 255, int(70 * a)), outline=(255, 255, 255, int(220 * a)), width=6)
    d.ellipse((85, 85, 135, 135), fill=(255, 255, 255, int(230 * a)))
    frame.paste(lay, (int(x - 110), int(y - 110)), lay)

CY = 1080; SP = 760
FIM_ELEM = None
def tela_final(frame, u):
    d = ImageDraw.Draw(frame)
    # leque de cartas
    for k in range(N):
        a = eob((u - k * 0.06) / 0.45)
        if a <= 0: continue
        ang = (k - (N - 1) / 2) * -9; cx = 540 + (k - (N - 1) / 2) * 120
        cy = 830 + abs(k - (N - 1) / 2) ** 2 * 10 + (1 - a) * 300
        desenha_carta(frame, cartas[k], cx, cy, 0.36 * min(1, a + .2), ang)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a1 = ease((u - 0.35) / 0.25)
    if a1 > 0:
        ctext(d, 540, 1150 - (1 - a1) * 40, "ESCOLHEU A SUA?", F(80, "Black"), fill=(255, 255, 255, int(255 * a1)))
    a2 = eob((u - 0.5) / 0.3)
    if a2 > 0:
        bx = Image.new("RGBA", (920, 300), (0, 0, 0, 0)); bd = ImageDraw.Draw(bx)
        bd.rounded_rectangle((0, 0, 919, 299), 44, fill="white")
        ctext(bd, 460, 22, "LEVA COM", F(52), fill=(12, 12, 14))
        ctext(bd, 460, 80, "IPVA 2027", F(150, "Black"), fill=RED)
        s = max(.01, a2); bx = bx.resize((int(920 * s), int(300 * s)))
        ov.paste(bx, (540 - bx.width // 2, 1410 - bx.height // 2), bx)
        d = ImageDraw.Draw(ov)
    a3 = ease((u - 0.62) / 0.2)
    if a3 > 0:
        ctext(d, 540, 1575, "PAGO!", F(84, "Black"), fill=(*GOLD, int(255 * a3)))
    a4 = ease((u - 0.7) / 0.2)
    if a4 > 0:
        pul = 1 + 0.04 * math.sin(u * 30)
        bw, bh = int(680 * pul), int(108 * pul)
        d.rounded_rectangle((540 - bw // 2, 1720 - bh // 2, 540 + bw // 2, 1720 + bh // 2), bh // 2, fill=(*RED, int(255 * a4)))
        ctext(d, 540, 1720 - 32, "CHAMA NO DIRECT", F(58), fill=(255, 255, 255, int(255 * a4)))
        ctext(d, 540, 1810, "*Consulte condições na loja.", F(30, "Medium"), fill=(190, 190, 195, int(255 * a4)))
    frame.alpha_composite(ov)

def quadro(t):
    fr = BG.copy().convert("RGBA")
    # cabeçalho entra com pulinho
    s = eob(t / 0.5)
    if s > 0:
        hd = HEAD if s == 1 else HEAD.resize((int(W * s), int(400 * s)))
        if t >= TEND: hd = HEAD
        fr.alpha_composite(hd, (540 - hd.width // 2, 40 + (400 - hd.height) // 2))
    if t >= TEND:
        tela_final(fr, (t - TEND) / 3.0); return fr
    p = pos(t)
    vis = sorted([k for k in range(N) if abs(k - p) < 2.2], key=lambda k: -abs(k - p))
    for k in vis:
        dd = k - p; ad = min(abs(dd), 1.6)
        s = 1 - 0.2 * min(ad, 1) - 0.08 * max(0, ad - 1)
        cx = 540 + dd * SP; cy = CY + 40 * min(ad, 1)
        im = cartas[k]
        if abs(dd) < 0.05 and t >= T0:
            r = (t - T0) - k * STEP; im = brilho(im, (r - 0.15) / 1.1)
        if ad > 0.02: im = escuro(im, 1 - 0.5 * min(ad, 1))
        desenha_carta(fr, im, cx, cy, s * 0.92, -dd * 8)
    idx = max(0, min(N - 1, round(p)))
    if t >= T0 - 0.3:
        fr.alpha_composite(RODAPES[idx], (0, 1640))
    # dedo deslizando antes de cada troca
    if t >= T0:
        k = int((t - T0) // STEP); r = (t - T0) - k * STEP; ini = STEP - TR - 0.25
        if r > ini:
            u = (r - ini) / (TR + 0.25)
            a = min(1, u * 5) * min(1, (1 - u) * 4)
            dedo(fr, 820 - ease(u) * 560, 1270, a)
    return fr

if __name__ == "__main__":
    if "--previa" in sys.argv:
        for t in [0.3, T0 + 1.0, T0 + STEP - 0.3, TEND + 3.5]:
            quadro(t).convert("RGB").save(f"{OUT}/previa-{t:05.2f}.png")
        sys.exit()
    nf = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                           "-pix_fmt", "yuv420p", f"{OUT}/video_mudo.mp4"], stdin=subprocess.PIPE)
    for n in range(nf):
        ff.stdin.write(quadro(n / FPS).convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    quadro(TEND + 3.5).convert("RGB").save(f"{OUT}/capa.png")
    print("DUR", DUR, "T0", T0, "STEP", STEP, "TEND", TEND)
