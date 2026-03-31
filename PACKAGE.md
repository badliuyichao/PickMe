# PickMe 抽奖系统 - 打包与部署指南

## 📦 打包为 Windows 可执行文件

### 步骤 1: 安装打包工具

```bash
pip install pyinstaller
```

### 步骤 2: 运行打包脚本

```bash
python build.py
```

或者手动执行：

```bash
pyinstaller --onefile --windowed --name=PickMe --add-data=data;data main.py
```

### 步骤 3: 获取可执行文件

打包完成后，在 `dist/` 目录下会生成 `PickMe.exe` 文件。

---

## 🚀 部署说明

### 单机部署

1. 将 `dist/PickMe.exe` 复制到目标位置
2. 创建 `data/` 目录并与 exe 放在同一位置
3. 双击 `PickMe.exe` 即可运行

### 分发给他人

**方式一: ZIP压缩包**
```
PickMe/
├── PickMe.exe
├── data/
└── README.txt (使用说明)
```

压缩后发送给用户。

**方式二: 制作安装包**

使用 `Inno Setup` 或 `NSIS` 制作专业安装程序。

---

## ⚠️ 注意事项

1. **数据文件**: 确保 `data/` 目录与 exe 文件在同一目录
2. **首次运行**: 需要手动添加参与者或导入名单
3. **数据备份**: 定期备份 `data/` 目录中的 JSON 文件
4. **系统要求**: Windows 10/11，无需安装 Python

---

## 🔧 常见打包问题

**Q: 打包后运行提示缺少模块？**

确保在打包前已安装所有依赖：
```bash
pip install -r requirements.txt
pip install pyinstaller
```

**Q: 如何添加自定义图标？**

准备一个 `.ico` 格式的图标文件，放在 `assets/icon.ico`
打包时会自动包含。

**Q: 打包后文件太大？**

可以使用 UPX 压缩：
```bash
pyinstaller --onefile --windowed --upx-dir=upx main.py
```

---

## 📋 发布检查清单

- [ ] 已安装所有依赖
- [ ] 测试程序运行正常
- [ ] 打包成功生成 exe
- [ ] exe 可正常运行
- [ ] data 目录包含在发布包中
- [ ] 提供使用说明文档
- [ ] 测试导入导出功能
- [ ] 测试抽奖功能

---

## 🎉 完成后即可分发！

用户无需安装 Python，直接双击 exe 即可使用。