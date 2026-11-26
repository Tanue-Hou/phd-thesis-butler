# 在客户端直接接入 PTB

在自己使用的客户端添加一次名为 `ptb` 的远程 MCP 服务，地址为 `https://91.149.239.14:10443/mcp`。认证使用管理员发放的 **12 位个人密钥**。如果界面有单独的 Bearer Token 栏，只填密钥本身。如果界面显示 Headers，请把头名称填为 `Authorization`，值填为 `Bearer ` 加个人密钥（Bearer 后恰有一个空格）。下列 KEY_PLACEHOLDER 均须替换。密钥区分大小写，PTB-001 等编号不能用于登录。

配置放在客户端的个人设置中。下列直接填写 HTTP 头的文件会保存明文凭证，请勿放进项目、Git、共享文件夹或截图。已用旧脚本配置过同名服务时，编辑原条目即可；同一条目仅使用一种 Authorization 来源。

## Codex

### 桌面端图形界面

1. 打开 **插件 → MCP → 添加**。已有 Ptb 条目时点齿轮编辑。
2. 名称填 `ptb`，选择 **Streamable HTTP**，URL 填 `https://91.149.239.14:10443/mcp`。
3. 展开 **标头**。左栏填 `Authorization`，右栏先输入 `Bearer` 和一个英文空格，再粘贴自己的 12 位密钥。使用这种填法时，把 **Bearer 令牌环境变量** 和 **来自环境变量的标头** 留空。
4. 保存并启用，新开对话，执行文末的连接测试。以后打开客户端会沿用这项配置。

### 配置文件与 Windows CLI


打开用户级 Codex 配置 `~/.codex/config.toml`（Windows 为 `%USERPROFILE%\.codex\config.toml`）。在现有配置中增改这一节，移除该节旧的 `bearer_token_env_var`，保存并重新打开 Codex 会话。随后可以正常启动 App 或 CLI，无需通过启动脚本。

```toml
[mcp_servers.ptb]
url = "https://91.149.239.14:10443/mcp"
http_headers = { Authorization = "Bearer KEY_PLACEHOLDER" }
```

在 Codex 的 MCP 列表或 CLI 的 `/mcp` 查看工具。偏好在 Windows 加密保存凭证的用户仍可选用 [DPAPI 启动脚本](../ptb-codex.ps1)。

## Claude Code

在终端注册一次 `user` 范围的 HTTP 服务，之后直接启动 Claude Code，在 `/mcp` 查看连接状态。下面是 PowerShell 示例，粘贴密钥时输入隐藏，命令历史只记录变量名。Claude Code 会将请求头保存到自己的用户配置。此方法面向 Claude Code；Claude 网页版和 Desktop 的云连接器有独立的认证设置。

```powershell
$secret = Read-Host 'PTB 12 位密钥' -AsSecureString
$key = [Net.NetworkCredential]::new('', $secret).Password
try {
    claude mcp add --transport http --scope user ptb https://91.149.239.14:10443/mcp --header "Authorization: Bearer $key"
} finally {
    Remove-Variable key,secret
}
```

如果已注册同名的用户级旧服务，需要替换时，先运行 `claude mcp remove ptb --scope user`。仅移除你要更新的这一项。[Claude Code MCP 文档](https://code.claude.com/docs/en/mcp)

## Antigravity

在 IDE 的 MCP Servers 设置中打开当前客户端的原始配置，把下面的 `ptb` 条目并入已有的 `mcpServers`，保存并刷新服务器。CLI 也支持同一协议，可使用 `agy mcp add --type http --header "Authorization: Bearer $key" ptb https://91.149.239.14:10443/mcp`，其中 PowerShell 变量 `$key` 可按上一节隐藏读取。CLI 选项要写在服务名之前。

```json
{
  "mcpServers": {
    "ptb": {
      "serverUrl": "https://91.149.239.14:10443/mcp",
      "headers": { "Authorization": "Bearer KEY_PLACEHOLDER" }
    }
  }
}
```

[Antigravity MCP 文档](https://antigravity.google/docs/ide/mcp)

## DeepSeek Harness

在 Web 或 Desktop 的凭证设置中创建个人凭证 `PTB_ACCESS_KEY`，值为 12 位密钥。然后在 Settings 的 MCP 管理中添加一个服务，填写下表并启用，使用 Probe 检查连接。已配置其他服务时，在 Settings 单独添加这一项即可。

| 字段 | 值 |
| --- | --- |
| 名称 | `ptb` |
| transport | `streamable-http` |
| url | `https://91.149.239.14:10443/mcp` |
| headers → Authorization | `Bearer ${credential:PTB_ACCESS_KEY}` |
| enabled | `true` |

保留凭证引用中的美元符号和花括号。自定义 Host profile 需为 MCP manager 注入 credentials provider。个人密钥与用于调用 DeepSeek 模型的 API key 分开设置。[DeepSeek Harness MCP manager 文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-manager/README.md)

## 确认连接

新开对话并刷新工具。找到 `ptb_lookup` 后，可以直接说：

> 我同意向 PTB 提交“只列论文结构”。请实际调用 ptb_lookup，把返回的结构卡展示给我。

看到工具调用和结构卡，说明已接通。再选中一段自己的中文原稿，说“帮我翻译成俄语，然后润色和核对”。在已通过组合任务实测的 Codex CLI 中，这一次委托会交回俄语稿、核对结果和可点击的编辑依据。

首次调用会把本轮指令、意图和场景标签发给 PTB。改译时还会发送选中的原稿及语言，组合任务会继续发送译稿。请只选中愿意提交的段落。服务提供写作参考，直接代写请求会被拒绝。

| 遇到的情况 | 怎么处理 |
|---|---|
| HTTP 401 | 检查个人密钥是否启用，核对大小写以及 Bearer 后的英文空格。 |
| 连接超时 | 检查本机网络能否访问服务器的 10443 端口。 |
| 返回 INTENT_REQUIRED | 认证已通过。让客户端按[调用说明](../SKILL.md)提交本轮原话及完整意图。 |
| 工具返回了卡片，但客户端停在第一步 | 提醒客户端按返回的 next_step 继续同一任务。 |

Codex CLI 已验证完整组合任务，Claude Code 已验证远程连接。Antigravity 和 DeepSeek Harness 的设置按各自配置规范整理，组合流程仍待实机验证。
