# 实验结果分析写在这里!
## 1.架构图
ImageOCRReader 在 LlamaIndex 的数据处理流程中扮演“数据加载器”（Data Loader）的角色。它位于数据源（图像文件）和 LlamaIndex 索引构建之间，负责将原始图像数据转换为标准的 Document 格式。
## 2.核心代码说明
+ 2.1 ImageOCRReader
  + init : 初始化PPOCR的相关参数
  + load_data : 利用PPocr的predict函数，提取图片的相关信息。
  其中rec_texts属性表示为 (List[str]) 文本识别结果列表，仅包含置信度超过text_rec_score_thresh的文本
+ 利用上述参数以及相关其他值，构建Document对象。
+ 2.2 setup_environment方法，初始化llama_index相关核心的参数
+ index = VectorStoreIndex.from_documents(documents)
  + 建立向量索引
+ 用户通过 Query Engine 提问，系统在索引中检索相关文本块，并交由 LLM 生成最终回答。

## 3. OCR 效果评估（人工评估）

| 图像类型     | 示例图片          | 文本特征                     | 分析                                                                    |
| :----------- |:--------------|:-------------------------|:----------------------------------------------------------------------|
| **屏幕截图** | `capture.jpg` | pycharm调试窗口字体、有色块背景、布局简单 | 识别效果很好。背景色块和字体渲染对识别影响很小。                                              |
| **自然场景** | `yushu.jpg`   | 书的封面，手机拍摄得来              | 这是最具挑战性的场景。虽然 PP-OCR 对常见场景有优化，但识别准确率会受字体、拍摄角度、光线和遮挡等因素影响。只识别到英文，中文未识别 |

## 4.错误案例分析（如倾斜、模糊、艺术字体）
由于PPOcr还是挺强大的，我特意上传一个相对倾斜的图片，也成功识别了
不过，这几张图片都是相对来说图片质量比较好的，如果到了真是场景，可能会出现对倾斜模糊图片识别不好的情况。
可能需要通过对模型进行训练和微调，尝试一下。
实在不行，就只能通过降级手段，最后转人工分析。

## 5. Document 封装合理性讨论
将所有的文本都放在text中，保证文本不丢失。
但是，实际上，缺失了父节点的描述，会导致后续溯源的时候，难以分析数据。
另外，由于只保留了最后的文本，丢失了很多关键信息，比如位置信息等。
元数据设计只能简单满足一些检索，当问题复杂的时候，就不行了。

## 6.局限性与改进建议：如何保留空间结构（如表格）？是否可加入 layout analysis（如 PP-Structure）？
+ 当前局限性
  + 丢失了布局信息，其中louba.jpg是一个表格信息，这里只保留了文本，没有保留相对位置。
+ 改进建议：引入 Layout Analysis (版面分析)，比如PP-Structure
+ PP-Structure的简介

  [PP-Structure](https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PP-StructureV3.html)

  参考如下代码修改实现
```python
from paddleocr import PPStructureV3

pipeline = PPStructureV3()
# pipeline = PPStructureV3(lang="en") # 将 lang 参数设置为使用英文文本识别模型。对于其他支持的语言，请参阅第5节：附录部分。默认配置为中英文模型。
# pipeline = PPStructureV3(use_doc_orientation_classify=True) # 通过 use_doc_orientation_classify 指定是否使用文档方向分类模型
# pipeline = PPStructureV3(use_doc_unwarping=True) # 通过 use_doc_unwarping 指定是否使用文本图像矫正模块
# pipeline = PPStructureV3(use_textline_orientation=True) # 通过 use_textline_orientation 指定是否使用文本行方向分类模型
# pipeline = PPStructureV3(device="gpu") # 通过 device 指定模型推理时使用 GPU
output = pipeline.predict("./pp_structure_v3_demo.png")
for res in output:
    res.print() ## 打印预测的结构化输出
    res.save_to_json(save_path="output") ## 保存当前图像的结构化json结果
    res.save_to_markdown(save_path="output") ## 保存当前图像的markdown格式的结果
  ```
附：可能是我的GPU比较差，1050TI，如果用PPocrV5的gpu版本，不能识别到任何文字，只有cpu可以。

