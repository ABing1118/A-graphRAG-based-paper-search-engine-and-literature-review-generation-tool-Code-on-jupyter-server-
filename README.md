## **1. 启动 Ollama**

在终端执行以下命令：

```markdown
cd ~
conda activate ./bishe2
export PATH=$PATH:$(pwd)/ollama/bin
ollama start
```

```markdown
# 启动 server.py（Uvicorn 服务）
# 新建一个终端
cd ~
conda activate ./bishe2
cd ragtest2
cd utils
uvicorn server:app --host 0.0.0.0 --port 8011
```

```markdown
# 启动 main.py
# 新建一个终端
cd ~
conda activate ./bishe2
cd ragtest2/utils
python main.py
```
