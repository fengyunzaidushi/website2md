# Changelog

All notable changes to this project will be documented in this file.

## [0.1.5] - 2025-07-31

### 🎯 新增功能 (New Features)

#### 精确域名过滤系统 (Precise Domain Filtering System)
- **精确域名匹配**：默认只抓取与用户输入完全相同的域名
  - 输入 `https://docs.anthropic.com/zh-CN/docs` 只抓取 `docs.anthropic.com` 域名
  - 不再抓取 `console.anthropic.com`, `www.anthropic.com` 等其他子域名
- **灵活的额外域名支持**：新增 `--allowed-domains` CLI 选项
  - 支持指定额外允许的域名列表
  - 示例：`--allowed-domains "api.example.com,console.example.com"`
- **支持常见域名后缀**：`.com`, `.ai`, `.so`, `.dev`, `.online`, `.org`, `.net`, `.cn`, `.info`, `.app`, `.io`, `.xyz`, `.co`, `.run`, `.me`, `.pro`, `.top`

#### CLI 增强 (CLI Enhancements)
- 新增 `--allowed-domains` 选项：指定额外允许的域名
- 保留 `--allow-external` 选项：允许抓取所有外部域名（谨慎使用）
- 改进了 Windows 系统编码兼容性：移除了所有可能导致 GBK 编码错误的 emoji 字符

### 🔧 技术改进 (Technical Improvements)

#### 配置系统升级
- 新增 `additional_allowed_domains` 配置选项
- 改进了域名检测和过滤逻辑
- 更精确的 URL 验证和域名提取

#### 代码结构优化
- 重构了项目结构，符合 Python 包标准规范
- 改进了 `utils.py` 中的域名处理函数
- 优化了爬虫中的域名过滤集成

### 🐛 问题修复 (Bug Fixes)
- 修复了 Windows 系统下的字符编码问题 (`'gbk' codec can't encode character` 错误)
- 解决了 emoji 字符在中文 Windows 系统中的显示问题
- 改进了错误处理和日志输出

### 📚 文档更新 (Documentation Updates)
- 更新了 README.md，包含新的安装和使用方法
- 添加了 uv 包管理器的安装说明和中国镜像源配置
- 新增了详细的域名过滤功能说明和使用示例
- 改进了开发环境设置指南

### ⚠️ 破坏性变更 (Breaking Changes)
- **域名过滤行为变更**：默认不再抓取子域名，只抓取完全相同的域名
- 如需保持旧行为，请使用 `--allow-external` 选项

### 📖 使用示例 (Usage Examples)

```bash
# 只抓取相同域名（新的默认行为）
website2md https://docs.anthropic.com/zh-CN/docs --output ./docs

# 包含额外相关域名
website2md https://docs.anthropic.com/zh-CN/docs \
  --allowed-domains "console.anthropic.com,api.anthropic.com" \
  --output ./docs

# 允许所有外部域名（旧行为）
website2md https://docs.anthropic.com/zh-CN/docs \
  --allow-external \
  --output ./docs

# Windows 用户建议使用 UTF-8 编码
PYTHONIOENCODING=utf-8 website2md https://docs.example.com --output ./docs
```

---

## [0.1.4] - 2025-07-30

### 🔧 项目结构重构
- 将项目文件重新组织为标准 Python 包结构
- 项目配置文件移至根目录
- 源代码统一放置在 `website2md/` 包目录中

---

## [0.1.3] - 2025-07-29

### 🎯 初始发布
- 基本的网站抓取功能
- 支持文档站点、完整网站和 URL 列表处理
- 基于 crawl4ai v0.6.x 的现代网络爬取
- Markdown 格式输出
- JavaScript 渲染支持