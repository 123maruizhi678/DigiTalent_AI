# 01_02 Python环境检查报告

## 检查信息

- 检查时间：2026-11-02T22:21:03+08:00（本机时区；用户时区 Asia/Shanghai）
- 项目：2026 AI 数字化人才平台；D:\AI\Agent
- Conda 环境：AI；路径：D:\anaconda3\envs\AI
- Python：3.11.18 | packaged by Anaconda, Inc. | (main, Oct 26 2026, 18:13:29) [MSC v.1942 64 bit (AMD64)]
- sys.executable：D:\anaconda3\envs\AI\python.exe
- sys.prefix：D:\anaconda3\envs\AI
- 目标 Python 3.11：符合。
- 环境来源：用户说明由 feiyu 克隆，本次未验证历史克隆过程，未操作 feiyu。

## Conda 环境与解释器定位

conda env list 已确认：
~~~text
base                   D:\anaconda3
AI                     D:\anaconda3\envs\AI
feiyu                  D:\anaconda3\envs\feiyu
~~~

临时命令会话激活 AI 后 where.exe python：
~~~text
D:\anaconda3\envs\AI\python.exe
D:\anaconda3\python.exe
C:\Users\mrz\AppData\Local\Microsoft\WindowsApps\python.exe
~~~

AI 解释器处于首位。后续检查全部直接指定该解释器，并加 -B 禁止写入 Python 字节码缓存。

## pip 版本及路径

pip 26.2.2 from D:\anaconda3\envs\AI\Lib\site-packages\pip (python 3.11)；退出码 0。pip 属于 AI 环境。

## pip check 结果

退出码：0
~~~text
No broken requirements found.

~~~

此检查仅验证包声明的依赖约束，不覆盖全部运行时、二进制或业务兼容问题。

## 当前依赖清单

- pip freeze 清单：D:\AI\Agent\docs\技术栈与部署方案\01_python依赖清单.txt
- 同内容保留副本：D:\AI\Agent\docs\技术栈与部署方案\ai_environment_packages.txt
- freeze 非空行数：261
- 元数据记录数：264；标准化包名数：264
- pip freeze 默认可能省略 pip 等打包工具，因此计数可能不同。

## 核心技术依赖检查表

依据 importlib.metadata 查询，不依据目录存在判断安装成功。

| 包名 | 元数据版本 | 安装状态 | 最小导入结果 |
| --- | --- | --- | --- |
| fastapi | 0.162.0 | 已安装 | 导入成功，兼容性尚未验证 |
| uvicorn | 0.54.0 | 已安装 | 导入成功，兼容性尚未验证 |
| pydantic | 2.14.2 | 已安装 | 导入成功，兼容性尚未验证 |
| pydantic-settings | 2.16.2 | 已安装 | 导入成功，兼容性尚未验证 |
| sqlalchemy | 2.1.6 | 已安装 | 导入成功，兼容性尚未验证 |
| pymysql | 1.2.3 | 已安装 | 导入成功，兼容性尚未验证 |
| alembic | — | 未安装 | 未执行 |
| langchain | 1.4.7 | 已安装 | 导入成功，兼容性尚未验证 |
| langgraph | 1.2.19 | 已安装 | 导入成功，兼容性尚未验证 |
| langchain-ollama | 1.1.0 | 已安装 | 导入成功，兼容性尚未验证 |
| pymilvus | 3.0.2 | 已安装 | 导入成功，兼容性尚未验证 |
| langchain-milvus | 0.4.0 | 已安装 | 导入成功，兼容性尚未验证 |
| apscheduler | — | 未安装 | 未执行 |
| pytest | 8.4.2 | 已安装 | 导入成功，兼容性尚未验证 |
| httpx | 0.28.1 | 已安装 | 导入成功，兼容性尚未验证 |
| pandas | 3.1.0 | 已安装 | 导入成功，兼容性尚未验证 |
| openpyxl | 3.1.5 | 已安装 | 导入成功，兼容性尚未验证 |
| psutil | 7.2.2 | 已安装 | 导入成功，兼容性尚未验证 |
| mineru | 4.1.3 | 已安装 | 导入成功，兼容性尚未验证 |

## 核心依赖导入检查结果

每个已安装核心包在独立 AI Python 子进程最小导入，单包超时30秒；未安装项不执行导入。
### fastapi

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\fastapi-0.162.0.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\fastapi\__init__.py
0.162.0

~~~

### uvicorn

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\uvicorn-0.54.0.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\uvicorn\__init__.py
0.54.0

~~~

### pydantic

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\pydantic-2.14.2.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\pydantic\__init__.py
2.14.2

~~~

### pydantic-settings

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\pydantic_settings-2.16.2.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\pydantic_settings\__init__.py
2.16.2

~~~

### sqlalchemy

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\sqlalchemy-2.1.6.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\sqlalchemy\__init__.py
2.1.6

~~~

### pymysql

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\pymysql-1.2.3.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\pymysql\__init__.py
2.2.8

~~~

### langchain

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\langchain-1.4.7.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\langchain\__init__.py
1.4.7

~~~

### langgraph

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\langgraph-1.2.19.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
None
δ�ṩ __version__

~~~

### langchain-ollama

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\langchain_ollama-1.1.0.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\langchain_ollama\__init__.py
1.1.0

~~~

### pymilvus

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\pymilvus-3.0.2.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\pymilvus\__init__.py
3.0.2

~~~

### langchain-milvus

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\langchain_milvus-0.4.0.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\langchain_milvus\__init__.py
δ�ṩ __version__

~~~

### pytest

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\pytest-8.4.2.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\pytest\__init__.py
8.4.2

~~~

### httpx

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\httpx-0.28.1.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\httpx\__init__.py
0.28.1

~~~

### pandas

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\pandas-3.1.0.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\pandas\__init__.py
3.1.0

~~~

### openpyxl

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\openpyxl-3.1.5.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\openpyxl\__init__.py
3.1.5

~~~

### psutil

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\psutil-7.2.2.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\psutil\__init__.py
7.2.2

~~~

### mineru

元数据路径：D:\anaconda3\envs\AI\Lib\site-packages\mineru-4.1.3.dist-info；退出码：0；导入成功，兼容性尚未验证

~~~text
IMPORT_OK
D:\anaconda3\envs\AI\Lib\site-packages\mineru\__init__.py
δ�ṩ __version__

~~~


## 重复依赖及版本异常初查

包名标准化后重复元数据：
~~~json
{}
~~~

版本格式异常：[]

未联网核对版本发布时间、官方来源或安全公告；不将版本格式正常、pip check 通过或最小导入成功视为整体兼容性验证完成。未测试数据库、向量库、模型服务、CUDA 或完整业务。

## 发现的问题

- 核心依赖缺失：alembic, apscheduler

## 后续建议

- 评审本报告后再制定依赖安装与版本调整方案，待用户确认后执行。
- 针对缺失项、pip check 冲突及导入错误逐项核查，形成面向 Python 3.11 的统一版本约束。
- 对重复元数据先核查来源，不自动删除。
- 对已导入成功的核心包，后续验证真实 API、数据库、向量库、模型调用等兼容性。

## 本次是否修改了环境

否。未安装、升级、降级、卸载依赖；未修改 Conda 环境、feiyu、系统 Python、业务代码、持久环境变量或 CUDA 配置。
仅创建本报告和两份清单。激活仅作用于临时命令子进程。第三方包导入会执行其初始化逻辑，本次未主动要求写入配置或连接外部服务。
