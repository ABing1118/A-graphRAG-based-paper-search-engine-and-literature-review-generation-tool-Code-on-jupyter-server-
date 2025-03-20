from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, WebSocket
from starlette.requests import Request
import asyncio
import os
import logging
import subprocess
import signal
import time
from pathlib import Path

app = FastAPI()

UPLOAD_FOLDER = "/home/jovyan/ragtest2/input"
REVIEW_FILE_PATH = "/home/jovyan/ragtest2/output/review.txt"

# 设置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 全局变量，用于跟踪当前运行的进程
current_process = None
current_task = None
current_query = None

def run_command(command):
    """ 运行 shell 命令并实时显示输出 """
    global current_process
    try:
        logging.info(f"Running command: {command}")
        # 使用Popen启动进程
        current_process = subprocess.Popen(
            command, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 合并标准错误到标准输出
            text=True,
            bufsize=1,  # 行缓冲
            universal_newlines=True,
            preexec_fn=os.setsid
        )
        
        # 实时读取并打印输出
        for line in iter(current_process.stdout.readline, ''):
            print(line, end='')  # 直接打印到控制台
            logging.info(f"CMD: {line.strip()}")  # 同时记录到日志
        
        return_code = current_process.wait()
        current_process = None
        return return_code == 0
        
    except Exception as e:
        logging.error(f"Command failed: {e}")
        current_process = None
        return False

def terminate_current_process():
    """终止当前正在运行的进程"""
    global current_process
    if current_process:
        try:
            # 终止整个进程组
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            logging.info(f"Terminated process group {os.getpgid(current_process.pid)}")
            current_process = None
            return True
        except Exception as e:
            logging.error(f"Failed to terminate process: {e}")
            return False
    return False

async def process_graphrag():
    """ 运行 GraphRAG 处理流程 """
    global current_task
    
    logging.info("Starting GraphRAG processing...")

    # 切换到工作目录
    os.chdir("/home/jovyan/ragtest2")

    # 清空之前的review文件
    if os.path.exists(REVIEW_FILE_PATH):
        with open(REVIEW_FILE_PATH, "w") as f:
            f.write("Generating new literature review...")

    # 运行 GraphRAG 相关命令
    # await asyncio.to_thread(run_command, "python -m graphrag.prompt_tune --config ./settings.yaml --root ./  --output ./prompts")
    await asyncio.to_thread(run_command, "python -m graphrag.index --root ./")
    # ★★★ 关键：给 apiTest.py 传递 --query 参数 ★★★
    # 假设 current_query 就是你想传递的用户查询
    if current_query:
        cmd = f'python utils/apiTest.py --query "{current_query}"'
    else:
        cmd = "python utils/apiTest.py"  # 如果没有就不传
    
    logging.info(f"Running command: {cmd}")
    await asyncio.to_thread(run_command, cmd)
    
    current_task = None
    logging.info("GraphRAG processing completed")

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),     # 上传的文件
    request: Request = None           # 用于获取 URL 查询参数
):
    """
    上传文件到服务器，并执行 GraphRAG 处理
    （通过 URL 查询参数 ?query=xxx 来获取查询词）
    """
    global current_task, current_query

    # 如果当前有正在运行的任务，先终止或取消
    terminate_current_process()
    if current_task and not current_task.done():
        try:
            current_task.cancel()
            logging.info("Cancelled previous task")
        except Exception as e:
            logging.error(f"Error cancelling task: {e}")

    # 从 URL 查询参数中获取 query（形如 .../upload?query=xxx）
    logging.info(f"Request query parameters: {request.query_params}")
    query = request.query_params.get("query", None)
    if query:
        logging.info(f"Found query in URL parameters: {query}")
    else:
        logging.warning("Query parameter 'query' not found in URL.")


    # 打印请求信息
    logging.info(f"Received upload request with query: {query}")

    # 保存上传的文件到本地
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 如果有 query，则写入 query.txt
    if query:
        current_query = query
        logging.info(f"File {file.filename} uploaded with query: {query}")
    else:
        logging.info(f"File {file.filename} uploaded without query")

    # 创建并启动新的处理任务
    current_task = asyncio.create_task(process_graphrag())

    return {"message": "File uploaded. GraphRAG processing has started."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """ WebSocket 监听 review.txt 是否更新，并通知客户端 """
    logging.info("New WebSocket connection received")
    await websocket.accept()
    logging.info("WebSocket connection accepted")
    last_mtime = None

    while True:
        try:
            await asyncio.sleep(1)  # 避免占用过多 CPU 资源
            if os.path.exists(REVIEW_FILE_PATH):
                current_mtime = os.path.getmtime(REVIEW_FILE_PATH)
                if last_mtime is None or current_mtime > last_mtime:
                    last_mtime = current_mtime  # 更新最新的修改时间
                    with open(REVIEW_FILE_PATH, "r", encoding="utf-8") as f:
                        review_content = f.read()
                    await websocket.send_text(review_content)  # 发送最新内容
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
            break