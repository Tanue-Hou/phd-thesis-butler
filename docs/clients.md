# 在客户端直接接入 PTB

在自己使用的客户端添加一次名为 `ptb` 的远程 MCP 服务，地址为 `https://91.149.239.14:10443/mcp`。认证使用管理员发放的 **12 位个人密钥**。如果界面有单独的 Bearer Token 栏，只填密钥本身。如果界面显示 Headers，请把头名称填为 `Authorization`，值填为 `Bearer ` 加个人密钥（Bearer 后恰有一个空格）。下列 KEY_PLACEHOLDER 均须替换。密钥区分大小写，PTB-001 等编号不能用于登录。

配置放在客户端的个人设置中。下列直接填写 HTTP 头的文件会保存明文凭证，请勿放进项目、Git、共享文件夹或截图。已用旧脚本配置过同名服务时，编辑原条目即可；同一条目仅使用一种 Authorization 来源。

## Codex App 与 CLI

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

## Antigravity IDE 与 agy CLI

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

## DeepSeek Harness（deepseek-ai/deepseek-harness）

在 Web 或 Desktop 的凭证设置中创建个人凭证 `PTB_ACCESS_KEY`，值为 12 位密钥。然后在 Settings 的 MCP 管理中添加一个服务，填写下表并启用，使用 Probe 检查连接。已配置其他服务时，在 Settings 单独添加这一项即可。

| 字段 | 值 |
| --- | --- |
| 名称 | `ptb` |
| transport | `streamable-http` |
| url | `https://91.149.239.14:10443/mcp` |
| headers → Authorization | `Bearer ${credential:PTB_ACCESS_KEY}` |
| enabled | `true` |

保留凭证引用中的美元符号和花括号。自定义 Host profile 需为 MCP manager 注入 credentials provider。个人密钥与用于调用 DeepSeek 模型的 API key 分开设置。[DeepSeek Harness MCP manager 文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-manager/README.md)

## 四个客户端的验收

重新打开客户端，刷新 MCP 工具。应能找到 `ptb_lookup`（客户端可能给工具名添加服务前缀）。向助手提出“只列论文结构”，同意提交本轮请求后，确认助手实际调用该工具，返回结构卡。若 HTTP 401，检查密钥是否已绑定、请求头空格和大小写；工具返回 `INTENT_REQUIRED` 则说明认证已通过，客户端需要按 [Skill](../SKILL.md) 补全用户意图。

**首次试用指令**：可以把下面这句话发给已连接的客户端。密钥仅由客户端附在 HTTP 请求头中。

> 同意向 PTB 提交本轮指令「只列论文结构」。请实际调用 PTB 的 ptb_lookup，参数 request 为 { "user_request": "只列论文结构", "intent": "plan", "source_kind": "none", "requested_output": "outline", "client_tags": ["篇章布局"] }，向我展示返回的结构卡。
