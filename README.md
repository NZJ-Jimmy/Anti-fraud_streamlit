### 项目简介

针对目前图神经网络（GNN）结合知识图谱（Knowledge Graph）在反诈研究上仍较少的现状，本开源项目在技术研究基础上，通过网络爬虫进行对象探测、数据收集、数据处理；利用jieba分词进行实体识别；使用py2neo库构建知识图谱；用neo4j图数据库存储知识图谱；运用 mindspore 构建图神经网络模型对知识图谱进行补全与推理。最后还提出了反诈骗小程序的设计方案。

### 项目设计

#### 聚焦爬虫

<center>
<img src="./images/聚焦爬虫流程图.png">
</center>  
<br>
<center>
<b>聚焦爬虫流程图</b>
</center>


#### 实体识别

<center>
<img src="./images/数据清洗与关键词抽取流程图.png">  
</center>  
<br>
<center>
<b>实体识别流程图</b>  
</center>


#### 知识图谱构建

<center>
<img src="./images/neo4j构建知识图谱的示意图.png">  
</center>  
<br>
<center>
<b>知识图谱构建示意图</b>
</center>


#### 知识图谱推理

<center>
<img src="./images/知识推理流程图.png">  
</center>  
<br>
<center>
<b>知识推理流程图</b>  
</center>




### 爬虫使用

#### 文章爬取

<center>
<img src="./images/文章1.png">
<img src="./images/文章2.png">  
</center>  
<br>
<center>
<b>爬取的文章部分展示</b>  
</center>


#### 数据清洗

<center>
<img src="./images/数据清洗后结果.png">  
</center>  
<br>
<center>
<b>数据清洗后展示</b>  
</center>


### Neo4j 图数据库使用

#### Neo4j 简介
Neo4j是一个高性能的,NOSQL图形数据库，它将结构化数据存储在网络上而不是表中。它是一个嵌入式的、基于磁盘的、具备完全的事务特性的Java持久化引擎，但是它将结构化数据存储在网络(从数学角度叫做图)上而不是表中。Neo4j也可以被看作是一个高性能的图引擎，该引擎具有成熟数据库的所有特性。程序员工作在一个面向对象的、灵活的网络结构下而不是严格、静态的表中——但是他们可以享受到具备完全的事务特性、企业级的数据库的所有好处。  

#### Neo4j安装
Neo4j官网：   
https://neo4j.com/

#### Neo4j使用
<center>
<img src="./images/neo4j1.png">  
</center>  
<center>
<img src="./images/neo4j2.png">  
</center>  
<center>
<img src="./images/neo4j3.png">  
</center>


### mindspore图神经网络使用

#### 代码简介
<center>
<img src="./images/程序说明.png">  
</center>


#### 安装环境

```bash
pip install -r requirements.txt
```

#### 使用

```bash
python Main.py
```

#### 结果图

<center>
<img src="./images/代码运行结果.png">  
</center>  
<br>
<center>
<b>程序结果图</b>  
</center>


打开neo4j输入如下指令
```cypher
MATCH (n) RETURN n LIMIT 100
```
<center>
<img src="./images/知识图谱结果.png">  
</center>  
<br>
<center>
<b>知识图谱结果</b>  
</center>


打开neo4j输入如下指令
```cypher
UNWIND ['0', '1'] AS label
MATCH (n {label: label})
CALL apoc.create.vNode([label], {content:n.content}) YIELD node AS vPerson
RETURN vPerson
```

<center>
<img src="./images/二分类结果.png">  
</center>  
<br>
<center>
<b>二分类结果</b>  
</center>


### 管理仓库

#### 从命令行创建一个新的仓库

```bash
touch README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin https://www.gitlink.org.cn/tmlwacre/fraudKG.git
git push -u origin master
```

#### 从命令行推送已经创建的仓库

```bash
git remote add origin https://www.gitlink.org.cn/tmlwacre/fraudKG.git
git push -u origin master
```

### 文件说明

#### MindSpore知识图谱图神经网络
里面包含测试数据、数据预处理文件、构建知识图谱代码、MindSpore图神经网络代码、测试代码。  
#### 爬虫
里面包含用于爬取网页数据的爬虫代码。  
#### 微信小程序
里面包含现有微信小程序的代码。  
#### 小程序设计图
里面包含未来微信小程序的设计图。  

#### 诈骗案例数据集

里面包含爬虫收集的各个平台的完整数据
