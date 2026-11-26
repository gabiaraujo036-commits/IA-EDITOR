"""Post estático do Feirão Black (feed 1080x1350): carros em destaque + ÚLTIMA SEMANA + IPVA 2027 pago.

Uso: python3 post.py <pasta com 1.webp..6.webp>
Gera post-feed-a.png (um carro em destaque + vitrine dos outros) e post-feed-b.png (grade com os 6).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__)); FOTOS = sys.argv[1]
FD = "/usr/share/fonts/opentype/inter/"
def F(s, w="ExtraBold"): return ImageFont.truetype(f"{FD}Inter-{w}.otf", s)
RED, INK = (225, 30, 55), (8, 8, 10)
W, H = 1080, 1350

CARROS = [  # (foto, nome curto, linha de info)
    (1, "C4 CACTUS", "2022/22 · Automático"),
    (2, "NIVUS", "2025/26 · 12.000 km · Automático"),
    (3, "AIRCROSS 7", "2024/25 · 7 lugares"),
    (4, "DUSTER", "2021/22 · Automático"),
    (5, "OROCH", "2023/24 · Picape"),
    (6, "ELANTRA", "2016/17 · Automático"),
]
def foto(n): return Image.open(f"{FOTOS}/{n}.webp").convert("RGB")
def recorte(im, w, h, cx=600, cy=540, largura=1000):
    """mesma proporção do espaço: só reduz, não deforma."""
    ch = largura * h / w
    if ch > im.height: ch = im.height; largura = ch * w / h
    x0 = max(0, min(im.width - largura, cx - largura / 2)); y0 = max(0, min(im.height - ch, cy - ch / 2))
    return im.crop((int(x0), int(y0), int(x0 + largura), int(y0 + ch))).resize((w, h), Image.LANCZOS)
def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
def ct(d, cx, y, t, f, fill="white"): d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)
def ct_esp(d, cx, y, t, f, fill="white", esp=0):
    w = sum(d.textlength(ch, font=f) for ch in t) + esp * (len(t) - 1); x = cx - w / 2
    for ch in t: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + esp
def fade(img, box, de_cima=True, cor=INK):
    x0, y0, x1, y1 = box; g = Image.linear_gradient("L").resize((x1 - x0, y1 - y0))
    if de_cima: g = g.transpose(Image.FLIP_TOP_BOTTOM)
    img.paste(cor, box, g)
def fita_canto(img, x1, y0, texto="IPVA 2027 PAGO", fs=38, alt=78, desloc=125):
    rib = Image.new("RGBA", (760, alt), RED); rd = ImageDraw.Draw(rib)
    ct(rd, 380, (alt - fs) // 2 - 6, texto, F(fs, "Black"))
    rib = rib.rotate(-38, expand=True, resample=Image.BICUBIC)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lay.paste(rib, (x1 - rib.width // 2 - desloc, y0 - rib.height // 2 + desloc), rib)
    return lay
def cabecalho(d, y=34, tam=110):
    ct_esp(d, W / 2, y, "FEIRÃO BLACK · MARIO CAR", F(32, "Bold"), fill=(195, 195, 202), esp=6)
    f = F(tam, "Black"); t1, t2 = "ÚLTIMA ", "SEMANA"; w = d.textlength(t1 + t2, font=f); x = W / 2 - w / 2
    d.text((x, y + 40), t1, font=f, fill="white"); d.text((x + d.textlength(t1, font=f), y + 40), t2, font=f, fill=RED)
def oferta(d, y, alt=160):
    d.rounded_rectangle((60, y, W - 60, y + alt), 30, fill=(18, 18, 20), outline=RED, width=4)
    ct(d, W / 2, y + 16, "COMPROU, GANHOU", F(36, "Bold"), fill=(205, 205, 212))
    f = F(86, "Black"); t1, t2 = "IPVA 2027 ", "PAGO"; w = d.textlength(t1 + t2, font=f); x = W / 2 - w / 2
    d.text((x, y + 58), t1, font=f, fill="white"); d.text((x + d.textlength(t1, font=f), y + 58), t2, font=f, fill=RED)
def rodape(d, y):
    ct(d, W / 2, y, "Chama no direct e garanta o seu!", F(38, "Bold"))
    ct(d, W / 2, y + 52, "*Consulte condições na loja.", F(24, "Medium"), fill=(150, 150, 158))

# ---------- A: um carro em destaque + vitrine ----------
def opcao_a(destaque=2):
    img = Image.new("RGB", (W, H), INK)
    HY, HH = 214, 640
    hero = recorte(foto(destaque), W, HH, cy=520, largura=1152)
    img.paste(hero, (0, HY)); fade(img, (0, HY, W, HY + 90)); fade(img, (0, HY + HH - 260, W, HY + HH), de_cima=False)
    img = img.convert("RGBA")
    fita = fita_canto(img, W, HY, desloc=150)
    corte = Image.new("L", img.size, 0); corte.paste(255, (0, HY, W, HY + HH))
    from PIL import ImageChops
    fita.putalpha(ImageChops.multiply(fita.getchannel("A"), corte)); img.alpha_composite(fita)
    d = ImageDraw.Draw(img, "RGBA")
    cabecalho(d)
    n, nome, info = CARROS[destaque - 1]
    d.text((50, HY + HH - 190), "VOLKSWAGEN", font=F(30, "Bold"), fill=RED)
    d.text((44, HY + HH - 160), nome, font=F(120, "Black"))
    d.text((50, HY + HH - 26), info, font=F(32, "SemiBold"), fill=(215, 215, 222))
    # vitrine dos outros
    outros = [c for c in CARROS if c[0] != destaque]
    gap, x0, ty = 12, 40, HY + HH + 46
    tw = (W - 2 * x0 - gap * (len(outros) - 1)) // len(outros); th = 128
    for k, (fn, nm, _) in enumerate(outros):
        x = x0 + k * (tw + gap)
        im = recorte(foto(fn), tw, th, largura=1000)
        img.paste(im, (x, ty), rmask(tw, th, 16))
        d.rounded_rectangle((x, ty, x + tw - 1, ty + th - 1), 16, outline=(255, 255, 255, 50), width=2)
        f = F(24, "ExtraBold");
        while d.textlength(nm, font=f) > tw - 8: f = F(f.size - 2, "ExtraBold")
        ct(d, x + tw / 2, ty + th + 8, nm, f)
    oferta(d, ty + th + 56)
    rodape(d, ty + th + 56 + 178)
    return img

# ---------- B: grade com os 6 ----------
def opcao_b():
    img = Image.new("RGBA", (W, H), INK + (255,)); d = ImageDraw.Draw(img, "RGBA")
    cabecalho(d)
    gx, gy, gap = 40, 224, 14
    cw = (W - 2 * gx - gap) // 2; ch = 262
    for k, (fn, nm, info) in enumerate(CARROS):
        x = gx + (k % 2) * (cw + gap); y = gy + (k // 2) * (ch + gap)
        im = recorte(foto(fn), cw, ch, cy=560, largura=1000)
        fade(im, (0, ch - 120, cw, ch), de_cima=False)
        img.paste(im, (x, y), rmask(cw, ch, 20))
        d.rounded_rectangle((x, y, x + cw - 1, y + ch - 1), 20, outline=(255, 255, 255, 45), width=2)
        d.text((x + 20, y + ch - 78), nm, font=F(40, "Black"))
        d.text((x + 22, y + ch - 32), info.split(" · ")[0], font=F(24, "SemiBold"), fill=RED)
    y = gy + 3 * ch + 2 * gap + 24
    oferta(d, y)
    rodape(d, y + 178)
    # selo
    lay = fita_canto(img, W, 0, texto="ÚLTIMA SEMANA", fs=34, alt=70, desloc=95)
    return img

if __name__ == "__main__":
    opcao_a().convert("RGB").save(f"{AQUI}/post-feed-a.png")
    opcao_b().convert("RGB").save(f"{AQUI}/post-feed-b.png")
