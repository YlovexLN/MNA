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

`skills/` 目录目前为空。

本项目日常使用 MaaFW 的通用技能 `create-maa-project`，它由 `skills` CLI 全局安装，
**不属于**本仓库资产，因此不在此处重复。
