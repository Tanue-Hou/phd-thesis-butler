"""PTB beta: positive command grammar; unrecognised instructions require clarification."""
from __future__ import annotations
import re
import secrets
import sqlite3
import time
import unicodedata
from collections import deque
from pathlib import Path
from editorial import GLOSSARY, Workflows, guidance, stages

OUTPUTS = {"translate": "translation", "polish": "revision", "plan": "outline",
           "compare": "comparison", "check_evidence": "evidence_feedback"}
SCENES = ("篇章布局", "方法选择", "实验验证", "综述分歧", "结果与不确定性", "边界与归属", "目标与假设")
SCOPES = {"plan": set(SCENES), "compare": {"实验验证", "方法选择", "综述分歧", "结果与不确定性"},
          "check_evidence": set(SCENES), "translate": set(SCENES), "polish": set(SCENES)}
SOURCES = {"draft", "outline", "data", "prior_cards", "none"}
TYPES = {
    "translate": {"俄语句式", "俄语语用"}, "polish": {"俄语句式", "俄语语用"},
    "plan": {"整篇布局", "双端依赖", "篇章衔接", "章间衔接", "论证步骤", "篇章布局", "顺序与计划"},
    "compare": {"比较边界", "民用比较", "替代与基线", "对照证据", "分层验证", "适用边界", "论证步骤"},
    "check_evidence": {"必要证据", "民用证据", "对照证据", "分层验证", "适用边界", "结论限定", "论证步骤"},
}
# Full-match the instruction. A pasted draft is data only when separately selected.
GRAMMAR = {
    "translate": r"(?:请|帮我)?(?:把|将)?(?:这段|这句|以下|下面的|我的)?(?:中文|俄文|俄语|原文|文字|内容)?(?:翻译|译)(?:成|为|到)?(?:中文|俄语|俄文)?|перевед(?:и|ите)(?: этот текст)? на (?:русский|китайский)(?: язык)?",
    "polish": r"(?:请|帮我)?(?:仅|只)?(?:润色|校对)(?:这段|我的|以下)?(?:俄语|俄文)?(?:原稿|文字|段落)?|(?:отредактируй(?:те)?|вычитай(?:те)?) (?:мой |этот )?текст",
    "plan": r"(?:请|帮我)?(?:只)?(?:列出|列|规划|设计|梳理)(?:一个|一下)?(?:章[节]?|论文|整篇|方法章|引言|结论章)?(?:的)?(?:提纲|大纲|结构|章节职责)|(?:论文|引言|结论章|结果讨论|方法章)(?:应该|一般)?(?:怎么|如何)(?:安排|组织|分章)|(?:предложи(?:те)?|составь(?:те)?) (?:план|структуру)(?: главы| статьи| диссертации)?",
    "compare": r"(?:请|帮我)?(?:比较|对比)(?:两种方法|两个方法|仿真与实测|这两项研究|两篇论文)(?:的可比性|的验证方式)?|сравни(?:те)? (?:методы|условия проверки)",
    "check_evidence": r"(?:请|帮我)?(?:仅|只)?(?:检查|核查|核对)(?:我的|这段)?(?:引用|证据|证据强度|结论依据|验证方式)|(?:仿真结果|仿真)(?:能否|能)(?:写成|证明)实车验证(?:吗)?|проверь(?:те)? (?:обоснованность вывода|аргументацию|ссылки)",
}
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

def inspect(request):
    if request is None:
        return "deny", "INTENT_REQUIRED"
    if not isinstance(request, dict):
        return "deny", "INVALID_REQUEST"
    required = ("user_request", "intent", "source_kind", "requested_output", "client_tags")
    if any(not request.get(k) for k in required):
        return "deny", "INTENT_REQUIRED"
    if set(request) - set(required) - {"source_text", "source_lang", "target_lang", "task_handle"}:
        return "deny", "INVALID_REQUEST"
    if any(not isinstance(v, str) for k, v in request.items() if k != "client_tags"):
        return "deny", "INVALID_REQUEST"
    tags = request["client_tags"]
    intent = request["intent"]
    if (intent not in OUTPUTS or request["source_kind"] not in SOURCES or
        not isinstance(tags, list) or not 1 <= len(tags) <= 3 or
        any(not isinstance(t, str) or t not in SCENES for t in tags) or
        request["requested_output"] not in {*OUTPUTS.values(), "new_prose"}):
        return "deny", "INVALID_REQUEST"
    instruction = clean(request["user_request"])
    original = request.get("source_text", "").strip()
    if not instruction or len(instruction) > 12000 or len(original) > 8000:
        return "deny", "INVALID_REQUEST"
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
    if (not matches or OUTPUTS[intent] != request["requested_output"] or
        not all(t in SCOPES[intent] for t in tags)):
        return "clarify", "INTENT_UNCLEAR"
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
                if request.get("intent")=="workflow" and not stages(scoped) and DRAFTING.search(scoped):
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
        decision, reason = inspect(request)
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
            cards = self.fetch(request["intent"], request["client_tags"], seen, count_select)
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

    def fetch(self, intent, tags, seen, count_select):
        from contextlib import closing
        cards = []
        ids = set(seen)
        with closing(sqlite3.connect(self.database.resolve().as_uri()+"?mode=ro", uri=True)) as db:
            db.set_trace_callback(count_select)
            db.row_factory = sqlite3.Row
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
