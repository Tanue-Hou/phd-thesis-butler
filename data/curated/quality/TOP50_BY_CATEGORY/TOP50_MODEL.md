# Top 50 Templates — MODEL

### 1. The model parameters, such as ___ and ___, are identified based on ___ (e.g., the physical constraints of the machining process) and ___ (e.g., preliminary experimental data).
- subtype: parameter_identifiability
- when_to_use: 在模型建立后，解释参数来源的段落。
- score: 2

### 2. The mathematical formulation of the [PHYSICAL PROBLEM] assumes [ASSUMPTION_1] and [ASSUMPTION_2], simplifying the [COMPLEXITY] to focus on [KEY EFFECT].
- subtype: boundary_conditions
- when_to_use: When presenting the assumptions behind a theoretical or computational model.
- score: 2

### 3. Принимаются следующие допущения: 1) движение КК описывается в рамках ___ ; 2) гравитационное поле моделируется как ___ ; 3) манёвры выполняются ___ .
- subtype: assumptions
- when_to_use: Chapter 1 or 2 when presenting the mathematical model
- score: 2

### 4. The mathematical model of the kinematics of the proposed method assumes ___ (e.g., rigid body tool motion) and ___ (e.g., ideal cutting conditions).
- subtype: assumptions
- when_to_use: 在理论建模章节的起始部分。
- score: 2

### 5. The boundary conditions are prescribed as follows: at surface ___, the displacement is set to ___, while at surface ___, a ___ load is applied.
- subtype: boundary_conditions
- when_to_use: Describing the FEM or analytical setup
- score: 2

### 6. The description of the [AERODYNAMIC] subsystem involves [SOURCES OF UNCERTAINTY] related to [PARAMETER] estimation and [PHENOMENON] modeling.
- subtype: uncertainties
- when_to_use: In the model description chapter to transparently discuss model limitations.
- score: 2

### 7. The following assumptions are adopted: (1) the workpiece behaves as a ___ structure; (2) the tool is ___; (3) the cutting process is ___.
- subtype: assumptions
- when_to_use: Opening a model description chapter
- score: 2

### 8. The parameters of the nonlinear transistor model are identifiable under the condition that ___ provides sufficient excitation across ___.
- subtype: parameter_identifiability
- when_to_use: Parameter estimation methodology
- score: 2

### 9. Граничные условия на поверхности задаются с учетом ___ (например, конвективного теплообмена, массового отвода, радиационного излучения).
- subtype: boundary_conditions
- when_to_use: При описании постановки задачи для математической модели.
- score: 2

### 10. The boundary conditions applied to the computational domain include ___ at the inlet, ___ at the outlet, and ___ on the solid surfaces.
- subtype: boundary_conditions
- when_to_use: 设置数值模拟或描述实验装置时。
- score: 2

### 11. Параметры многослойного экрана удовлетворяют следующим ограничениям: ___ ≤ ___ ≤ ___, причём суммарная толщина ___ не превышает ___.
- subtype: constraints
- when_to_use: Defining feasible region for optimization
- score: 2

### 12. The boundary conditions are specified as follows: on the surface ___ , the ___ is prescribed, while on ___ the ___ condition holds.
- subtype: boundary_conditions
- when_to_use: Problem formulation
- score: 2

### 13. The amplitude and phase errors in the transmitting path are modeled as ___ with standard deviations of ___ and ___, respectively.
- subtype: errors
- when_to_use: Error modeling section
- score: 2

### 14. For tractability, the following simplifications are introduced: ___ is assumed to be ___ , and the effect of ___ is neglected.
- subtype: simplifications
- when_to_use: Model section, just before solutions
- score: 2

### 15. At the inlet boundary, a velocity profile corresponding to ___ is prescribed, while at the outlet, a ___ condition is applied.
- subtype: boundary_conditions
- when_to_use: When describing the setup of a CFD simulation or boundary value problem.
- score: 2

### 16. Для упрощения расчётов предполагается, что влиянием ___ можно пренебречь, поскольку его вклад составляет не более ___ от ___.
- subtype: simplifications
- when_to_use: Justifying why certain effects are neglected
- score: 2

### 17. The proposed model assumes that ___ [assumption]. This simplification allows ___ [benefit], but may limit ___ [limitation].
- subtype: assumptions
- when_to_use: 模型或方法描述的开头部分。
- score: 2

### 18. Let ___ denote the complex weight applied to the n-th element, where ___ represents the amplitude and ___ the phase shift.
- subtype: notation
- when_to_use: Notation introduction for array signal model
- score: 2

### 19. To reduce computational cost, the ___ is approximated by a ___, which is justified when the ___ is much smaller than ___.
- subtype: simplifications
- when_to_use: When a simplification is necessary
- score: 2

### 20. The parameters ___ and ___ cannot be independently identified from the available data and are therefore treated as ___.
- subtype: parameter_identifiability
- when_to_use: When describing the calibration procedure
- score: 2

### 21. The solution must satisfy the constraint ___, which ensures that the ___ does not exceed the physically allowable ___.
- subtype: constraints
- when_to_use: When imposing physical or geometric constraints
- score: 2

### 22. The optimization is subject to the constraints: the stress must not exceed ___, and the deflection is limited to ___.
- subtype: constraints
- when_to_use: 在优化模型描述中，列出必须满足的物理或工程限制
- score: 2

### 23. To make the analysis tractable, we simplify the system by assuming [SIMPLIFICATION], which is valid when [CONDITION].
- subtype: simplifications
- when_to_use: 在建立简化物理模型时
- score: 2

### 24. The ___ edge of the workpiece is clamped, corresponding to zero displacement and rotation at nodes belonging to ___.
- subtype: boundary_conditions
- when_to_use: Defining fixture or clamping conditions
- score: 2

### 25. Реализуя свою функцию с цикличностью [X лет], ___ зачастую превосходит по временным затратам время, за которое ___
- subtype: constraints
- when_to_use: 模型分析中，指出系统性约束或瓶颈
- score: 2

### 26. Значение ___ определяется путём подбора таким образом, чтобы расчётная кривая ___ совпадала с экспериментальной.
- subtype: parameter_identifiability
- when_to_use: Parameter identification discussion
- score: 2

### 27. The simulation assumes that the flow is ___ and that the structures can be represented as quasi-stationary ___.
- subtype: assumptions
- when_to_use: At the beginning of a modeling chapter to set the scope and boundaries.
- score: 2

### 28. Для описания кинематической схемы введены следующие обозначения: ___ — угол поворота звена, ___ — длина звена.
- subtype: notation
- when_to_use: При введении системы обозначений.
- score: 2

### 29. The analysis assumes that each T/R channel operates with ___ and that mutual coupling between elements is ___.
- subtype: assumptions
- when_to_use: Model assumptions declaration
- score: 2

### 30. Обозначим через ___ характеристическую скорость манёвра, через ___ — радиус ___ , через ___ — время перелёта.
- subtype: notation
- when_to_use: Notation introduction section or beginning of mathematical formulation
- score: 2

### 31. Обозначим через ___ количество слоёв экрана, через ___ — толщину i-го слоя, через ___ — плотность материала.
- subtype: notation
- when_to_use: Introducing mathematical notation for the model
- score: 2

### 32. The design of the T/R module must satisfy constraints on ___, ___, and ___ imposed by the aircraft platform.
- subtype: constraints
- when_to_use: Design constraint specification
- score: 2

### 33. The following assumptions are adopted: (1) the material behaves as ___ ; (2) the damage is ___ distributed.
- subtype: assumptions
- when_to_use: Theory section, before derivations
- score: 2

### 34. For the purpose of initial analysis, the ___ effect is neglected, as its contribution to ___ is below ___.
- subtype: simplifications
- when_to_use: Justifying simplifications in theoretical analysis
- score: 2

### 35. Let ___ denote ___ (e.g., the axial feed rate), and ___ represent ___ (e.g., the tool geometry parameter).
- subtype: notation
- when_to_use: 在推导公式或建立模型之前。
- score: 2

### 36. At the inlet, ___ is prescribed; at the outlet, ___ is specified; on the walls, ___ condition is applied.
- subtype: boundary_conditions
- when_to_use: Describing CFD setup
- score: 2

### 37. Among the model parameters, ___ can be directly measured via ___ , while ___ must be estimated from ___ .
- subtype: parameter_identifiability
- when_to_use: Model calibration discussion
- score: 2

### 38. The following assumptions are adopted: (1) the fluid is ___, (2) the flow is ___, (3) ___ is negligible.
- subtype: assumptions
- when_to_use: Opening of model/method chapter
- score: 2

### 39. The boundary conditions for the analysis are set as follows: the wing root is ___, while the tip is ___.
- subtype: boundary_conditions
- when_to_use: 在数值模拟或理论推导中，设定问题的边界
- score: 2

### 40. For the analytical model, it is assumed that the system is ___ and that the material properties are ___.
- subtype: assumptions
- when_to_use: In a modeling or methodology chapter to clarify the model's scope and boundaries.
- score: 2

### 41. The discrete-continuum model is based on the assumption that ___ of the mesh structure can be averaged.
- subtype: assumptions
- when_to_use: When introducing a new theoretical model in the methodology.
- score: 2

### 42. The proposed model is based on the following key assumptions: 1) [ASSUMPTION_1], and 2) [ASSUMPTION_2].
- subtype: assumptions
- when_to_use: 在提出理论模型或公式推导前
- score: 2

### 43. Граничные условия задачи включают: начальную орбиту ___ , конечную орбиту ___ и ограничение на ___ .
- subtype: boundary_conditions
- when_to_use: Problem formulation specifying start and end conditions
- score: 2

### 44. The model assumes that the laser source is ___ and that heat transfer occurs primarily through ___.
- subtype: assumptions
- when_to_use: When describing a mathematical model for transparency.
- score: 2

### 45. Функционирование модели ограничено условиями: ___ не превышает ___, ___ находится в пределах ___.
- subtype: constraints
- when_to_use: При описании области применимости модели.
- score: 2

### 46. Для упрощения расчётов предполагается, что ___ является жёстким звеном с ___ степенями свободы.
- subtype: simplifications
- when_to_use: При описании упрощений в модели.
- score: 2

### 47. При построении математической модели предполагается, что ___ является ___, а ___ остаётся ___.
- subtype: assumptions
- when_to_use: Declaring assumptions before presenting a model
- score: 2

### 48. В основе разработанного метода лежит предположение о ___ , что справедливо при условиях ___ .
- subtype: assumptions
- when_to_use: 在提出理论模型或方法时，界定其适用范围。
- score: 2

### 49. Геометрия конструкции упрощена до ___ для снижения вычислительных затрат при сохранении ___.
- subtype: simplifications
- when_to_use: Geometry simplification justification
- score: 2

### 50. The boundary condition at the blade root is modeled as ___, while the tip is considered ___.
- subtype: boundary_conditions
- when_to_use: When describing the setup of a finite element simulation or analytical model.
- score: 2

