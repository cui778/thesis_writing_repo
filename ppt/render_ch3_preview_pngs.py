from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"E:\11.16\thesis_writing_repo\ppt")
OUT = ROOT / "preview_ch3_midterm"
FIG = Path(r"E:\11.16\script2_new\chapter3_data_generation\figures")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
C = {
    "ink": "#172033",
    "muted": "#667085",
    "soft": "#F4F7FB",
    "blue": "#246BFE",
    "cyan": "#00A7C8",
    "green": "#16A36A",
    "amber": "#F59E0B",
    "red": "#E04F5F",
    "line": "#D8E0EA",
    "white": "#FFFFFF",
}

FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

def font(size, bold=False):
    p = FONT_BOLD if bold and Path(FONT_BOLD).exists() else FONT
    return ImageFont.truetype(p, size)

def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines

def draw_text(draw, xy, text, size, color=C["ink"], bold=False, max_w=None, line_gap=8):
    fnt = font(size, bold)
    x, y = xy
    if max_w:
        for line in wrap(draw, text, fnt, max_w):
            draw.text((x, y), line, font=fnt, fill=color)
            y += size + line_gap
        return y
    draw.text((x, y), text, font=fnt, fill=color)
    return y + size + line_gap

def fit_image(path, box):
    img = Image.open(path).convert("RGB")
    x, y, w, h = box
    img.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), "white")
    canvas.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return canvas

def paste_fig(slide, path, box):
    x, y, w, h = box
    slide.paste(fit_image(path, box), (x, y))

def title(draw, t):
    draw_text(draw, (86, 64), "第三部分", 22, C["blue"], True)
    draw_text(draw, (86, 102), t, 52, C["ink"], True)

def save(slide, idx):
    path = OUT / f"slide_{idx:02d}.png"
    slide.save(path)
    return path

paths = []

# 1
s = Image.new("RGB", (W, H), "#F8FBFF")
d = ImageDraw.Draw(s)
draw_text(d, (120, 170), "第三部分", 28, C["blue"], True)
draw_text(d, (120, 240), "基于 SWMM 的 I/E\n缺陷多场景数据生成", 68, C["ink"], True)
draw_text(d, (120, 460), "从工程资料与 SWMM 基线模型出发，批量生成可用于缺陷诊断的全网节点时序数据。", 28, C["muted"], max_w=900)
d.rectangle([120, 590, 400, 596], fill=C["blue"])
metrics = [("128", "全网节点", C["blue"]), ("50", "候选缺陷节点", C["green"]), ("25", "固定监测节点", C["cyan"]), ("421", "仿真场景", C["amber"])]
for i, (num, lab, col) in enumerate(metrics):
    x = 1180 + (i % 2) * 300
    y = 260 + (i // 2) * 240
    draw_text(d, (x, y), num, 72, col, True)
    draw_text(d, (x, y + 92), lab, 24, C["muted"])
paths.append(save(s, 1))

# 2
s = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(s); title(d, "研究子区与建模资料")
bullets = ["研究对象来自黄孝河-机场河流域水环境综合治理工程资料。", "依据排水分区、泵站服务范围、主干管连通关系和边界条件划定研究子区。", "资料包括管网、泵站、闸门、调蓄池、河道、污水处理厂、降雨与调度运行资料。", "现场水位、流量及 NH4、TSSs 等指标用于正常工况合理性检查。"]
y = 230
for b in bullets:
    d.text((96, y), "•", font=font(28, True), fill=C["blue"])
    y = draw_text(d, (130, y), b, 25, C["ink"], max_w=710) + 10
paste_fig(s, FIG / "fig3_1_network_candidate_monitor_map.png", (930, 210, 880, 620))
draw_text(d, (930, 850), "可替换：更适合答辩的黄孝河-机场河研究子区边界图。", 20, C["red"])
paths.append(save(s, 2))

# 3
s = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(s); title(d, "SWMM 基线模型构建")
steps = ["资料整理", "数据清理", "子区划分", "DWF注入", "结构修复", "边界设置", "正常工况"]
for i, st in enumerate(steps):
    x = 86 + i * 124
    d.rounded_rectangle([x, 210, x+112, 288], radius=10, fill="#E8F1FF" if st=="DWF注入" else C["soft"])
    draw_text(d, (x+13, 235), st, 18, C["blue"] if st=="DWF注入" else C["ink"], True)
draw_text(d, (86, 340), "模型目标：可独立运行、可批量注入缺陷、可输出节点级水力与水质响应。", 28, C["ink"], True, max_w=850)
rows = [("全网节点", "128", "图结构表达与仿真输出范围"), ("Junction", "113", "普通连接节点"), ("Outfall", "2", "出流边界节点"), ("Storage", "13", "蓄水或调蓄单元"), ("Conduit", "137", "管段数量")]
y = 470
for r in rows:
    draw_text(d, (110, y), r[0], 22); draw_text(d, (330, y), r[1], 22, C["blue"], True); draw_text(d, (470, y), r[2], 22)
    y += 54
d.rounded_rectangle([1080, 250, 1780, 790], radius=16, fill="#EEF4FF", outline="#B8C7E6", width=3)
draw_text(d, (1130, 330), "图件占位", 34, C["blue"], True)
draw_text(d, (1130, 400), "建议补图：SWMM GUI 中研究子区模型截图，或 DWF / TIMESERIES 设置界面截图。", 25, C["ink"], max_w=580)
paths.append(save(s, 3))

# 4
s = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(s); title(d, "I/E 缺陷场景矩阵设计")
rows = [("正常工况", "1", "无缺陷参照"), ("I 类渗入", "250", "覆盖 50 个候选节点"), ("E 类渗漏", "170", "覆盖 34 个合法节点"), ("合计", "421", "正常工况 + IE420")]
y = 230
for r in rows:
    draw_text(d, (100, y), r[0], 24); draw_text(d, (330, y), r[1], 30, C["blue"], True); draw_text(d, (470, y), r[2], 24)
    y += 70
for b in ["I 类：正向入流扰动，模拟外来水进入管网。", "E 类：负向流量扰动，模拟管网水量向外损失。", "全网拓扑保留 128 节点，诊断范围限定在 50 个候选缺陷节点。", "25 个固定监测节点用于模拟有限传感器观测条件。"]:
    d.text((100, y), "•", font=font(26, True), fill=C["green"])
    y = draw_text(d, (135, y), b, 23, C["ink"], max_w=650) + 12
paste_fig(s, FIG / "fig3_2_ie_matrix_distribution.png", (930, 220, 850, 620))
paths.append(save(s, 4))

# 5
s = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(s); title(d, "PySWMM 批量仿真与节点时序输出")
paste_fig(s, FIG / "fig3_3_swmm_data_generation_flow.png", (90, 210, 820, 620))
y = 220
for b in ["读取 baseline INP 与 IE420 缺陷矩阵。", "逐场景启动 PySWMM 仿真。", "依据 start_hour 与 duration_h 控制缺陷活跃期。", "通过 generated_inflow(flow) 动态注入 I/E 异常流量。", "每 10 min 固定采样一次，保证所有场景时间对齐。"]:
    d.text((1010, y), "•", font=font(26, True), fill=C["cyan"])
    y = draw_text(d, (1045, y), b, 23, C["ink"], max_w=720) + 10
for num, lab in [("421", "全部场景"), ("287", "每场景时间点"), ("10 min", "采样间隔"), ("36736", "每场景记录")]:
    draw_text(d, (1040, y+20), num, 42, C["cyan"], True); draw_text(d, (1240, y+32), lab, 22, C["muted"])
    y += 72
paths.append(save(s, 5))

# 6
s = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(s); title(d, "数据特征构建与有效性检查")
y = 220
for b in ["保留全网 128 节点原始水力水质时序。", "构造 residual 派生特征。", "核心水力特征：depth、total_outflow。", "水质伴随特征：NH4、TSSs。", "检查场景完整性、时间步一致性、节点覆盖性。"]:
    d.text((100, y), "•", font=font(26, True), fill=C["blue"])
    y = draw_text(d, (135, y), b, 23, C["ink"], max_w=620) + 12
paste_fig(s, FIG / "fig3_6_active_inactive_residual_energy_boxplot.png", (820, 185, 900, 410))
paste_fig(s, FIG / "fig3_5a_I_typical_residual_curve.png", (820, 640, 430, 250))
paste_fig(s, FIG / "fig3_5b_E_typical_residual_curve.png", (1290, 640, 430, 250))
paths.append(save(s, 6))

print("\n".join(str(p) for p in paths))
