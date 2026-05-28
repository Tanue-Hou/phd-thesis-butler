# Writing Scene → Category Mapping

Use this when goal=query to recommend sub-skills for a specific writing task.

## 引言 (Введение)

| Subscene | Category.subtype |
|----------|-----------------|
| 动机/背景 | INTRO.motivation, INTRO.relevance |
| 问题提出 | INTRO.problem_statement |
| 目标与任务 | INTRO.objective, INTRO.tasks |
| 研究对象 | INTRO.object_subject |
| 贡献预告 | INTRO.contributions_preview |
| 结构概述 | INTRO.thesis_structure |

## 文献综述 (Обзор)

| Subscene | Category.subtype |
|----------|-----------------|
| 流派梳理 | SURVEY.taxonomy |
| 方法对比 | SURVEY.comparison |
| 前人局限 | SURVEY.limitations_of_prior |
| 研究空白 | SURVEY.gap |
| 本文定位 | SURVEY.positioning |
| 基线选择 | SURVEY.baseline_selection |

## 建模 (Моделирование)

| Subscene | Category.subtype |
|----------|-----------------|
| 假设前提 | MODEL.assumptions |
| 边界条件 | MODEL.boundary_conditions |
| 符号单位 | MODEL.notation, MODEL.units |
| 坐标系 | MODEL.coordinate_frames |
| 不确定性 | MODEL.uncertainties |
| 约束条件 | MODEL.constraints |
| 简化说明 | MODEL.simplifications |
| 参数可辨识性 | MODEL.parameter_identifiability |

## 方法与算法 (Метод)

| Subscene | Category.subtype |
|----------|-----------------|
| 整体流程 | METHOD.pipeline_overview |
| 输入输出 | METHOD.input_output |
| 算法步骤 | METHOD.algorithm_steps |
| 参数设置 | METHOD.parameter_setting |
| 复杂度 | METHOD.complexity |
| 实现细节 | METHOD.implementation_details |

## 实验与仿真 (Эксперименты)

| Subscene | Category.subtype |
|----------|-----------------|
| 数据描述 | EXPERIMENT.data_description |
| 场景设计 | EXPERIMENT.scenario_design |
| 评价指标 | EXPERIMENT.metrics |
| 基线设置 | EXPERIMENT.baselines |
| 超参数 | EXPERIMENT.hyperparams |

## 结果汇报 (Результаты)

| Subscene | Category.subtype |
|----------|-----------------|
| 报数 | RESULT.numeric_reporting |
| 性能提升 | RESULT.improvement_reporting |
| 分布汇报 | RESULT.distribution_reporting |
| 案例分析 | RESULT.case_studies |
| 失败案例 | RESULT.failure_cases |
| 对比表 | RESULT.comparison_table |
| 数字汇报口径 | UTIL.NUMERIC.* |

## 讨论 (Обсуждение)

| Subscene | Category.subtype |
|----------|-----------------|
| 机制解释 | DISCUSSION.mechanism_explanation |
| 敏感性 | DISCUSSION.sensitivity |
| 权衡 | DISCUSSION.tradeoff |
| 泛化性 | DISCUSSION.generalization |
| 有效性威胁 | DISCUSSION.threat_to_validity |
| 谨慎解释 | DISCUSSION.interpretation_hedged |

## 结论与展望 (Выводы)

| Subscene | Category.subtype |
|----------|-----------------|
| 总结 | CONCLUSION.summary |
| 贡献回顾 | CONCLUSION.contributions_recap |
| 适用性 | CONCLUSION.applicability |
| 局限性 | CONCLUSION.limitations |
| 未来工作 | CONCLUSION.future_work |

## 过渡与结构 (Переходы)

| Subscene | Category.subtype |
|----------|-----------------|
| 章节开头 | TRANSITION.section_openers |
| 章节结尾 | TRANSITION.section_closers |
| 段间连接 | TRANSITION.paragraph_linkers |
| 下文预告 | TRANSITION.signposting |
| 连接词 | UTIL.CONNECTIVE.* |

## 定义与符号 (Определения)

| Subscene | Category.subtype |
|----------|-----------------|
| 定义 | FORMAL_DEFS.definition |
| 引理引入 | FORMAL_DEFS.lemma_style |
| 约束引入 | FORMAL_DEFS.constraint_introductions |
| 符号引入 | FORMAL_DEFS.symbol_introductions |

## 工程实现 (Инженерия)

| Subscene | Category.subtype |
|----------|-----------------|
| 部署 | ENGINEERING.deployment |
| 实时性 | ENGINEERING.real_time |
| 资源占用 | ENGINEERING.resource_usage |
| 可复现 | ENGINEERING.code_reproducibility |

## Автореферат 模块

| Subscene | Category.subtype |
|----------|-----------------|
| 选题意义 | АКТУАЛЬНОСТЬ.* |
| 对象主题 | ОБЪЕКТ_ПРЕДМЕТ.* |
| 目标任务 | ЦЕЛЬ_ЗАДАЧИ.* |
| 研究方法 | МЕТОДЫ.* |
| 创新点 | НОВИЗНА.*, НОВИЗНА_ФОРМУЛИРОВКИ.* |
| 理论意义 | ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ.* |
| 实践意义 | ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ.* |
| 保护条款 | ПОЛОЖЕНИЯ.* |
| 结果 | РЕЗУЛЬТАТЫ.* |
| 检验 | АПРОБАЦИЯ.*, ПУБЛИКАЦИИ.* |
| 结构 | СТРУКТУРА.* |
| 结论 | ВЫВОДЫ.* |
