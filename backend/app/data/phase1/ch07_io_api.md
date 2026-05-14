# Python IO与API调用

## 学习目标
- 掌握Python文件读写、JSON/YAML/CSV处理
- 学会用requests调用REST API
- 了解异步IO(async/await)基础

---

## 1. 文件读写

### 1.1 文本文件

```python
# 读取
with open('data.txt', 'r', encoding='utf-8') as f:   # with自动关闭文件
    content = f.read()           # 全部读取
    # lines = f.readlines()     # 按行读取为列表
    # for line in f:            # 逐行迭代(内存友好)

# 写入
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write("Hello, Python!\n")
    f.writelines(["line1\n", "line2\n"])

# 追加
with open('log.txt', 'a', encoding='utf-8') as f:
    f.write("新的日志条目\n")
```

**Java对比**: Python的`with`语句 = Java 7的try-with-resources, 但更简洁。

### 1.2 Pathlib——现代路径操作

```python
from pathlib import Path

# 比os.path更优雅
p = Path('data') / 'raw' / 'sales.csv'    # 路径拼接
p.exists()                                  # 是否存在
p.is_file()                                 # 是否是文件
p.stem                                      # "sales"(不含扩展名)
p.suffix                                    # ".csv"
p.parent                                    # Path('data/raw')
p.read_text(encoding='utf-8')               # 一步读取
p.write_text("hello", encoding='utf-8')     # 一步写入

# 批量操作
for csv_file in Path('data').glob('*.csv'):
    print(csv_file)
```

---

## 2. 结构化数据格式

### 2.1 JSON

```python
import json

# Python对象 -> JSON字符串
data = {"name": "Alice", "scores": [90, 85, 92]}
json_str = json.dumps(data, ensure_ascii=False, indent=2)

# JSON字符串 -> Python对象
parsed = json.loads(json_str)

# 直接读写文件
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### 2.2 YAML(配置文件常用)

```python
# 需要安装: pip install pyyaml
import yaml

config = '''
database:
  host: localhost
  port: 5432
  name: mydb
models:
  - name: bert-base
    size: 110M
  - name: gpt2
    size: 124M
'''

parsed = yaml.safe_load(config)    # safe_load防止代码注入
```

### 2.3 CSV

```python
import csv

# 标准库
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)       # 每行是字典
    for row in reader:
        print(row['name'], row['age'])

# Pandas(更强大)
import pandas as pd
df = pd.read_csv('data.csv')
```

---

## 3. HTTP请求(requests库)

### 3.1 基础请求

```python
import requests

# GET
response = requests.get('https://api.example.com/users', params={'page': 1})
data = response.json()               # 自动解析JSON

# POST
response = requests.post(
    'https://api.example.com/users',
    json={'name': 'Alice', 'age': 25},  # 自动序列化+设置Content-Type
    headers={'Authorization': 'Bearer xxx'}
)

# 状态码
response.status_code                  # 200
response.ok                           # True (2xx)
response.raise_for_status()           # 非2xx抛异常

# 超时
response = requests.get(url, timeout=10)
```

### 3.2 Session(连接复用)

```python
# 多次请求复用连接(类似Java的HttpClient连接池)
session = requests.Session()
session.headers.update({'Authorization': 'Bearer xxx'})

# 多个请求共享认证
r1 = session.get('https://api.example.com/me')
r2 = session.get('https://api.example.com/orders')

session.close()

# 或用with
with requests.Session() as session:
    session.get(url)
```

### 3.3 实战: 调用LLM API

```python
import requests

def call_llm(prompt, model="deepseek-chat"):
    '''调用DeepSeek API'''
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

result = call_llm("用Python实现快速排序")
```

---

## 4. 异步IO基础

```python
import asyncio
import aiohttp

async def fetch(session, url):
    '''异步HTTP请求'''
    async with session.get(url) as response:
        return await response.json()

async def fetch_all(urls):
    '''并发请求多个URL'''
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)    # 并发执行
        return results

# 运行
urls = [f"https://api.example.com/page/{i}" for i in range(10)]
results = asyncio.run(fetch_all(urls))
```

**Java对比**: Python的async/await = Java的CompletableFuture, 但语法更简洁。

**何时用异步**: 大量IO等待(如并发请求100个API) -> 异步。CPU密集计算 -> 多进程。一般场景 -> 同步足够。

---

## 练习题

1. 写一个函数`download_dataset(urls: list[str], target_dir: str)`, 并发下载多个文件, 支持重试和进度显示
2. 封装一个`LLMClient`类, 支持同步调用、流式输出、自动重试
3. 写一个CSV->JSON转换器, 支持列类型推断(自动识别日期、数字、布尔值)
