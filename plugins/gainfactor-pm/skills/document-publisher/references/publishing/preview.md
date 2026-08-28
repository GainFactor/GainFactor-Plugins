# 门户运行与预览

只有用户要求打开、关闭、预览或检查运行状态时执行本 Shortcut。普通发布完成后不默认启动服务。

门户根目录的 `打开文档门户.command` 与 `关闭文档门户.command` 由导入器安装或更新。启动器只监听 `127.0.0.1`，运行状态和日志位于可删除的 `.portal-runtime/`。

检查端口时同时检查进程命令，区分 `next dev`、`serve <portal>/out` 和未运行，不能只根据端口可访问推断内容会刷新。用户要求打开时执行门户自带启动器并返回目标文档 URL；要求关闭时执行关闭启动器。

预览时检查首屏、导航、目录、正文、图片、图形和内部引用。日常修改必须把本轮目标路由传给 Quick：

```bash
PORTAL_URL=<portal-origin> \
PORTAL_GATE_QUICK=1 \
PORTAL_GATE_ROUTES=/docs/<affected-route-1>,/docs/<affected-route-2> \
pnpm run visual:gate
```

Quick 仅检查 1280×800 桌面视口、双主题和指定路由，但不会省略空白图形、图片失败、横向溢出、无效引用、裁切、键盘操作与严重可访问性等核心规则。未提供 `PORTAL_GATE_ROUTES` 时才回退到三个门户基础页；基础页通过不能证明业务文档已验证。

公共组件、Token、响应式或图形能力完成，以及正式 release 前，必须执行 Full：

```bash
PORTAL_URL=<url> pnpm run visual:gate
```

Full 自动发现正式文档，并覆盖 320×720、390×844、768×1024、1280×800、1920×1080 五种视口与双主题。失败后读取 [`troubleshooting`](troubleshooting.md)。
