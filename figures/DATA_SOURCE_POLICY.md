# 第3至第5章绘图数据管理规则

## 三层数据结构

```text
原始数据与实验输出
        ↓ 提取、审计、汇总
figures/ch*/source_data
        ↓ 正式绘图脚本
figures/ch*/generated_results
```

`source_data` 是论文图件的轻量证据包，不是原始数据的完整副本。

## 允许直接读取原始资产的情况

以下图件需要大文件或结构对象，可以直接读取实验仓库：

- 第3章残差时序、空间响应和动画：正式 Parquet；
- 第3章和第5章管网空间图：拓扑 JSON；
- 第4章单场景过程图：窗口级和事件级预测 CSV；
- 第5章布局空间图：各方法布局 JSON。

## 每个绘图脚本必须记录

1. 科学问题；
2. 图件身份；
3. 直接输入文件；
4. 原始数据来源；
5. 正式协议；
6. 输出 PNG、SVG 和 cleaned CSV；
7. 是否依赖其他图件生成的中间表。

## 禁止行为

- 自动选取最新文件；
- 自动搜索任意 defect matrix；
- 正式文件缺失时回退到 legacy；
- 在同一图中混合 normal10、normal20、persistent 或 fulltime；
- 将 `legacy_old_protocol` 表用于正文图。

