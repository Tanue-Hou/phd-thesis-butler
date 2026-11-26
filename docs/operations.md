# PTB 部署与本地测试

以下命令在仓库根目录执行。

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

随包 demo.sqlite 完全由 [虚构样例生成器](../make_demo.py) 创建。生成器要求输出路径尚不存在。回归测试会启动临时 HTTP 服务，通过 MCP 客户端实际发现工具并调用。手动联调时设置 PTB_BETA_TOKEN，清除 PTB_DB_PATH，然后运行 `python server.py --demo`。知识库与服务端的 SSH 私钥均无需分发给测试客户端。

设置 PTB_RELEASE_COMMIT 为部署提交的完整 SHA，可让编辑依据指向对应版本。
