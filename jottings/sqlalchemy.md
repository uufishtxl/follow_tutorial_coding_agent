# SQLAlchemy ORM 学习笔记

## Skeleton Procedures（骨架步骤）

1. **继承 DeclarativeBase，创建 Base model**
2. **继承 Base，创建表格模型**
3. **创建 engine**，连接到既有 URL 或者文件 (`create_engine`，此时 db 可能是空的）
4. **将 Base 交给 engine**，创建具体的表格 (`Base.metadata.create_all`)
5. **用 sessionmaker 创建 Session 类**，引导后续会话
6. **创建上下文管理器**，yield session，并安全地提交/回滚/关闭会话

```python
# 1. 创建 Base model
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# 2. 继承 Base，定义表格模型
class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")

# 3. 创建 engine（此时数据库可能是空的）
from sqlalchemy import create_engine
engine = create_engine("sqlite:///my_database.db")

# 4. 用 Base.metadata 创建所有表格
Base.metadata.create_all(engine)

# 5. 用 sessionmaker 创建 Session 类
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

# 6. 上下文管理器安全管理会话
from contextlib import contextmanager

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

---

## 表格定义知识点

### ForeignKey（外键）

- 定义外键约束，建立表间物理关联
- 是**数据库层面**的约束

```python
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
```

### relationship 和 back_populates（双向同步）

- `relationship` 是 **ORM 层面**的便利功能，用于在 Python 中访问相关对象
- `back_populates` 确保双向同步：修改一方，另一方自动更新

```python
class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # relationship 让我们可以通过 customer.orders 访问所有订单
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    # 通过 order.customer 访问对应的客户
    customer: Mapped["Customer"] = relationship(back_populates="orders")
```

### 关键理解

| 概念 | 层面 | 作用 |
|------|------|------|
| `ForeignKey` | 数据库层 | 建立物理约束 |
| `relationship` | ORM 层 | 便于访问相关对象 |
| `back_populates` | ORM 层 | 确保双向引用同步 |

---

## 待学习

- [ ] 查询操作 (Session.query / select)
- [ ] 级联删除 (cascade)
- [ ] 懒加载 vs 预加载 (lazy loading)
