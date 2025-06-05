# 🖼️ 微信公众号图片下载助手

一个专业的微信公众号文章图片提取和下载工具，支持智能筛选、批量下载和高清原图获取。

## 🚀 快速使用指南

### 📥 首次启动（自动安装环境）

**Windows用户（推荐）**：
- 双击运行：`one_click_deploy.bat`
- ✅ 自动检查Python环境
- ✅ 自动安装所需依赖
- ✅ 自动打开浏览器
- ✅ 无需任何手动配置

**所有平台通用**：
```bash
python one_click_deploy.py
```
- ✅ 支持Windows/Mac/Linux
- ✅ 智能依赖安装（多镜像源）
- ✅ 详细进度反馈
- ✅ 自动处理安装失败

### ⚡ 后续启动（快速启动）

**Windows用户（推荐）**：
- 双击运行：`quick_start.bat`
- ✅ 跳过环境检查，直接启动
- ✅ 启动速度更快
- ✅ 自动打开浏览器

**所有平台通用**：
```bash
python run.py
```
- ✅ 简单直接启动
- ✅ 适合开发者使用

### 📝 使用步骤
1. **首次使用**：运行 `one_click_deploy.bat` 或 `python one_click_deploy.py`
2. **后续使用**：运行 `quick_start.bat` 或 `python run.py`
3. 在浏览器中访问 `http://127.0.0.1:5000`
4. 粘贴微信公众号文章链接到输入框
5. 点击"开始分析"提取图片
6. 选择需要的图片预览
7. 点击"下载选中图片"获取ZIP文件

> 💡 **提示**：应用支持智能筛选，自动排除头像、小图片和GIF动图。

## ✨ 项目特色

### 🎯 核心功能
- **智能链接解析**：自动识别和解析微信公众号文章结构
- **高清原图提取**：获取图片的最高质量版本，而非压缩预览图
- **智能筛选系统**：自动排除头像、装饰图、GIF等非正文内容
- **批量下载管理**：支持选择性下载和ZIP压缩包输出
- **实时进度监控**：完整的处理进度显示和详细日志

### 🎨 用户体验
- **现代化界面**：采用Bootstrap 5设计，界面简洁美观
- **响应式布局**：完美适配桌面和移动设备
- **操作直观**：仅需输入链接即可一键完成所有操作
- **实时反馈**：丰富的状态提示和错误处理机制

## 🛠️ 技术架构

### 后端技术栈
- **Web框架**：Flask 3.0.0
- **HTTP处理**：requests + beautifulsoup4
- **图片处理**：Pillow
- **并发下载**：concurrent.futures
- **跨域支持**：Flask-CORS

### 前端技术栈
- **UI框架**：Bootstrap 5.3.0
- **图标库**：Font Awesome 6.4.0
- **交互逻辑**：原生JavaScript ES6+
- **响应式设计**：CSS3 + Flexbox/Grid

## 📦 快速开始

### 环境要求
- Python 3.8 或更高版本
- 稳定的网络连接
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 一键启动
```bash
# 克隆或下载项目文件到本地
# 进入项目目录
cd 微信公众号图片下载助手

# 运行启动脚本（自动检查环境并启动）
python run.py
```

启动脚本会自动完成以下操作：
- ✅ 检查Python版本兼容性
- ✅ 检查并安装依赖包
- ✅ 创建必要的目录结构
- ✅ 配置Git环境（避免意外提交）
- ✅ 启动Web应用

### 手动安装（可选）
如果自动启动失败，可以手动安装：

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 创建目录
mkdir downloads temp logs

# 3. 启动应用
python app.py
```

## 🎮 使用指南

### 基本操作流程

1. **启动应用**
   ```bash
   python run.py
   ```

2. **打开浏览器**
   - 访问：`http://127.0.0.1:5000`
   - 或局域网访问：`http://[你的IP]:5000`

3. **输入文章链接**
   - 复制微信公众号文章链接
   - 粘贴到输入框中
   - 示例：`https://mp.weixin.qq.com/s/xxxxxxxxxxxxx`

4. **配置选项（可选）**
   - 排除头像图片 ✅
   - 排除GIF动图 ✅
   - 排除小尺寸图片 ✅
   - 获取高清原图 ✅

5. **开始分析**
   - 点击"开始分析"按钮
   - 等待系统解析文章结构
   - 查看识别出的图片预览

6. **选择下载**
   - 勾选需要下载的图片
   - 或点击"全选"选择所有图片
   - 点击"下载选中图片"

7. **获取文件**
   - 等待下载和打包完成
   - 自动下载ZIP压缩包
   - 解压即可获得所有图片

### 高级功能

#### 智能筛选规则
系统会自动应用以下筛选规则：

- **位置筛选**：排除页眉页脚的装饰图
- **尺寸筛选**：排除过小的图标和装饰元素
- **类型筛选**：可选择性排除GIF动图
- **语义筛选**：基于alt文本和URL特征排除头像等

#### 原图获取算法
针对微信图片CDN的特殊处理：

- **URL规律识别**：自动识别微信图片URL格式
- **参数优化**：移除尺寸限制参数获取原图
- **格式保持**：保持原始图片格式和质量
- **容错处理**：原图获取失败时自动降级

## 📁 项目结构

```
wechat-image-download-assistant/
├── app.py                      # Flask main application file
├── run.py                      # Simple startup script
├── one_click_deploy.py         # One-click deployment script
├── one_click_deploy.bat        # Windows one-click startup
├── quick_start.bat             # Windows quick start script
├── one_click_deploy_guide.md   # Deployment guide
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── templates/                  # HTML template files
│   └── index.html             # Main page template
├── downloads/                  # Downloaded files output directory
├── temp/                      # Temporary files directory
├── logs/                      # Log files directory
└── .PLAN/                     # Project planning documents
    ├── project-overview.md
    ├── requirements.md
    └── ui-mockup.html
```

## 🔧 配置说明

### 主要配置项（app.py）

```python
# 文件夹配置
DOWNLOAD_FOLDER = "downloads"    # 下载文件夹
TEMP_FOLDER = "temp"            # 临时文件夹

# 性能配置
MAX_WORKERS = 5                 # 最大并发下载数
REQUEST_TIMEOUT = 30            # 请求超时时间（秒）
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 最大图片大小（50MB）

# 服务器配置
HOST = '0.0.0.0'               # 监听地址
PORT = 5000                    # 监听端口
DEBUG = True                   # 调试模式
```

### 自定义筛选规则

可以在 `WeChatImageExtractor._should_skip_image()` 方法中自定义筛选规则：

```python
def _should_skip_image(self, img_info: Dict, options: Dict) -> bool:
    # 自定义筛选逻辑
    alt_text = img_info.get('alt', '').lower()
    url = img_info.get('original_url', '')
    
    # 添加自定义关键词
    custom_skip_keywords = ['your_custom_keyword']
    
    # 添加自定义URL模式
    if 'your_pattern' in url:
        return True
    
    return False
```

## 🚀 性能优化

### 下载性能
- **并发下载**：支持最多5个图片同时下载
- **断点续传**：网络中断时自动重试
- **内存优化**：流式下载避免大文件占用内存
- **压缩打包**：使用ZIP压缩减少文件大小

### 网络优化
- **连接复用**：使用Session复用HTTP连接
- **超时控制**：合理的超时设置避免长时间等待
- **错误重试**：智能重试机制提高成功率
- **用户代理**：模拟真实浏览器避免反爬虫

## 🛡️ 注意事项

### 合规使用
- **个人用途**：仅用于个人学习和合法用途
- **版权尊重**：请尊重原作者的版权和知识产权
- **服务条款**：遵守微信公众平台相关规定
- **频率控制**：避免过于频繁的请求

### 技术限制
- **反爬虫**：微信可能更新反爬虫策略
- **链接时效**：部分图片链接可能有时效性
- **网络依赖**：需要稳定的网络连接
- **浏览器兼容**：建议使用现代浏览器

### 安全考虑
- **输入验证**：严格验证用户输入的URL
- **文件安全**：下载的文件仅保存在本地
- **隐私保护**：不收集或存储用户个人信息
- **临时清理**：定期清理临时文件释放空间

## 🐛 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 手动安装依赖
pip install flask flask-cors requests beautifulsoup4 pillow

# 使用国内源（如果网络慢）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2. 无法访问文章
- 检查链接格式是否正确
- 确认文章是否为公开可访问
- 尝试在浏览器中直接打开链接验证

#### 3. 图片下载失败
- 检查网络连接是否稳定
- 某些图片可能有防盗链保护
- 尝试减少并发下载数量

#### 4. 浏览器无法访问
- 确认防火墙设置允许5000端口
- 尝试使用127.0.0.1:5000替代localhost:5000
- 检查是否有其他程序占用5000端口

### 调试模式

启用详细日志：

```python
# 在app.py中设置
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 技术支持

### 文档资源
- 项目概览：`.PLAN/project-overview.md`
- 详细需求：`.PLAN/requirements.md`
- UI设计：`.PLAN/ui-mockup.html`

### 开发指南
- Flask官方文档：https://flask.palletsprojects.com/
- Bootstrap文档：https://getbootstrap.com/docs/5.3/
- requests库文档：https://docs.python-requests.org/

## 📄 开源协议

本项目仅供学习和个人使用，请勿用于商业用途。

## 🎉 更新日志

### v1.0.0 (2024-12-XX)
- ✨ 初始版本发布
- 🎯 完整的微信公众号图片提取功能
- 🎨 现代化的Web界面
- 🚀 智能筛选和批量下载
- 📱 响应式设计支持

---

**🎈 感谢使用微信公众号图片下载助手！如有问题或建议，欢迎反馈。** 