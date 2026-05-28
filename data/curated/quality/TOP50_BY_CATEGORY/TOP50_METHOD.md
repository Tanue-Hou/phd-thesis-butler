# Top 50 Templates — METHOD

### 1. The proposed methodology for ___ (e.g., tool design) involves a pipeline comprising ___ (e.g., kinematic modeling), ___ (e.g., geometric analysis), and ___ (e.g., cutting mode calculation).
- subtype: pipeline_overview
- when_to_use: 在方法章节的引言或概述部分。
- score: 2

### 2. The cutting parameters, such as ___ (e.g., feed rate) and ___ (e.g., depth of cut), are selected according to ___ (e.g., the developed mathematical models and recommendations).
- subtype: parameter_setting
- when_to_use: 在实验设计或工艺参数设定部分。
- score: 2

### 3. Given the input parameters ___ (e.g., the required surface profile and material), the method outputs ___ (e.g., the optimal tool geometry and cutting modes).
- subtype: input_output
- when_to_use: 在描述一个具体算法或设计方法时。
- score: 2

### 4. The model takes ___ (e.g., geometric parameters, flow velocity) as input and predicts ___ (e.g., drag coefficient, pressure distribution) as output.
- subtype: input_output
- when_to_use: 介绍一个特定的计算模型或分析工具时。
- score: 2

### 5. The solution algorithm for the [SPECIFIC PROBLEM] consists of the following key steps: [STEP_1], [STEP_2], and iterative [STEP_3] until convergence.
- subtype: algorithm_steps
- when_to_use: To present a clear, structured overview of a proposed computational method.
- score: 2

### 6. The discrete vortex method proceeds as follows: (1) initialization of ___, (2) computation of induced ___, and (3) ___ of particle positions.
- subtype: algorithm_steps
- when_to_use: Detailing a custom or key computational algorithm.
- score: 2

### 7. Under the assumed operating conditions, the calibration algorithm is expected to maintain convergence provided that ___ remains within ___.
- subtype: stability_claims_conservative
- when_to_use: Stability discussion
- score: 2

### 8. The proposed methodology consists of three stages: (1) ___ of the specimen, (2) ___ during loading, and (3) ___ of the collected data.
- subtype: pipeline_overview
- when_to_use: Method chapter opening
- score: 2

### 9. Preliminary tests indicate that the method is ___ stable with respect to ___ , although further investigation under ___ is warranted.
- subtype: stability_claims_conservative
- when_to_use: Discussion of method robustness
- score: 2

### 10. The developed control strategy involves generating the toolpath, generating velocity/acceleration profiles, and an algorithm for ___.
- subtype: pipeline_overview
- when_to_use: To provide an overview of a proposed multi-step technical solution.
- score: 2

### 11. The proposed approach, while comprehensive, demands significant [RESOURCE] for [APPLICATION_CONTEXT] due to its [CHARACTERISTIC].
- subtype: complexity
- when_to_use: To set realistic expectations about the methodology's applicability.
- score: 2

### 12. Сценарный анализ проводится в следующей последовательности: 1. Идентификация ___; 2. Прогнозирование ___; 3. Формирование ___
- subtype: algorithm_steps
- when_to_use: 当需要详细解释一个复杂分析流程时。
- score: 2

### 13. Реализация алгоритма выполнена на языке ___ с использованием библиотеки ___ . Ключевой параметр ___ был установлен равным ___
- subtype: implementation_details
- when_to_use: В отдельном разделе или подразделе для обеспечения воспроизводимости.
- score: 2

### 14. The overall methodology comprises three stages: ___ of vortex structures, their ___ using RANS, and finally the ___ analysis.
- subtype: pipeline_overview
- when_to_use: Introducing the methodological approach at the start of a methods chapter.
- score: 2

### 15. Алгоритм расчёта траектории: шаг 1 — задаём ___ ; шаг 2 — определяем ___ ; шаг 3 — вычисляем ___ ; шаг 4 — проверяем ___ .
- subtype: algorithm_steps
- when_to_use: Detailed algorithm description in methodology chapters
- score: 2

### 16. Step 1: ___ is performed on the raw signal. Step 2: ___ is applied to identify ___. Step 3: ___ is computed for each ___.
- subtype: algorithm_steps
- when_to_use: Detailed method description
- score: 2

### 17. The overall pipeline consists of three main stages: ___ [stage 1], followed by ___ [stage 2], and finally ___ [stage 3].
- subtype: pipeline_overview
- when_to_use: 方法章节的开头，提供鸟瞰图。
- score: 2

### 18. Алгоритм работает следующим образом: 1) на входе получаем ___ ; 2) выполняем операцию ___ ; 3) результатом является ___
- subtype: algorithm_steps
- when_to_use: В разделе с детальным описанием алгоритма, пошагово.
- score: 2

### 19. The algorithm proceeds as follows: Step 1, compute [VARIABLE]; Step 2, update [PARAMETER]; Step 3, verify [CONDITION].
- subtype: algorithm_steps
- when_to_use: 在描述具体算法或工艺流程时
- score: 2

### 20. To evaluate the contribution of each calibration stage, the following configurations are tested: ___, ___, and ___.
- subtype: ablation_plan
- when_to_use: Ablation study description
- score: 2

### 21. Вычислительная сложность предложенного алгоритма составляет O(___) по времени и O(___) по памяти, где ___ — ___.
- subtype: complexity
- when_to_use: Providing complexity analysis of the algorithm
- score: 2

### 22. The overall methodology involves a multi-stage pipeline: first, ___, then ___, followed by ___, and finally ___.
- subtype: pipeline_overview
- when_to_use: At the beginning of the methodology chapter to give a schematic overview.
- score: 2

### 23. Вычислительная сложность предложенного алгоритма составляет ___ , что позволяет использовать его в режиме ___ .
- subtype: complexity
- when_to_use: Для оценки практических ограничений метода
- score: 2

### 24. Алгоритм силового расчета состоит из следующих шагов: 1) определение ___ ; 2) вычисление ___ ; 3) анализ ___ .
- subtype: algorithm_steps
- when_to_use: 在详细方法描述部分，用于逐步分解算法，使其具有可复现性。
- score: 2

### 25. The simulation pipeline consists of ___ stages: ___ , ___ , and ___, executed sequentially at each time step.
- subtype: pipeline_overview
- when_to_use: Opening of a methodology chapter
- score: 2

### 26. To assess the contribution of ___, we compare the full system against a variant where ___ is replaced by ___.
- subtype: ablation_plan
- when_to_use: Designing ablation experiments
- score: 2

### 27. The controller gain was tuned to ensure stability across the entire frequency range of interest, although ___
- subtype: stability_claims_conservative
- when_to_use: When reporting results from a control or active damping system to temper claims.
- score: 2

### 28. Алгоритм работы состоит из последовательности шагов: 1) выполнить ___; 2) рассчитать ___; 3) проверить ___ .
- subtype: algorithm_steps
- when_to_use: 详细阐述技术方法、计算流程时。
- score: 2

### 29. Расчет ___ выполняется в следующей последовательности: определяется ___; рассчитывается ___; вычисляется ___
- subtype: algorithm_steps
- when_to_use: Describing multi-step calculation procedure
- score: 2

### 30. The computational complexity of the proposed calibration algorithm is ___ per element per calibration cycle.
- subtype: complexity
- when_to_use: Complexity analysis section
- score: 2

### 31. Выбор параметров ___ осуществляется на основе критерия ___ для обеспечения условий работы системы ___.
- subtype: parameter_setting
- when_to_use: When explaining the rationale behind specific design choices in the methodology.
- score: 2

### 32. Under the given assumptions, the proposed scheme is expected to exhibit sufficient stability for ___.
- subtype: stability_claims_conservative
- when_to_use: When asserting robustness without absolute guarantees.
- score: 2

### 33. Алгоритм выбора вентилятора выполняется в следующей последовательности: на шаге 1 ___; на шаге 2 ___.
- subtype: algorithm_steps
- when_to_use: Для детального описания процедуры или алгоритма.
- score: 2

### 34. Исследование проводилось в следующей последовательности: сначала ___, затем ___, и в завершение ___
- subtype: pipeline_overview
- when_to_use: 在方法章节开头，提供研究工作的逻辑流程概览。
- score: 2

### 35. Алгоритм согласования интересов предполагает выполнение следующих шагов: 1) ___ ; 2) ___ ; 3) ___ .
- subtype: algorithm_steps
- when_to_use: 在方法章节，详细说明核心算法的执行过程。
- score: 2

### 36. The computational pipeline consists of the following stages: ___, followed by ___, and finally ___
- subtype: pipeline_overview
- when_to_use: Methods section opening
- score: 2

### 37. Алгоритм определения координат дефекта реализуется следующим образом: на шаге ___ выполняется ___.
- subtype: algorithm_steps
- when_to_use: Детальное описание важнейшего алгоритмического решения.
- score: 2

### 38. Алгоритм ___ выполняется следующим образом: для каждого ___ вычисляется ___, затем результат ___.
- subtype: algorithm_steps
- when_to_use: Detailing algorithmic steps within a stage
- score: 2

### 39. The threshold value for ___ was set to ___ based on ___ , following the recommendations of ___ .
- subtype: parameter_setting
- when_to_use: Experimental setup description
- score: 2

### 40. На входе методики задаются ___ и ___ , на выходе — оптимальные параметры траектории: ___ и ___ .
- subtype: input_output
- when_to_use: Interface description for the proposed method
- score: 2

### 41. The calibration frame duration is set to ___ to ensure that ___ achieves convergence within ___.
- subtype: parameter_setting
- when_to_use: Parameter justification subsection
- score: 2

### 42. The key parameter [PARAMETER] is set to [VALUE] based on [RATIONALE] to ensure [DESIRED_EFFECT].
- subtype: parameter_setting
- when_to_use: 在解释实验或仿真参数设置时
- score: 2

### 43. Для каждого типа кризиса нормированы сигнальные коэффициенты, значение которых определяется ___
- subtype: parameter_setting
- when_to_use: 在介绍模型参数时，解释其来源或计算方法。
- score: 2

### 44. Алгоритм контроля конфигурации выполняется в следующей последовательности:
1. ___
2. ___
3. ___
- subtype: algorithm_steps
- when_to_use: 详细介绍一个具体的、可重复的计算或工程步骤序列。
- score: 2

### 45. The calibration block accepts ___ from each channel and outputs ___ for subsequent beamforming.
- subtype: input_output
- when_to_use: Interface description of the calibration module
- score: 2

### 46. A critical implementation detail is the use of [TOOL/MATERIAL/TECHNIQUE] to handle [CHALLENGE].
- subtype: implementation_details
- when_to_use: 在方法描述中，解释解决特定难点的方法时
- score: 2

### 47. Предложенная методика (алгоритм) включает в себя следующие основные этапы: ___,随后 ___, 最终 ___.
- subtype: pipeline_overview
- when_to_use: 在方法章开头，为读者提供一幅全局“地图”，再分步详解。
- score: 2

### 48. The overall workflow consists of [STEP_1], followed by [STEP_2], and concluding with [STEP_3].
- subtype: pipeline_overview
- when_to_use: 在方法章节开头，概述技术路线时
- score: 2

### 49. Для проверки роли компонента ___ будет проведено сравнение полной модели с вариантом без ___.
- subtype: ablation_plan
- when_to_use: 方法设计或实验计划中，用于论证各组件贡献。
- score: 2

### 50. The complete system comprises three sequential stages: ___， followed by ___， and finally ___.
- subtype: pipeline_overview
- when_to_use: To give the reader a roadmap of a multi-step algorithm or methodology.
- score: 2

