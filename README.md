# NapCat Mofish Client

>  终端风格的 QQ 客户端 - 看起来像在写代码，实际在摸鱼

基于 [NapCatQQ](https://github.com/NapNeko/NapCatQQ) (OneBot 11 协议) 的终端 QQ 客户端，使用 Python Textual 框架实现。

## ✨ 特性

-  **视觉伪装** - Hacker 风格配色，看起来像终端工具
-  **老板键** - 一键切换到虚假编译日志
-  **智能交互** - 支持 @补全、点击回复、命令提示
-  **关键词高亮** - 重要消息自动高亮
-  **完整聊天** - 支持私聊和群聊

## 🚀 快速开始

### 前置要求

- Python 3.10+
- [NapCatQQ](https://github.com/NapNeko/NapCatQQ) 已运行 (WebSocket 端口 3001)

### 安装

```bash
# 使用 uv 安装
uv sync

# 或使用 pip
pip install -e .
```

### 运行

```bash
# 启动客户端
uv run mofish
```

## ⌨️ 快捷键 / 命令

| 按键/命令 | 功能 |
|---|---|
| `F10` / `Ctrl+B` | **老板键** - 切换伪装模式 |
| `Ctrl+Q` | 退出程序 |
| `@` | 解锁**提及自动补全** (支持拼音/QQ号) |
| `/` | 显示命令提示 |
| `/img` | 发送剪贴板/本地图片 |
| `↑/↓` | 切换会话 / 选择补全项 |
| `Click` | 点击消息快速**引用回复** |

## 界面展示
聊天界面
![聊天界面](./docs/chat.png)

老板键伪装界面
![老板键伪装界面](docs/boss.png)

## 📝 License

MIT
