# 基于Langgraph实现多代理的写作系统

## 1. 系统设计
本项目实现了一个简易的多代理的写作系统，主要包含如下两快内容：

* **1.基于LangGraph实现的客户端**
主要构成：
  * 研究角色 (Research Agent): 收集信息。
  * 撰写代理 (Writing Agent): 基于上述信息，撰写文章草稿。
  * 审核代理 (Review Agent): 检查初稿的内容质量和逻辑，并提供修改建议。
  * 润色代理 (Polishing Agent): 结合初稿和修改建议，生成最终稿件。
* **2.基于FastMcp的mcp服务器**
  * 为LLM提供网络搜索能力
  * 利用fastMcp框架，提供mcp能力

## 2. 实验流程
* 正常情况
  * 执行python mcp_server.py，启动mcp服务器
  * 执行python main.py，启动客户端
  * 输入介绍F1.
  * 系统通过研究-》撰写-》审核-》润色之后，输出article_output_20260106_221102.md文档
  并在文档中记录相关内容
* 异常情况
  * 代码中增加相关简易测试代码，断网后，再次按上述测试，观看控制台出现如下提示
```console
[重试策略] researcher - 尝试 1/3
---- 当前节点：研究节点 ----
研究报告已经生成完毕。
[重试策略] writer - 尝试 1/3
--- 当前节点: 撰写节点 ---
文章草稿已经完成。
[重试策略] reviewer - 尝试 1/3
--- 当前节点: 审核节点 ---
[2026-01-06 22:23:24] reviewer 执行失败 (尝试 1/3): ('Connection aborted.', ConnectionAbortedError(10053, '你的主机中的软件中止了一个已建立的连接。', None, 10053, None))
[重试策略] reviewer - 尝试 2/3
--- 当前节点: 审核节点 ---
[2026-01-06 22:23:25] reviewer 执行失败 (尝试 2/3): ('Connection aborted.', ConnectionAbortedError(10053, '你的主机中的软件中止了一个已建立的连接。', None, 10053, None))
[重试策略] reviewer - 切换至备用代理
--- 当前节点: 高级审核节点 ---
[2026-01-06 22:23:25] reviewer 备用代理执行失败: ('Connection aborted.', ConnectionAbortedError(10053, '你的主机中的软件中止了一个已建立的连接。', None, 10053, None))
[重试策略] reviewer - 尝试 3/3
--- 当前节点: 审核节点 ---
[2026-01-06 22:23:26] reviewer 执行失败 (尝试 3/3): ('Connection aborted.', ConnectionAbortedError(10053, '你的主机中的软件中止了一个已建立的连接。', None, 10053, None))
[重试策略] reviewer - 切换至备用代理
--- 当前节点: 高级审核节点 ---
[2026-01-06 22:23:26] reviewer 备用代理执行失败: ('Connection aborted.', ConnectionAbortedError(10053, '你的主机中的软件中止了一个已建立的连接。', None, 10053, None))
[重试策略] reviewer - 所有重试均失败

==================================================
⚠️  reviewer 执行失败
```
成功实现了作业选做部分的内容


## 3. 后续优化方向
当前只是用一个agent实现研究、撰写、审核、润色等角色。可以结合课上所说的A2A，将上述四个角色拆成4个独立的agent处理。
