# W2 MySQL 环境准备

> 进入 W2（工具层开发）前必须完成的环境准备。预计耗时 1.5 小时。

---

## 前置条件

- **MySQL 已部署到 D:\mysql**（ZCode 于 2026-09-25 完成：华为云镜像下载 8.0.29 → 解压 → my.ini → 数据目录初始化 → 控制台模式自测通过）。**还剩两步需要你的管理员权限**，见下节；
- Navicat 或 MySQL Workbench 已安装（用于可视化管理，可选）；
- Python 虚拟环境已激活（OpenManus 的 `.venv`）。

## Step 0：激活 MySQL 服务（仅两步，约 3 分钟）

1. **右键** `install_mysql_service.bat` → **以管理员身份运行**（注册 MySQL80 服务 + 启动 + 加 PATH）。
   看到 `[OK] MySQL80 installed and RUNNING` = 成功。
2. **新开一个终端**（PATH 生效需要新终端），设 root 密码（密码只在你手里，进记事本，不进 git 不发任何人）：
   ```
   mysql -u root
   ```
   （此刻是空密码，直接回车进得去）然后在 `mysql>` 提示符下：
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY '你自己设的密码';
   exit
   ```

**四条验收**（考核官口径，全绿才算完）：
1. `services.msc` 里 MySQL80 状态「正在运行」；
2. `netstat -an | findstr 3306` 有 LISTENING；
3. 新终端 `mysql -u root -p` 输密码能登录；
4. 双击 `一键初始化数据库.bat` → 输密码 → `✓ 初始化完成` + 200/100/1000。

## 数据导入（Step 0 完成后）

---

## 方式一：一键初始化（推荐，考核官验收口径）

双击 `一键初始化数据库.bat`，或在 OpenManus 虚拟环境里执行：

```bash
python D:\projects\ecommerce-data-agent\scripts\w2_setup\one_click_init.py
```

脚本会依次：建库建表（执行 `01_create_database.sql`）→ 清空重导三张 CSV（幂等，重复跑不翻倍）→ 验证行数（200/100/1000）→ 跑一条真实的月度销售额 SQL 给你看。密码运行时输入（不回显、不落盘），或提前 `set MYSQL_PASSWORD=你的密码`。

看到 `✓ 初始化完成，W2 可以开工了` = 数据库就绪。也可在 Navicat 里执行 `03_verify.sql` 四段查询二次确认。

## 方式二：手动三步（理解每一步在干什么时用）

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
   ✓ 成功导入 200 行到 Customers 表
   ✓ 成功导入 100 行到 Products 表
   ✓ 成功导入 1000 行到 Transactions 表
   ```

---

## 验证

用 Navicat 打开 `ecommerce_agent` 库，双击任意表查看数据：
- Customers：200 行
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
- **Customers**：200 位客户（ID/姓名/地区/注册日期）
- **Products**：100 件商品（ID/名称/品类/单价）
- **Transactions**：1000 笔交易（ID/客户/商品/时间/数量/总额）

这是 W2 四个工具（SQL查询/pandas统计/Plotly绘图/报告生成）的数据基础。

---

## 下一步

环境准备完成后，进入 W2 核心任务：亲手写四个工具。
详见《ZCode-修订版计划.md》（review）W2 部分 + 《ZCode-03-W2工具设计草案.md》。
