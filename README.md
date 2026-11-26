# PTB MCP Beta

PhD Thesis Butler 向写作客户端提供结构、方法、表达与证据检查知识卡。支持中俄互译、俄语润色、结构规划、研究比较和证据检查。客户端根据作者的材料完成改译或列出提纲。直接代写论文或章节会被拒绝。

## 从另一台电脑接入

云端服务已上线。可直接在 Codex、Claude Code、Antigravity 或 DeepSeek Harness 的个人配置中保存一次密钥。按所用客户端选择[原生接入步骤](docs/clients.md)。Windows Codex CLI 也可使用下文的加密保存脚本。

1. 在支持 **Streamable HTTP** 的 MCP 客户端添加远程服务器。URL 填 `https://91.149.239.14:10443/mcp`，认证头填 `Authorization: Bearer <独立测试令牌>`。将令牌保存在客户端的秘密配置中。
2. 将 [客户端 Skill](SKILL.md) 配置为该工具的调用指导，连接并刷新工具列表，应只出现 `ptb_lookup`。客户端电脑只需要地址和令牌。
3. 首次调用前，客户端告知用户并取得同意。VPS 接收本轮实际指令、申报意图、材料类型、期望产物与 1–3 个场景标签。翻译和润色另发用户选定的原稿及源语言、目标语言。继续同一任务时发回任务句柄。服务器用固定规则独立核对字段，意图缺失时拒绝，含义不清时要求澄清。规则判断的是收到的请求，客户端应保留用户原话。

### 三个可复现的调用

以下每行是一组完整工具参数，测试库中前两项各返回一张虚构卡。

```jsonl
{"request":{"user_request":"只列论文结构","intent":"plan","source_kind":"none","requested_output":"outline","client_tags":["篇章布局"]}}
{"request":{"user_request":"请把这段中文译成俄语","intent":"translate","source_kind":"draft","source_text":"我们观察了纸飞机的飞行。","source_lang":"zh","target_lang":"ru","requested_output":"translation","client_tags":["边界与归属"]}}
{"request":{"user_request":"按这个提纲替我写完整俄语引言","intent":"plan","source_kind":"outline","requested_output":"new_prose","client_tags":["篇章布局"]}}
```

结构请求返回布局卡，翻译请求返回表达卡供客户端译写。代写请求返回 `deny / DIRECT_DRAFTING`、空卡组及 `db_query_count=0`。查询计数是该业务请求在知识库实际执行的 SELECT 次数。查过库但无匹配时返回 `no_match` 和正数计数。每次最多三张卡。

## 管理员在 VPS 启动

使用 Python 3.11 或更新版本，在单独的虚拟环境中安装依赖。将真实脱敏数据库放在发布目录之外，仅授予服务账户读取权限。在权限受限的服务环境文件中配置以下变量；给服务进程授予密钥映射库读取权限、审计目录写入权限。

```text
PTB_KEY_REGISTRY=/srv/ptb-access/keys.sqlite
PTB_AUDIT_PATH=/srv/ptb-audit/events.sqlite
PTB_PUBLIC_HOST=ptb.example.org
PTB_DB_PATH=/srv/ptb-private/writing-knowledge.sqlite
```

```sh
python -m pip install -r requirements.txt
python server.py --port 8765
```

也可用 `--db /path/to/private.sqlite` 显式指定库。服务启动时检查库及查询字段；生产配置缺库或误选演示库时启动失败。使用单进程运行，由进程管理器负责重启。在 HTTPS 反向代理将 `/mcp` 转至 `http://127.0.0.1:8765/mcp`，保留外部 Host、Authorization 和 Origin。域名与 PTB_PUBLIC_HOST 对应。每次 HTTP 请求按 Bearer 密钥的 SHA-256 摘要查用户映射。绑定和停用即时生效；每个用户与密钥组合独立计限额。管理员通过 SSH 使用下列命令。用户标签填内部别名，历史调用保留当时的标签。

```sh
cd /opt/ptb-beta/build
python3 access_keys.py list
python3 access_keys.py bind PTB-002 student-02
python3 access_keys.py revoke PTB-002
python3 access_keys.py usage
```

新实例用 200 行的私有 CSV（列 id,digest，digest 为随机密钥字节串的 SHA-256 十六进制值，按密钥的 ASCII 文本计算）运行 `python3 access_keys.py init manifest.csv`。新槽位须绑定后才能访问。换人时分配一个未披露过的密钥，撤销旧密钥；修改标签不会改变秘密。审计记录知识查询的判定、拒绝原因、卡数、查询数、请求号与时间，以及认证失败事件。缺少或未知密钥无法归属到真实用户。保护并备份两个 SQLite 库和管理员的独立密钥保管库。

### 客户端一次录入

支持凭证存储的 harness：在用户级 MCP 设置中保存 HTTPS 地址及 Bearer 密钥，启用记住凭证。业务调用时由客户端自动携带请求头。请勿在模型对话或共享工作区填写密钥。

Windows Codex CLI 可在本地下载本仓库的 `ptb-codex.ps1`。首次运行 `.\ptb-codex.ps1 -Setup` 并在隐藏输入框粘贴一次。以后用 `.\ptb-codex.ps1` 启动 Codex。脚本使用当前 Windows 用户的 DPAPI 加密保存密钥，只在启动进程时提供环境变量。每台新设备各配置一次。


回退时将服务切换到已验证的 MCP 提交及其兼容数据库，保留当前库备份，然后重启；首次部署若无可回退版本，先关闭测试端点。Git 保留旧 Skill 提交供历史查阅。

远程验收须从另一台电脑发现工具，再验证正常请求、缺意图（零查询）、直接代写（零查询）和错误令牌（HTTP 401）。GitHub 发布与 VPS 验收分别记录。

## 开发者本机测试

```sh
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows PowerShell 可改用 .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest -v
python make_demo.py rebuilt-demo.sqlite
```

随包 demo.sqlite 完全由 [虚构样例生成器](make_demo.py) 创建。生成器要求输出路径尚不存在。回归测试会启动临时 HTTP 服务，通过 MCP 客户端实际发现工具并调用。手动联调时设置 PTB_BETA_TOKEN，清除 PTB_DB_PATH，然后运行 `python server.py --demo`。知识库与服务端的 SSH 私钥均无需分发给测试客户端。

个人访问密钥为 12 个区分大小写的随机字符（A–Z、a–z、0–9、短横线或下划线）。PTB-001 等编号仅用于管理。密钥轮换后，重新运行一次客户端配置即可。

### 组合改译与编辑依据

一次提出中文原稿的翻译、润色和核对，按 MCP 的 next_step 继续同一任务。客户端执行改译并回传采用记录。服务端在润色响应中直接提供 [反防御性编辑规范及原章节](docs/editorial-policy.md)，规则不占知识卡名额。PTB_RELEASE_COMMIT 可由发布者指定为本次部署的完整 Git 提交号。
