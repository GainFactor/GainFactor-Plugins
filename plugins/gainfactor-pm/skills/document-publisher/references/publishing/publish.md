# 同步、预览或正式发布文档

本流程只接受已经完成的 `.md` / `.mdx`，以及同名可选 `.portal.json` 和调用方提供的 `.review.json`。不得在这里改写正文语义。

## 1. 确认终点

先沿用入口选定的终点，不得因为调用了发布器而自动升级：

| 终点 | 执行动作 |
| --- | --- |
| `validated` | 只执行内容契约校验 |
| `imported` | 校验并同步门户源码、manifest、资产与评审 |
| `previewed` | 完成导入，构建一次，只检查受影响路由 |
| `released` | 构建、Full、契约测试全部通过 |

多个文档属于同一工作流时，逐份校验和导入，但只在全部导入完成后构建与验证一次。

需要 Python 3 执行校验与导入；需要 Node.js、`pnpm` 和 Playwright Chromium 执行构建与视觉门禁。缺依赖时停在实际状态，不改用其他包管理器。

## 2. 校验并导入

先按 [`../validation`](../validation.md) 校验源文件。标准产物使用工作区 `.gainfactor/portal`：

```bash
python3 <plugin-root>/scripts/create_document_portal.py \
  <document.md-or-mdx> \
  --subject-slug=<product-or-project-slug> --subject-title=<visible-title> \
  --artifact=<artifact-key> \
  --version=<version> --status=<status> \
  --owner=<owner> --updated=<YYYY-MM-DD>
```

传入 presentation 使用 `--presentation=<file>`，要求富首屏时加 `--rich`；挂载评审使用 `--review=<file>`。只解析身份使用 `--dry-run`。显式 target、slug、group 等兼容参数见 [`artifact-management`](../artifact-management.md)，仅在标准身份无法表达时使用。

导入成功即达到 `imported`。如果终点是 `imported`，到此停止，不运行类型检查、构建或视觉门禁。

## 3. 目标路由预览

`previewed` 用于让用户查看本轮变更，不做全站 release。先按 [`preview`](preview.md) 判断当前服务类型：

- 已有指向当前门户源码的 `next dev`：复用热更新，不运行 build；等待目标路由出现新内容后直接执行目标路由 Quick。
- 已有 `serve <portal>/out`、服务未运行或静态产物过期：全部文档导入后只构建一次，再执行目标路由 Quick；需要 URL 时复用或重启静态服务。
- 服务归属无法确认：不得借用该端口，按当前门户重新构建或停止并报告冲突。

需要构建时执行：

```bash
pnpm run types:check
pnpm run lint
pnpm run build
```

随后对实际服务执行一次：

```bash
PORTAL_URL=<portal-origin> \
PORTAL_GATE_QUICK=1 \
PORTAL_GATE_ROUTES=/docs/<affected-route-1>,/docs/<affected-route-2> \
pnpm run visual:gate
```

`PORTAL_GATE_ROUTES` 必须包含本轮修改的每个目标路由。Quick 使用 1280×800 桌面视口和明暗双主题，并对这些路由执行空白图形、图片失败、横向溢出、无效引用、裁切、键盘操作和严重可访问性检查。固定基础页 Quick 只用于门户骨架自检，不能证明业务文档已验证。

route、导航或共享资源变化时，把受影响的相邻路由一并加入；仍只构建一次。

## 4. 正式 release

只有用户明确要求正式发布，或公共组件、Token、响应式、Mermaid、AntV、Screenshot 与视觉门禁能力发生变化时运行 Full。正式 release 还必须运行 Skill 契约测试：

```bash
python3 -m unittest discover -s <plugin-root>/scripts/tests -p 'test_document_publisher_skill.py'
pnpm run types:check
pnpm run lint
pnpm run publish:check
```

Full 自动发现全部正式文档，覆盖 1920×1080、1280×800、768×1024、390×844、320×720 五种视口和明暗双主题，并阻止空白图形、图片失败、横向溢出、无效引用、容器裁切、主题切换后未重绘及严重可访问性问题。

## 5. 状态与证据

- `validated`：源文件与内容契约通过。
- `imported`：门户正文、manifest、导航、presentation、review 和资产已更新。
- `previewed`：目标路由构建完成、可访问并通过目标路由 Quick。
- `released`：全量构建、Full 和契约测试通过。

构建后检查目标静态产物或路由数据、导航、预期标题和本地资源。服务运行时再检查目标 URL；服务未运行可报告“已构建并验证，预览服务未启动”。任何失败都停止提升状态，失败后才读取 [`troubleshooting`](troubleshooting.md)。

恢复时从最早未满足状态继续：已校验源文件未变化则不重跑校验；已导入条目和 manifest 未变化则不重复导入；构建产物仍对应当前源码则不重建；仅视觉门禁失败时修复后只重跑受影响路由 Quick。
