"""Post estático do Feirão Black: destaque em ÚLTIMA SEMANA + leque com as cartas dos carros.

Uso: python3 post.py  (lê cartas/carta-XX.png desta pasta; gera post-feed.png 1080x1350 e post-story.png 1080x1920)
"""
import os, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

AQUI = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/opentype/inter/"
def F(s, w="ExtraBold"): return ImageFont.truetype(f"{FD}Inter-{w}.otf", s)
RED, RED2, INK = (225, 30, 55), (150, 10, 30), (10, 10, 12)
CARTAS = [Image.open(p).convert("RGBA") for p in sorted(glob.glob(f"{AQUI}/cartas/carta-*.png"))]

def ct(d, cx, y, t, f, fill="white"): d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)
def ct_esp(d, cx, y, t, f, fill="white", esp=0):
    w = sum(d.textlength(ch, font=f) for ch in t) + esp * (len(t) - 1); x = cx - w / 2
    for ch in t: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + esp

def fundo(W, H, cy):
    img = Image.new("RGB", (W, H), (8, 8, 10))
    glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((-300, cy - 420, W + 300, cy + 420), fill=255)
    img = Image.composite(Image.new("RGB", (W, H), (110, 10, 25)), img, glow.filter(ImageFilter.GaussianBlur(200)).point(lambda v: int(v * .55)))
    st = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(st)
    for k in range(-8, 16):
        x = k * 150; sd.polygon([(x, 0), (x + 36, 0), (x + 36 - H, H), (x - H, H)], fill=255)
    fm = Image.linear_gradient("L").resize((W, H)).point(lambda v: (255 - v) // 5)
    return Image.composite(Image.new("RGB", (W, H), (30, 30, 36)), img, ImageChops.multiply(st, fm)).convert("RGBA")

def fita(img, y, texto, ang=-4, alt=78, fs=44):
    """faixa vermelha atravessando a arte, tipo fita de aviso."""
    W = img.width; lay = Image.new("RGBA", (W + 400, alt), RED); d = ImageDraw.Draw(lay)
    unid = f"{texto}   •   "; f = F(fs, "Black"); x = -40
    while x < lay.width: d.text((x, (alt - fs) // 2 - 6), unid, font=f, fill="white"); x += d.textlength(unid, font=f)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(lay, (-200, int(y - lay.height / 2)))

def leque(img, cx, cy, escala, abre=118, giro=8):
    n = len(CARTAS)
    for k, c in enumerate(CARTAS):
        m = k - (n - 1) / 2
        w, h = int(c.width * escala), int(c.height * escala)
        im = c.resize((w, h), Image.LANCZOS).rotate(-m * giro, expand=True, resample=Image.BICUBIC)
        x = cx + m * abre; y = cy + abs(m) ** 2 * 9
        sh = im.getchannel("A").point(lambda v: int(v * .7)).filter(ImageFilter.GaussianBlur(14))
        img.paste((0, 0, 0), (int(x - im.width / 2 + 10), int(y - im.height / 2 + 22)), sh)
        img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

def oferta(img, cy, larg=900):
    W = img.width; d = ImageDraw.Draw(img)
    x0, x1 = (W - larg) // 2, (W + larg) // 2
    d.rounded_rectangle((x0, cy, x1, cy + 200), 36, fill=(16, 16, 18), outline=RED, width=5)
    ct(d, W / 2, cy + 22, "COMPROU, GANHOU", F(44, "Bold"), fill=(210, 210, 215))
    f = F(104, "Black"); t1, t2 = "IPVA 2027 ", "PAGO"
    w = d.textlength(t1 + t2, font=f); x = W / 2 - w / 2
    d.text((x, cy + 70), t1, font=f, fill="white"); d.text((x + d.textlength(t1, font=f), cy + 70), t2, font=f, fill=RED)

def cta(img, cy, txt="CHAMA NO DIRECT"):
    W = img.width; d = ImageDraw.Draw(img); f = F(48, "Black")
    w = d.textlength(txt, font=f) + 110
    d.rounded_rectangle((W / 2 - w / 2, cy, W / 2 + w / 2, cy + 92), 46, fill=RED)
    ct(d, W / 2, cy + 18, txt, f)

def titulo(img, y, tam=196):
    d = ImageDraw.Draw(img); W = img.width
    ct_esp(d, W / 2, y, "FEIRÃO BLACK · MARIO CAR", F(36, "Bold"), fill=(200, 200, 206), esp=6)
    ct(d, W / 2, y + 50, "ÚLTIMA", F(tam, "Black"))
    ct(d, W / 2, y + 50 + tam * 0.95, "SEMANA", F(tam, "Black"), fill=RED)

def feed():
    W, H = 1080, 1350; img = fundo(W, H, 720)
    titulo(img, 52, 190)
    leque(img, 540, 725, 0.31, abre=122, giro=7)
    fita(img, 950, "ÚLTIMA SEMANA DO FEIRÃO BLACK", ang=-2.5, alt=64, fs=36)
    oferta(img, 1015)
    d = ImageDraw.Draw(img)
    ct(d, W / 2, 1238, "Chama no direct e garanta o seu!", F(40, "Bold"))
    ct(d, W / 2, 1300, "*Consulte condições na loja.", F(26, "Medium"), fill=(160, 160, 168))
    return img

def story():
    W, H = 1080, 1920; img = fundo(W, H, 960)
    titulo(img, 170, 200)
    fita(img, 680, "CORRE QUE ACABA", ang=-4, alt=72, fs=40)
    leque(img, 540, 1010, 0.36, abre=128, giro=8)
    oferta(img, 1330)
    cta(img, 1600)
    ct(ImageDraw.Draw(img), W / 2, 1730, "*Consulte condições na loja.", F(28, "Medium"), fill=(160, 160, 168))
    return img

if __name__ == "__main__":
    feed().convert("RGB").save(f"{AQUI}/post-feed.png")
    story().convert("RGB").save(f"{AQUI}/post-story.png")
