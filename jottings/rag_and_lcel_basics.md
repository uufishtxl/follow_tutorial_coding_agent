# RAG 与 LCEL 基础笔记

## 一、RAG (Retrieval-Augmented Generation) 核心流程

### 1. 准备文档
使用 LangChain 的 `Document` 类型：
```python
from langchain_classic.schema import Document

docs = [
    Document(page_content="文档正文内容", metadata={"source": "来源文件"})
]
```
- `page_content`: 正文内容
- `metadata`: 元数据（来源、时间等）

### 2. 创建 Embeddings
将文本转换为高维向量，用于语义相似度计算：
```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

### 3. 创建向量数据库
使用 Chroma（轻量级，适合开发/中小规模）：
```python
from langchain_community.vectorstores import Chroma

db = Chroma.from_documents(
    docs,                              # 文档列表
    embeddings,                        # embedding 方法
    persist_directory="./data/chroma_db"  # 持久化路径（可选）
)
```

### 4. 创建检索器
```python
retriever = db.as_retriever(search_kwargs={"k": 2})  # 返回 top 2 条
# 或使用相似度阈值
# retriever = db.as_retriever(search_kwargs={"score_threshold": 0.5})
```

---

## 二、LCEL (LangChain Expression Language)

### 核心概念
**管道操作符 `|`**: 将前者的输出作为输入传递给后者

### RAG Chain 示例
```python
retrieval_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

### 数据流解析

| 步骤 | 组件 | 输入 → 输出 |
|------|------|-------------|
| 1 | `retriever` | 用户问题 → 相关 Document 列表 |
| 2 | `format_docs` | Document 列表 → 拼接成长字符串 |
| 3 | `RunnablePassthrough()` | 用户问题 → 原样透传 |
| 4 | 字典组装 | → `{"context": "...", "question": "..."}` |
| 5 | `prompt` | 字典 → 填充模板生成 ChatPromptValue |
| 6 | `llm` | prompt → AIMessage |
| 7 | `StrOutputParser()` | AIMessage → 纯字符串 |

### 并行处理
字典形式 `{"key1": runnable1, "key2": runnable2}` 表示并行执行，结果合并成字典传给下一步。

---

## 三、`invoke()` 的输入

**核心原则**: `invoke()` 的参数类型由 **链的入口组件** 决定

| 场景 | 入口组件 | invoke 输入类型 |
|------|----------|-----------------|
| 直接调用 LLM | `ChatOpenAI` | `List[Message]` |
| RAG 链 | 字典（包含 retriever） | `str` |
| 以 prompt 开头 | `ChatPromptTemplate` | `dict`（模板变量） |

示例：
```python
# RAG 链 - 输入字符串
retrieval_chain.invoke("What does the dog like?")

# 直接调用 LLM - 输入消息列表
llm.invoke([SystemMessage(...), HumanMessage(...)])
```

---

## 四、一句话总结 RAG 流程

```
用户问题 → 检索相关文档 → 拼成 context → 填入 prompt → LLM 回答 → 提取字符串
```
