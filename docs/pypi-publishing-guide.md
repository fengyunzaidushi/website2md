# PyPI 发布指南

本指南详细介绍了如何将Python项目发布到PyPI（Python Package Index），让全球用户可以通过pip安装你的包。

## 📋 目录

- [准备工作](#准备工作)
- [项目配置](#项目配置)
- [构建分发包](#构建分发包)
- [发布到PyPI](#发布到pypi)
- [验证发布](#验证发布)
- [版本管理](#版本管理)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)

## 🚀 准备工作

### 1. 安装必要的工具

```bash
# 安装构建和发布工具
pip install --upgrade build twine
```

### 2. 准备PyPI账户

1. 注册PyPI账户：https://pypi.org/account/register/
2. 启用两步验证（推荐）
3. 创建API Token：https://pypi.org/manage/account/token/

### 3. 配置认证信息

创建或编辑 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## ⚙️ 项目配置

### 1. pyproject.toml 配置

确保你的 `pyproject.toml` 文件包含所有必要信息：

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package-name"
version = "0.1.0"
description = "Your package description"
readme = "README.md"
license = "MIT"  # 使用SPDX许可证标识符
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
]

[project.scripts]
your-command = "your_package.cli:main"

[project.urls]
Homepage = "https://github.com/username/your-repo"
Repository = "https://github.com/username/your-repo"
Issues = "https://github.com/username/your-repo/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["your_package*"]
```

### 2. 必需文件

确保项目包含以下文件：

- `pyproject.toml` - 项目配置
- `README.md` - 项目说明文档
- `LICENSE` - 许可证文件
- `__init__.py` - 包初始化文件

## 🔨 构建分发包

### 1. 清理之前的构建文件

```bash
# 删除之前的构建文件
rm -rf dist/ build/ *.egg-info/
```

### 2. 构建分发包

```bash
# 构建源码包和wheel包
python -m build
```

构建成功后会生成：
- `dist/your-package-0.1.0.tar.gz` - 源码分发包
- `dist/your-package-0.1.0-py3-none-any.whl` - wheel分发包

### 3. 检查分发包

```bash
# 检查分发包是否有问题
twine check dist/*
```

## 📤 发布到PyPI

### 选项1：发布到测试PyPI（推荐先测试）

```bash
# 发布到测试PyPI
twine upload --repository testpypi dist/*
```

### 选项2：发布到正式PyPI

```bash
# 发布到正式PyPI
twine upload dist/*
```

### 选项3：发布到测试PyPI并安装测试

```bash
# 发布到测试PyPI
twine upload --repository testpypi dist/*

# 从测试PyPI安装测试
pip install --index-url https://test.pypi.org/simple/ your-package-name
```

## ✅ 验证发布

### 1. 检查PyPI页面

访问你的包页面：
- 正式PyPI：https://pypi.org/project/your-package-name/
- 测试PyPI：https://test.pypi.org/project/your-package-name/

### 2. 验证安装

```bash
# 从正式PyPI安装
pip install your-package-name

# 检查版本
pip show your-package-name
```

### 3. 测试功能

```bash
# 测试命令行工具（如果有）
your-command --help

# 测试Python导入
python -c "import your_package; print('Import successful')"
```

## 🔄 版本管理

### 1. 语义化版本控制

遵循 [语义化版本控制](https://semver.org/lang/zh-CN/) 规范：

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 2. 更新版本号

```bash
# 编辑 pyproject.toml 中的版本号
version = "0.1.1"  # 从 0.1.0 更新到 0.1.1
```

### 3. 版本检查

发布前检查版本是否已存在：

```bash
# 检查版本是否已发布
curl -s "https://pypi.org/pypi/your-package-name/json" | python -m json.tool
```

## ❗ 常见问题

### 1. 版本冲突

**问题**：`HTTPError: 400 Client Error: File already exists.`

**解决方案**：
- 更新版本号
- 删除已存在的版本（如果刚发布且没有用户）

### 2. 认证失败

**问题**：`HTTPError: 401 Client Error: Unauthorized`

**解决方案**：
- 检查 `~/.pypirc` 配置
- 验证API Token是否正确
- 确认Token有上传权限

### 3. 许可证警告

**问题**：构建时出现许可证配置警告

**解决方案**：
```toml
# 使用SPDX标识符而不是文件引用
license = "MIT"  # 而不是 license = {file = "LICENSE"}

# 移除过时的许可证分类器
# 删除 "License :: OSI Approved :: MIT License"
```

### 4. 包名冲突

**问题**：包名已被占用

**解决方案**：
- 选择新的包名
- 联系包所有者转让
- 使用不同的包名

## 🎯 最佳实践

### 1. 发布前检查清单

- [ ] 更新版本号
- [ ] 更新CHANGELOG.md
- [ ] 测试所有功能
- [ ] 检查依赖项
- [ ] 验证README.md格式
- [ ] 运行代码检查工具

### 2. 自动化发布

考虑使用GitHub Actions自动化发布流程：

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build and publish
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        python -m build
        twine upload dist/*
```

### 3. 测试策略

1. **本地测试**：在发布前本地测试所有功能
2. **测试PyPI**：先发布到测试PyPI验证
3. **渐进式发布**：使用预发布版本测试

### 4. 文档维护

- 保持README.md更新
- 提供清晰的安装和使用说明
- 包含示例代码
- 维护CHANGELOG.md

## 📚 相关资源

- [PyPI官方文档](https://packaging.python.org/tutorials/packaging-projects/)
- [setuptools文档](https://setuptools.pypa.io/en/latest/)
- [twine文档](https://twine.readthedocs.io/)
- [语义化版本控制](https://semver.org/lang/zh-CN/)

## 🔧 实用命令

```bash
# 查看已安装的包信息
pip show your-package-name

# 卸载包
pip uninstall your-package-name

# 查看包的元数据
python -c "import your_package; print(your_package.__version__)"

# 检查包的依赖
pip check your-package-name

# 验证分发包
twine check dist/*

# 查看PyPI包信息
curl -s "https://pypi.org/pypi/your-package-name/json" | python -m json.tool
```

---

**注意**：发布到PyPI后，包将对全球用户可用。请确保代码质量和文档完整性，为用户提供良好的体验。 