# 域名过滤功能示例

## 📋 概述

Website2MD 现在支持精确的域名过滤，确保只抓取相关域名下的页面。

## 🎯 新的过滤逻辑

### 默认行为：只抓取相同完整域名
```bash
# 用户输入：https://docs.anthropic.com/zh-CN/docs/claude-code/cli-reference
# 只会抓取：docs.anthropic.com 下的页面
# 不会抓取：console.anthropic.com, www.anthropic.com 等其他子域名

website2md https://docs.anthropic.com/zh-CN/docs --output ./output
```

**抓取范围：**
- ✅ `https://docs.anthropic.com/zh-CN/docs/...` (相同域名)
- ✅ `https://docs.anthropic.com/en/api/...` (相同域名)
- ❌ `https://console.anthropic.com/legal/...` (不同子域名)
- ❌ `https://www.anthropic.com/press-kit` (不同子域名)

## 🔧 CLI 选项

### 1. 允许额外域名
```bash
# 允许抓取指定的额外域名
website2md https://docs.anthropic.com/zh-CN/docs \
  --allowed-domains "console.anthropic.com,api.anthropic.com" \
  --output ./output
```

**抓取范围：**
- ✅ `https://docs.anthropic.com/...` (原始域名)
- ✅ `https://console.anthropic.com/...` (允许的额外域名)
- ✅ `https://api.anthropic.com/...` (允许的额外域名)
- ❌ `https://www.anthropic.com/...` (未明确允许)

### 2. 允许所有外部域名
```bash
# 允许抓取任何域名（使用时需谨慎）
website2md https://docs.anthropic.com/zh-CN/docs \
  --allow-external \
  --output ./output
```

**抓取范围：**
- ✅ 任何域名下的页面 (需谨慎使用)

## 📝 实际示例

### 示例1：只抓取文档站
```bash
# 只抓取 docs.cursor.com 域名下的页面
website2md https://docs.cursor.com/en/get-started/concepts \
  --output ./cursor-docs \
  --max-pages 50 \
  --verbose
```

### 示例2：包含API文档域名
```bash
# 同时抓取文档站和API站点
website2md https://docs.anthropic.com/zh-CN/docs \
  --allowed-domains "api.anthropic.com" \
  --output ./anthropic-docs \
  --max-pages 100
```

### 示例3：处理多个相关子域名
```bash
# 抓取多个相关子域名的内容
website2md https://docs.openai.com/api \
  --allowed-domains "platform.openai.com,cookbook.openai.com" \
  --output ./openai-complete \
  --max-pages 200
```

## 🔍 技术实现

### 域名检测逻辑
```python
# 精确域名匹配
target_domain = "docs.anthropic.com"
base_domain = "docs.anthropic.com" 
# 结果：允许抓取

target_domain = "console.anthropic.com"
base_domain = "docs.anthropic.com"
# 结果：不允许抓取（不同子域名）
```

### 支持的域名后缀
- `.com`, `.ai`, `.so`, `.dev`, `.online`
- `.org`, `.net`, `.cn`, `.info`, `.app`
- `.io`, `.xyz`, `.co`, `.run`, `.me`
- `.pro`, `.top`, `.edu`, `.gov`, `.mil`

## ⚠️ 重要说明

1. **默认行为变化**：现在默认只抓取相同完整域名，不再包含子域名
2. **精确控制**：用户可以通过 `--allowed-domains` 精确指定要包含的额外域名
3. **安全性提升**：避免意外抓取到无关的外部网站内容
4. **向后兼容**：可以通过 `--allow-external` 恢复旧的宽松行为

## 🎉 优势

- ✅ **精确控制**：只抓取用户真正需要的域名内容
- ✅ **避免污染**：不会抓取到无关的外部链接
- ✅ **性能提升**：减少不必要的网络请求
- ✅ **内容质量**：生成的文档更加聚焦和相关
- ✅ **灵活配置**：支持多种使用场景的配置选项