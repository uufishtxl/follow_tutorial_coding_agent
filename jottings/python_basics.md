## 数据类型

#### `Sequence` vs `list`

- **`list`**: 指具体的列表实现（Mutable）。
    
- **`Sequence`**: 指任何可以按顺序访问的集合（接口），包括列表、元组、字符串等。
    
- **结论**: 在定义 LangGraph 的 State 时，直接写 `list` 即可。因为 LangGraph 专门写的合并函数 `add_messages` 在运行时总是返回一个标准的 `list`。虽然源码中常写 `Sequence` 是为了兼容性，但在应用层没必要。
    
```Python
from typing import TypedDict, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    question: str
    # 推荐写法：明确列表内容类型
    messages: Annotated[list[BaseMessage], add_messages]
```

#### `Annotated`

- **含义**: 顾名思义，`Annotated` 就是“带有注释的数据类型”。
    
- **结构**: `Annotated[T, x]`。
    
    - `T`: 真实数据类型（如 `int`, `list`）。**IDE 和静态检查器只看这里。**
        
    - `x`: 附加的元数据（Metadata）。**运行时工具（如 Pydantic, LangGraph）看这里来执行特定逻辑。**
        

**Pydantic 示例（数据校验）：**

```Python
from typing import Annotated
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    # 运行时检查：必须是 int，且必须 > 18
    age: Annotated[int, Field(gt=18, description="用户年龄")]
```

**LangGraph 示例（状态合并）：**

```Python
# 运行时逻辑：使用 add_messages 函数进行 Append/Upsert，而不是直接覆盖
messages: Annotated[list, add_messages]
```