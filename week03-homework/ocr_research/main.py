import os
from pathlib import Path
from typing import Union, List

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.core.readers.base import BaseReader
from paddleocr import PaddleOCR

def setup_environment():
    """配置 LlamaIndex 所需的环境和模型"""
    from dotenv import load_dotenv
    from llama_index.core import Settings
    from llama_index.llms.openai_like import OpenAILike
    from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels

    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not found in .env file")

    Settings.llm = OpenAILike(
        model="qwen-plus",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key,
        is_chat_model=True
    )
    Settings.embed_model = DashScopeEmbedding(
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
        api_key=api_key
    )
    print("LlamaIndex environment setup complete.")

class ImageOCRReader(BaseReader):
    """使用 PP-OCR v5 从图像中提取文本并返回 Document"""

    def __init__(self, lang='en', ocr_version='PP-OCRv5',device = 'cpu',
                 img_save_path=None, json_save_path=None,
                 **kwargs):
        """
        Args:
            lang: OCR 语言 ('ch', 'en', 'fr', etc.)
            **kwargs: 其他传递给 PaddleOCR 的参数
        """
        super().__init__()
        self.lang = lang
        self.ocr_version = ocr_version,
        self.img_save_path = img_save_path
        self.json_save_path = json_save_path
        self._ocr = PaddleOCR(
            lang=lang,
            ocr_version=ocr_version,
            device=device,
            **kwargs)

    def load_data(self, file: Union[str, List[str]]) -> List[Document]:
        """
        从单个或多个图像文件中提取文本，返回 Document 列表
        Args:
            file: 图像路径字符串 或 路径列表
        Returns:
            List[Document]
        """
        # 实现 OCR 提取逻辑
        # 将每张图的识别结果拼接成文本
        # 构造 Document 对象，附带元数据（如 image_path, ocr_confidence_avg）

        if isinstance(file, (str, Path)):
            files = [file]
        else:
            files = file

        documents = []

        for file in files:
            image_path_str = str(file)
            # 使用 PaddleOCR 提取文本
            result = self._ocr.predict(image_path_str)

            text_blocks = []

            for i, res in enumerate(result):

                text = res['rec_texts']
                print(text)

                text_blocks.append(f"[Text Block {i + 1}] : {text}")

            # 拼接所有文本块
            full_text = "\n".join(text_blocks)

            # 构造 Document 对象
            doc = Document(
                text=full_text,
                metadata={
                    "image_path": image_path_str,
                    "ocr_model": self.ocr_version,
                    "language": self.lang,
                    "num_text_blocks": len(text_blocks),
                }
            )
            documents.append(doc)

        return documents

def main():
# 作业的入口写在这里。你可以就写这个文件，或者扩展多个文件，但是执行入口留在这里。
# 在根目录可以通过python -m ocr_research.main

    reader = ImageOCRReader(lang='en', ocr_version='PP-OCRv5', device='cpu', img_save_path="output", json_save_path="output")
    documents = reader.load_data(["stocks/louba.jpg","stocks/yushu.jpg","stocks/car.jpg"])

    print(f"Successfully loaded {len(documents)} documents from images.")
    for doc in documents:
        print("\n--- Document ---")
        print(f"Text: {doc.text[:100]}...")
        print(f"Metadata: {doc.metadata}")


    setup_environment()


    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    question1 = "有没有楼巴的时刻表?"
    print(f"\nQuerying: {question1}")
    response1 = query_engine.query(question1)
    print(f"Response: {response1}")

    question2 = "我想学习深度学习，应该看哪本书？"
    print(f"\nQuerying: {question2}")
    response2 = query_engine.query(question2)
    print(f"Response: {response2}")


    question3 = "汽车的胎压是多少？"
    print(f"\nQuerying: {question3}")
    response3 = query_engine.query(question3)
    print(f"Response: {response3}")

if __name__ == "__main__":
    main()