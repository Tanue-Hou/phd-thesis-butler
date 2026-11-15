# 剩余审计问题：第二批止损修复候选（2026-11-15）

基于本地首批提交 `4e08cac`，其树对应已上传分支提交 `31a227378339bbf86c5f7a60f7c199cbdfc88b2c`。本批未推送；不是 v5.4.2 全部完成或合规认证。不触碰真实源资产、用户本地、实验或外部模型。

## 已修复与行为变化

1. **来源错配停止生成**：L1 删除按来源/学科排队配对、模糊配对及旧目录自动推标签。现在必须明确提供经审阅身份映射，并在输入树以外新建输出副本。不匹配记录保持原字段并标为 `legacy_unverified` / `unmapped`。映射记录的人工审阅声明不是程序独立验证的事实，更不是版权授权。
2. **转换重跑保护**：完整新格式直接不写，混合/未知格式拒绝；旧格式转换先保留逐字节 `.json.pre-v5.1.bak`，备份冲突拒绝；临时文件原子替换。生成 ID 使用完整内容 SHA-256，重复语义拒绝。现有库的重复 ID 不自动重写，避免悄悄破坏引用。
3. **引用候选与证据分开**：词重合/角色匹配不再自动判 `strong/covered`，重复 ID/DOI 不重复计数。兼容旧枚举使用 `partial/weak`，新增 `candidate_unverified` 和匹配依据，提示核对原文。不能判语义蕴含，反向论断仍可能进入候选，不能误称消灭了语义误检。
4. **稳定身份、无损去重与失败退出**：保留已有 ID，无标识使用稳定 SHA-256；仅完全相同规范化记录自动去重，相似题名/不同 DOI 不再被吞并。同 ID 冲突或输入校验失败非零退出且不覆盖旧输出。哈希只是记录标识，不证明真实作品身份。
5. **导入止损**：Zotero 异常/不可用/坏响应非零；机构作者保留；成功空搜索写 `[]`，不沿用旧查询结果。全部验证均为 mock，未访问实际服务。
6. **landscape/L2**：空章节字段继续读备用字段；对象标题可用，章节计数仅含有效标题、全无效时不生成空模式；未观察到的方法不再宣传创新；近期窗口按参考年减5。deep E2E仅一次且失败计入退出。L2任何目标类别缺源即明确失败、不替换已有规则。

## 使用与回退

- 候选只包含9个现有脚本修改、4个新增回归脚本及本说明。将补丁应用到首批树，先运行以下离线验证，再决定合并；不需安装新依赖。
- `git apply --check remaining_repairs.patch`，再 `git apply remaining_repairs.patch`。回退用 `git apply -R remaining_repairs.patch`，仅限这些文件没有后续更改时；否则逐项审查，勿覆盖他人工作。
- 新 L1 CLI（旧 `--chunks/--chunk` 不再支持，防止读取旧不可靠缓存）：
  `python scripts/l1_annotate_templates.py --verified-map REVIEWED.json --input-dir INPUT --output-dir NEW_OUTPUT`
- `REVIEWED.json` 是对象列表，各项要求 `source/pdf_id/paper_id/cluster/identity_evidence` 非空字符串，`reviewed: true`；cluster为五个正式枚举之一。由可核源证据确认，不从旧标签倒造。相同 `(source,pdf_id)` 冲突拒绝。
- 转换脚本对当前新格式仅报告 no-op，不代表验证现有数据质量；旧格式保存在旁路备份中，采用新输出前需审阅备份与差异。

## 实际验证

- 新回归：来源/转换10、元数据13、引用9、landscape9，共41项通过；首批检索16项继续通过。
- 已有 smoke11/11、planning22/22、research17/17、evidence27/27 通过；skill通过但仍有缺失可选evals警告。
- 由仓库样例生成临时landscape后deep229/229通过，包含本地Zotero样例，不是在线服务。
- 脚本AST、`git diff --check`通过。全部跟踪assets逐字节对照首批树未改，详见日志 `asset_integrity.json`。
- 回归命令：`python scripts/test_source_conversion_safety.py`、`python scripts/test_metadata_safety.py`、`python scripts/test_evidence_safety.py`、`python scripts/test_landscape_safety.py`。详细输出在 `remaining_test_results/`。

## 仍未解决，不应扩库前忽略

- 旧记录真实作品映射、分类可信度及原文支持未恢复；缺原始身份/目录/全文证据，不能靠修代码把历史标签变真。
- 1405行损坏键、质量分数缺失、现有画像13组重复ID、结构统计噪声和BUILD_INFO口径尚未重建；保留原资产，未大规模清洗。
- 权利来源/作品清单/撤销链、完整Git历史私有内容、源许可及公开网站MIT说明仍待核，不宣称脱敏或授权完成。
- 证据验证器固定 `/tmp` 测试文件的并发隔离风险尚未修；本轮验证串行运行。
- 新L1非就地写保护源数据，但输出中途I/O失败可能留下不完整新目录，退出非零后应检查该目录，不能当完整交付。
- 未修私有下载/蒸馏管线，也未做30,000篇扩库、外部模型调用或端到端生产验收。
