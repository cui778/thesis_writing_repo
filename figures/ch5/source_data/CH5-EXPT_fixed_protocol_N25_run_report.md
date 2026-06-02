# 第五章 fixed protocol N25 主实验运行报告

> **历史执行记录。** 本文件记录正式主表生成前的运行安排，不再表示当前仍有实验缺失。
> 当前正式结果请以 `CH5-EXPT_fixed_protocol_N25_main_table.csv` 为准；未完成清单
> `CH5-EXPT_fixed_protocol_missing_main_runs.csv` 现已为空。

## 1. 实验目的

本轮实验用于把第五章布局优化方法重新对齐到第4章最新固定诊断协议。

第4章已经确定的固定协议为：

```text
dataset = IE420 + normal20
teacher_subdir = ie420_plus_normal20_v1
feature_set = raw_plus_residual
lambda_loc = 0.5
model = hydraulic_inverse_deepattn
split = scenario
diagnosis_seed = 42
budget = N25
```

第五章只改变监测节点集合 `S` 与 observed mask，不重新定义诊断任务、不改变特征组合、不改变模型结构、不改变定位损失权重。

本轮实验要补齐第五章 `N=25` 主表中的 5 个诊断导向布局优化方法：

```text
Cand-Obs
Two-stage v1
Node-Feedback
Surrogate-Search
Embedding-Guided
```

`degree_N25` 已经由第4章主结果提供，不在本轮重复训练。

## 2. 当前证据状态

已完成结果索引：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_result_index.csv
```

结论如下：

| 方法 | 当前状态 | 是否可进入新 fixed protocol 正式主表 |
|---|---|---|
| Degree | strict `IE420 + normal20` 已完成 | 是，作为参照基线 |
| Cand-Obs | 只有旧路径结果 | 否，需本轮重跑 |
| Two-stage v1 | 旧路径和 bridge 结果已有 | 否，需本轮重跑 |
| Node-Feedback | 只有旧路径结果 | 否，需本轮重跑 |
| Surrogate-Search | 只有旧路径结果 | 否，需本轮重跑 |
| Embedding-Guided | 旧路径三 seed 已有 | 否，需本轮重跑 |

因此，本轮不是补某一个单独方法，而是补齐第五章主线优化方法的统一 fixed protocol `N=25, seed=42` 结果。

## 3. Manifest 文件

本轮训练命令已经写入：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_N25_main_manifest.csv
```

字段说明：

| 字段 | 含义 |
|---|---|
| `method` | 正文方法名 |
| `layout_id` | 布局文件标识 |
| `budget` | 监测节点数量，本轮固定为 25 |
| `diagnosis_seed` | 诊断训练 seed，本轮固定为 42 |
| `layout_json` | 监测节点布局 JSON |
| `output_tag` | 训练输出标识 |
| `expected_metrics_file` | 训练完成后应生成的 metrics JSON |
| `command` | 可直接执行的训练命令 |

已校验：

```text
5 条训练命令均已生成
5 个 layout_json 均存在
5 个 expected_metrics_file 当前均不存在
```

## 4. 推荐运行方式

由于当前机器曾出现内存诊断异常、访问冲突和蓝屏，不建议一次性批量执行 5 条命令。

推荐执行策略：

```text
一次只跑 1 条
每条训练完成后立即检查 metrics JSON
确认 JSON 可读后再跑下一条
```

## 5. PowerShell 运行模板

先进入工作目录并激活环境：

```powershell
cd E:\11.16
D:/conda3/Scripts/activate
conda activate swmm_gpu
```

读取 manifest：

```powershell
$manifest = "E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_N25_main_manifest.csv"
$rows = Import-Csv $manifest
```

查看待运行命令：

```powershell
$rows | Select-Object method, layout_id, output_tag, expected_metrics_file | Format-Table -AutoSize
```

## 6. 单条运行方法

建议先跑第一条 `Cand-Obs`：

```powershell
$row = $rows[0]
Write-Host "Running $($row.method): $($row.output_tag)" -ForegroundColor Cyan
Invoke-Expression $row.command
```

训练结束后立刻检查 metrics 文件是否存在：

```powershell
if (Test-Path $row.expected_metrics_file) {
    Write-Host "OK: $($row.expected_metrics_file)" -ForegroundColor Green
} else {
    Write-Host "MISS: $($row.expected_metrics_file)" -ForegroundColor Red
}
```

检查 JSON 是否可读：

```powershell
python -c "import json,sys; p=r'$($row.expected_metrics_file)'; json.load(open(p,'r',encoding='utf-8')); print('JSON OK:', p)"
```

如果 JSON 可读，再继续下一条：

```powershell
$row = $rows[1]
Write-Host "Running $($row.method): $($row.output_tag)" -ForegroundColor Cyan
Invoke-Expression $row.command
```

依次运行：

| 顺序 | 方法 |
|---:|---|
| 1 | Cand-Obs |
| 2 | Two-stage v1 |
| 3 | Node-Feedback |
| 4 | Surrogate-Search |
| 5 | Embedding-Guided |

## 7. 不建议的批量运行方式

以下命令可以批量跑，但当前不建议使用：

```powershell
foreach ($row in $rows) {
    Write-Host "Running $($row.method): $($row.output_tag)" -ForegroundColor Cyan
    Invoke-Expression $row.command
}
```

原因：

```text
当前机器存在内存稳定性风险
批量运行时如果某条命令写坏 JSON，不容易及时发现
系统蓝屏可能导致多个结果文件同时损坏
```

## 8. 训练完成后的结果检查

全部运行完成后检查 5 个 metrics JSON：

```powershell
$rows | ForEach-Object {
    if (Test-Path $_.expected_metrics_file) {
        Write-Host "OK   $($_.method) $($_.output_tag)" -ForegroundColor Green
    } else {
        Write-Host "MISS $($_.method) $($_.output_tag)" -ForegroundColor Red
    }
}
```

检查所有 JSON 是否可读：

```powershell
$rows | ForEach-Object {
    python -c "import json; p=r'$($_.expected_metrics_file)'; json.load(open(p,'r',encoding='utf-8')); print('JSON OK:', p)"
}
```

## 9. 训练完成后的汇总步骤

训练完成后，回到本仓库执行：

```powershell
python E:\11.16\thesis_writing_repo\figures\ch5\scripts\build_ch5_fixed_protocol_result_index.py
```

该脚本会更新：

```text
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_result_index.csv
E:\11.16\thesis_writing_repo\figures\ch5\source_data\CH5-EXPT_fixed_protocol_missing_main_runs.csv
```

如果 5 条 fixed protocol 结果均生成成功，`CH5-EXPT_fixed_protocol_missing_main_runs.csv` 后续应不再把这些方法标为缺失。

## 10. 正文可写口径

训练完成前：

```text
只能写：第五章主线方法已有旧路径结果和机制证据，但新 fixed protocol 主表仍待补齐。
不能写：某个优化方法已经在 IE420 + normal20 下正式优于 degree_N25。
```

训练完成后：

```text
可以写：在第4章固定诊断协议下，比较 Cand-Obs、Two-stage v1、Node-Feedback、Surrogate-Search、Embedding-Guided 与 degree_N25 参照基线。
```

仍需注意：

```text
本轮只有 diagnosis_seed = 42。
若结果差距较小，后续需要补 seed 7 和 seed 123。
预算 N=5/10/15/20/25 的性能曲线不在本轮完成。
```

## 11. 本轮实验完成判据

本轮实验完成需要同时满足：

```text
5 个 expected_metrics_file 均存在
5 个 metrics JSON 均可被 json.load 正常读取
所有结果均使用 teacher_subdir = ie420_plus_normal20_v1
所有结果均使用 feature_set = raw_plus_residual
所有结果均使用 lambda_loc = 0.5
所有结果均使用 diagnosis_seed = 42
```

若任一 JSON 缺失或不可读，该方法不进入正式主表。
