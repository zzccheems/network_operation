# Python 网络自动化运维系统
一个企业级网络自动化运维系统，支持网络设备批量配置、多维度巡检、定时巡检守护、Web可视化管理，大幅提升网络运维效率，降低人工操作成本。
## 🌟 核心功能
| 功能模块         | 核心能力                                                                  |
|----------------- |--------------------------------------------------------------------------|
| 批量配置         | 基于模板批量下发配置（VLAN/接口/ACL等），支持参数化模板，适配多厂商设备        |
| 设备巡检         | 巡检接口状态、CPU/内存使用率、VLAN配置、设备在线状态，生成结构化巡检报告       |
| 定时巡检         | 后台守护进程，按自定义周期自动巡检，异常自动记录日志，支持多设备组巡检          |
| Web可视化        | Flask 可视化界面，支持远程操作、历史报告查看、系统日志追溯，无需命令行操作      |
| 日志系统         | 统一日志记录，所有操作可追溯，支持文件+控制台双输出，便于问题排查               |
## 📁 项目结构
network_operation/
├── main.py                 # 主程序入口（CLI交互菜单）
├── config/                 # 配置模块目录
│   ├── config_read.py      # 设备配置读取工具（解析YAML）
│   └── devices.yaml        # 设备组配置文件（核心配置）
├── configure/              # 批量配置核心模块
│   ├── batch_configuration.py # 批量配置逻辑（模板渲染+命令下发）
│   └── templates/          # 配置模板目录
│       ├── vlan_tpl.txt    # VLAN配置模板示例
│       └── interface_tpl.txt # 接口配置模板示例
├── connect/                # 设备连接模块
│   └── connect_core.py     # Netmiko设备连接封装（SSH）
├── inspect_module/         # 巡检核心模块
│   ├── batch_inspect.py    # 批量巡检逻辑（CPU/内存/接口/VLAN）
│   └── inspect_report/     # 巡检报告存储目录（JSON格式）
├── log/                    # 日志模块
│   └── log_record.py       # 统一日志配置（文件+控制台输出）
├── web/                    # Web可视化模块
│   ├── app.py              # Flask Web服务核心（路由+逻辑）
│   └── templates/          # Web页面模板目录
│       ├── base.html       # 页面基础模板（共用头部/导航）
│       ├── index.html      # 系统首页
│       ├── inspect.html    # 巡检页面
│       ├── config.html     # 批量配置页面
│       └── logs.html       # 日志查看页面
├── logs/                   # 日志存储目录
│   └── main.log            # 系统主日志文件
├── requirements.txt        # 项目依赖清单
└── README.md               # 项目说明文档
