"""PTB beta: positive command grammar; unrecognised instructions require clarification."""
from __future__ import annotations
import re
import secrets
import sqlite3
import time
import unicodedata
from collections import deque
from pathlib import Path
from editorial import GLOSSARY, Workflows, field_repair, guidance, stages

OUTPUTS = {"translate": "translation", "polish": "revision", "plan": "outline",
           "compare": "comparison", "check_evidence": "evidence_feedback"}
SCENES = ("篇章布局", "方法选择", "实验验证", "综述分歧", "结果与不确定性", "边界与归属", "目标与假设")
SCOPES = {"plan": set(SCENES), "compare": {"实验验证", "方法选择", "综述分歧", "结果与不确定性", "边界与归属"},
          "check_evidence": set(SCENES), "translate": set(SCENES), "polish": set(SCENES)}
SOURCES = {"draft", "outline", "data", "prior_cards", "none"}
TYPES = {
    "translate": {"俄语句式", "俄语语用"}, "polish": {"俄语句式", "俄语语用"},
    "plan": {"整篇布局", "双端依赖", "篇章衔接", "章间衔接", "论证步骤", "篇章布局", "顺序与计划"},
    "compare": {"比较边界", "民用比较", "替代与基线", "对照证据", "分层验证", "适用边界", "论证步骤"},
    "check_evidence": {"适用条件", "必要证据", "民用证据", "对照证据", "分层验证", "适用边界", "结论限定", "论证步骤"},
}
# Full-match the instruction. A pasted draft is data only when separately selected.
GRAMMAR = {
    "translate": r"(?:请|帮我)?(?:把|将)?(?:这段|这句|以下|下面的|我的)?(?:中文|俄文|俄语|原文|文字|内容)?(?:翻译|译)(?:成|为|到)?(?:中文|俄语|俄文)?|перевед(?:и|ите)(?: этот текст)? на (?:русский|китайский)(?: язык)?",
    "polish": r"(?:请|帮我)?(?:仅|只)?(?:润色|校对)(?:这段|我的|以下)?(?:俄语|俄文)?(?:原稿|文字|段落)?|(?:отредактируй(?:те)?|вычитай(?:те)?) (?:мой |этот )?текст",
    "plan": r"(?:请|帮我)?(?:只)?(?:列出|列|规划|设计|梳理)(?:一个|一下)?(?:章[节]?|论文|整篇|方法章|引言|结论章)?(?:的)?(?:提纲|大纲|结构|章节职责)|(?:论文|引言|结论章|结果讨论|方法章)(?:应该|一般)?(?:怎么|如何)(?:安排|组织|分章)|(?:предложи(?:те)?|составь(?:те)?) (?:план|структуру)(?: главы| статьи| диссертации)?",
    "compare": r"(?:请|帮我)?(?:比较|对比)(?:两种方法|两个方法|仿真与实测|这两项研究|两篇论文)(?:的可比性|的验证方式)?|сравни(?:те)? (?:методы|условия проверки)",
    "check_evidence": r"(?:请|帮我)?(?:仅|只)?(?:检查|核查|核对)(?:我的|这段)?(?:引用|证据|证据强度|结论依据|验证方式)|(?:仿真结果|仿真)(?:能否|能)(?:写成|证明)实车验证(?:吗)?|проверь(?:те)? (?:обоснованность вывода|аргументацию|ссылки)",
}
# These are complete, bounded requests. Each joined item must be a known dimension.
_REQUEST_PREFIX = r"(?:请帮我|请|帮我)?"
_JOIN = r"\s*(?:与|和|及|以及|、)\s*"
_METHOD = r"(?:方案|方法|模型|控制器)\s*(?:[a-z](?:[0-9]{1,2})?|[甲乙丙丁一二三四]|[0-9]{1,2})"
_COMPARE_AXIS = r"(?:研究职责|职责|分工|用途|试验条件|实验条件|验证方式|可比性|适用范围)"
_EVIDENCE_AXIS = r"(?:证据强度|证据充分性|适用范围|适用条件|结论依据|局限性)"
GRAMMAR["compare"] += (
    rf"|{_REQUEST_PREFIX}(?:比较|对比)(?:一下)?\s*{_METHOD}{_JOIN}{_METHOD}\s*的"
    rf"{_COMPARE_AXIS}(?:{_JOIN}{_COMPARE_AXIS})*")
GRAMMAR["check_evidence"] += (
    rf"|{_REQUEST_PREFIX}(?:检查|核查|核对|评估)(?:一下)?(?:上述|这些|该|本段|这段)?"
    rf"(?:结果|结论|研究|论述)的{_EVIDENCE_AXIS}(?:{_JOIN}{_EVIDENCE_AXIS})*")

# Parse the whole instruction. Only standalone preservation clauses may accompany editing.
EDIT_TARGET = (r"(?:(?:上述|上面(?:的)?|这段|这篇|我的|以下)(?:的)?)?"
               r"(?:俄语|俄文)?(?:原稿|译稿|段落|文字|文本|译文)")
EDIT_ACTION = r"(?:进行)?(?:学术)?(?:润色|校对)"
EDIT_REQUEST = re.compile(
    r"(?:请|请帮我|帮我|直接帮助我|帮助我)?(?:把|将|对)?"
    rf"(?:{EDIT_TARGET}|(?:你|刚才)翻译(?:的)?这段)(?:通过(?:我的)?\s*mcp\s*)?{EDIT_ACTION}")
PRESERVED_ITEM = r"(?:技术信息|技术细节|公式编号|表格编号|附录引用|引用|原意|数值|单位)"
EDIT_CONSTRAINT = re.compile(
    rf"(?:请)?(?:保留(?:全部|所有)?{PRESERVED_ITEM}(?:(?:及|和|与|、){PRESERVED_ITEM})*"
    r"|(?:不|不要|不得|无需)(?:扩写|续写|代写)(?:正文|论文|段落)?)")

def matches_polish(instruction):
    clauses = [part.strip() for part in re.split(r"[,，;；。]", instruction)]
    # A comma may separate the selected draft from the MCP action.
    if len(clauses) > 1 and re.fullmatch(r"通过(?:我的)?\s*mcp\s*" + EDIT_ACTION, clauses[1]):
        clauses = [clauses[0] + clauses[1], *clauses[2:]]
    actions = 0
    for clause in clauses:
        if EDIT_REQUEST.fullmatch(clause) or re.fullmatch(GRAMMAR["polish"], clause):
            actions += 1
        elif not EDIT_CONSTRAINT.fullmatch(clause):
            return False
    return actions == 1

DRAFTING = re.compile(r"(?:代写|续写|扩写|补齐|补写|写成|撰写|写出|生成|起草|替我写|帮我写|写一|写完整|写引言|写正文|напиш|допиш|сгенерир|перепиш.{0,18}в.{0,10}глав|write.{0,20}(?:paper|chapter|introduction))", re.I)
MESSAGES = {"ALLOW": "按本次任务返回知识卡。", "INTENT_REQUIRED": "请提交本轮请求及完整意图申报。",
            "INVALID_REQUEST": "参数无效，请按工具说明提交。", "DIRECT_DRAFTING": "PTB 不提供直接代写或扩写正文。",
            "INTENT_UNCLEAR": "请单独说明所需操作及产物。", "SOURCE_REQUIRED": "请选择要翻译或润色的原稿。",
            "SOURCE_MISMATCH": "请核对原文及源语言、目标语言。", "NO_MATCH": "当前库没有可下发的匹配项。",
            "TASK_EXPIRED": "任务已过期，请重新提交本轮请求。", "LIMIT": "本次访问已达限额。",
            "UNAVAILABLE": "知识服务暂不可用。"}

def clean(text):
    return unicodedata.normalize("NFKC", text).strip().lower()

REQUIRED = ("user_request", "intent", "source_kind", "requested_output", "client_tags")

def malformed(request):
    if not isinstance(request, dict):
        return field_repair("request", "object_required", "把参数放入 request 对象。")
    allowed = (*REQUIRED, "source_text", "source_lang", "target_lang", "task_handle")
    for key in request:
        if key not in allowed:
            return field_repair("request", "unknown_field", f"移除未定义的参数 {key!r}。允许字段为 " + ", ".join(allowed))
    for key, value in request.items():
        if key != "client_tags" and not isinstance(value, str):
            return field_repair(key, "string_required", "使用字符串；无可选值时省略该字段。")
    for key, choices in (("intent", OUTPUTS), ("source_kind", SOURCES),):
        if request[key] not in choices:
            return field_repair(key, "unknown_value", "根据原委托选择一个值：" + "、".join(sorted(choices)))
    tags = request["client_tags"]
    if not isinstance(tags, list) or not 1 <= len(tags) <= 3 or any(t not in SCENES for t in tags):
        repair = field_repair("client_tags", "scene_list_required",
                              "传入含 1 至 3 个标签的 JSON 数组，可选：" + "、".join(SCENES))
        if isinstance(tags, str) and tags in SCENES:
            repair["replace_with"] = [tags]
        return repair
    instruction = clean(request["user_request"])
    if not instruction or len(instruction) > 12000:
        return field_repair("user_request", "instruction_size", "需提供原始指令，规范化后为 1 至 12000 字符；保留完整意图。", automatic=False)
    if len(request.get("source_text", "").strip()) > 8000:
        return field_repair("source_text", "draft_too_long", "所选原稿超过 8000 字符，需缩小处理范围。", automatic=False)
    return None


def inspect(request):
    tags = request["client_tags"]
    intent = request["intent"]
    instruction = clean(request["user_request"])
    original = request.get("source_text", "").strip()
    # Strip only an exact, delimited duplicate of the separately supplied material.
    if original:
        prefix, sep, body = instruction.partition(":")
        if sep and body.strip() == clean(original):
            instruction = prefix
    instruction = instruction.strip(" \n。.!！?？")
    instruction = re.sub(r"^(?:请)?(?:不要|无需|不用)(?:生成|代写|写)(?:论文|正文|文章)[，,。；; ]+", "", instruction)
    if request["requested_output"] == "new_prose":
        return "deny", "DIRECT_DRAFTING"
    matches = matches_polish(instruction) if intent == "polish" else re.fullmatch(GRAMMAR[intent], instruction)
    if not matches and DRAFTING.search(instruction):
        return "deny", "DIRECT_DRAFTING"
    if (not matches or
        not all(t in SCOPES[intent] for t in tags)):
        return "clarify", "INTENT_UNCLEAR"
    if OUTPUTS[intent] != request["requested_output"]:
        return "deny", "INVALID_REQUEST"
    if intent in {"translate", "polish"}:
        if not original or request["source_kind"] != "draft":
            return "clarify", "SOURCE_REQUIRED"
        src, dst = request.get("source_lang"), request.get("target_lang")
        if (src, dst) not in ({("zh","ru"),("ru","zh")} if intent == "translate" else {("ru","ru")}):
            return "clarify", "SOURCE_MISMATCH"
        if not re.search(r"[\u3400-\u9fff]" if src == "zh" else r"[а-яё]", original, re.I):
            return "clarify", "SOURCE_MISMATCH"
        if intent == "translate":
            target = re.search(r"(?:成|为|到|на )?(中文|俄语|俄文|русский|китайский)(?: язык)?$", instruction)
            if target and dst != ("zh" if target[1] in {"中文","китайский"} else "ru"):
                return "clarify", "SOURCE_MISMATCH"
    return "allow", "ALLOW"

class Gateway:
    """Single-process beta; the server serializes calls in one event loop."""
    def __init__(self, database: Path):
        self.database = database
        self.tasks = {}
        self.calls = deque()
        self.workflows = Workflows()

    def lookup(self, request):
        if isinstance(request, dict):
            wording = request.get("user_request")
            if isinstance(wording, str) and len(wording)<=12000:
                # Explicit fabrication or a positive drafting clause blocks the complete commission.
                original = request.get("source_text")
                scoped = clean(wording)
                prefix, sep, body = scoped.partition(":")
                if isinstance(original,str) and sep and body.strip()==clean(original):
                    scoped = prefix
                match = re.search(r"(?:编造|虚构|编一组|捏造)(?:[^，。；]{0,16})(?:数据|结果)", scoped)
                if match:
                    return dict(decision="deny", reason_code="DIRECT_DRAFTING", request_id=secrets.token_hex(8),
                                cards=[], db_query_count=0, task_handle=None, message="请求包含编造数据或结果，已在查库前停止。")
                # A positive standalone drafting command takes precedence over malformed client metadata.
                explicit_draft = re.search(
                    r"(?:^|[，,。；;：:\n])\s*(?:请)?(?:按|根据)?(?:这个|以下|上述)?(?:提纲|题目)?"
                    r"(?:替我|帮我|给我)(?:写|生成|起草)(?:一篇|一段|完整的?)?(?:中文|俄语|俄文)?"
                    r"(?:引言|正文|论文|讨论章|结论章|章节)", scoped)
                if (explicit_draft or request.get("requested_output") == "new_prose" or
                    (request.get("intent")=="workflow" and not stages(scoped) and DRAFTING.search(scoped))):
                    return dict(decision="deny",reason_code="DIRECT_DRAFTING",request_id=secrets.token_hex(8),
                                cards=[],db_query_count=0,task_handle=None,message="请求包含新增或扩写正文，已在查库前停止。")
            if "workflow_id" in request or request.get("intent")=="workflow" or (isinstance(wording,str) and len(wording)<=12000 and stages(wording)):
                return self.workflows.run(request,self._single)
        return self._single(request)

    def _single(self, request):
        now = time.monotonic()
        rid = secrets.token_hex(8)
        query_count = 0

        def count_select(statement):
            nonlocal query_count
            if statement.lstrip().upper().startswith("SELECT "):
                query_count += 1

        def result(decision, reason, cards=None, handle=None):
            return dict(request_id=rid, decision=decision, reason_code=reason,
                        db_query_count=query_count, message=MESSAGES[reason], cards=cards or [], task_handle=handle)
        while self.calls and now - self.calls[0] >= 60:
            self.calls.popleft()
        if len(self.calls) >= 30:
            return result("deny", "LIMIT")
        self.calls.append(now)
        if request is None or (isinstance(request, dict) and any(not request.get(k) for k in REQUIRED)):
            missing = next((k for k in REQUIRED if not (request or {}).get(k)), "request")
            return result("deny", "INTENT_REQUIRED") | {"repair": field_repair(
                missing, "required", "从当前已授权的委托中补全必填字段，保留原话。")}
        repair = malformed(request)
        if repair:
            return result("deny", "INVALID_REQUEST") | {"repair": repair, "message": repair["hint"]}
        decision, reason = inspect(request)
        if reason == "INVALID_REQUEST":
            expected = OUTPUTS[request["intent"]]
            hint = f"当前意图 {request['intent']} 对应 requested_output={expected}。保留用户原话后重试。"
            repair = field_repair("requested_output", "intent_output_mismatch", hint)
            return result(decision, reason) | {"repair": repair | {"replace_with": expected}, "message": hint}
        if decision != "allow":
            return result(decision, reason)
        self.tasks = {k:v for k,v in self.tasks.items() if now-v[0]<1800}
        handle = request.get("task_handle")
        if handle and handle not in self.tasks:
            return result("clarify", "TASK_EXPIRED")
        handle = handle or secrets.token_urlsafe(24)
        seen = self.tasks.get(handle, (now,set()))[1]
        if len(seen) >= 12 or (handle not in self.tasks and len(self.tasks) >= 1000):
            return result("deny", "LIMIT")
        try:
            cards = self.fetch(request["intent"], request["client_tags"], seen, count_select, request["user_request"])
        except sqlite3.Error:
            return result("error", "UNAVAILABLE")
        cards = cards[:min(3, 12-len(seen))]
        self.tasks[handle] = (now, seen | {c["knowledge_id"] for c in cards})
        reply = result("allow" if cards else "no_match", "ALLOW" if cards else "NO_MATCH", cards, handle)
        if request["intent"] in ("translate","polish"):
            reply["glossary_guidance"]=GLOSSARY
        if request["intent"]=="polish":
            reply["editorial_guidance"]=guidance(request["source_text"])
        if request["intent"]=="translate":
            reply["translation_guidance"]="保留原文条件、否定、归属、比较对象、数值、编号和证据强度。"
        return reply

    def fetch(self, intent, tags, seen, count_select, wording):
        from contextlib import closing
        cards = []
        ids = set(seen)
        with closing(sqlite3.connect(self.database.resolve().as_uri()+"?mode=ro", uri=True)) as db:
            db.set_trace_callback(count_select)
            db.row_factory = sqlite3.Row
            if intent in {"compare", "check_evidence"}:
                tags = list(dict.fromkeys(tags))
                if intent == "compare" and re.search("职责|分工|用途|可比性|试验条件|实验条件", wording):
                    tags.extend(["方法选择", "实验验证"])
                if intent == "check_evidence" and re.search("证据强度|适用范围|适用条件|证据充分性", wording):
                    tags.extend(["实验验证", "边界与归属"])
                tags = list(dict.fromkeys(tags))
                marks = ",".join("?" for _ in tags)
                rows = db.execute(f"""SELECT scenario, stage, knowledge_id, kind, move,
                    requirements, misuse, evidence_basis, independent_support, template, grammar
                    FROM scene_route WHERE scenario IN ({marks})""", tags)
                priority = (("方法选择/论证步骤", "比较边界", "对照证据", "替代与基线", "民用比较")
                            if intent == "compare" else
                            ("适用边界", "分层验证", "适用条件", "必要证据", "结论限定"))
                def rank(row):
                    scoped = row["scenario"] + "/" + row["kind"]
                    key = scoped if scoped in priority else row["kind"]
                    return (priority.index(key) if key in priority else len(priority),
                            tags.index(row["scenario"]), row["stage"], row["knowledge_id"])
                ranked = sorted((r for r in rows if r["kind"] in TYPES[intent]
                                 and r["knowledge_id"] not in ids), key=rank)
                # Cover distinct research moves before adding a second card of the same kind.
                kinds = set()
                for distinct in (True, False):
                    for row in ranked:
                        if row["knowledge_id"] in ids or (distinct and row["kind"] in kinds):
                            continue
                        cards.append({k: row[k] for k in row.keys() if k not in ("scenario", "stage")})
                        kinds.add(row["kind"])
                        ids.add(row["knowledge_id"])
                        if len(cards) == 3:
                            return cards
                return cards
            for tag in tags:
                for row in db.execute("""SELECT knowledge_id, kind, move, requirements, misuse,
                    evidence_basis, independent_support, template, grammar FROM scene_route
                    WHERE scenario=? ORDER BY stage""", (tag,)):
                    if row["kind"] in TYPES[intent] and row["knowledge_id"] not in ids:
                        cards.append(dict(row))
                        ids.add(row["knowledge_id"])
                        if len(cards) == 3:
                            return cards
        return cards
