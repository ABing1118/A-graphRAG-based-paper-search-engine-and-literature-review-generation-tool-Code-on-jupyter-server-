## **1. 启动 Ollama** run ollama

在终端执行以下命令：
注意：所有的conda虚拟环境的名称换成自己的虚拟环境

```markdown
cd ~
conda activate ./bishe2
export PATH=$PATH:$(pwd)/ollama/bin
ollama start
```

# 启动 server.py（Uvicorn 服务） run uvicorn service
# 新建一个终端

```markdown
cd ~
conda activate ./bishe2
cd ragtest2
cd utils
uvicorn server:app --host 0.0.0.0 --port 8011
```

# 启动 main.py run main.py
# 新建一个终端

```markdown
cd ~
conda activate ./bishe2
cd ragtest2/utils
python main.py
```

Please check the following link for the local startup method：https://github.com/ABing1118/A-graphRAG-based-paper-search-engine-and-literature-review-generation-tool/tree/new-feature-branch
