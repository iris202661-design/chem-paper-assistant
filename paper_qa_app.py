import os  # 用来读取环境变量，比如 DEEPSEEK_API_KEY
from io import BytesIO  # 用来把上传的 PDF 二进制内容包装成“内存文件”

import streamlit as st  # Streamlit，用来做网页界面
from pypdf import PdfReader  # pypdf，用来读取 PDF 文本
from openai import OpenAI  # DeepSeek 兼容 OpenAI SDK，所以仍然用 OpenAI 这个类


DEEPSEEK_MODEL = "deepseek-v4-flash"  # DeepSeek 模型名，练习阶段用 flash
DEEPSEEK_BASE_URL = "https://api.deepseek.com"  # DeepSeek 的 OpenAI 兼容 API 地址


def extract_pdf_text(uploaded_file):
    """从上传的 PDF 文件中提取文本。"""

    pdf_bytes = uploaded_file.getvalue()  # 读取上传文件的二进制内容

    reader = PdfReader(BytesIO(pdf_bytes))  # 用 PdfReader 打开这个 PDF；reader 就是 PDF 阅读器对象

    all_text = []  # 创建一个空列表，用来保存每一页提取出的文字

    for page_number, page in enumerate(reader.pages, start=1):  # 遍历 PDF 的每一页，页码从 1 开始
        text = page.extract_text()  # 提取当前页的文字

        if text is None:  # 如果这一页没有提取到文字
            text = ""  # 就把它变成空字符串，避免后面报错

        all_text.append(f"\n\n===== 第 {page_number} 页 =====\n")  # 给每页文字前面加一个页码标记
        all_text.append(text)  # 把当前页的文字加入列表

    return "\n".join(all_text)  # 把所有页面的文字拼接成一个大字符串并返回


def build_qa_prompt(question, paper_text):
    """把用户问题和论文文本拼成完整 Prompt。"""

    prompt = f"""
你是一名计算化学与机器学习交叉方向的科研助手。
请严格根据我提供的论文文本回答用户问题。

重要要求：
1. 只能根据论文文本回答，不要编造。
2. 如果论文文本中没有相关信息，请明确回答“论文文本中未找到相关信息”。
3. 回答要清晰、具体，适合研究生做文献阅读。
4. 涉及软件、模型、泛函、基组、数据集、评价指标时，请尽量保留英文原名。
5. 如果可以，请指出答案依据来自论文的哪类内容，例如方法、结果、结论等。

用户问题：
{question}

下面是论文文本：
{paper_text}
"""  # 用 f-string 把问题和论文文本插入 Prompt 模板

    return prompt  # 返回完整 Prompt


def ask_deepseek(prompt):
    """调用 DeepSeek API，并返回模型回答。"""

    api_key = os.environ.get("DEEPSEEK_API_KEY")  # 从环境变量里读取 DeepSeek API Key

    if not api_key:  # 如果没有读到 key
        raise ValueError("没有检测到 DEEPSEEK_API_KEY，请先在终端设置 API key。")  # 主动报错，提醒用户设置 key

    client = OpenAI(  # 创建 API 客户端
        api_key=api_key,  # 使用环境变量里的 DeepSeek API Key
        base_url=DEEPSEEK_BASE_URL  # 把请求地址改成 DeepSeek
    )

    response = client.chat.completions.create(  # 调用 DeepSeek 的 Chat Completions 接口
        model=DEEPSEEK_MODEL,  # 指定使用哪个 DeepSeek 模型
        messages=[  # messages 是对话消息列表
            {
                "role": "system",  # system 消息用来设定模型角色
                "content": "你是一名严谨的计算化学与机器学习交叉方向科研助手。"
            },
            {
                "role": "user",  # user 消息是用户真正的问题
                "content": prompt
            }
        ],
        stream=False,  # False 表示一次性返回完整回答
        extra_body={  # DeepSeek 的额外参数放这里
            "thinking": {
                "type": "disabled"  # 关闭 thinking，练习阶段速度更快
            }
        }
    )

    answer = response.choices[0].message.content  # 从返回结果里取出模型回答文本

    return answer  # 返回模型回答


st.title("论文问答助手 Day20")  # 网页标题

st.write("上传论文 PDF 后，系统会提取文本。你可以输入问题，让 DeepSeek 基于论文内容回答。")  # 网页说明文字

uploaded_file = st.file_uploader(  # 创建 PDF 上传按钮
    "请上传论文 PDF",  # 上传按钮显示的文字
    type=["pdf"]  # 限制只能上传 PDF
)

question = st.text_area(  # 创建多行文本框，用来输入问题
    "请输入你想问论文的问题",  # 文本框标题
    value="这篇论文主要解决了什么问题？使用了哪些计算化学或机器学习方法？"  # 默认问题
)

max_chars = st.slider(  # 创建滑块，用来控制发送给模型的论文文本长度
    "最多发送给模型的论文文本字符数",  # 滑块标题
    min_value=1000,  # 最少发送 1000 个字符
    max_value=30000,  # 最多发送 30000 个字符
    value=8000,  # 默认发送 8000 个字符
    step=1000  # 每次滑动增加或减少 1000
)

st.info(f"当前使用模型：{DEEPSEEK_MODEL}")  # 在网页上显示当前使用的模型名

if uploaded_file is not None:  # 如果用户已经上传了 PDF
    with st.spinner("正在提取 PDF 文本..."):  # 显示加载提示
        paper_text = extract_pdf_text(uploaded_file)  # 调用函数，从 PDF 中提取文字

    st.subheader("PDF 文本提取预览")  # 显示小标题

    st.write("提取字符数：", len(paper_text))  # 显示提取出的字符数量

    st.text_area(  # 显示论文文本预览框
        "论文文本前 2000 个字符",  # 预览框标题
        paper_text[:2000],  # 只显示前 2000 个字符
        height=300  # 文本框高度
    )

    if len(paper_text.strip()) < 200:  # 如果提取出的有效文字太少
        st.warning("提取出的文本较少，可能是扫描版 PDF。当前程序不做 OCR，建议换文字型 PDF 测试。")  # 给出提醒

    if st.button("回答问题"):  # 创建按钮，点击后才开始调用模型
        if not os.environ.get("DEEPSEEK_API_KEY"):  # 如果没有设置 DeepSeek API Key
            st.error("没有检测到 DEEPSEEK_API_KEY，请先在终端设置 DeepSeek API Key。")  # 在网页显示错误提示

        elif not question.strip():  # 如果问题为空
            st.warning("请输入一个问题。")  # 提醒用户输入问题

        else:  # 如果 PDF、问题、API Key 都有
            short_text = paper_text[:max_chars]  # 截取前 max_chars 个字符，避免一次发太长

            prompt = build_qa_prompt(question, short_text)  # 构造最终发给模型的 Prompt

            with st.expander("查看发送给模型的 Prompt 预览"):  # 创建一个可展开区域
                st.text_area(  # 显示 Prompt 预览
                    "Prompt 预览",  # 文本框标题
                    prompt[:3000],  # 只预览前 3000 个字符
                    height=300  # 文本框高度
                )

            with st.spinner("正在调用 DeepSeek 回答问题..."):  # 显示模型调用中的提示
                try:  # 尝试调用 DeepSeek
                    answer = ask_deepseek(prompt)  # 调用 DeepSeek API，得到回答

                except Exception as e:  # 如果调用过程中出错
                    st.error("调用 DeepSeek API 失败。")  # 显示错误提示
                    st.exception(e)  # 在网页上显示具体错误信息
                    answer = None  # 把 answer 设置为空，避免后面报错

            if answer:  # 如果成功拿到了模型回答
                st.subheader("回答结果")  # 显示小标题

                st.markdown(answer)  # 用 Markdown 格式显示模型回答

                st.download_button(  # 创建下载按钮
                    label="下载问答结果 Markdown",  # 按钮文字
                    data=answer.encode("utf-8"),  # 下载内容，转成 utf-8 字节
                    file_name="paper_qa_answer.md",  # 下载文件名
                    mime="text/markdown"  # 文件类型
                )

else:  # 如果还没有上传 PDF
    st.info("请先上传 PDF 文件。")  # 提示用户先上传文件