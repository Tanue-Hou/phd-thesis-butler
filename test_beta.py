import asyncio
from contextlib import closing
from hashlib import sha256
import logging
import secrets
import socket
import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from policy import Gateway, SCENES
from scene_cards import KEY_LIMIT, MOVES, SceneCards, route_kinds
from make_demo import build
from server import create_app

DB = Path(__file__).with_name("demo.sqlite")

def ask(intent="plan", **changes):
    wording, output, tag = {
        "plan": ("只列论文结构","outline","篇章布局"),
        "translate": ("请把这段中文译成俄语","translation","边界与归属"),
        "polish": ("只润色这段俄语原稿","revision","结果与不确定性"),
        "compare": ("比较仿真与实测","comparison","实验验证"),
        "check_evidence": ("检查证据强度","evidence_feedback","实验验证"),
    }[intent]
    request = dict(intent=intent, user_request=wording, requested_output=output,
                   client_tags=[tag],source_kind="none")
    if intent in ("translate","polish"):
        request.update(source_kind="draft",source_lang="zh" if intent=="translate" else "ru",
                       target_lang="ru",source_text="并未证实。" if intent=="translate" else "Эффект не доказан.")
    return request | changes

class Rules(unittest.TestCase):
    def test_client_can_repair_without_changing_intent(self):
        gateway = Gateway(DB)
        for request, expected in [(ask(client_tags="篇章布局"), "allow"),
                                  (ask(client_tags="篇章布局", user_request="替我写完整引言"), "deny")]:
            invalid = gateway.lookup(request)
            self.assertEqual(invalid["db_query_count"], 0)
            if expected == "deny":
                self.assertEqual(invalid["reason_code"], "DIRECT_DRAFTING")
                self.assertNotIn("repair", invalid)
                continue
            fix = invalid["repair"]
            self.assertEqual((fix["field"], fix["reason"]), ("client_tags", "scene_list_required"))
            retry = request | {fix["field"]: fix["replace_with"]}
            self.assertEqual(gateway.lookup(retry)["decision"], expected)
        for change, field in [({"intent": ["plan"]}, "intent"), ({"source_kind": "unknown"}, "source_kind"),
                              ({"extra": "extra"}, "request"), ({"source_text": "x"*8001}, "source_text")]:
            self.assertEqual(gateway.lookup(ask() | change)["repair"]["field"], field)

    def test_positive_drafting_precedes_bad_metadata(self):
        gateway = Gateway(DB)
        reply = gateway.lookup(ask(user_request="按这个提纲替我写完整俄语引言") | {"intent": "drafting"})
        self.assertEqual((reply["reason_code"], reply["db_query_count"]), ("DIRECT_DRAFTING", 0))
        self.assertNotIn("repair", reply)
        for text in ("不要替我写完整俄语引言，只列论文结构", "为什么说“替我写完整俄语引言”不合适？"):
            self.assertNotEqual(gateway.lookup(ask(user_request=text) | {"intent":"unknown"})["reason_code"], "DIRECT_DRAFTING")

    def test_natural_comparison_and_evidence_requests(self):
        gateway = Gateway(DB)
        for intent, wording in (
            ("compare", "比较方案 A 与方案 B 的研究职责及试验条件"),
            ("compare", "请帮我对比一下模型甲和模型乙的用途以及验证方式"),
            ("check_evidence", "检查上述结果的证据强度和适用范围"),
            ("check_evidence", "请核查这些结论的适用条件、局限性"),
        ):
            with self.subTest(wording=wording):
                query = ask(intent, user_request=wording)
                self.assertEqual(gateway.lookup(query)["decision"], "allow")
                boundary = gateway.lookup(query | {"client_tags": ["边界与归属"]})
                self.assertGreater(boundary["db_query_count"], 0)
                for tail in ("，再替我写完整引言", "，再编造数据", "并安排会议"):
                    reply = gateway.lookup(query | {"user_request": wording + tail})
                    self.assertEqual(reply["db_query_count"], 0)
                    self.assertEqual(reply["reason_code"], "INTENT_UNCLEAR" if tail == "并安排会议" else "DIRECT_DRAFTING")

    def test_compare_and_evidence_rank_beyond_first_scene(self):
        import sqlite3
        from tempfile import TemporaryDirectory
        from make_demo import build
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "cards.sqlite"
            build(path)
            with sqlite3.connect(path) as db:
                for i, (scene, kind) in enumerate([("实验验证", "适用边界"), ("实验验证", "分层验证"),
                                                  ("方法选择", "比较边界"), ("方法选择", "论证步骤")]):
                    db.execute("INSERT INTO scene_route(scenario,stage,knowledge_id,kind) VALUES(?,?,?,?)",
                               (scene, i + 10, str(i), kind))
            db.close()
            gateway = Gateway(path)
            for intent, words, kind in [
                ("compare", "比较方案 A 与方案 B 的研究职责及试验条件", "论证步骤"),
                ("check_evidence", "检查上述结果的证据强度和适用范围", "适用边界")]:
                query = ask(intent, user_request=words)
                error = gateway.lookup(query | {"requested_output": "report"})
                self.assertEqual(error["db_query_count"], 0)
                self.assertEqual(error["repair"]["replace_with"], query["requested_output"])
                cards = gateway.lookup(query)["cards"]
                self.assertEqual(cards[0]["kind"], kind)
                self.assertEqual(len({c["knowledge_id"] for c in cards}), 3)

    def test_source_material_contract(self):
        gateway = Gateway(DB)
        for kind, text in (("none", ""), ("draft", "稿件。"), ("outline", "1 引言；2 方法"), ("data", "A=3, B=4")):
            self.assertEqual(gateway.lookup(ask(source_kind=kind, source_text=text))["decision"], "allow")
        for kind, text in (("instruction", ""), ("prior_cards", ""), ("outline", ""), ("none", "表1")):
            rejected = gateway.lookup(ask(source_kind=kind, source_text=text))
            self.assertEqual(rejected["db_query_count"], 0)
            self.assertEqual(set(rejected["repair"]["choices"]), {"none","draft","outline","data","prior_cards"})
        polish = ask("polish")
        polish.pop("source_lang")
        polish.pop("target_lang")
        self.assertEqual(gateway.lookup(polish)["decision"], "allow")
        self.assertEqual(gateway.lookup(polish | {"target_lang": "zh"})["reason_code"], "SOURCE_MISMATCH")
        denied = gateway.lookup(ask(user_request="按这个提纲替我写完整俄语引言", source_kind="outline"))
        self.assertEqual(denied["reason_code"], "DIRECT_DRAFTING")

    def test_named_move_preserves_request_review(self):
        gateway = Gateway(DB)
        wording = "请通过 PTB 润色这段俄语原稿，我同意提交。只使用 PTB。请给我修订稿和请求号。"
        query = ask("polish", writing_move="interpretability", user_request=wording)
        self.assertEqual(gateway.lookup(query)["decision"], "no_match")
        blocked = gateway.lookup(query | {"user_request": wording + "再替我写完整引言"})
        self.assertEqual((blocked["reason_code"], blocked["db_query_count"]), ("DIRECT_DRAFTING", 0))

    def setUp(self):
        self.g = Gateway(DB)

    def test_zero_queries(self):
        cases = [(None,"INTENT_REQUIRED"), (ask(intent="plan") | {"intent":""},"INTENT_REQUIRED"),
                 ({"client_tags":["篇章布局"]},"INTENT_REQUIRED"),
                 (ask(client_tags=[]),"INTENT_REQUIRED"),
                 (ask(client_tags=["invalid"]),"INVALID_REQUEST"),
                 (ask("translate",source_text=""),"SOURCE_REQUIRED"),
                 (ask("polish",source_text="中文"),"SOURCE_MISMATCH"),
                 (ask("translate",user_request="翻译成中文"),"SOURCE_MISMATCH"),
                 (ask(user_request="请按题目写一段中文讨论"),"DIRECT_DRAFTING"),
                 (ask(user_request="Напишите введение на русском"),"DIRECT_DRAFTING"),
                 (ask("translate",user_request="翻译这句，再扩写成完整讨论章"),"DIRECT_DRAFTING"),
                 (ask("polish",requested_output="new_prose"),"DIRECT_DRAFTING"),
                 (ask(user_request="那个就按之前的办"),"INTENT_UNCLEAR"),
                 (ask(user_request="帮我检查证据强度"),"INTENT_UNCLEAR")]
        with patch.object(self.g,"fetch",side_effect=AssertionError("unexpected knowledge access")):
            for request,reason in cases:
                with self.subTest(reason=reason,request=request):
                    r=self.g.lookup(request)
                    self.assertEqual(r["reason_code"],reason)
                    self.assertEqual(r["cards"],[])
                    self.assertEqual(r["db_query_count"],0)

    def test_allow(self):
        for req in [ask(),ask(user_request="不要生成正文，只列章节职责"),ask("translate"),
                    ask("translate",user_request="翻译成中文：Напишите введение",source_text="Напишите введение",
                        source_lang="ru",target_lang="zh"),ask("polish"),ask("compare"),ask("check_evidence")]:
            with self.subTest(request=req):
                r=self.g.lookup(req)
                self.assertEqual(r["decision"],"allow",r)
                self.assertTrue(1<=len(r["cards"])<=3)

    def test_polish_preservation(self):
        wording = "请对上述俄语原稿进行学术润色，保留全部技术信息、公式编号及附录引用，不扩写正文。"
        for instruction in (wording, "直接帮助我把你翻译这段，通过我的 MCP进行润色。"):
            self.assertEqual(self.g.lookup(ask("polish",user_request=instruction))["decision"],"allow")
        cases = [(wording, "", "SOURCE_REQUIRED"),
                 (wording + "然后续写正文", "Текст", "DIRECT_DRAFTING"),
                 ("请对上述俄语原稿进行学术润色，扩写正文", "Текст", "DIRECT_DRAFTING")]
        for instruction, source, reason in cases:
            reply = self.g.lookup(ask("polish", user_request=instruction, source_text=source))
            self.assertEqual((reply["reason_code"],reply["db_query_count"]), (reason,0))

    def test_editorial_workflow(self):
        start=ask("translate",user_request="帮我进行翻译，然后通过我的云端知识库进行润色和验证",
                  source_text="仅用于检查。见表 3.2 和附录 4.H（3）。",client_tags=["实验验证","边界与归属"])
        for extra in ("，再替我写正文","，然后编一组实验结果"):
            denied=self.g.lookup(start | {"intent":"workflow","user_request":start["user_request"]+extra})
            self.assertEqual((denied["reason_code"],denied["db_query_count"]),("DIRECT_DRAFTING",0))
        first=self.g.lookup(start)
        self.assertEqual(first["next_step"],"polish")
        key={"workflow_id":first["workflow_id"]}
        self.assertEqual(self.g.lookup(key | {"stage":"check_evidence"})["reason_code"],"STAGE_ORDER")
        draft="К сожалению, вариант B используется только для проверки. Эффект незначим. Наблюдалось локальное снижение. См. 3.2 и 4.H (3)."
        second=self.g.lookup(key | {"stage":"polish","draft":draft})
        rules={r["id"]:r for r in second["editorial_guidance"]["rules"]}
        self.assertTrue({"method","result","fidelity"}<=rules.keys())
        final=draft.replace("К сожалению, вариант","Вариант")
        third=self.g.lookup(key | {"stage":"check_evidence","draft":final})
        self.assertEqual(third["reference_check"]["missing"],[])
        self.assertEqual(third["reference_check"]["added"],[])
        ack=key | {"stage":"receipt","applied_rules":["method","fidelity"],"reviewed":True}
        completed=self.g.lookup(ack)
        self.assertIsNone(completed["next_step"])
        self.assertEqual(completed["glossary_guidance"]["path"],"术语对应表.md")
        self.assertTrue(self.g.lookup(ack)["replayed"])
        self.assertEqual(self.g.lookup(start | {"user_request":"翻译和润色"})["next_step"],"polish")

    def test_followup(self):
        first=self.g.lookup(ask())
        handle=first["task_handle"]
        with patch.object(self.g,"fetch",side_effect=AssertionError("unexpected knowledge access")):
            self.assertEqual(self.g.lookup(ask(task_handle=handle,user_request="把刚才提纲写成俄语正文"))["decision"],"deny")
            self.assertEqual(self.g.lookup(ask(task_handle="expired"))["reason_code"],"TASK_EXPIRED")
        second=self.g.lookup(ask(task_handle=handle))
        self.assertEqual(second["decision"],"no_match")
        self.assertGreater(second["db_query_count"],0)
        self.assertFalse({c["knowledge_id"] for c in first["cards"]} &
                         {c["knowledge_id"] for c in second["cards"]})

    def test_no_match_and_failure(self):
        with patch.object(self.g,"fetch",return_value=[]):
            self.assertEqual(self.g.lookup(ask())["decision"],"no_match")
        import sqlite3
        with patch.object(self.g,"fetch",side_effect=sqlite3.OperationalError("synthetic")):
            self.assertEqual(self.g.lookup(ask())["cards"],[])

    def test_session_limits(self):
        with patch.object(self.g,"fetch",side_effect=AssertionError("unexpected knowledge access")):
            self.g.tasks["used"]=(time.monotonic(),set(range(12)))
            self.assertEqual(self.g.lookup(ask(task_handle="used"))["reason_code"],"LIMIT")
            self.g.calls.extend([time.monotonic()]*30)
            self.assertEqual(self.g.lookup(ask())["reason_code"],"LIMIT")

class PrivacyRouting(unittest.TestCase):
    def test_task_binding_pagination_and_limits_across_all_scenes(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "test.sqlite"
            build(database)
            with sqlite3.connect(database) as db:
                db.executemany("INSERT INTO scene_route VALUES (?,?,?,?,?,?,?,?,?,?,?)", [
                    (scene, stage, f"fixture-{index}-{stage}", "合成知识类别",
                     tuple(MOVES.values())[stage], "", "", "", 1, "", "")
                    for index, scene in enumerate(SCENES) for stage in range(5 if index == 0 else len(MOVES))
                ])
            db.close()
            gateway = Gateway(database)
            route = SceneCards(gateway, route_kinds(database))
            request = {"intent": "polish", "scene": SCENES[0], "kind": "合成知识类别"}
            first = route.lookup(request)
            self.assertEqual(len(first["cards"]), 3)
            self.assertTrue(first["has_more"])
            handle = first["task_handle"]
            follow = request | {"task_handle": handle}
            self.assertEqual(len(route.lookup(follow)["cards"]), 2)
            self.assertEqual(route.lookup(follow)["decision"], "no_match")
            self.assertEqual(SceneCards(Gateway(database), route.kinds).lookup(follow)["reason_code"],
                             "TASK_EXPIRED")
            for scene in SCENES[1:]:
                for move in MOVES:
                    request = {"intent": "translate", "scene": scene,
                               "kind": "合成知识类别", "writing_move": move}
                    reply = route.lookup(request)
                    if len(route.released) < KEY_LIMIT:
                        self.assertEqual(reply["cards"][0]["move"], MOVES[move])
                    if reply["decision"] == "deny":
                        self.assertEqual(reply["reason_code"], "LIMIT")
            self.assertEqual(len(route.released), KEY_LIMIT)
            with patch("scene_cards.time.monotonic", return_value=time.monotonic() + 1801):
                self.assertEqual(route.lookup(follow)["reason_code"], "TASK_EXPIRED")
            gateway.calls.clear()
            gateway.calls.extend([time.monotonic()] * 30)
            self.assertEqual(route.lookup(follow)["db_query_count"], 0)

    def test_same_task_cannot_release_more_than_twelve_cards(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "test.sqlite"
            build(database)
            with sqlite3.connect(database) as db:
                db.executemany("INSERT INTO scene_route VALUES (?,?,?,?,?,?,?,?,?,?,?)", [
                    (SCENES[0], index, f"fixture-{index}", "合成知识类别",
                     "", "", "", "", 1, "", "")
                    for index in range(15)
                ])
            db.close()
            route = SceneCards(Gateway(database), route_kinds(database))
            request = {"intent": "plan", "scene": SCENES[0], "kind": "合成知识类别"}
            for _ in range(4):
                reply = route.lookup(request)
                request["task_handle"] = reply["task_handle"]
                self.assertEqual(len(reply["cards"]), 3)
            self.assertFalse(reply["has_more"])
            self.assertEqual(route.lookup(request)["reason_code"], "LIMIT")

class Transport(unittest.TestCase):
    def test_real_mcp(self):
        self.run_transport(False)

    def test_labels_only_mcp(self):
        with tempfile.TemporaryDirectory() as directory:
            token = "test-key-001"
            registry = Path(directory) / "keys.sqlite"
            events = Path(directory) / "events.sqlite"
            with closing(sqlite3.connect(registry)) as db, db:
                db.execute("CREATE TABLE keys(id, owner, digest, active)")
                db.execute("INSERT INTO keys VALUES (?, ?, ?, ?)",
                           ("test-slot", "test-user", sha256(token.encode()).hexdigest(), 1))
            self.run_transport(True, token=token, registry=registry, events=events)
            with closing(sqlite3.connect(events)) as db:
                self.assertIn(("scene_cards", "deny", "INVALID_REQUEST", 0, 0),
                              db.execute("SELECT action, decision, reason, queries, cards FROM events").fetchall())
            self.assertNotIn(b"PRIVATE-TEXT-SENTINEL", events.read_bytes())

    def run_transport(self, labels_only, *, token=None, registry=None, events=None):
        token = token or secrets.token_urlsafe(32)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1",0))
            app=create_app(token,DB,listener.getsockname()[1], demo=True, labels_only=labels_only,
                           registry=registry, events=events)
            server=uvicorn.Server(uvicorn.Config(app,access_log=False,log_level="error"))
            thread=threading.Thread(target=server.run,kwargs={"sockets":[listener]},daemon=True)
            thread.start()
            try:
                for _ in range(100):
                    if server.started: break
                    time.sleep(.05)
                self.assertTrue(server.started)
                asyncio.run(self.client(listener.getsockname()[1],token,labels_only))
            finally:
                server.should_exit=True
                thread.join(5)
    async def client(self,port,token,labels_only):
        url=f"http://127.0.0.1:{port}/mcp"
        async with httpx.AsyncClient(trust_env=False) as anonymous:
            self.assertEqual((await anonymous.post(url,json={})).status_code,401)
        async with httpx.AsyncClient(headers={"Authorization":"Bearer "+token},trust_env=False) as http:
            async with streamable_http_client(url,http_client=http) as (read,write,_):
                async with ClientSession(read,write) as session:
                    await session.initialize()
                    tools = {tool.name: tool for tool in (await session.list_tools()).tools}
                    allowed = {"ptb_scene_cards"} if labels_only else {"ptb_lookup", "ptb_scene_cards"}
                    self.assertEqual(set(tools), allowed)
                    tool_schema = tools["ptb_scene_cards"].inputSchema
                    self.assertFalse(tool_schema["additionalProperties"])
                    self.assertEqual(tool_schema["required"], ["request"])
                    schema = tool_schema["properties"]["request"]
                    self.assertEqual(schema["required"], ["intent", "scene"])
                    self.assertFalse(schema["additionalProperties"])
                    self.assertEqual(set(schema["properties"]),
                                     {"intent", "scene", "kind", "writing_move", "task_handle"})
                    labels = {"intent": "plan", "scene": "篇章布局"}
                    marker = "PRIVATE-TEXT-SENTINEL"
                    response = await session.call_tool("ptb_scene_cards", {"request": labels, "source_text": marker})
                    self.assertEqual(response.structuredContent["reason_code"], "INVALID_REQUEST")
                    self.assertEqual(response.structuredContent["db_query_count"], 0)
                    self.assertNotIn(marker, str(response))
                    for extra in ("user_request", "source_text", "summary", "path", "filename", "quote"):
                        with self.assertNoLogs(level="WARNING"):
                            response = await session.call_tool("ptb_scene_cards", {"request": labels | {extra: marker}})
                        denied = response.structuredContent
                        self.assertEqual(denied["reason_code"], "INVALID_REQUEST")
                        self.assertEqual(denied["db_query_count"], 0)
                        self.assertNotIn(marker, str(response))
                    for invalid in ({"intent": marker}, {"scene": [marker]}, {"kind": marker},
                                    {"writing_move": marker}, {"task_handle": marker}):
                        response = await session.call_tool("ptb_scene_cards", {"request": labels | invalid})
                        self.assertEqual(response.structuredContent["db_query_count"], 0)
                        self.assertNotIn(marker, str(response))
                    response = await session.call_tool("ptb_scene_cards", {"request": labels})
                    self.assertEqual(response.structuredContent["decision"], "allow")
                    if labels_only:
                        response = await session.call_tool("ptb_lookup", {})
                        self.assertTrue(response.isError)
                        return
                    for request,expected in [(ask(),"allow"),(ask("translate"),"allow"),({}, "deny"),(ask("translate",source_text=""),"clarify"),
                                              (ask(user_request="按这个提纲替我写完整俄语引言"),"deny")]:
                        response=await session.call_tool("ptb_lookup",{"request":request})
                        self.assertFalse(response.isError)
                        reply = response.structuredContent
                        self.assertEqual(reply["decision"],expected)
                        self.assertEqual(reply["db_query_count"] > 0, expected == "allow")
                        self.assertEqual(bool(reply["cards"]), expected == "allow")
if __name__=="__main__":
    unittest.main()
