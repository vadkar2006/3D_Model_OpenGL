# -*- coding: utf-8 -*-
"""Схемы для документации (PIL) с автоматической высотой блоков."""
import math
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "assets")
os.makedirs(OUT, exist_ok=True)
FD = r"C:\Windows\Fonts"

F_BODY = ImageFont.truetype(os.path.join(FD, "arial.ttf"), 26)
F_SMALL = ImageFont.truetype(os.path.join(FD, "arial.ttf"), 22)
F_HUGE = ImageFont.truetype(os.path.join(FD, "arialbd.ttf"), 46)

INK = (22, 30, 44)
MUTED = (88, 100, 118)
LINE = (142, 156, 176)

C_CPU = ((226, 236, 249), (52, 92, 156))
C_GPU = ((222, 242, 231), (28, 120, 74))
C_OUT = ((238, 238, 242), (108, 114, 130))
C_AUX = ((255, 242, 221), (176, 116, 18))
C_SIM = ((240, 231, 248), (102, 58, 148))


def font(size, bold=True):
    return ImageFont.truetype(os.path.join(FD, "arialbd.ttf" if bold else "arial.ttf"), size)


def wrap(draw, text, f, maxw):
    out = []
    for chunk in text.split("\n"):
        cur = ""
        for w in chunk.split():
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= maxw or not cur:
                cur = t
            else:
                out.append(cur)
                cur = w
        if cur:
            out.append(cur)
    return out


def measure(draw, w, title, body, title_size=38, pad=18):
    tf = font(title_size)
    tl = wrap(draw, title, tf, w - 34)
    bl = wrap(draw, body, F_BODY, w - 34) if body else []
    h = pad * 2 + len(tl) * (tf.size + 6) + (10 if bl else 0) + len(bl) * (F_BODY.size + 6)
    return max(h, 110), tf, tl, bl


def box(draw, x, y, w, h, title, body, colors, title_size=38, pad=18):
    fill, stroke = colors
    draw.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=fill, outline=stroke, width=3)
    tf = font(title_size)
    tl = wrap(draw, title, tf, w - 34)
    bl = wrap(draw, body, F_BODY, w - 34) if body else []
    content = len(tl) * (tf.size + 6) + (10 if bl else 0) + len(bl) * (F_BODY.size + 6)
    cy = y + max(pad, (h - content) / 2)
    for line in tl:
        draw.text((x + w / 2, cy), line, font=tf, fill=INK, anchor="ma")
        cy += tf.size + 6
    if bl:
        cy += 10
    for line in bl:
        draw.text((x + w / 2, cy), line, font=F_BODY, fill=MUTED, anchor="ma")
        cy += F_BODY.size + 6
    return (x, y, w, h)


def head(draw, p1, p2, color, width):
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    L, W = 19, 8
    bx, by = p2[0] - L * math.cos(ang), p2[1] - L * math.sin(ang)
    draw.polygon([(p2[0], p2[1]),
                  (bx - W * math.sin(ang), by + W * math.cos(ang)),
                  (bx + W * math.sin(ang), by - W * math.cos(ang))], fill=color)


def arrow(draw, p1, p2, color=LINE, width=4, label=None, label_dy=-34):
    draw.line([p1, p2], fill=color, width=width)
    head(draw, p1, p2, color, width)
    if label:
        mx = (p1[0] + p2[0]) / 2
        draw.text((mx, min(p1[1], p2[1]) + label_dy), label, font=F_SMALL, fill=MUTED, anchor="ma")


def canvas(w, h):
    img = Image.new("RGB", (w, h), (255, 255, 255))
    return img, ImageDraw.Draw(img)


def title_block(d, text, sub):
    d.text((50, 26), text, font=F_HUGE, fill=INK)
    d.text((50, 86), sub, font=F_BODY, fill=MUTED)


# ------------------------------------------------------------------ 1
def diagram_pipeline():
    W = 1840
    img, d = canvas(W, 2400)
    title_block(d, "Поток данных одного кадра",
                "CPU (C++) → GPU (OpenGL 4.6): один draw call, камера считается в compute-шейдере")

    w, gap, y1 = 310, 47, 150
    x = [50 + i * (w + gap) for i in range(5)]
    top = [
        ("main.cpp", "сцена: 2 модели, конвейер, цикл кадра", C_CPU),
        ("Figure_Conveyor", "VBO + EBO + SSBO 1 (матрицы фигур)", C_CPU),
        ("Vertex Shader", "мировые координаты и clip space", C_GPU),
        ("Fragment Shader", "цвет фрагмента: пока без текстур", C_GPU),
        ("Framebuffer", "glfwSwapBuffers → окно", C_OUT),
    ]
    hs = [measure(d, w, t, b)[0] for t, b, _ in top]
    ht = max(hs)
    for i, (t, b, c) in enumerate(top):
        box(d, x[i], y1, w, ht, t, b, c, title_size=30)
    for i in range(4):
        arrow(d, (x[i] + w + 8, y1 + ht / 2), (x[i + 1] - 8, y1 + ht / 2))

    y2 = y1 + ht + 240
    bot = [
        ("Camera (C++)", "ввод: WASD, мышь, Q/E, Space", C_AUX),
        ("Camera_Shader", "compute 1×1×1: Грама–Шмидт, движение", C_SIM),
        ("SSBO 0", "vec3[4]: позиция и базис камеры", C_AUX),
    ]
    hb = max(measure(d, w, t, b)[0] for t, b, _ in bot)
    for i, (t, b, c) in enumerate(bot):
        box(d, x[i], y2, w, hb, t, b, c, title_size=30)

    arrow(d, (x[0] + w + 8, y2 + hb / 2), (x[1] - 8, y2 + hb / 2), label="uniforms", label_dy=-150)
    arrow(d, (x[1] + w + 8, y2 + hb / 2), (x[2] - 8, y2 + hb / 2), label="запись", label_dy=-150)
    arrow(d, (x[2] + w / 2, y2 - 12), (x[2] + w / 2, y1 + ht + 12))

    H = y2 + hb + 90
    img = img.crop((0, 0, W, H))
    d = ImageDraw.Draw(img)
    d.text((50, y2 + hb + 26),
           "Барьер между compute и vertex: glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT).",
           font=F_BODY, fill=MUTED)
    img.save(os.path.join(OUT, "pipeline.png"))


# ------------------------------------------------------------------ 2
def diagram_modules():
    W = 1840
    img, d = canvas(W, 2400)
    title_block(d, "Карта модулей проекта",
                "Связи — через #include и общие GL-объекты; отдельных .cpp, кроме main.cpp, нет")

    box(d, 520, 140, 800, 130, "main.cpp", "точка входа: окно, сцена, цикл кадра", C_CPU)

    w2, gap2, y2 = 390, 60, 380
    xs = [50 + i * (w2 + gap2) for i in range(4)]
    row2 = [
        ("Camera.h", "окно GLFW 4.6, ввод, Step_Frame", C_CPU),
        ("Shader_Compilation.h", "чтение .glsl, компиляция, линковка", C_CPU),
        ("Figure_Conveyor.h", "vec3, Figure, конвейер, буферы GPU", C_CPU),
        ("NVIDIA.h", "NvOptimusEnablement", C_AUX),
    ]
    h2 = max(measure(d, w2, t, b, 34)[0] for t, b, _ in row2)
    for i, (t, b, c) in enumerate(row2):
        box(d, xs[i], y2, w2, h2, t, b, c, title_size=34)
        arrow(d, (920, 278), (xs[i] + w2 / 2, y2 - 10))

    y3 = y2 + h2 + 110
    row3 = [
        ("Shaders/*.glsl", "вершинный, фрагментный, 2 compute", C_GPU),
        ("Texture/*", "модели и текстуры (LFS-указатели)", C_OUT),
        ("Image/stb_image.h", "загрузка PNG/JPG (v2.30)", C_OUT),
        ("external/", "GLFW 3.5 + GLAD (GL 4.6 core)", C_OUT),
    ]
    h3 = max(measure(d, w2, t, b, 34)[0] for t, b, _ in row3)
    for i, (t, b, c) in enumerate(row3):
        box(d, xs[i], y3, w2, h3, t, b, c, title_size=34)
        arrow(d, (xs[i] + w2 / 2, y2 + h2 + 10), (xs[i] + w2 / 2, y3 - 10))

    y4 = y3 + h3 + 90
    box(d, 520, y4, 800, 110, "Figure_Conveyor.h → GL",
        "VBO: 10 float/вершина · EBO: uint32 · SSBO 1", C_SIM, title_size=32)
    arrow(d, (920, y3 + h3 + 10), (920, y4 - 10))

    img = img.crop((0, 0, W, y4 + 130))
    img.save(os.path.join(OUT, "modules.png"))


# ------------------------------------------------------------------ 3
def diagram_layers():
    W = 1840
    img, d = canvas(W, 2400)
    title_block(d, "Целевая слоистая архитектура",
                "Зависимости направлены вниз: верхний слой знает о нижнем, но не наоборот")

    x, w = 120, 1080
    layers = [
        ("App / Editor / Tools", "сценарии, ImGui, горячая перезагрузка, экспорт", C_CPU),
        ("Scene", "узлы, трансформации, компоненты, сериализация JSON", C_CPU),
        ("Renderer", "батчинг, материалы, свет, тени, пост-обработка", C_GPU),
        ("GPU Device", "Buffer, Texture, Pipeline, CommandList, RAII", C_GPU),
        ("Foundation", "math, лог, assert, время, файлы, профилировщик", C_OUT),
    ]
    y = 150
    for i, (t, b, c) in enumerate(layers):
        hh = measure(d, w, t, b)[0]
        box(d, x, y, w, hh, t, b, c)
        if i:
            arrow(d, (x + w / 2, y - 52), (x + w / 2, y - 8))
        y += hh + 60

    y_assets = 370
    box(d, 1330, y_assets, 450, 180, "Assets", "импорт OBJ/PNG, кэш, hot reload, ссылки по id",
        C_AUX, title_size=34)
    box(d, 1330, 640, 450, 180, "Simulation", "fixed step, задачи на compute, снапшоты",
        C_SIM, title_size=34)
    arrow(d, (1330, y_assets + 90), (1212, y_assets + 90))
    arrow(d, (1330, 730), (1212, 730))

    img = img.crop((0, 0, W, y + 60))
    d = ImageDraw.Draw(img)
    d.text((50, y + 10), "Правило: Scene не вызывает gl* напрямую, Renderer не знает про window.",
           font=F_BODY, fill=MUTED)
    img.save(os.path.join(OUT, "layers.png"))


# ------------------------------------------------------------------ 4
def diagram_frame():
    W = 1840
    img, d = canvas(W, 2400)
    title_block(d, "Порядок работ в кадре (целевой)",
                "Явные фазы вместо одного Step_Frame: проще профилировать и расширять")

    names = [
        ("1. Input", "события и состояние"),
        ("2. Simulate", "фиксированный шаг"),
        ("3. Cull", "frustum + LOD"),
        ("4. Passes", "shadow → opaque → transparent"),
        ("5. Post", "tonemap, FXAA, UI"),
    ]
    w, y = 300, 190
    gap = (W - 100 - w * len(names)) / (len(names) - 1)
    hs = [measure(d, w, t, b, 30)[0] for t, b in names]
    h = max(hs)
    xs = []
    for i, (t, b) in enumerate(names):
        x = 50 + i * (w + gap)
        xs.append(x)
        box(d, x, y, w, h, t, b, C_GPU if i == 3 else C_CPU, title_size=30)
        if i:
            arrow(d, (xs[i - 1] + w + 8, y + h / 2), (x - 8, y + h / 2))

    img = img.crop((0, 0, W, y + h + 100))
    d = ImageDraw.Draw(img)
    d.text((50, y + h + 30), "Каждая фаза — отдельный список команд; ресурсы передаются по именам.",
           font=F_BODY, fill=MUTED)
    img.save(os.path.join(OUT, "frame.png"))


if __name__ == "__main__":
    diagram_pipeline()
    diagram_modules()
    diagram_layers()
    diagram_frame()
    print("ok")
