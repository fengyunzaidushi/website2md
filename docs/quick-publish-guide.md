# PyPI 快速发布指南

这是一个简化的PyPI发布指南，包含最常用的发布步骤。

## 🚀 快速发布步骤

### 1. 准备工作

```bash
# 安装工具
pip install --upgrade build twine

# 确保 ~/.pypirc 已配置
cat ~/.pypirc
```

### 2. 更新版本号

编辑 `pyproject.toml`：
```toml
version = "0.1.4"  # 更新版本号
```

### 3. 构建和发布

```bash
# 清理旧文件
rm -rf dist/ build/ *.egg-info/

# 构建分发包
python -m build

# 检查分发包
twine check dist/*

# 发布到PyPI
twine upload dist/*
```

### 4. 验证发布

```bash
# 检查PyPI页面
open https://pypi.org/project/your-package-name/

# 安装测试
pip install --index-url https://pypi.org/simple/ your-package-name

# 验证版本
pip show your-package-name
```

## 📋 发布检查清单

- [ ] 更新版本号
- [ ] 测试代码功能
- [ ] 更新README.md（如需要）
- [ ] 构建分发包
- [ ] 检查分发包
- [ ] 发布到PyPI
- [ ] 验证安装

## ❗ 常见问题

### 版本冲突
```bash
# 检查版本是否已存在
curl -s "https://pypi.org/pypi/your-package-name/json" | python -c "import sys, json; data=json.load(sys.stdin); print('Latest version:', data['info']['version'])"
```

### 认证问题
```bash
# 测试认证
twine check dist/*
```

## 🔧 实用命令

```bash
# 查看当前版本
python -c "import your_package; print(your_package.__version__)"

# 查看PyPI包信息
curl -s "https://pypi.org/pypi/your-package-name/json" | python -m json.tool

# 卸载包
pip uninstall your-package-name
```

---

**提示**：首次发布建议先使用测试PyPI：`twine upload --repository testpypi dist/*` 