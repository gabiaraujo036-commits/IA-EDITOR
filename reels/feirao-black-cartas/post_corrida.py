"""Post "ÚLTIMA VOLTA do Feirão Black": jogo de corrida com a cara da Mario Car.

Pista em perspectiva com zebra, carros recortados no grid de largada, semáforo da loja
e placas no estilo das placas de rua da Mario Car (preto, borda branca).
Uso: python3 post_corrida.py <pasta com recortes 1.png..6.png>  -> post-corrida-feed.png (1080x1350)
"""
import os, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__)); REC = sys.argv[1]
FD = "/usr/share/fonts/opentype/inter/"
def F(s, w="ExtraBold"): return ImageFont.truetype(f"{FD}Inter-{w}.otf", s)
RED, INK, ASF = (225, 30, 55), (8, 8, 10), (30, 30, 34)
W, H = 1080, 1350

def carro(n):
    im = Image.open(f"{REC}/{n}.png").convert("RGBA")
    a = im.getchannel("A").point(lambda v: 0 if v < 70 else min(255, int((v - 70) * 255 / 120)))
    im.putalpha(a); return im.crop(a.getbbox())
def ct(d, cx, y, t, f, fill="white"): d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)

def placa(txt, fs, sub=None, sub_fs=None, pad=(34, 16), cor_txt="white", cor_sub=(200, 200, 206)):
    """placa de rua no estilo Mario Car: fundo preto, filete branco por dentro."""
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    f = F(fs, "Black"); tw = tmp.textlength(txt, font=f); w = int(tw + 2 * pad[0]); h = int(fs * 1.05 + 2 * pad[1])
    if sub:
        fsub = F(sub_fs, "Bold"); w = max(w, int(tmp.textlength(sub, font=fsub) + 2 * pad[0])); h += int(sub_fs * 1.3)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    i = max(4, fs // 6); lw = 2 if fs < 30 else 3
    d.rounded_rectangle((8, 8, w + 8, h + 8), 8 + i, fill=(12, 12, 14))
    d.rounded_rectangle((8 + i, 8 + i, w + 8 - i, h + 8 - i), 4 + i // 2, outline="white", width=lw)
    y = 8 + pad[1] - fs * 0.08
    if sub: ct(d, (w + 16) / 2, y + 2, sub, fsub, fill=cor_sub); y += sub_fs * 1.3
    ct(d, (w + 16) / 2, y, txt, f, fill=cor_txt)
    return im

def sombra_de(im, k=18, o=0.75):
    return im.getchannel("A").point(lambda v: int(v * o)).filter(ImageFilter.GaussianBlur(k))

def cola(img, im, x, y, sombra=True):
    if sombra:  # sombra de contato embaixo das rodas
        sh = Image.new("L", (im.width + 80, 120), 0)
        ImageDraw.Draw(sh).ellipse((20, 30, im.width + 60, 90), fill=200)
        img.paste((0, 0, 0), (int(x) - 40, int(y + im.height - 75)), sh.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(im, (int(x), int(y)))

def semaforo(img, x, y, esc=1.0):
    w, h = int(120 * esc), int(330 * esc); r = int(42 * esc)
    lay = Image.new("RGBA", (w + 160, h + 160), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ox, oy = 80, 80
    d.rounded_rectangle((ox, oy, ox + w, oy + h), int(26 * esc), fill=(16, 16, 18), outline=(70, 70, 76), width=4)
    cores = [(RED, True), ((250, 190, 30), False), ((40, 200, 90), False)]
    for k, (c, aceso) in enumerate(cores):
        cx, cy = ox + w / 2, oy + int(60 * esc) + k * int(105 * esc)
        if aceso:
            g = Image.new("RGBA", lay.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((cx - r * 2.2, cy - r * 2.2, cx + r * 2.2, cy + r * 2.2), fill=c + (150,))
            lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(30 * esc)))
            d = ImageDraw.Draw(lay); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
            d.ellipse((cx - r * .45, cy - r * .6, cx - r * .05, cy - r * .2), fill=(255, 150, 160))
        else:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(int(v * .22) for v in c))
    img.alpha_composite(lay, (int(x - 80), int(y - 80)))

def pista(img, horiz=372, base=1035):
    d = ImageDraw.Draw(img)
    def borda(y):  # meia-largura da pista em cada altura
        t = (y - horiz) / (base - horiz); return 210 + t * 470
    d.polygon([(540 - borda(horiz), horiz), (540 + borda(horiz), horiz), (540 + borda(base), base), (540 - borda(base), base)], fill=ASF)
    # textura de asfalto
    rnd = random.Random(3); tex = Image.new("L", img.size, 0); td = ImageDraw.Draw(tex)
    for _ in range(9000):
        y = rnd.uniform(horiz, base); x = 540 + rnd.uniform(-1, 1) * borda(y); td.point((x, y), fill=rnd.randint(20, 70))
    img.paste((90, 90, 96), (0, 0), tex)
    # zebras e faixa central (espaçamento em perspectiva)
    ys = [horiz]; s = 14
    while ys[-1] < base: ys.append(min(base, ys[-1] + s)); s *= 1.16
    for k in range(len(ys) - 1):
        y0, y1 = ys[k], ys[k + 1]; cor = RED if k % 2 == 0 else (235, 235, 238)
        for lado in (-1, 1):
            a0, a1 = borda(y0), borda(y1); z0, z1 = a0 * .1, a1 * .1
            d.polygon([(540 + lado * a0, y0), (540 + lado * (a0 + z0), y0), (540 + lado * (a1 + z1), y1), (540 + lado * a1, y1)], fill=cor)
        if k % 2 == 0:
            for faixa in (-1 / 3, 1 / 3):
                c0, c1 = 540 + faixa * borda(y0), 540 + faixa * borda(y1); m0, m1 = borda(y0) * .015, borda(y1) * .015
                d.polygon([(c0 - m0, y0), (c0 + m0, y0), (c1 + m1, y1), (c1 - m1, y1)], fill=(200, 200, 205))
    # linha de largada quadriculada
    ya, yb = base - 62, base - 10; n = 22
    for lin, (y0, y1) in enumerate(((ya, (ya + yb) / 2), ((ya + yb) / 2, yb))):
        for k in range(n):
            if (k + lin) % 2: continue
            def px(y, t): return 540 - borda(y) + t * 2 * borda(y)
            d.polygon([(px(y0, k / n), y0), (px(y0, (k + 1) / n), y0), (px(y1, (k + 1) / n), y1), (px(y1, k / n), y1)], fill="white")
    return borda

def fundo():
    img = Image.new("RGBA", (W, H), INK + (255,))
    # luzes de estádio + brilho vermelho atrás do título
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse((-200, -300, W + 200, 460), fill=(130, 10, 28, 120))
    for x in (120, 960): gd.ellipse((x - 260, 250, x + 260, 520), fill=(255, 255, 255, 30))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(110)))
    return img

def feed():
    img = fundo()
    pista(img)
    # carros no grid (de trás pra frente)
    grid = [  # (foto, centro x, base y, largura)
        (1, 345, 590, 190), (5, 540, 582, 172), (6, 735, 590, 200),
        (3, 245, 770, 300), (4, 835, 770, 312),
        (2, 540, 990, 560),
    ]
    for n, cx, by, lw in grid:
        im = carro(n); im = im.resize((lw, int(im.height * lw / im.width)), Image.LANCZOS)
        cola(img, im, cx - lw / 2, by - im.height)
    d = ImageDraw.Draw(img)
    # placas com o nome de cada carro (estilo placa de rua)
    rot = {1: "C4 CACTUS", 5: "OROCH", 6: "ELANTRA", 3: "AIRCROSS 7", 4: "DUSTER"}
    for n, cx, by, lw in grid[:-1]:
        im = carro(n); top = by - int(im.height * lw / im.width)
        fs = 19 if by < 650 else 24
        p = placa(rot[n], fs, pad=(14, 6)); img.alpha_composite(p, (int(cx - p.width / 2), int(top - p.height + 2)))
    p = placa("NIVUS 2025/26", 34, sub="POLE POSITION", sub_fs=18, pad=(26, 10), cor_sub=RED)
    img.alpha_composite(p, (int(545 - p.width / 2), 1000 - 22))
    # cabeçalho: semáforo + ÚLTIMA VOLTA
    semaforo(img, 70, 52, esc=0.86)
    d = ImageDraw.Draw(img)
    d.text((222, 54), "FEIRÃO BLACK · MARIO CAR", font=F(30, "Bold"), fill=(205, 205, 212))
    d.text((214, 92), "ÚLTIMA", font=F(150, "Black"))
    d.text((214, 230), "VOLTA", font=F(150, "Black"), fill=RED)
    # poste com placas de rua (cara de Recife / Mario Car)
    d.rectangle((958, 150, 968, 372), fill=(90, 90, 96))
    for k, (t, fs) in enumerate((("MARCO ZERO", 24), ("OXE, CORRE!", 24))):
        p = placa(t, fs, pad=(14, 7), cor_txt="white" if k == 0 else RED)
        img.alpha_composite(p, (int(963 - p.width / 2), 170 + k * 66))
    d = ImageDraw.Draw(img)
    # oferta e chamada
    pl = placa("IPVA 2027 PAGO", 92, sub="COMPROU, GANHOU", sub_fs=34, pad=(48, 18))
    img.alpha_composite(pl, (int(W / 2 - pl.width / 2), 1072))
    d = ImageDraw.Draw(img)
    fb = F(36, "Black"); t = "É A ÚLTIMA SEMANA DO FEIRÃO!"; tw = d.textlength(t, font=fb) + 60
    d.rounded_rectangle((W / 2 - tw / 2, 1268, W / 2 + tw / 2, 1324), 28, fill=RED); ct(d, W / 2, 1276, t, fb)
    return img

if __name__ == "__main__":
    feed().convert("RGB").save(f"{AQUI}/post-corrida-feed.png")
