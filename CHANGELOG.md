# Changelog

All notable changes to this project will be documented in this file.

## [0.1.8] - 2025-07-31

### 🔧 重要修复 (Critical Fixes)

#### URL发现问题修复 (URL Discovery Fix)
- **修复CLI中默认exclude_selectors格式错误**：之前所有选择器被连接成单个字符串，现在正确分离为列表
- **修复示例脚本参数错误**：移除了CrawlConfig中不支持的`verbose`参数
- **改进URL发现机制**：对于复杂的文档站点，推荐使用`--type site`以获得更好的URL发现效果

#### 示例脚本重构 (Example Scripts Refactor)
- **Cursor文档示例完全重写**：从DocSiteCrawler改为WebCrawler，成功抓取75个页面（vs之前的1个）
- **添加markdown文件保存功能**：示例脚本现在能正确保存单独的markdown文件
- **优化选择器配置**：使用更有效的选择器组合排除导航元素

#### 性能和稳定性提升
- **更好的错误处理**：改进了异常捕获和错误报告
- **文件保存优化**：添加了完整的metadata和格式化
- **编码问题修复**：解决了Windows环境下的Unicode字符显示问题

### 💡 使用建议 (Usage Recommendations)

#### 获得最佳抓取效果
```bash
# 对于复杂的文档站点，建议使用site类型
website2md https://docs.cursor.com/en/welcome --type site --output ./docs

# 使用优化的选择器排除导航
website2md https://example.com --exclude-selectors "nav,aside,header,footer" --output ./clean
```

#### Python脚本改进
- 所有examples脚本现在都能成功抓取完整站点
- 支持自动保存为单独的markdown文件
- 包含完整的元数据和时间戳

### 🛠️ 技术改进 (Technical Improvements)
- 修复了CLI选择器解析逻辑
- 改进了WebCrawler与DocSiteCrawler的选择策略
- 优化了文件命名和保存机制
- 增强了跨平台兼容性

## [0.1.7] - 2025-07-31

### 🎯 新增功能 (New Features)

#### 内容过滤系统 (Content Filtering System)
- **新增 `--exclude-selectors` 参数**：支持使用CSS选择器排除不需要的内容
- **多选择器支持**：可以同时指定多个选择器，用逗号分隔
- **智能合并**：对于docs类型，用户指定的选择器会与默认的文档站选择器合并
- **全类型支持**：site、docs、list三种爬取类型都支持内容排除

#### 使用示例
```bash
# 排除广告和弹窗
website2md https://example.com --exclude-selectors ".advertisement,.popup,.cookie-banner"

# 排除导航和侧边栏
website2md https://docs.example.com --exclude-selectors "nav,.sidebar"

# 组合使用其他参数
website2md https://site.com --type site --exclude-selectors ".ads,.footer" --max-pages 10
```

#### 技术实现
- 通过crawl4ai的`excluded_selector`参数实现内容排除
- 支持任何有效的CSS选择器语法
- 在页面处理阶段就移除匹配的元素，提高效率

---

## [0.1.6] - 2025-07-31

### 🐛 重要修复 (Critical Bug Fixes)

#### WebCrawler 缓存和编码问题修复
- **修复了Windows下的编码错误**：禁用crawl4ai的verbose输出以避免GBK编码错误
- **修复了内容哈希值问题**：强制禁用crawl4ai缓存模式，确保获取实际内容而不是缓存标识符
- **改进了内容处理**：正确处理`StringCompatibleMarkdown`类型，确保获取真实的markdown内容
- **增强了调试信息**：添加了详细的日志记录来诊断内容获取问题

#### 技术细节
- 将`cache_mode`设置为`CacheMode.BYPASS`以避免缓存相关的哈希值
- 禁用`verbose=False`来避免rich库的Unicode字符编码错误
- 添加了内容长度检查和警告，帮助识别异常的短内容

### 📝 文档更新 (Documentation Updates)
- 更新了Windows用户使用指南，推荐设置`PYTHONIOENCODING=utf-8`

---

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