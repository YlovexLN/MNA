# .agents

本目录存放**属于本仓库**的 agent 资产，随项目一起提交和分发。

## 目录约定

```
.agents/
└── skills/
    └── <skill-name>/
        ├── SKILL.md        # 必需；YAML frontmatter 需含 name 与 description
        └── references/     # 可选；技能用到的参考文档
```

## 规则

- 项目级 skill 放 `.agents/skills/<name>/SKILL.md`，**不要**装到全局技能目录
  （`~/.agents/skills/`、`~/.dsh/skills/` 等）。完整约束见仓库根目录 `AGENTS.md` 第一节。
- 技能引用的文档用**相对路径**，放在该 skill 自己的目录内，保证整个仓库可独立分发。
- 临时脚本、探针、中间产物不放在这里；它们应在用完后立即删除，
  见 `AGENTS.md` 第二节。

## 当前内容

### `pipeline-guide/`

MaaFramework Pipeline 编写指南，**原样取自** MaaEnd/MaaEnd 仓库 `v2` 分支的
`.agents/skills/pipeline-guide/`，用于参考节点设计、识别算法、流程控制与审查清单。

**注意**：该文档基于 MaaEnd 的 **Pipeline v2 格式**编写，而本项目使用 **v1 扁平格式**；
文中 `Common/Button/`、`SceneManager`、`Custom 节点`、`tools/i18n` 等本节项目均不存在。
`SKILL.md` 开头已列出完整的差异对照表，**使用前必读**。

`field-reference.md` 是该 skill 的配套参考文档，原样保留。

本项目日常使用 MaaFW 的通用技能 `create-maa-project`，它由 `skills` CLI 全局安装，
**不属于**本仓库资产，因此不在此处重复。
