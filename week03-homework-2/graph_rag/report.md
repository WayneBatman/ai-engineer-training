# GraphRAG 多跳问答系统 - 实验结果分析报告
## 1. 项目简介
本程序实现了一个RAG+KG的多跳问答系统
## 2. 核心技术
- 知识图谱：Neo4J
- 检索框架 LlamaIndex
- LLM：qwen-plus
## 3. 核心功能分析
### 3.1 场景一
- **用户问题**："上汽通用五菱的最大股东是谁？"
- **预期系统行为**：
- 1. 从问题中识别实体"上汽通用五菱"和"最大股东"这一意图
- 2. 匹配成功之后，在Neo4j里执行精确查找到上汽集团背后的大股东--上海汽车工业（集团）有限公司
- 3. 通过RAG检索关于上汽通用五菱的背景文档
- 4. 结合上述搜索结果，并利用LLM生成最后的回答
- **结果**:
```json

  "final_answer": "上汽通用五菱的最大股东是**上海汽车工业（集团）有限公司**，持股比例为60.0%。",
  "reasoning_path": [
    "步骤 1: 从问题 '上汽通用五菱的最大股东是谁？' 中识别出核心实体 -> '上汽集团'",
    "步骤 2: 识别到关键词'最大股东'，构造精确 Cypher 查询在图谱中查找。",
    "   - Cypher 查询: MATCH (shareholder:Entity)-[r:HOLDS_SHARES_IN]->(company:Entity {name: '上汽集团'})\n        RETURN shareholder.name AS shareholder, r.share_percentage AS percentage\n        ORDER BY percentage DESC\n        LIMIT 1",
    "   - 图谱查询结果: [{'shareholder': '上海汽车工业（集团）有限公司', 'percentage': 60.0}]",
    "步骤 3: 通过 RAG 检索关于 '上汽集团' 的背景文档信息。",
    "   - RAG 检索到的上下文: 公司名称: 上汽通用五菱\r\n成立日期: 2002-11-18\r\n总部地点: 中国柳州\r\n主营业务: 各类乘用车以及特种汽车生产、制造以及与汽车相关配件的生产、制造\r\n公司简介: 上汽通用五菱企业愿景为“成为全球创新、跨界、体验的标杆公司”。拥有五菱和宝骏两个高价值汽车品牌：五菱品牌不忘初心，持续深耕人民需求，要造人民买得起、用得上、用得好的产品；宝骏品牌以“年轻、科技、向上”为标签，致力于对未来生...",
    "步骤 4: 综合图谱结果和文档信息，由 LLM 生成最终的自然语言回答。"
  ]
}
``` 
- 成功实现了题目要求的多跳功能，
### 3.1 场景二
- **用户问题**："上汽通用五菱的成立时间？"
- **预期系统行为**：
- 1. 从问题中识别实体"上汽通用五菱"和"成立时间"这一意图
- 2. 未匹配到特定模式，由LLM将上述查询转化为Cypher 查询，
- 3. 通过RAG检索关于上汽通用五菱的背景文档
- 4. 结合上述搜索结果，并利用LLM生成最后的回答
- **结果**:
```json
{
  "detail": "处理查询时发生内部错误: {code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '为了查询与': expected 'ALTER', 'ORDER BY', 'CALL', 'USING PERIODIC COMMIT', 'CREATE', 'LOAD CSV', 'START DATABASE', 'STOP DATABASE', 'DEALLOCATE', 'DELETE', 'DENY', 'DETACH', 'DROP', 'DRYRUN', 'FINISH', 'FOREACH', 'GRANT', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REALLOCATE', 'REMOVE', 'RENAME', 'RETURN', 'REVOKE', 'ENABLE SERVER', 'SET', 'SHOW', 'SKIP', 'TERMINATE', 'UNWIND', 'USE' or 'WITH' (line 1, column 1 (offset: 0))\n\"为了查询与“上汽通用五菱”相关的信息并生成查询图谱，我们可以从以下几个维度构建知识图谱的节点和关系。以下是基于公开信息构建的“上汽通用五菱”知识查询图谱结构：\"\n ^}"
}
```
观察控制台，会出现如下报错
```bash
当前用户问题: 上汽通用五菱的成立时间是什么时候？
Graph Store Query:
为了查询与“上汽通用五菱”相关的信息并生成查询图谱，我们可以从以下几个维度构建知识图谱的节点和关系。以下是基于公开信息构建的“上汽通用五菱”知识查询图谱结构：                                                                          
                                                                                                                                                                                                                                    
---                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                    
### 🌐 **查询图谱：上汽通用五菱（SAIC-GM-Wuling）**                                                                                                                                                                                 
                                                                                                                                                                                                                                    
#### 1. **核心实体（中心节点）**                                                                                                                                                                                                    
- **企业名称**：上汽通用五菱汽车股份有限公司（SAIC-GM-Wuling Automobile Co., Ltd.）                                                                                                                                                 
- **简称**：上汽通用五菱 / SGMW                                                                                                                                                                                                     
- **成立时间**：2002年11月18日                                                                                                                                                                                                      
- **总部地点**：中国广西壮族自治区柳州市                                                                                                                                                                                            
                                                                                                                                                                                                                                    
---                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                    
#### 2. **股东与股权结构（关联企业节点）**                                                                                                                                                                                          
--- mermaid                                                                                                                                                                                                                          
graph LR                                                                                                                                                                                                                            
    A[上汽通用五菱] --> B[上汽集团 SAIC Motor]                                                                                                                                                                                      
    A --> C[通用汽车 General Motors]                                                                                                                                                                                                
    A --> D[广西汽车集团 Guangxi Auto Group]                                                                                                                                                                                        
---                                                                                                                                                                                                                                                                                                            
- **上汽集团（SAIC Motor）**：持股约50.1%                                                                                                                                                                                                                                                                        
- **通用汽车（General Motors）**：持股约44%                                                                                                                                                                                                                                                                      
- **广西                                                                                                                                                                                                                                                                                                         
查询处理时发生错误: {code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input '为了查询与': expected 'ALTER', 'ORDER BY', 'CALL', 'USING PERIODIC COMMIT', 'CREATE', 'LOAD CSV', 'START DATABASE', 'STOP DATABASE', 'DEALLOCATE', 'DELETE', 'DENY', 'DETACH', 'DROP', 'DRYRUN', 'FINISH', 'FOREACH', 'GRANT', 'INSERT', 'LIMIT', 'MATCH', 'MERGE', 'NODETACH', 'OFFSET', 'OPTIONAL', 'REALLOCATE', 'REMOVE', 'RENAME', 'RETURN', 'REVOKE', 'ENABLE SERVER', 'SET', 'SHOW', 'SKIP', 'TERMINATE', 'UNWIND', 'USE' or 'WITH' (line 1, column 1 (offset: 0))
"为了查询与“上汽通用五菱”相关的信息并生成查询图谱，我们可以从以下几个维度构建知识图谱的节点和关系。以下是基于公开信息构建的“上汽通用五菱”知识查询图谱结构："
 ^}
```
通过观察发现，是因为在 LLM 将自然语言转换为 Cypher 查询过程中，混入了自然语言的 为了查询 这几个字
这里就比较奇怪了，之前系统提示词里(如下)，明确说明不需要添加其他文字，但是最终还是加上，
```python
    entity_extraction_prompt = PromptTemplate(
        "从以下问题中提取出公司或机构的名称：'{question}'\n"
        "只返回名称，不要添加任何其他文字。"
    )
```

20251224

```python
    DEFAULT_GRAPH_QUERY_PROMPT = PromptTemplate(
        """
        根据问题产生查询图谱
        {query_str}
        请不要额外添加自然语言的描述。
        请符合Cypher语法规范
        """,
        prompt_type=PromptType.TEXT_TO_GRAPH_QUERY,
    )
```
通过构建明确的提示词，解决其他情况下，LLM将自然语言准确的转换为Cypher查询时，混入了其他自然语言描述
问题：通用公司是什么时候成立的？
回答结果：
```json
{
  "final_answer": "“通用公司”通常指的是美国的**通用汽车公司**（General Motors Company）。根据相关信息，其前身为1903年戴维·别克创办的别克汽车公司，而通用汽车公司正式成立于**1908年**。虽然知识库中未明确列出具体日期，但结合历史背景，通用汽车公司于1908年9月16日由威廉·C·杜兰特在美国成立。\n\n因此，通用汽车公司成立于**1908年**。",
  "reasoning_path": [
    "步骤 1: 从问题 '通用公司是什么时候成立的？' 中识别出核心实体 -> '通用公司'",
    "步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。",
    "   - 图谱查询结果: 未找到与 '通用公司' 相关的信息。",
    "步骤 3: 通过 RAG 检索关于 '通用公司' 的背景文档信息。",
    "   - RAG 检索到的上下文: 公司名称: 上汽通用五菱\r\n成立日期: 2002-11-18\r\n总部地点: 中国柳州\r\n主营业务: 各类乘用车以及特种汽车生产、制造以及与汽车相关配件的生产、制造\r\n公司简介: 上汽通用五菱企业愿景为“成为全球创新、跨界、体验的标杆公司”。拥有五菱和宝骏两个高价值汽车品牌：五菱品牌不忘初心，持续深耕人民需求，要造人民买得起、用得上、用得好的产品；宝骏品牌以“年轻、科技、向上”为标签，致力于对未来生...",
    "步骤 4: 综合图谱结果和文档信息，由 LLM 生成最终的自然语言回答。"
  ]
}
```
不过，这个答案虽然解决了报错问题，但是，从结果上看，似乎回答成了上汽通用五菱的成立时间。
## 4. 总结
本程序成功了一半，即实现了精确的匹配。另外一半，由于混入了自然语言，导致解析失败，最终导致查询失败。
目前还不知道怎么解决。
由于引入了Neo4j的图数据库，这个是一个新的数据库，需要花些时间学习其用法。
通过参考别人的代码并加以调试，在不断的调试过程中，积累并消化GraphRAG的使用、技术构成。