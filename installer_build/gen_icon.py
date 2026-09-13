"""
生成应用图标 app.ico
风格：深色主题（#1e1e2e 背景 + #cdd6f4 W 字母），与 main_gui.py 托盘图标一致
"""
from PIL import Image, ImageDraw, ImageFont

sizes = [256, 128, 64, 48, 32, 16]
images = []
for sz in sizes:
    img = Image.new('RGBA', (sz, sz), (30, 30, 46, 255))  # #1e1e2e
    draw = ImageDraw.Draw(img)
    # W 字母
    try:
        font = ImageFont.truetype('arial.ttf', int(sz * 0.6))
    except Exception:
        font = ImageFont.load_default()
    # 居中绘制 W
    bbox = draw.textbbox((0, 0), 'W', font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (sz - tw) // 2 - bbox[0]
    y = (sz - th) // 2 - bbox[1]
    draw.text((x, y), 'W', fill='#cdd6f4', font=font)  # #cdd6f4
    images.append(img)

# 保存为 ICO（多尺寸）
images[0].save(
    'app.ico',
    format='ICO',
    sizes=[(s, s) for s in sizes],
    append_images=images[1:]
)
print('图标生成完成: app.ico')
