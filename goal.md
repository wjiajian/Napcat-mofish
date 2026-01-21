### 1. 整体架构设计

采用 **Client-Server** 架构：

*   **Server 端**: **NapCatQQ**
    *   负责登录 QQ，处理协议细节。
    *   通过 WebSocket 暴露接口。
    *   后台静默运行。
*   **Client 端**: **终端程序 (你的程序)**
    *   连接 NapCat 的 WebSocket。
    *   负责渲染界面 (好友列表、聊天记录、输入框)。
    *   负责伪装 (看起来像在编译代码或查看日志)。

```mermaid
graph LR
    A[终端 Client] -- WebSocket (JSON) --> B[NapCat (OneBot 11)]
    B -- 协议 --> C[腾讯 QQ 服务器]
```

### 2. 技术选型

为了快速开发且界面美观，推荐使用 **Python** 生态。

*   **编程语言**: Python 3.10+
*   **TUI 框架**: **Textual** 
    *   *理由*: Textual 是目前 Python 最现代的 TUI 框架，支持 CSS 布局，原生支持 Async/Await (对 WebSocket 很重要)，组件化开发容易。
*   **网络库**: `websockets` (用于异步连接 NapCat)。

### 3. 关键功能与“摸鱼”专属优化

要在公司放心使用，必须在 **UI 和 交互** 上下功夫：

#### A. 视觉伪装 (Camouflage)
不要用鲜艳的 QQ 配色。
*   **配色方案**: 使用黑/绿（Hacker 风格）或 黑/灰（服务器日志风格）。
*   **界面元素**:
    *   把 `Send` 按钮去掉，纯回车发送。
    *   输入框提示文字改为 `>>>` 或 `admin@local:~$`。
    *   窗口标题动态修改为 `node_modules install` 或 `webpack building...`。

#### B. 老板键 (Boss Key)
在 Textual 中绑定全局快捷键（例如 `F10` 或 `Ctrl+B`）：
*   **功能**: 按下后，瞬间清屏，并显示一段预设的虚假代码（例如正在编译的 Java 堆栈报错，或者 Ping 的输出），并且屏蔽新消息通知。

#### C. 消息过滤与提醒
*   **关键词高亮**: 只有包含“吃饭”、“下班”、“名字”时才高亮，其他消息以灰色低对比度显示。
*   **图片处理**: 终端看图很麻烦。为了隐蔽，建议**完全屏蔽图片**或只显示 `[图片]` 占位符

#### D. 会话管理
你需要维护一个本地 State：
*   获取好友列表 (`get_friend_list`) 和群列表 (`get_group_list`)。
*   在左侧 Sidebar 渲染列表。
*   点击不同 Item 时，切换右侧 Log 组件的内容（需要内存中存储历史消息 buffer）。

### 总结

方案核心在于 **NapCat 做协议转换** + **Python Textual 做终端 UI**。这个组合开发效率极高，且 Textual 现在的组件丰富度足以支撑一个复杂的聊天界面，同时看着就像一个专业的运维工具，隐蔽性满分。