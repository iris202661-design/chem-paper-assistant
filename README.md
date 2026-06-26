# Chem Paper Assistant

一个面向计算化学与机器学习方向的论文问答助手 Demo。

本项目基于 Streamlit 构建网页界面，支持上传论文 PDF，自动提取 PDF 文本，并调用 DeepSeek API，根据论文内容回答用户问题。项目适合用于计算化学、AI for Science、分子性质预测等方向的文献阅读辅助。

## 1. 项目功能

- 上传论文 PDF 文件
- 自动提取 PDF 中的文本内容
- 支持用户输入论文相关问题
- 调用 DeepSeek API 生成回答
- 基于论文文本进行问答，减少人工阅读压力
- 支持在网页端查看 PDF 文本预览和模型回答

## 2. 技术栈

- Python
- Streamlit
- pypdf
- OpenAI SDK
- DeepSeek API

## 3. 项目结构

```text
chem-paper-assistant/
├── paper_qa_app.py
├── requirements.txt
├── README.md
├── screenshots/
└── .gitignore