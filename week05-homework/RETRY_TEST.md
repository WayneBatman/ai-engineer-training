# 重试机制测试指南

## 测试方法

### 方法1：使用测试模式（推荐）

测试模式会自动模拟节点失败，无需修改代码。

1. **启用测试模式运行：**
   ```bash
   # Windows (PowerShell)
   $env:TEST_MODE="true"; python -m multi-agent.main

   # Windows (CMD)
   set TEST_MODE=true && python -m multi-agent.main

   # Linux/Mac
   TEST_MODE=true python -m multi-agent.main
   ```

2. **预期行为：**
   - 研究节点会失败 2 次，然后在第 3 次使用备用代理成功
   - 撰写节点会失败 2 次，然后在第 3 次使用备用代理成功
   - 审核节点会失败 2 次，然后在第 3 次使用高级代理成功
   - 最终文档会包含完整的重试日志

### 方法2：断网测试（真实场景）

模拟网络故障测试重试机制：

1. **启动 MCP 服务器**
2. **运行主程序**
3. **在执行过程中断开网络**
4. 观察重试行为
5. **重新连接网络**
6. 观察是否继续执行

### 方法3：手动触发错误

临时修改代码引入错误：

#### 测试一级重试（相同代理）

在 `angent_nodes.py` 的节点函数中添加：
```python
# 在研究节点开头添加
if state.get("retry_count", 0) < 2:
    raise Exception("模拟研究失败")
```

#### 测试二级重试（备用代理）

```python
# 在研究节点开头添加
if not use_backup and state.get("retry_count", 0) < 2:
    raise Exception("主代理失败，测试切换到备用代理")
```

### 方法4：环境变量测试

在 `.env` 文件中添加：
```env
# 测试模式
TEST_MODE=true

# 或者设置错误的 API Key 来测试错误处理
DASHSCOPE_API_KEY=invalid_key
```

## 验证点

### 1. 检查控制台输出

查看是否出现以下标记：
```
[重试策略] researcher - 尝试 1/3
[重试策略] researcher - 尝试 2/3
[重试策略] researcher - 尝试 3/3
[重试策略] researcher - 切换至备用代理
[重试成功] researcher 备用代理执行成功
```

### 2. 检查生成的文档

在 `article_output_*.md` 文件末尾应该有：

```markdown
---

# 异常处理日志

[2026-01-06 10:30:15] researcher 执行失败 (尝试 1/3): [测试] research 模拟执行失败
[2026-01-06 10:30:17] researcher 执行失败 (尝试 2/3): [测试] research 模拟执行失败
[2026-01-06 10:30:19] researcher 执行失败 (尝试 3/3): [测试] research 模拟执行失败
[2026-01-06 10:30:21] reviewer 备用代理执行成功
```

### 3. 验证备用代理是否被使用

检查文档中的内容：
- 研究报告应该比平时更详细（备用研究员）
- 文章草稿质量应该更高（备用撰稿人）
- 审核建议应该更全面（高级审核代理）

## 测试场景矩阵

| 场景 | 预期行为 | 验证方法 |
|------|---------|---------|
| 研究节点失败1次 | 自动重试1次，成功 | 查看日志中的重试计数 |
| 研究节点失败3次 | 切换至备用代理 | 查看日志中的"切换至备用代理" |
| 撰写节点失败多次 | 使用备用撰稿人 | 查看文档质量是否有提升 |
| 审核节点失败多次 | 使用高级审核代理 | 查看审核建议是否更详细 |
| 所有重试均失败 | 记录错误，请求用户干预 | 查看错误提示信息 |

## 调试技巧

### 启用详细日志

在 `retry_utils.py` 中修改：
```python
print(f"[DEBUG] 当前状态: {state}")
print(f"[DEBUG] 重试次数: {retry_count}")
```

### 检查 MCP 连接

确保 MCP 服务器正在运行：
```bash
# 测试连接
curl http://localhost:8000/mcp
```

### 单独测试节点

创建测试脚本：
```python
import asyncio
from angent_nodes import ArticleAgentNode

async def test_single_node():
    # 测试单个节点
    pass
```

## 清理测试数据

测试完成后，删除生成的测试文档：
```bash
rm week05-homework/multi-agent/article_output_*.md
```

## 常见问题

### Q: 测试模式没有生效？
A: 确保环境变量设置正确，或直接在 `main.py` 中设置 `test_mode = True`

### Q: 重试没有按预期工作？
A: 检查 `retry_utils.py` 中的重试逻辑，确保 `max_same_agent_retries` 参数正确

### Q: 备用代理提示词没有加载？
A: 重启 MCP 服务器以加载更新后的 `angent_prompts.py`
