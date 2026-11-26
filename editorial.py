"""Built-in editorial guidance and sequential translation/editing tasks."""
import hashlib
import json
import os
import re
import secrets
import time
import unicodedata
from collections import Counter

DOC_COMMIT = "6c74d36c2e4eba6d8dead679016b4f84a556ceaf"
GLOSSARY = {
    "path":"术语对应表.md",
    "columns":["中文术语","首选俄语译名","缩写或符号","适用条件或出处"],
    "instruction":"终稿后提醒：建议在论文工作目录建立并持续维护《术语对应表.md》，后续章节优先沿用已确认的译名。已有表则复用，有冲突列出供作者确认；写入、更新前取得用户同意。",
}

RULES = {
    "method": ("第1、4节", "先交代方法选择与模型职责，再写实现；保留“仅用于”等范围限定。"),
    "result": ("第1、3、6节", "先陈述有依据的发现；保留真实下降、比较基准和不显著结果。"),
    "discussion": ("第1、5、6节", "分别归属于观察、解释和推测；保留证据强度与适用条件。"),
    "fidelity": ("第2、6节", "去除译者自行添加的道歉、自贬和辩解；忠实保留否定、条件、归属、数值和引用。"),
}

def guidance(draft=None):
    roles = []
    for role, pattern in [
        ("method", r"метод|модел|вариант|方案|方法"),
        ("result", r"сни[жз]|значим|результат|下降|显著|结果"),
        ("discussion", r"возмож|предполож|обсужд|可能|推测|讨论"),
    ]:
        if draft is None or re.search(pattern, draft, re.I):
            roles.append(role)
    roles.append("fidelity")
    rev = os.getenv("PTB_RELEASE_COMMIT", DOC_COMMIT)
    if not re.fullmatch("[0-9a-f]{40}", rev):
        rev = DOC_COMMIT
    base = f"https://github.com/Tanue-Hou/phd-thesis-butler/blob/{rev}/docs/editorial-policy.md"
    return {"version":"1.0","source":"anti-defensive-writing《学术写作原则（The Press-Release Principle）》",
            "rules":[{"id":r,"sections":RULES[r][0],"instruction":RULES[r][1],"url":base+"#"+r} for r in roles],
            "display":"终稿后用一行“编辑依据”列出实际采用的规则、原章节和可点击链接。"}

STAGES = {"翻译":"translate","翻一下":"translate","译成俄语":"translate","润色":"polish",
          "顺一顺":"polish","验证":"check_evidence","检查":"check_evidence","核对":"check_evidence"}
def stages(text):
    # Recognize every token of the instruction, never authorize from keywords alone.
    rest = re.sub(r"\s+", "", unicodedata.normalize("NFKC", text).lower())
    grammar = r"帮我|请|将|把|上述|这段|这份|中文|原稿|文本|学术|俄语|成|为|译稿|进行|翻成俄语|翻译|翻一下|译成俄语|润色|顺一顺|验证|检查|核对|通过|我的|云端|知识库|mcp|然后|最后|先|再|并|和|与|及|一下|[,。;、.!]|不要扩写正文|不扩写正文"
    tokens = re.findall(grammar, rest)
    if "".join(tokens) != rest:
        return []
    found = [STAGES.get(t,"translate") for t in tokens if t in STAGES or t=="翻成俄语"]
    return found if found in (["translate","polish"], ["translate","polish","check_evidence"]) else []

def fingerprint(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def references(text):
    # Compare printed identifiers, including appendix subdivisions, independently of spacing.
    norm = unicodedata.normalize("NFKC",text)
    return Counter(re.sub(r"\s+","",v) for v in re.findall(
        r"(?<![\d.])\d+(?:\.(?:[A-Za-z]|\d+[A-Za-z]?))+(?:\s*\(\s*\d+\s*\))?",norm))

def field_repair(field, reason, hint, *, automatic=True):
    """Field and reason are server-defined codes, safe to record in audit logs."""
    return {"field": field, "reason": reason, "hint": hint, "auto_retry": automatic}


class Workflows:
    def __init__(self):
        self.active = {}

    def run(self, request, single):
        now = time.monotonic()
        self.active = {k:v for k,v in self.active.items() if now-v["time"]<1800}
        def failure(reason, message, decision="clarify", repair=None):
            return dict(request_id=secrets.token_hex(8),decision=decision,reason_code=reason,
                        message=message,cards=[],db_query_count=0,task_handle=None,
                        **({"repair": repair} if repair else {}))
        token=request.get("workflow_id")
        if token is None:
            wording=request.get("user_request","")
            seq=stages(wording) if isinstance(wording,str) else []
            if not seq or len(wording)>12000:
                return failure("INTENT_UNCLEAR","请说明对所选中文原稿的操作，例如翻译、润色并核对。")
            if request.get("requested_output")=="new_prose":
                return failure("DIRECT_DRAFTING","请求产物包含新增正文，已在查库前停止。","deny")
            if request.get("source_lang")!="zh" or request.get("target_lang")!="ru":
                return failure("SOURCE_MISMATCH","本组合需要中文原稿和俄语目标；请核对语种。")
            if request.get("intent") not in ("workflow","translate") or request.get("requested_output") not in ("translation","revision","workflow"):
                return failure("INTENT_UNCLEAR","所声明的操作或产物与该组合任务不一致。")
            if len(self.active)>=1000:
                return failure("LIMIT","活动任务已满，请稍后重试。","deny")
            args=dict(request,intent="translate",requested_output="translation",user_request="翻译成俄语")
            out=single(args)
            if out["decision"] not in ("allow","no_match"):
                return out
            token=secrets.token_urlsafe(24)
            flow={"time":now,"seq":seq,"source":request["source_text"],"index":1,"cache":{},
                  "handle":out["task_handle"],"tags":args["client_tags"]}
            self.active[token]=flow
            stage="translate"
        else:
            flow=self.active.get(token) if isinstance(token,str) else None
            if not flow:
                return failure("TASK_EXPIRED","任务不存在或已过期，请重新提交完整委托。")
            if set(request)-{"workflow_id","stage","draft","applied_rules","reviewed"}:
                return failure("TASK_CHANGED","后续步骤只接收本任务的稿件与回执；新增委托须整体审核。")
            stage=request.get("stage")
            stamp=fingerprint(request)
            if stamp in flow["cache"]:
                return dict(flow["cache"][stamp],replayed=True,db_query_count=0)
            expected=(flow["seq"]+["receipt"])[flow["index"]:]
            if not expected or stage!=expected[0]:
                return failure("STAGE_ORDER","请按上次返回的 next_step 顺序继续。")
            if stage=="receipt":
                ids=request.get("applied_rules")
                if not isinstance(ids,list) or any(not isinstance(i,str) or i not in flow.get("rules", ()) for i in ids):
                    return failure("INVALID_REQUEST","请列出实际采用的已下发规则编号，可为空。", repair=field_repair("applied_rules", "issued_rule_list_required", "传入实际采用的已下发规则编号数组；没有采用则传 []。"))
                reviewed=request.get("reviewed")
                if type(reviewed) is not bool or (reviewed and "check_evidence" not in flow["seq"]):
                    return failure("INVALID_REQUEST","请如实报告是否已完成原稿核对。", repair=field_repair("reviewed", "review_status_required", "传入 JSON 布尔值；只有本流程包含核对且确实完成时传 true，否则传 false。"))
                out=dict(request_id=secrets.token_hex(8),decision="allow",reason_code="RECEIPT",cards=[],
                         db_query_count=0,client_report={"applied_rules":ids,"reviewed":reviewed})
            else:
                draft=request.get("draft")
                if not isinstance(draft,str) or not re.search("[а-яё]",draft,re.I) or len(draft)>8000:
                    return failure("SOURCE_REQUIRED","请客户端传入本步实际俄语稿件。")
                polish=stage=="polish"
                args=dict(user_request="润色" if polish else "核对证据",intent=stage,source_kind="draft",
                          requested_output="revision" if polish else "evidence_feedback",client_tags=flow["tags"],
                          task_handle=flow["handle"], source_text=draft)
                if polish:
                    args.update(source_text=draft,source_lang="ru",target_lang="ru")
                out=single(args)
                if out["decision"] not in ("allow","no_match"):
                    return out
                if polish:
                    flow["rules"]=[r["id"] for r in out["editorial_guidance"]["rules"]]
                else:
                    a,b=references(flow["source"]),references(draft)
                    out["reference_check"]={"missing":list((a-b).elements()),"added":list((b-a).elements()),
                                            "scope":"仅比较稿件编号；请客户端逐项核对原意，表内值待原件确认。"}
            flow["index"]+=1
        next_stage=(flow["seq"]+["receipt",None])[flow["index"]]
        out.update(workflow_id=token,stage=stage,next_step=next_stage)
        out["continue_instruction"]={"polish":"忠实翻译原稿，传入 workflow_id、stage=polish、draft=俄译。",
          "check_evidence":"应用 editorial_guidance，保留编辑依据。传入 workflow_id、stage=check_evidence、draft=润色终稿。",
          "receipt":"完成所请求的编辑与核对后传入 workflow_id、stage=receipt、applied_rules 和 reviewed 布尔值，再呈现终稿、核对结果和编辑依据。",
          None:"向用户交付终稿，附所用规则链接及核对范围。"}[next_stage]
        out["glossary_guidance"]=GLOSSARY
        flow["time"]=now
        if stage!="translate":
            flow["cache"][stamp]=out
        return out
