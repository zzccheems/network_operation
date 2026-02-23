# Python 网络自动化运维系统
一个网络自动化运维系统，支持网络设备批量配置、多维度巡检、定时巡检守护、Web可视化管理，大幅提升网络运维效率，降低人工操作成本。

---

## 🌟 核心功能

| 功能模块     | 核心能力                                                                 |
|--------------|--------------------------------------------------------------------------|
| 批量配置     | 基于模板批量下发配置（VLAN/接口/ACL等），支持参数化模板，适配多厂商设备   |
| 设备巡检     | 巡检接口状态、CPU/内存使用率、VLAN配置、设备在线状态，生成结构化巡检报告 |
| 定时巡检     | 后台守护进程，按自定义周期自动巡检，异常自动记录日志，支持多设备组巡检   |
| Web可视化    | Flask 可视化界面，支持远程操作、历史报告查看、系统日志追溯，无需命令行操作 |
| 日志系统     | 统一日志记录，所有操作可追溯，支持文件+控制台双输出，便于问题排查         |

---

## 📦 项目模块

- **main.py**：主程序入口，提供 CLI 交互菜单，统一调度各功能模块
- **run_web.py**：一键启动 Web 界面（推荐直接使用）
- **config/**：配置模块，负责设备组配置读取与管理
- **configure/**：批量配置模块，基于模板批量下发配置
- **connect/**：设备连接模块，封装 Netmiko 实现 SSH 连接
- **inspect_module/**：巡检核心模块，支持批量巡检与报告生成
- **log/**：统一日志模块，支持文件+控制台双输出
- **web/**：Web 可视化模块，基于 Flask 提供可视化管理界面
- **requirements.txt**：项目依赖清单
- **README.md**：项目说明文档

---

## 📋 环境要求

- Python 3.8+
- 操作系统：Linux / macOS / Windows
- 依赖库：`netmiko`, `flask`, `schedule` 等（详见 `requirements.txt`）

---

## 🚀 快速开始

1. 进入项目目录
   ```bash
   cd network_operation
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 配置设备（可选）
   - 在 `config/devices.yaml` 中配置设备组与设备信息（IP、账号、设备类型等）。若未配置，Web 可正常启动，设备组列表为空。
   - 系统配置可编辑 `config/settings.yaml`（巡检间隔、日志、Web 端口等）。

4. 启动方式（任选其一）

   **方式一：仅启动 Web 界面（推荐，一键使用）**
   ```bash
   python run_web.py
   ```
   浏览器访问：**http://127.0.0.1:5000**

   **方式二：完整 CLI 菜单（含定时巡检、批量配置等）**
   ```bash
   python main.py
   ```
   在菜单中选择「4. 启动Web可视化界面」即可打开 Web。

5. 若从仓库克隆，可先克隆再按上述步骤操作：
   ```bash
   git clone https://github.com/你的用户名/network_operation.git
   cd network_operation
   pip install -r requirements.txt
   python run_web.py
