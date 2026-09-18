# SuohaChan Skills

一组可复用的 Agent 技能。每个技能都是一个独立目录，以 `SKILL.md` 作为入口，并可携带脚本、示例配置和参考资料。

## 技能列表

| 技能 | 用途 | 平台/依赖 |
| --- | --- | --- |
| [anime-schedule](./anime-schedule/) | 查询今日或指定日期的新番播出信息，并按卡片布局生成拼图 | Python 3.9+、`requests`、Pillow |
| [desktop-screenshot](./desktop-screenshot/) | 截取当前桌面或所有显示器并保存为 PNG | Windows PowerShell、.NET |
| [power-on-computer](./power-on-computer/) | 通过 Bemfa 向已配置的 ESP8266 发送一次开机指令 | Windows PowerShell、Bemfa 配置 |
| [obsidian-cli-knowledge-base](./obsidian-cli-knowledge-base/) | 使用官方 Obsidian CLI 管理知识库，并遵循目标 vault 自己的规范 | Obsidian Desktop、官方 CLI |

## 安装

克隆仓库后，将需要的技能目录放入 Agent 的技能目录：

```bash
git clone https://github.com/SuohaChan/skills.git
```

例如只使用 `anime-schedule`：

```text
<skills-directory>/skills/anime-schedule/
```

每个技能的具体安装、依赖和使用方式，请阅读对应目录中的 `README.md`（如果有）和 `SKILL.md`。

## 目录约定

```text
skills/
├── README.md
├── anime-schedule/
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   ├── references/
│   └── sources.json
├── desktop-screenshot/
│   ├── SKILL.md
│   └── scripts/
├── power-on-computer/
│   ├── SKILL.md
│   ├── config.example.json
│   ├── scripts/
│   └── tests/
└── obsidian-cli-knowledge-base/
    ├── SKILL.md
    └── agents/openai.yaml
```

技能运行产生的缓存、截图、输出图片和本机配置不应提交到仓库。各技能的 `.gitignore` 已排除这些内容；真实的 Bemfa UID 只能放在本地 `power-on-computer/config.json` 中。

## 开发与验证

在仓库根目录执行：

```bash
python -m unittest discover -s anime-schedule/scripts -p "test_*.py" -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\power-on-computer\tests\verify.ps1
```

修改技能后，应同时检查：

- `SKILL.md` 的 YAML frontmatter 包含 `name` 和 `description`
- 脚本使用相对技能目录定位资源，不依赖个人电脑或服务器的绝对路径
- 示例配置不包含真实 UID、密码、Token、私钥或服务器地址
- 运行时数据、缓存和生成物不会进入 Git

## 安全说明

本仓库只保存技能代码和示例配置。不要提交以下内容：

- SSH 私钥或真实公钥登录配置
- 云服务器 IP、密码和面板凭据
- API Key、Token、Bemfa UID 等访问凭据
- 个人缓存、截图、封面和生成图片

如果凭据曾经误提交，应立即撤销或轮换凭据；仅从当前文件删除并不能消除 Git 历史中的泄露。

## 许可证

各技能的许可证以其目录内说明为准。目前 `anime-schedule` 使用 MIT License。
