import asyncio
import logging
import secrets
import socket
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from policy import Gateway
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

class Transport(unittest.TestCase):
    def test_real_mcp(self):
        token=secrets.token_urlsafe(32)
        with socket.socket() as listener:
            listener.bind(("127.0.0.1",0))
            app=create_app(token,DB,listener.getsockname()[1], demo=True)
            server=uvicorn.Server(uvicorn.Config(app,access_log=False,log_level="error"))
            thread=threading.Thread(target=server.run,kwargs={"sockets":[listener]},daemon=True)
            thread.start()
            try:
                for _ in range(100):
                    if server.started: break
                    time.sleep(.05)
                self.assertTrue(server.started)
                asyncio.run(self.client(listener.getsockname()[1],token))
            finally:
                server.should_exit=True
                thread.join(5)
    async def client(self,port,token):
        url=f"http://127.0.0.1:{port}/mcp"
        async with httpx.AsyncClient(trust_env=False) as anonymous:
            self.assertEqual((await anonymous.post(url,json={})).status_code,401)
        async with httpx.AsyncClient(headers={"Authorization":"Bearer "+token},trust_env=False) as http:
            async with streamable_http_client(url,http_client=http) as (read,write,_):
                async with ClientSession(read,write) as session:
                    await session.initialize()
                    self.assertEqual([t.name for t in (await session.list_tools()).tools],["ptb_lookup"])
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
