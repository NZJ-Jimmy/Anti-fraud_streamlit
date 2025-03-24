import streamlit as st
from llm import llm
from graph import graph



# Create the Cypher QA chain
from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about Arcaea's contents.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Do not return entire nodes or embedding properties.

Fine Tuning:

- For the name of titles, songs, packs, etc., the case does not matter.
- For the "ratingClass" property, it is a string that can be "Past" (PST), "Present" (PRS), "Future" (FTR), "Beyond" (BYD), or "Eternal" (ETR). A song always has "Past", "Present" and "Future" ratings, but may have "Beyond" and "Eternal" ratings optionally. For Chinese, you should not translate them into "过去", "现在", "未来", "超越", "永恒". Just use the English words. For example, "Past 谱面的定数是 2.0".
- For the "constant" property, Human may call it "potential" (ptt), "潜力值", "定数", or "constant".
- For ChartDesigners, the name of the chart designers may not be same as the "chartDesigner" property in Chart nodes, so as the "name" property in Artist nodes and "name" property in JacketDesigner nodes.
- You should not answer the "id" property of the chart, but its Song title and its ratingClass instead.
- For Chinese, if asking "谁写的谱", it means "Who composed the chart", and the answer should be the name of the ChartDesigner; if asking "谁画的封面", it means "Who illustrated the jacket", and the answer should be the name of the JacketDesigner; if asking "谁创作/唱/写的歌曲", it means "Who created the song", and the answer should be the name of the Artist.
- The "Return" clause should return more information to answer the question. For example, if asking for a song, you should return its whole node.

根据你提供的 Neo4j 命令，当前的图数据库 Schema 可以总结如下：

### 节点类型 (Node Types)
1. **Song**
   - 属性:
     - `id`: 歌曲的唯一标识符。
     - `idx`: 歌曲的索引。
     - `title`: 歌曲的标题（英文）。
     - `artist`: 歌曲的艺术家（曲师）。
     - `bpm`: 歌曲的 BPM（每分钟节拍数），数据类型为字符串。例如 "200", "190-220"。
     - `bpm_base`: 歌曲的基础 BPM。数据类型为整数。例如 200, 190。
     - `version`: 歌曲的版本。
     - `set`: 歌曲所属的集合（通常与 Pack 相关）。
     - `song_date`: 歌曲的发布日期。

2. **Chart**
   - 属性:
     - `id`: 谱的唯一标识符（基于歌曲 ID 和难度等级生成）。
     - `rating`: 谱的难度评级
     - `chartDesigner`: 谱的设计师（谱师）。
     - `ratingClass`: 谱的难度等级（Past, Present, Future, Beyond, Eternal, Null）。
     - `version`: 谱所出现的版本（默认为歌曲的版本）。
     - `chart_date`: 谱的发布日期
     - `constant`: 谱的定数（常数）。

3. **Pack**
   - 属性:
     - `id`: 曲包的唯一标识符。
     - `name`: 曲包的名称（英文）。
     - `description`: 曲包的描述（英文）。

4. **Person**
   - 属性:
     - `name`: 人物的名称。
   - Labels:
     - `ChartDesigner`: 表示该人物是谱面设计师（谱师）。
     - `Artist`: 表示该人物是艺术家（曲师）。
     - `JacketDesigner`: 表示该人物是封面设计师（画师）。

### 关系类型 (Relationship Types)
1. **HAS_CHART**
   - 方向: `Song` → `Chart`
   - 属性:
     - `ratingClass`: 图表的难度等级（Past, Present, Future, Beyond, Eternal, Null）。

2. **HAS_SONG**
   - 方向: `Pack` → `Song`
   - 无属性。

3. **COMPOSED**
   - 方向: `Person` (ChartDesigner) → `Chart`
   - 无属性。

4. **CREATED**
   - 方向: `Person` (Artist) → `Song`
   - 无属性。

5. **ILLUSTRATED**
   - 方向: `Person` (JacketDesigner) → `Song`
   - 无属性。

Example Cypher Statements:

1. To find the songs created by the "Nitro" artist:
```cypher
MATCH (a:Artist {{name: "Nitro"}})-[:CREATED]->(s:Song)
RETURN s AS song
```

2. To find the songs in the "Vicious Labyrinth" pack:
```cypher
MATCH (p:Pack {{name: "Vicious Labyrinth"}})-[:HAS_SONG]->(s:Song)
RETURN s AS song
```

3. To find the constants of the "Grievous Lady" song:
```cypher
MATCH (s:Song {{title: "Grievous Lady"}})-[r:HAS_CHART]->(c:Chart)
RETURN r.ratingClass AS ratingClass, c.constant AS constant
```

4. To find the songs composed by "石樂":
```cypher
MATCH (a:ChartDesigner {{name: "石樂"}})-[:COMPOSED]->(c:Chart)<-[:HAS_CHART]-(s:Song)
RETURN DISTINCT s AS song
```

5. To find the songs illustrated by "雨風雪夏":
```cypher
MATCH (a:JacketDesigner {{name: "雨風雪夏"}})-[:ILLUSTRATED]->(s:Song)
RETURN s AS song
```

Schema:
{schema}

Question:
{question}
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt,
    allow_dangerous_requests=True
)