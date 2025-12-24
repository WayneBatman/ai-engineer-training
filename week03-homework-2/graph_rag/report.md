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

20251224
```python
    #通过增加文本语义分割的节点解析器，来提高rag的检索准确性
    spliter = SemanticSplitterNodeParser.from_defaults(
        embed_model=config.Settings.embed_model
    )
```
通过增加节点解析器，提高rag的检索准确性
对于问题： "通用汽车公司的成立日期？"
通过控制台打印看，已经检索到准确的的信息--通用汽车公司的成立时间。但是实际最终结果，还是返回了上汽通用五菱的背景信息
控制台打印：
```console
当前用户问题: 通用汽车公司的成立日期？
步骤 1: 从问题 '通用汽车公司的成立日期？' 中识别出核心实体 -> '通用汽车公司'
步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。
Graph Store Query:
MATCH (c:Company {name: '通用汽车公司'})-[:RELATED_TO*0..]-(related)                                                                                                                                                                                                                                             
RETURN c, related                                                                                                                                                                                                                                                                                                
2025-12-24 10:00:39,843 - WARNING - Received notification from DBMS server: {severity: WARNING} {code: Neo.ClientNotification.Statement.UnknownRelationshipTypeWarning} {category: UNRECOGNIZED} {title: The provided relationship type is not in the database.} {description: One of the relationship types in your query is not available in the database, make sure you didn't misspell it or that the label is available when you run this statement in your application (the missing relationship type is: RELATED_TO)} {position: line: 1, column: 38, offset: 37} for query: "MATCH (c:Company {name: '通用汽车公司'})-[:RELATED_TO*0..]-(related)\nRETURN c, related"
2025-12-24 10:00:39,843 - WARNING - Received notification from DBMS server: {severity: WARNING} {code: Neo.ClientNotification.Statement.UnknownLabelWarning} {category: UNRECOGNIZED} {title: The provided label is not in the database.} {description: One of the labels in your query is not available in the database, make sure you didn't misspell it or that the label is available when you run this statement in your application (the missing label name is: Company)} {position: line: 1, column: 10, offset: 9} for query: "MATCH (c:Company {name: '通用汽车公司'})-[:RELATED_TO*0..]-(related)\nRETURN c, related"
Graph Store Response:
[]                                                                                                                                                                                                                                                                                                               
Final Response: 未找到与“通用汽车公司”相关的信息。                                                                                                                                                                                                                                                               
rag检索：通用汽车公司成立于1908年9月22日，总部位于美国。其主营业务涵盖整车及相关配件的生产、移动出行服务以及汽车行业上下游服务。公司前身为1903年由戴维·别克创办的别克汽车公司，业务遍及全球汽车生产与销售，旗下拥有别克、雪佛兰、凯迪拉克、GMC等多个知名品牌。2023年，公司实现收入1718亿美元。近年来，通用汽车积 极推进电气化转型，包括更换企业LOGO以及投资电池材料领域。
```
但是实际返回:
```浏览器
{
  "final_answer": "通用汽车公司（General Motors Company）成立于1908年9月22日。",
  "reasoning_path": [
    "步骤 1: 从问题 '通用汽车公司的成立日期？' 中识别出核心实体 -> '通用汽车公司'",
    "步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。",
    "   - 图谱查询结果: 未找到与“通用汽车公司”相关的信息。",
    "步骤 3: 通过 RAG 检索关于 '通用汽车公司' 的背景文档信息。",
    "   - RAG 检索到的上下文: 公司名称: 上汽通用五菱\r\n成立日期: 2002-11-18\r\n总部地点: 中国柳州\r\n主营业务: 各类乘用车以及特种汽车生产、制造以及与汽车相关配件的生产、制造\r\n公司简介: 上汽通用五菱企业愿景为“成为全球创新、跨界、体验的标杆公司”。拥有五菱和宝骏两个高价值汽车品牌：五菱品牌不忘初心，持续深耕人民需求，要造人民买得起、用得上、用得好的产品；宝骏品牌以“年轻、科技、向上”为标签，致力于对未来生...",
    "步骤 4: 综合图谱结果和文档信息，由 LLM 生成最终的自然语言回答。"
  ]
}
```
20251224
```python
rag_response = _rag_query_engine.query(question)
    print("rag_response:", rag_response)
    for node in rag_response.source_nodes:
        # 从节点文本中解析出原始问题和答案
        print("score:", node.get_score())

    rag_context = rag_response.response
    reasoning_path.append(f"步骤 3: 通过 RAG 检索关于 '{entity_name}' 的背景文档信息。")
    reasoning_path.append(f"   - RAG 检索到的上下文: {rag_context[:200]}...")  # 仅显示部分
```
通过调整最后输出解析，解决找到答案，但实际回答不对的问题。
控制台如下
```console
当前用户问题: 通用成立时间？
步骤 1: 从问题 '通用成立时间？' 中识别出核心实体 -> '通用'
步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。
Graph Store Query:
MATCH (n {name: '通用'}) RETURN n                                                                                                                                                                                                                                                                                
Graph Store Response:                                                                                                                                                                                                                                                                                            
[]                                                                                                                                                                                                                                                                                                               
Final Response: 未找到与 '通用' 相关的信息。                                                                                                                                                                                                                                                                     
rag_response: 1908-09-22                                                                                                                                                                                                                                                                                         
score: 0.5339464480349062
```
浏览器返回信息
```浏览器
{
  "final_answer": "通用汽车公司（General Motors）成立于1908年9月16日。",
  "reasoning_path": [
    "步骤 1: 从问题 '通用成立时间？' 中识别出核心实体 -> '通用'",
    "步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。",
    "   - 图谱查询结果: 未找到与 '通用' 相关的信息。",
    "步骤 3: 通过 RAG 检索关于 '通用' 的背景文档信息。",
    "   - RAG 检索到的上下文: 1908-09-22...",
    "步骤 4: 综合图谱结果和文档信息，由 LLM 生成最终的自然语言回答。"
  ]
}
```
不过，还是发现了一个bug，大模型自己又去网络搜索（成立于1908年9月16日），然后没有使用本地RAG中的成立时间---1908-09-22
之前的原因分析：
是因为在milvus_faq这个作业里，本地文档的格式是csv，且是 问题：答案这种表格形式的，
如果直接拿过来用，就会出现解析不对的问题。

20251224
```python
    final_answer_prompt = PromptTemplate(
        "你是一个专业的金融分析师。请根据以下信息，以清晰、简洁的语言回答用户的问题。\n"
        "请严格根据以下信息回答问题，不要使用任何外部知识或实时搜索功能。"
        "即使你觉得信息有误，也不要纠正，只需照原文回答。"
        "--- 用户问题 ---\n{question}\n\n"
        "--- 知识图谱查询结果 ---\n{kg_result}\n\n"
        "--- 相关文档信息 ---\n{rag_context}\n\n"
        "--- 最终回答 ---\n"
    )
```
最终，通过提示词的严格限制，不让大模型去联网搜索。
qwen-plus的enable_search:False属性，怎么放都有问题。
控制台打印如下
```console
DEBUG:dashscope:Request body: {'model': 'qwen-plus', 'parameters': {'max_tokens': 256, 'temperature': 0.1, 'seed': 1234, 'result_format': 'message'}, 'input': {'messages': [{'role': 'system', 'content': "You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines."}, {'role': 'user', 'content': 'Context information is below.\n---------------------\nfile_path: data\\company.txt\n\n公司名称: 上汽通用五菱\r\n成立日期: 2002-11-18\r\n总部地点: 中国柳州\r\n主营业务: 各类乘用车以及特种汽车生产、制造以及与汽车相关配件的生产、制造\r\n公司简介: 上汽通用五菱企业愿景为“成为全球创新、跨界、体验的标杆公司”。拥有五菱和宝骏两个高价值汽车品牌：五菱品牌不忘初心，持续深耕人民需求，要造人民买得起、用得上、用得好的产品；宝骏品牌以“年轻、科技、向上”为标签，致力于对未来生活的探索，以“科技宜人，时尚为民”为品牌宣言，宝骏品牌历久弥新，转型新时代，目标成为新能源“民心”科技的普及者，开发人民享受得起的科技产品，成为公司新质生产力的增长点。\r\n\r\n公司名称: 上汽集团\r\n成立日期: 1920-01-01\r\n总部地点: 中国上海\r\n主营业务: 整车以及相关配件的生产、移动出行服务\r\n公司简介: 上海汽车集团股份有限公司（简称"上汽集团"，股票代码600104）于2011年实现整体上市。集团全年实现整车批售401.3万辆，零售463.9万辆。其中，自主品牌销量274.1万辆，销量占比近百分 之六十。新能源车销量136.8万辆，同比增长百分三十，海外市场销量108.2万辆，集团"双百万"规模进一步扩大。2025年7月，上汽集团以2024年度合并报表872.239亿美元的营业收入，名列《财富》杂志世界500强第138位，第21次上榜。\r\n\r\n公司名称: 通用汽车公司\r\n成立日期: 1908-09-22\r\n总部地点: 美国\r\n主营业务: 整车以及相 关配件的生产、移动出行服务、汽车行业上下游服务\r\n公司简介: 公司业务涵盖全球汽车生产与销售，旗下品牌包括别克、雪佛兰、凯迪拉克、GMC等，2023年收入达1718亿美元。其前身为1903年戴维·别克创办的别克汽车公司。近年来，通用汽车积极推进电气化转型，包括更换企业LOGO ,和投资电池材料领域。\r\n\r\n公司名称: 上海汽车工 业（集团）有限公司\r\n成立日期: 1997年12月31日\r\n总部地点: 中国上海\r\n主营业务: 经营范围包括汽车，拖拉机，摩托车的生产、研制、销售、开发投资，授权范围内的国有资产经营与管理，国内贸易（除专项规定），咨询服务\r\n公司简介: 上海汽车工业（集团）有限公司成立于1996年03月01日，注册地位于上海市武康路390号，法定代表人为王晓秋。上海汽车工业（集团）有限公司对外投资34家公司，具有6处分支机构。\r\n\r\n公司名称: 中国远洋海运集团有限公司\r\n成立日期: 2016年2月18日\r\n总部地点: 中国\r\n主营业务: 国际船舶运输、国际海运辅助业务；从事货物及技术的进出口业务；海上、陆路、航空国际货运代理业务；自有船舶租赁；船舶、集装箱、钢 材销售；\r\n公司简介: 中国远洋海运集团将打造以航运、综合物流及相关金融服务为支柱，多产业集群、全球领先的综合性物流供应链服务集团。\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: 通用成立时间？\nAnswer: '}]}}
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): dashscope.aliyuncs.com:443
DEBUG:urllib3.connectionpool:https://dashscope.aliyuncs.com:443 "POST /api/v1/services/aigc/text-generation/generation HTTP/1.1" 200 None
DEBUG:dashscope:Response: {'output': {'choices': [{'message': {'content': '1908-09-22', 'role': 'assistant'}, 'finish_reason': 'stop'}]}, 'usage': {'total_tokens': 899, 'output_tokens': 10, 'input_tokens': 889, 'prompt_tokens_details': {'cached_tokens': 0}}, 'request_id': 'd53f26b1-516d-4380-bb65-8d9d7b1a4037'}
rag_response: 1908-09-22
score: 0.5339464480349062
DEBUG:dashscope:Request body: {'model': 'qwen-plus', 'parameters': {'max_tokens': 256, 'temperature': 0.1, 'seed': 1234, 'result_format': 'message'}, 'input': {'messages': [{'role': 'user', 'content': "你是一个专业的金融分析师。请根据以下信息，以清晰、简洁的语言回答用户的问题。\n请严格根据以下信息回答问 题，不要使用任何外部知识或实时搜索功能。即使你觉得信息有误，也不要纠正，只需照原文回答。--- 用户问题 ---\n通用成立时间？\n\n--- 知识图谱查询结果 ---\n未找到与 '通用' 相关的信息。\n\n--- 相关文档信息 ---\n1908-09-22\n\n--- 最终回答 ---\n"}]}}
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): dashscope.aliyuncs.com:443
DEBUG:urllib3.connectionpool:https://dashscope.aliyuncs.com:443 "POST /api/v1/services/aigc/text-generation/generation HTTP/1.1" 200 None
DEBUG:dashscope:Response: {'output': {'choices': [{'message': {'content': '通用成立时间是1908年9月22日。', 'role': 'assistant'}, 'finish_reason': 'stop'}]}, 'usage': {'total_tokens': 126, 'output_tokens': 15, 'input_tokens': 111, 'prompt_tokens_details': {'cached_tokens': 0}}, 'request_id': 'ea454a5c-1da4-426d-92d6-b0dafd31eac4'}
INFO:     127.0.0.1:53253 - "POST /api/query HTTP/1.1" 200 OK
```
浏览器的回复：
```浏览器
{
  "final_answer": "通用成立时间是1908年9月22日。",
  "reasoning_path": [
    "步骤 1: 从问题 '通用成立时间？' 中识别出核心实体 -> '通用'",
    "步骤 2: 未识别到特定模式，使用 LLM 将自然语言转换为 Cypher 查询。",
    "   - 图谱查询结果: 未找到与 '通用' 相关的信息。",
    "步骤 3: 通过 RAG 检索关于 '通用' 的背景文档信息。",
    "   - RAG 检索到的上下文: 1908-09-22...",
    "步骤 4: 综合图谱结果和文档信息，由 LLM 生成最终的自然语言回答。"
  ]
}
```
## 4. 总结
由于引入了Neo4j的图数据库，这个是一个新的数据库，需要花些时间学习其用法。
通过参考别人的代码并加以调试，在不断的调试过程中，积累并消化GraphRAG的使用、技术构成。
20241224
1，通过构建明确的提示词，告知大模型，想要做什么。
2，通过增加合适的节点解析器，将文档拆分，提高rag的检索的准确性
3，要注意本地文档的解析问题。
4，通过系统提示词，可以约束大模型的行为。