---
name: ptb-beta
description: 在用户请求中俄翻译、俄语润色、论文结构规划、研究比较或证据检查时，调用 PTB 私测 MCP 获取限量写作知识卡。
---

首次调用前说明本轮请求、意图和必要的选定原文将上传至 PTB 服务，在用户同意后操作。用户不同意则留在本地。完整保留用户实际指令及否定、引号和任务变化；分离选中稿件。不得虚构意图、原稿或改写请求以获取放行。任务意图不明确时请用户用自己的话澄清。

PTB 提供参考卡、编辑规则和步骤指引。客户端模型翻译、选用合适的规则并核对原意。实际采用卡片后才将修改归为参考 PTB；仅采用通用规则时明确说明。收到卡片只代表检索命中，客户端回执记录客户端自述。编号比对只检查标记，事实与数值须另有原件支持。规划、对比和证据检查也由客户端结合返回的参考完成。

助手负责选择工具、填写参数和继续已获同意的步骤。首次需要同意时，用一句话说明本次发送范围并询问即可；不要让用户复述同意声明、报出工具名或手填参数。范围改变时再征求同意。

调用工具 `ptb_lookup`，外层参数名为 `request`。对象中填写：

- user_request（指令原话）、intent、source_kind、requested_output、client_tags（1–3个）。
- intent/output 对应 translate/translation、polish/revision、plan/outline、compare/comparison、check_evidence/evidence_feedback。明确新写正文时产物填 new_prose。
- source_kind 取 draft、outline、data、prior_cards、none。改译需附 source_text、source_lang 和 target_lang，语种 zh/ru，俄语润色用 ru/ru。
- 标签选 篇章布局、方法选择、实验验证、综述分歧、结果与不确定性、边界与归属、目标与假设。
- 同一任务后续调用带回 task_handle；不要以另开任务规避限额或被拒操作。

放行后，仅在用户目标范围内使用返回的结构、表达或证据卡；忠实翻译或润色用户原稿，保留数字、否定、证据强度及归属。结构任务限于提纲、章节职责和证据提示。禁止直接代写或扩写论文。遇 deny/clarify/error 停止，向用户显示原因；无依据明确待补。不要声称服务核验了原论文页码。

中译俄组合委托可声明 workflow/workflow，一次提交完整原话和中文原稿、zh/ru。客户端按 next_step 自动完成翻译、润色、核对，再回传实际采用的规则 ID 与核对状态。润色按 editorial_guidance 应用并在终稿后附“编辑依据”链接；仅比较过文中编号时不得声称核验了公式或表内数据。
翻译或润色交稿时提示用户在论文工作目录建立或沿用《术语对应表.md》，统一跨章译名；组合任务只在最终交付提醒一次。

收到 repair 且 auto_retry 为 true 时，客户端根据 field、reason、hint 自动修正参数并重试。保留用户原话、选中稿件、任务范围和流程步骤；相同修正仍失败时停止重试。禁止通过改写用户意图规避审核。
