import os

import pandas as pd
from neo4j import GraphDatabase

import config


def build_graph():
    print("初始化必要的知识图谱数据开始")
    #加载neo4j
    driver = GraphDatabase.driver(
        config.NEO4J_URI,
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    )

    df = pd.read_csv(os.path.join(config.DATA_DIR, "shareHolder.csv"))
    with driver.session(database=config.NEO4J_DATABASE) as session:
        print("先清空源数据")
        session.run("CREATE (n) RETURN n")

        print("创建节点和关系...")
        # 1. 创建所有公司和股东节点
        query_create_nodes = """
        UNWIND $rows AS row
        MERGE (c:Entity {name: row.company_name})
        ON CREATE SET c.type = '公司'
        MERGE (s:Entity {name: row.shareholder_name})
        ON CREATE SET s.type = row.shareholder_type
        """
        session.run(query_create_nodes, rows=df.to_dict('records'))

        # 2. 创建持股关系
        query_create_rels = """
        UNWIND $rows AS row
        MATCH (shareholder:Entity {name: row.shareholder_name})
        MATCH (company:Entity {name: row.company_name})
        MERGE (shareholder)-[r:HOLDS_SHARES_IN]->(company)
        SET r.share_percentage = toFloat(row.share_percentage)
        """
        session.run(query_create_rels, rows=df.to_dict('records'))

        print("图谱节点和关系创建完成。")

        # 创建索引以优化查询性能
        # print("正在为 'Entity' 节点的 'name' 属性创建索引...")
        # try:
        #     session.run("CREATE INDEX entity_name_index IF NOT EXISTS FOR (n:Entity) ON (n.name)")
        #     print("索引创建成功。")
        # except Exception as e:
        #     print(f"创建索引时出错: {e}")


    driver.close()
    print("初始化必要的知识图谱数据完成")

if __name__ == "__main__":
    build_graph()