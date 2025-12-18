## `add_messages`

### 默认行为

在 LangGraph 的 State 中，如果没有使用 Annotated 定义 Reducer（合并策略），默认行为是 "Overwrite"（覆盖）。即新的状态值会完全替换掉旧的状态值，而不是合并。

### 用 `operator.add(old_msg, new_msg)`

`operator.add` 是 Python 内置的函数，用于将两个对象相加。特点是只追加，不检查。也就是如果将两个包含同样 id 的 `Message` 对象的列表相加，`operator.add` 会直接将后一个列表的元素追加到前一个列表的末尾，不会检查 id 是否重复。这对于 Langchain 来说是致命的。

### `add_messages`：带主键索引的 `UPSERT`

`add_messages` 是 LangChain 专门写的一个函数。它的真容其实是一个**带有去重和更新逻辑的合并算法**。它不仅仅是把两个列表拼起来，还会检查消息的 `id`。

逻辑（伪代码）

```Python
def add_messages(existing_list, new_list):
    # 1. 把现有的消息建成一个字典，Key是ID
    idx = {m.id: m for m in existing_list}

    for m in new_list:
        # 2. 如果新消息的ID已存在 -> 覆盖旧的 (Update)
        # 3. 如果新消息是特殊指令 (RemoveMessage) -> 删除旧的 (Delete)
        # 4. 如果是新ID -> 追加 (Insert)
        idx[m.id] = m 

    return list(idx.values())
```


