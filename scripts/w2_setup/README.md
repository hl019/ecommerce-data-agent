# W2 MySQL 环境准备

> 进入 W2（工具层开发）前必须完成的环境准备。预计耗时 1.5 小时。

---

## 前置条件

- MySQL 已安装并启动（推荐 MySQL 8.0+）
- Navicat 或 MySQL Workbench 已安装（用于可视化管理）
- Python 虚拟环境已激活（OpenManus 的 `.venv`）

---

## 三步完成环境准备

### Step 1：建库建表（10 分钟）

**方式 A：Navicat 可视化执行**
1. 打开 Navicat → 连接 MySQL
2. 右键连接 → 「新建数据库」→ 名称 `ecommerce_agent`，字符集 `utf8mb4`
3. 双击打开数据库 → 菜单栏「查询」→「新建查询」
4. 复制 `01_create_database.sql` 内容 → 粘贴 → 点击「运行」
5. 刷新左侧树，应看到三张表：Customers / Products / Transactions

**方式 B：命令行执行**
```bash
mysql -u root -p < D:\projects\ecommerce-data-agent\scripts\w2_setup\01_create_database.sql
```

### Step 2：安装 Python 依赖（2 分钟）

```bash
pip install pandas sqlalchemy pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Step 3：导入数据（5 分钟）

1. 打开 `02_import_data.py`，修改配置区：
   - `MYSQL_PASSWORD`：你的 MySQL 密码（空字符串=无密码）
   - 其他配置保持默认即可

2. 运行脚本：
   ```bash
   python D:\projects\ecommerce-data-agent\scripts\w2_setup\02_import_data.py
   ```

3. 看到以下输出 = 成功：
   ```
   ✓ 成功导入 199 行到 Customers 表
   ✓ 成功导入 100 行到 Products 表
   ✓ 成功导入 1000 行到 Transactions 表
   ```

---

## 验证

用 Navicat 打开 `ecommerce_agent` 库，双击任意表查看数据：
- Customers：199 行
- Products：100 行
- Transactions：1000 行

---

## 可能踩的坑

| 现象 | 原因 | 解决 |
|---|---|---|
| `Access denied for user 'root'` | 密码错误 | 检查 `MYSQL_PASSWORD` 配置 |
| `Can't connect to MySQL server` | MySQL 未启动 | 服务管理器启动 MySQL |
| `Table already exists` | 表已存在 | 忽略（`CREATE TABLE IF NOT EXISTS` 不会报错） |
| 导入后行数为 0 | CSV 路径错误 | 检查 `DATA_DIR` 路径是否正确 |

---

## 数据说明

三张表来自 `hl019-ecommerce-viaapi` 仓库（你的电商数据分析项目）：
- **Customers**：199 位客户（ID/姓名/地区/注册日期）
- **Products**：100 件商品（ID/名称/品类/单价）
- **Transactions**：1000 笔交易（ID/客户/商品/时间/数量/总额）

这是 W2 四个工具（SQL查询/pandas统计/Plotly绘图/报告生成）的数据基础。

---

## 下一步

环境准备完成后，进入 W2 核心任务：亲手写四个工具。
详见《ZCode-修订版四周计划.md》W2 部分 + 《ZCode-03-W2工具设计草案.md》。
