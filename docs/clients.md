# 在客户端直接接入 PTB

在自己使用的客户端添加一次名为 `ptb` 的远程 MCP 服务，地址为 `https://ptb.tanue.co.uk/mcp`。认证使用管理员发放的 **12 位个人密钥**。如果界面有单独的 Bearer Token 栏，只填密钥本身。如果界面显示 Headers，请把头名称填为 `Authorization`，值填为 `Bearer ` 加个人密钥（Bearer 后恰有一个空格）。下列 KEY_PLACEHOLDER 均须替换。密钥区分大小写，PTB-001 等编号不能用于登录。

配置放在客户端的个人设置中。下列直接填写 HTTP 头的文件会保存明文凭证，请勿放进项目、Git、共享文件夹或截图。已用旧脚本配置过同名服务时，编辑原条目即可；同一条目仅使用一种 Authorization 来源。

## 接好后怎么用

选中原稿，说“把这段译成俄语，顺便润色一下”。你当前用的模型先翻译，再参考 PTB 卡片修订。比如原文写“仅用于离线校核”，卡片可以提醒模型保留用途限定；具体选哪个俄语词，由模型结合上下文决定。组合流程可以比较两稿中的引用编号，表内数值和实验结论仍需作者查原件。

## Codex

### 桌面端图形界面

1. 打开 **插件 → MCP → 添加**。已有 Ptb 条目时点齿轮编辑。
2. 名称填 `ptb`，选择 **Streamable HTTP**，URL 填 `https://ptb.tanue.co.uk/mcp`。
3. 展开 **标头**。左栏填 `Authorization`，右栏先输入 `Bearer` 和一个英文空格，再粘贴自己的 12 位密钥。使用这种填法时，把 **Bearer 令牌环境变量** 和 **来自环境变量的标头** 留空。
4. 保存并启用。回到对话就可以提问，以后会沿用这项配置。

### 配置文件与 Windows CLI


打开用户级 Codex 配置 `~/.codex/config.toml`（Windows 为 `%USERPROFILE%\.codex\config.toml`）。在现有配置中增改这一节，移除该节旧的 `bearer_token_env_var`，保存并重新打开 Codex 会话。随后可以正常启动 App 或 CLI，无需通过启动脚本。

```toml
[mcp_servers.ptb]
url = "https://ptb.tanue.co.uk/mcp"
http_headers = { Authorization = "Bearer KEY_PLACEHOLDER" }
```

偏好在 Windows 加密保存凭证的用户仍可选用 [DPAPI 启动脚本](../ptb-codex.ps1)。

## Claude Code

在终端注册一次 `user` 范围的 HTTP 服务，之后直接启动 Claude Code，在 `/mcp` 查看连接状态。下面是 PowerShell 示例，粘贴密钥时输入隐藏，命令历史只记录变量名。Claude Code 会将请求头保存到自己的用户配置。此方法面向 Claude Code；Claude 网页版和 Desktop 的云连接器有独立的认证设置。

```powershell
$secret = Read-Host 'PTB 12 位密钥' -AsSecureString
$key = [Net.NetworkCredential]::new('', $secret).Password
try {
    claude mcp add --transport http --scope user ptb https://ptb.tanue.co.uk/mcp --header "Authorization: Bearer $key"
} finally {
    Remove-Variable key,secret
}
```

如果已注册同名的用户级旧服务，需要替换时，先运行 `claude mcp remove ptb --scope user`。仅移除你要更新的这一项。[Claude Code MCP 文档](https://code.claude.com/docs/en/mcp)

## Antigravity

在 IDE 的 MCP Servers 设置中打开当前客户端的原始配置，把下面的 `ptb` 条目并入已有的 `mcpServers`，保存并刷新服务器。CLI 也支持同一协议，可使用 `agy mcp add --type http --header "Authorization: Bearer $key" ptb https://ptb.tanue.co.uk/mcp`，其中 PowerShell 变量 `$key` 可按上一节隐藏读取。CLI 选项要写在服务名之前。

```json
{
  "mcpServers": {
    "ptb": {
      "serverUrl": "https://ptb.tanue.co.uk/mcp",
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
| url | `https://ptb.tanue.co.uk/mcp` |
| headers → Authorization | `Bearer ${credential:PTB_ACCESS_KEY}` |
| enabled | `true` |

保留凭证引用中的美元符号和花括号。自定义 Host profile 需为 MCP manager 注入 credentials provider。个人密钥与用于调用 DeepSeek 模型的 API key 分开设置。[DeepSeek Harness MCP manager 文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/mcp/mcp-manager/README.md)

## 开始使用

配好以后，在平时写论文的对话里直接问：

> 方法章怎么安排？

如果手头已经有一段中文，选中它，再说：

> 帮我翻译成俄语，然后润色和核对。

第一次使用时，助手会说明此次会发给 PTB 的内容，由你确认。普通提问会发送本轮指令、意图和场景标签；改译还会发送选中的段落及后续译稿。同一段的翻译、润色和核对可以一次委托。

<details>
<summary>连接遇到问题？</summary>

- 新添加的 PTB 没有出现：刷新客户端的工具列表，必要时新开对话。
- 提示 401：核对密钥是否启用，以及标头中 Bearer 后面的英文空格。
- 连接超时：检查当前网络能否访问 `https://ptb.tanue.co.uk/`。

</details>
