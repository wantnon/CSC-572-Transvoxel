# 提取 transitionVertexData 数据

## 问题
Python 脚本失败的原因：
1. **系统未安装 Python**：错误代码 9009 表示命令未找到
2. **Python 不在 PATH 中**：即使安装了 Python，也可能不在系统 PATH 中

## 解决方案

### 方案 1：安装 Python（推荐）
1. 从 https://www.python.org/downloads/ 下载并安装 Python 3.x
2. 安装时勾选 "Add Python to PATH"
3. 运行脚本：
   ```bash
   python extract_transition_vertex_data.py > transition_vertex_data_output.txt
   ```
   或者：
   ```bash
   py extract_transition_vertex_data.py > transition_vertex_data_output.txt
   ```

### 方案 2：使用在线 Python 环境
1. 访问 https://repl.it 或 https://www.online-python.com
2. 复制 `extract_transition_vertex_data.py` 的内容
3. 上传 `LOGLEngine/Headers/Transvoxel.h` 文件
4. 运行脚本并复制输出

### 方案 3：手动提取（不推荐，数据量太大）
从 `LOGLEngine/Headers/Transvoxel.h` 第 521-1035 行手动提取所有数据

## 脚本修复
已修复脚本逻辑，现在可以正确处理跨多行的 case。


