import {
  Presentation,
  PresentationFile,
  row,
  column,
  grid,
  layers,
  panel,
  text,
  image,
  shape,
  rule,
  fill,
  hug,
  fixed,
  wrap,
  grow,
  fr,
} from 'file:///C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import { readFileSync } from 'node:fs';

const OUT = 'E:/11.16/thesis_writing_repo/ppt/ch3_midterm_swmm_data_generation.pptx';
const FIG = 'E:/11.16/script2_new/chapter3_data_generation/figures';
const dataUrl = (path) => `data:image/png;base64,${readFileSync(path).toString('base64')}`;
const BLOB = {
  network: dataUrl(`${FIG}/fig3_1_network_candidate_monitor_map.png`),
  matrix: dataUrl(`${FIG}/fig3_2_ie_matrix_distribution.png`),
  flow: dataUrl(`${FIG}/fig3_3_swmm_data_generation_flow.png`),
  box: dataUrl(`${FIG}/fig3_6_active_inactive_residual_energy_boxplot.png`),
  curveI: dataUrl(`${FIG}/fig3_5a_I_typical_residual_curve.png`),
  curveE: dataUrl(`${FIG}/fig3_5b_E_typical_residual_curve.png`),
};

const W = 1920;
const H = 1080;
const C = {
  ink: '#172033',
  muted: '#667085',
  soft: '#F4F7FB',
  blue: '#246BFE',
  cyan: '#00A7C8',
  green: '#16A36A',
  amber: '#F59E0B',
  red: '#E04F5F',
  line: '#D8E0EA',
  white: '#FFFFFF',
};

const deck = Presentation.create({ slideSize: { width: W, height: H } });

function title(textValue, kicker = '第三部分') {
  return column({ name: 'title-stack', width: fill, height: hug, gap: 12 }, [
    text(kicker, {
      name: 'kicker',
      width: fill,
      height: hug,
      style: { fontSize: 22, bold: true, color: C.blue, fontFace: 'Microsoft YaHei' },
    }),
    text(textValue, {
      name: 'title',
      width: fill,
      height: hug,
      style: { fontSize: 52, bold: true, color: C.ink, fontFace: 'Microsoft YaHei' },
    }),
  ]);
}

function smallNote(value) {
  return text(value, {
    name: 'note',
    width: fill,
    height: hug,
    style: { fontSize: 18, color: C.muted, fontFace: 'Microsoft YaHei' },
  });
}

function bulletList(items, options = {}) {
  return column({ name: options.name || 'bullets', width: fill, height: hug, gap: 18 }, items.map((item, i) =>
    row({ name: `bullet-${i}`, width: fill, height: hug, gap: 14 }, [
      text('•', { name: `dot-${i}`, width: fixed(20), height: hug, style: { fontSize: 26, bold: true, color: options.color || C.blue } }),
      text(item, { name: `bullet-text-${i}`, width: fill, height: hug, style: { fontSize: options.fontSize || 25, color: C.ink, fontFace: 'Microsoft YaHei' } }),
    ])
  ));
}

function metric(num, label, color = C.blue) {
  return column({ name: `metric-${label}`, width: fill, height: hug, gap: 8 }, [
    text(num, { name: `metric-num-${label}`, width: fill, height: hug, style: { fontSize: 64, bold: true, color, fontFace: 'Arial' } }),
    text(label, { name: `metric-label-${label}`, width: fill, height: hug, style: { fontSize: 20, color: C.muted, fontFace: 'Microsoft YaHei' } }),
  ]);
}

function tableRows(rows, colWidths, opts = {}) {
  return column({ name: opts.name || 'table', width: fill, height: hug, gap: 0 }, rows.map((r, i) =>
    row({ name: `tr-${i}`, width: fill, height: hug, gap: 0 }, r.map((cell, j) =>
      text(cell, {
        name: `td-${i}-${j}`,
        width: fixed(colWidths[j]),
        height: fixed(i === 0 ? 46 : 42),
        style: {
          fontSize: i === 0 ? 19 : 18,
          bold: i === 0,
          color: i === 0 ? C.white : C.ink,
          fill: i === 0 ? opts.header || C.ink : (i % 2 ? '#F8FAFC' : C.white),
          fontFace: 'Microsoft YaHei',
        },
        margin: { x: 10, y: 8 },
      })
    ))
  ));
}

function imagePanel(source, alt, caption) {
  return column({ name: 'image-panel', width: fill, height: fill, gap: 10 }, [
    image({ name: 'image', dataUrl: source, width: fill, height: grow(1), fit: 'contain', alt }),
    text(caption, { name: 'caption', width: fill, height: hug, style: { fontSize: 17, color: C.muted, fontFace: 'Microsoft YaHei' } }),
  ]);
}

function placeholder(label) {
  return panel({ name: 'placeholder', width: fill, height: fill, padding: 28, fill: '#EEF4FF', border: { color: '#B8C7E6', width: 2 }, borderRadius: 10 },
    column({ width: fill, height: fill, gap: 18 }, [
      text('图件占位', { width: fill, height: hug, style: { fontSize: 30, bold: true, color: C.blue, fontFace: 'Microsoft YaHei' } }),
      text(label, { width: fill, height: hug, style: { fontSize: 24, color: C.ink, fontFace: 'Microsoft YaHei' } }),
      text('建议：使用 SWMM GUI 截图、研究区边界图或管网拓扑图替换。', { width: fill, height: hug, style: { fontSize: 19, color: C.muted, fontFace: 'Microsoft YaHei' } }),
    ])
  );
}

function addSlide(rootChildren, bg = C.white) {
  const s = deck.slides.add();
  s.compose(
    layers({ name: 'slide', width: fill, height: fill }, [
      shape({ name: 'bg', width: fill, height: fill, fill: bg }),
      column({ name: 'content', width: fill, height: fill, padding: { x: 86, y: 64 }, gap: 34 }, rootChildren),
    ]),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

// Slide 1
addSlide([
  row({ width: fill, height: grow(1), gap: 60 }, [
    column({ width: grow(1), height: fill, gap: 28, justifyContent: 'center' }, [
      text('第三部分', { width: fill, height: hug, style: { fontSize: 26, bold: true, color: C.blue, fontFace: 'Microsoft YaHei' } }),
      text('基于 SWMM 的 I/E 缺陷多场景数据生成', {
        width: wrap(980), height: hug,
        style: { fontSize: 68, bold: true, color: C.ink, fontFace: 'Microsoft YaHei' },
      }),
      text('从工程资料与 SWMM 基线模型出发，批量生成可用于缺陷诊断的全网节点时序数据。', {
        width: wrap(980), height: hug,
        style: { fontSize: 28, color: C.muted, fontFace: 'Microsoft YaHei' },
      }),
      rule({ width: fixed(280), stroke: C.blue, weight: 6 }),
    ]),
    grid({ width: fixed(610), height: fixed(560), columns: [fr(1), fr(1)], rows: [fr(1), fr(1)], gap: 28 }, [
      metric('128', '全网节点', C.blue),
      metric('50', '候选缺陷节点', C.green),
      metric('25', '固定监测节点', C.cyan),
      metric('421', '仿真场景', C.amber),
    ]),
  ]),
], '#F8FBFF');

// Slide 2
addSlide([
  title('研究子区与建模资料'),
  row({ width: fill, height: grow(1), gap: 44 }, [
    column({ width: fixed(760), height: fill, gap: 26 }, [
      bulletList([
        '研究对象来自黄孝河-机场河流域水环境综合治理工程资料。',
        '依据排水分区、泵站服务范围、主干管连通关系和边界条件划定研究子区。',
        '资料包括管网、泵站、闸门、调蓄池、河道、污水处理厂、降雨与调度运行资料。',
        '现场水位、流量及 NH4、TSSs 等指标用于正常工况合理性检查。',
      ]),
      smallNote('PPT 讲述建议：区域背景快速带过，重点落在“研究子区可独立仿真”。'),
    ]),
    column({ width: grow(1), height: fill, gap: 18 }, [
      imagePanel(BLOB.network, '研究区管网与节点示意', '已有图：全网节点、候选缺陷节点与监测节点关系'),
      text('可替换：更适合答辩的黄孝河-机场河研究子区边界图。', { width: fill, height: hug, style: { fontSize: 17, color: C.red, fontFace: 'Microsoft YaHei' } }),
    ]),
  ]),
]);

// Slide 3
addSlide([
  title('SWMM 基线模型构建'),
  row({ width: fill, height: grow(1), gap: 42 }, [
    column({ width: fixed(930), height: fill, gap: 26 }, [
      row({ width: fill, height: hug, gap: 12 }, ['资料整理', '数据清理', '子区划分', 'DWF注入', '结构修复', '边界设置', '正常工况'].map((v, i) =>
        panel({ width: fixed(120), height: fixed(78), padding: 8, fill: i === 3 ? '#E8F1FF' : '#F4F7FB', borderRadius: 8 },
          text(v, { width: fill, height: hug, style: { fontSize: 18, bold: true, color: i === 3 ? C.blue : C.ink, fontFace: 'Microsoft YaHei' } })
        )
      )),
      text('模型目标：可独立运行、可批量注入缺陷、可输出节点级水力与水质响应。', {
        width: fill, height: hug,
        style: { fontSize: 28, bold: true, color: C.ink, fontFace: 'Microsoft YaHei' },
      }),
      tableRows([
        ['对象', '数量', '说明'],
        ['全网节点', '128', '图结构表达与仿真输出范围'],
        ['Junction', '113', '普通连接节点'],
        ['Outfall', '2', '出流边界节点'],
        ['Storage', '13', '蓄水或调蓄单元'],
        ['Conduit', '137', '管段数量'],
      ], [170, 110, 430], { header: C.blue }),
      smallNote('水力输出：depth、head、volume、lateral_inflow、total_inflow、total_outflow、flooding。'),
    ]),
    placeholder('建议补图：SWMM GUI 中研究子区模型截图，或 DWF / TIMESERIES 设置界面截图。'),
  ]),
]);

// Slide 4
addSlide([
  title('I/E 缺陷场景矩阵设计'),
  row({ width: fill, height: grow(1), gap: 44 }, [
    column({ width: fixed(760), height: fill, gap: 26 }, [
      tableRows([
        ['场景类型', '数量', '覆盖范围'],
        ['正常工况', '1', '无缺陷参照'],
        ['I 类渗入', '250', '覆盖 50 个候选节点'],
        ['E 类渗漏', '170', '覆盖 34 个合法节点'],
        ['合计', '421', '正常工况 + IE420'],
      ], [190, 120, 380], { header: C.ink }),
      bulletList([
        'I 类：正向入流扰动，模拟外来水进入管网。',
        'E 类：负向流量扰动，模拟管网水量向外损失。',
        '全网拓扑保留 128 节点，诊断范围限定在 50 个候选缺陷节点。',
        '25 个固定监测节点用于模拟有限传感器观测条件。',
      ], { fontSize: 23, color: C.green }),
    ]),
    imagePanel(BLOB.matrix, 'IE420 场景分布', '已有图：IE420 缺陷矩阵分布，可用于说明类型、节点和强度覆盖'),
  ]),
]);

// Slide 5
addSlide([
  title('PySWMM 批量仿真与节点时序输出'),
  row({ width: fill, height: grow(1), gap: 42 }, [
    imagePanel(BLOB.flow, 'SWMM 数据生成流程', '已有图：自动化仿真流程'),
    column({ width: fixed(710), height: fill, gap: 24 }, [
      bulletList([
        '读取 baseline INP 与 IE420 缺陷矩阵。',
        '逐场景启动 PySWMM 仿真。',
        '依据 start_hour 与 duration_h 控制缺陷活跃期。',
        '通过 generated_inflow(flow) 动态注入 I/E 异常流量。',
        '每 10 min 固定采样一次，保证所有场景时间对齐。',
      ], { fontSize: 23, color: C.cyan }),
      tableRows([
        ['指标', '数值'],
        ['全部场景', '421'],
        ['每场景时间点', '287'],
        ['采样间隔', '10 min'],
        ['每场景记录', '36736'],
      ], [260, 180], { header: C.cyan }),
    ]),
  ]),
]);

// Slide 6
addSlide([
  title('数据特征构建与有效性检查'),
  row({ width: fill, height: grow(1), gap: 38 }, [
    column({ width: fixed(650), height: fill, gap: 24 }, [
      text('数据输出', { width: fill, height: hug, style: { fontSize: 30, bold: true, color: C.ink, fontFace: 'Microsoft YaHei' } }),
      bulletList([
        '保留全网 128 节点原始水力水质时序。',
        '在原始时序基础上构造 residual 派生特征。',
        '核心水力特征：depth、total_outflow。',
        '水质伴随特征：NH4、TSSs。',
      ], { fontSize: 23 }),
      text('检查重点', { width: fill, height: hug, style: { fontSize: 30, bold: true, color: C.ink, fontFace: 'Microsoft YaHei' } }),
      bulletList([
        '场景完整性、时间步一致性、节点覆盖性。',
        'I/E 缺陷活跃期是否出现可识别扰动。',
        '监测节点与缺陷节点不完全重合，保留诊断难度。',
      ], { fontSize: 23, color: C.green }),
    ]),
    grid({ width: grow(1), height: fill, columns: [fr(1)], rows: [fr(1), fr(1)], gap: 18 }, [
      imagePanel(BLOB.box, 'active/inactive residual energy', '已有图：活跃期与非活跃期 residual 能量对比'),
      row({ width: fill, height: fill, gap: 18 }, [
        image({ dataUrl: BLOB.curveI, width: grow(1), height: fill, fit: 'contain', alt: 'I 类典型残差曲线' }),
        image({ dataUrl: BLOB.curveE, width: grow(1), height: fill, fit: 'contain', alt: 'E 类典型残差曲线' }),
      ]),
    ]),
  ]),
]);

const pptxBlob = await PresentationFile.exportPptx(deck);
await pptxBlob.save(OUT);
console.log(OUT);
