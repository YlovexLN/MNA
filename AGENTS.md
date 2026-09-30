# AGENTS.md

本文件约束**在本仓库内工作的 AI agent**。面向使用者的 MaaFW 说明在 `README.md` /
`README.en.md`，两者不要互相抄。

项目标识：slug `mna`，显示名 `MNA`，模板 `pipeline`，控制器 `Win32`，发布 UI 为 **MXU**。

## 一、文件落位（硬性）

**本项目生成的一切产物必须留在本仓库内。**

- 项目级 skill 放 `.agents/skills/<name>/SKILL.md`，随仓库提交。
- 技能用到的参考文档、schema、模板，一律放该 skill 自己的目录下，用相对路径引用。
- **禁止**把本项目生成的东西写到以下位置：
    - `~/.agents/skills/`、`~/.dsh/skills/`、`~/.claude/skills/` 等**全局**技能目录
    - 系统临时目录（`$env:TEMP` / `/tmp`）
    - 任何仓库之外的路径
- 唯一例外：用户**明确要求**安装全局技能时。此时先说明"这会写到仓库之外"，再执行。

`--global` 及同类参数默认不用。上一轮误用 `skills add --global` 把技能装到了
`~/.agents/skills/`，已确认那是**错误示范**，不要复现。

## 二、一次性脚本用完即删（硬性）

为完成某次任务临时写的脚本、探针、抓取/转换工具，**测试通过后立即删除**，不得留在仓库里。

- 判断标准：这个脚本会被第二次使用吗？不会被删。
- 适用对象：临时 `.mjs` / `.ps1` / `.py` / `.sh`、调试用 JSON、解包出的中间文件、
  探查用的日志与截图。
- 交付物**不适用**本规则：`tools/` 下的正式脚本、`.agents/skills/` 下的技能文档、
  `resource/`、`tasks/`、`interface.json` 等，都是项目资产，必须保留。
- 写临时脚本时优先直接写进仓库内的临时路径并在结束时删除，**不要**为图省事写到仓库外。

## 三、文件命名规范

**适用范围仅限这三个目录：**

- `resource/base/image/`
- `resource/base/pipeline/`
- `tasks/`

这三个目录内的文件一律使用**连字符 + 每个词首字母大写**：

- `Start-Game.json`、`Comeback-Claim-All.png`、`Announcement-Close.png`
- 单词之间用 `-` 连接，**不用空格、不用下划线**
- 除专有名词外不用全大写缩写

**其余文件一概不管**，不要因为本条去改动这三个目录之外的任何文件名。

同一资产在 pipeline 中的节点名沿用 **PascalCase**（如 `StartGame.ClickStart`、
`ClaimReward.Confirm`），这是 MaaFW 社区惯例，与文件名规则并存。

## 四、本项目内不要做的事

- **不要修** `tools/build-release.mjs` 的格式问题。它不符合本项目 Prettier 配置，
  `pnpm format:check` 会报 `[warn]`，导致 CI 的 `check.yml` 失败。
  用户已明确决定**保留不修**。不要"顺手"跑 `pnpm format`，也不要改 `.prettierrc.mjs` 去迁就它。
- **不要手改** `.github/workflows/release.yml` 来选择 UI。该文件是 CLI 生成的 managed 文件
  （`templates/addons/github/.github/workflows/release.yml` 渲染而来），手改会在下次
  `--update` 时被覆盖。UI 选择由 `maa-project.json` 的 `runtime.mfa` / `runtime.mxu` 决定，
  由 `tools/build-release.mjs` 在运行时读取。
- **不要提交** `dist/`、`node_modules/`、`.create-maa-project/`、`config/`、
  `resource/base/model/ocr/`。它们都在 `.gitignore` 里，属派生物。
- **不要改** `.gitignore` 里 `# BEGIN/END create-maa-project` 标记之间的内容，那由 CLI 管理。

## 五、CLI 的使用纪律

`create-maa-project` 是本项目的生成与维护工具（全局安装，3.6.0）。

- 手工跑时必须带 `CREATE_MAA_PROJECT_AUTO_UPDATE=0`。否则它会检查 npm 并把命令交给
  **已发布版本**执行，等于在测旧代码。
- **绝不要**驱动交互式提示，agent 无法回答。创建用 `--yes --no-interactive` 并显式给出
  `--template` / `--slug` / `--name` 等参数；维护命令加 `--report`。
- `--report` 在 stdout 输出**恰好一个** JSON 文档，进度和人类可读错误走 stderr。
  解析 stdout，只在失败原因不明时才看 stderr。exit 0 成功，exit 1 是失败或 doctor findings。
- `--update all` **不存在**，是刻意设计。一次只更新一个 target，这样 `pending` 和日志
  才能归因到具体原因。
- `--force`、`--clear-stale-lock`、`--allow-non-git-dir`、`--allow-pending-commit` 都不要用，
  除非报告的 error 明确要求该 flag 或用户明确同意。每个都会豁免一道刻意设置的保护。
- 写命令会先备份并返回 `backupId`。回滚路径是 `--list-backups` → `--show-backup <id>` →
  `--restore <id> --dry-run` → `--restore <id>`，不要用删文件的方式"回滚"。
- `<path>` 是**路径**，`--slug` 才是项目标识。想生成到当前目录就用 `.`。
  （此前用 `create-maa-project MNA` 误建了子目录 `MNA\`，属错误用法。）

## 六、本机环境约束（会让你困惑的部分）

- **沙箱会杀死 shell**：默认 `workspace-write` 模式下任何进程都无法创建，`pwsh` 连
  `echo test` 都返回 `0xC0000142`（DLL 初始化失败）。这不是命令写错，是沙箱边界。
  需要执行命令时按流程申请放宽权限，不要靠反复重试。
- **npm 是坏的**：`E:\Node` 的 npm 11.13.0 在 `ping` / `view` / `exec` 上崩溃
  （`Class extends value undefined`），`npx` 因此不可用。**用 pnpm 替代**：
  `pnpm dlx <pkg>` 代替 `npx <pkg>`，`pnpm add -g <pkg>` 代替 `npm i -g <pkg>`。
- **pnpm 版本由项目 pin**：`packageManager` 是 `pnpm@11.5.1`，corepack 会自动切换，
  所以看到与全局 `pnpm --version` 不一致是正常的。
- **Node 版本**：项目 pin Node 22（`.node-version`），本机 `E:\Node` 是 Node 24.16。
  两者不同属正常，不要"顺手"把 `.node-version` 改成本机版本。
- **GitHub release 资产下载会失败**：`--update runtime:mxu` 在本机报
  `CMP_UPDATE_FAILED`（Node `fetch` 失败）。但 PowerShell 拉同一 URL 返回 200，
  即**网络可达、问题在 Node fetch 链路**。不要把这类失败当成配置错误去改 `maa-project.json`。

## 七、改动的验证要求

不要只跑 `--version` 就宣称完成。按改动性质选择验证：

- 改运行时/UI 配置 → `pnpm release:dry-run`（需 `CREATE_MAA_PROJECT_RUNTIME_PLATFORM=win-x64`），
  确认产物名符合预期，例如 `MNA-win-x86_64-v0.1.0-MXU.zip`。
- 改项目配置 → `create-maa-project --doctor --report`，检查 `doctor.checks` 每项。
- 改 pipeline / interface → `pnpm check`（`format:check` + `check:schema` + `check:maa`）。
  注意其中 `format:check` 会因第四节那个已知问题失败，属预期。
- 改完用 `git status --porcelain` 确认变更范围与预期一致，别带出意外文件。

报告结论时区分「已验证」和「未验证」，不要把推测写成事实。
