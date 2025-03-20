import requests
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--query", type=str, default=None, help="User query from server")
args = parser.parse_args()

query = args.query

# 获取当前查询
print(f"Processing query: {query}")

url = "http://localhost:8012/v1/chat/completions"
headers = {"Content-Type": "application/json"}

# 构建消息内容，将用户查询插入到内容中
message_content = f"Task: User query is '{query}', and relevant papers are provided. Please tell me what the area of the all article I provided is, and what bywords are in the provided informations. Besides, As an AI assistant specializing in academic writing, Please generate a comprehensive literature review for the research field represented in the provided knowledge base. Your review should offer a coherent overview of current state of the field by synthesizing the global insights from the knowledge graph and RAG database. In your review, please address the following guidelines:1. Global Overview: Summarize the main research themes, methodologies, and breakthroughs that have shaped the field.2. Current State: Describe the present status of the research domain, highlighting key achievements and innovations.3. Future Directions: Discuss potential future research directions and emerging trends that could drive the field forward.4. Integration: Ensure that the review integrates the collective insights from the knowledge graph rather than providing individual paper summaries.5. Referencing: Use Harvard referencing style; insert reference numbers in square brackets where applicable. The final output should be written in a formal academic tone and as comprehensive as you can, as long as you can."

# 1、测试全局搜索  graphrag-global-search:latest
global_data = {
    "model": "graphrag-global-search:latest",
    "messages": [{"role": "user", "content": message_content}],
    "temperature": 0.7,
    "max_tokens": 8000
    # "stream": True,#True or False
}

# 2、测试本地搜索  graphrag-local-search:latest
local_data = {
    "model": "graphrag-local-search:latest",
    "messages": [{"role": "user", "content": message_content}],
    "temperature": 0.7,
    "max_tokens": 8000
    # "stream": True,#True or False
}

# 3、测试全局和本地搜索  full-model:latest
full_data = {
    "model": "full-model:latest",
    "messages": [{"role": "user", "content": message_content}],
    "temperature": 0.7,
    "max_tokens": 8000
    # "stream": True,#True or False
}

# 接收非流式输出
# 1、测试全局搜索  graphrag-global-search:latest
response = requests.post(url, headers=headers, data=json.dumps(global_data))
# 2、测试本地搜索  graphrag-local-search:latest
# response = requests.post(url, headers=headers, data=json.dumps(local_data))
# 3、测试全局和本地搜索  full-model:latest
# response = requests.post(url, headers=headers, data=json.dumps(full_data))

# print(response.json())
print(response.json()['choices'][0]['message']['content'])

# 确保请求成功
if response.status_code == 200:
    review_content = response.json()['choices'][0]['message']['content']
    
    # 定义 review.txt 文件存储路径
    output_dir = "/home/jovyan/ragtest2/output"
    output_file = os.path.join(output_dir, "review.txt")

    # 确保 output 目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 将内容写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(review_content)
    
    print("Literature review generated and saved to:", output_file)

else:
    print("Error:", response.status_code, response.text)



# # 接收非流式输出
# try:
#     with requests.post(url, stream=True, headers=headers, data=json.dumps(data)) as response:
#         for line in response.iter_lines():
#         # for line in response.iter_content(chunk_size=16):
#             if line:
#                 json_str = line.decode('utf-8').strip("data: ")
#
#                 # 检查是否为空或不合法的字符串
#                 if not json_str:
#                     print("Received empty string, skipping...")
#                     continue
#
#                 # 确保字符串是有效的JSON格式
#                 if json_str.startswith('{') and json_str.endswith('}'):
#                     try:
#                         data = json.loads(json_str)
#                         print(f"Received JSON data: {data['choices'][0]['delta']['content']}")
#                         # print(f"{data['choices'][0]['delta']['content']}")
#                     except json.JSONDecodeError as e:
#                         print(f"Failed to decode JSON: {e}")
#                 else:
#                     print(f"Invalid JSON format: {json_str}")
# except Exception as e:
#     print(f"Error occurred: {e}")





