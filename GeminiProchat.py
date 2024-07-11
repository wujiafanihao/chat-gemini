from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify,session,redirect,url_for
import pathlib
import PIL.Image
from PIL import Image
from flask_cors import CORS
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import webbrowser
import os
from flask import send_from_directory

app = Flask(__name__)
CORS(app) 
app.config['JSON_AS_ASCII'] = False
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

text_model = genai.GenerativeModel('gemini-pro')
img_model = genai.GenerativeModel('gemini-pro-vision')

# 定义一个函数来检查用户是否已经设置了 API 密钥
def check_api_key(username):
    key_file_path = f"user_data/{username}_api_key.txt"
    return os.path.exists(key_file_path)

gemini_key = None

# 用于接收用户 Gemini API 密钥的路由
@app.route("/set_gemini_api_key", methods=["POST"])
def set_gemini_api_key():
    global gemini_key  # 声明 gemini_key 是全局变量
    try:
        # 获取用户名
        username = request.form.get("username")
        
        # 检查用户是否已经设置了 API 密钥
        if check_api_key(username):
            return jsonify(status="Gemini API key already saved for this user"), 400

        # 从请求中获取用户提供的 Gemini API 密钥
        gemini_api_key = request.form.get("gemini_api_key")
        
        # 检查是否提供了 API 密钥
        if not gemini_api_key:
            return jsonify(status="Please provide a Gemini API key"), 400
        
        # 在这里可以将 API 密钥存储到文件中
        # 这里只是简单地将 API 密钥写入到以用户名命名的文件中
        key_file_path = f"user_data/{username}_api_key.txt"
        with open(key_file_path, "w") as key_file:
            key_file.write(gemini_api_key)
        
        print("Gemini API Key saved for user:", gemini_api_key)
        gemini_key = genai.configure(api_key=gemini_api_key)
        app.logger.log(20, "User API key saved")
        return jsonify(status="Gemini API key saved successfully")
    except Exception as e:
        app.logger.error(f"Error setting Gemini API key: {e}")
        return jsonify(status="Error setting Gemini API key"), 500

# 开始和模型进行新的聊天
history = []  # 可以用先前的聊天历史记录替换该处，如果有的话
chat = img_model.start_chat(history=history)

@app.route('/templates/<path:filename>')
def serve_static(filename):
    """Serve static files from the 'templates' folder."""
    return send_from_directory('templates', filename)

@app.route("/")

# 主页
def home():
        return render_template("Gemini-Pro-ui.html")

# 获取响应
@app.route("/get_response", methods=["POST"])

# 获取用户输入
def get_response():
    try:
        user_input = request.form.get("user_input")
        response = text_model.generate_content(user_input,stream=True)
        response.resolve()
        # 确保文本内容是安全的，这里可以添加更多检查
        return jsonify(bot_response=response.text)
    except Exception as e:
        app.logger.error(f"Error generating response: {e}")
        return jsonify(bot_response="I'm sorry, there was an error processing your request."), 500
    
    
@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        # 获取上传的文件
        uploaded_file = request.files['file']
        
        # 获取动态上传文件的路径参数
        upload_path = request.args.get('upload_path', '/default/upload/folder')

        # 保存上传的文件到服务器
        file_path = os.path.join(app.root_path, upload_path)
        os.makedirs(file_path, exist_ok=True)  # 创建所需的文件夹路径
        file_path = os.path.join(file_path, secure_filename(uploaded_file.filename))
        uploaded_file.save(file_path)

        # 打开上传的文件并获取图像数据
        img = Image.open(file_path)

        # 将图像数据传递给模型进行生成内容
        response = img_model.generate_content(img, stream=True)
        response.resolve()

        # 返回成功上传的响应
        return jsonify(bot_response=response.text, status="File uploaded successfully")

    except Exception as e:
        app.logger.error(f"Error uploading file: {e}")
        return jsonify(status="Error uploading file"), 500
        
# 上传文件和文本
@app.route('/upload_with_input', methods=['POST'])
def upload_with_input():
    try:
        # 获取用户文本输入
        user_input = request.form['user_input']

        # 获取上传的文件
        uploaded_file = request.files['file']

        # 获取上传文件的路径，如果没有提供，默认为'/default/upload/folder'
        upload_path = '/dynamic/upload/folder'  # 或其他您希望的路径

        # 保存上传的文件到服务器
        file_path = os.path.join(app.root_path, upload_path)
        os.makedirs(file_path, exist_ok=True)  # 创建所需的文件夹路径
        file_path = os.path.join(file_path, secure_filename(uploaded_file.filename))
        uploaded_file.save(file_path)

        # 打开上传的文件并获取图像数据
        img = PIL.Image.open(file_path)

        # 将图像数据传递给模型进行内容生成
        response = img_model.generate_content([user_input, img], stream=True)

        # 异步处理解析，如果需要的话
        response.resolve()

        # 返回同时含有用户输入和文件上传结果的响应
        return jsonify(
            user_input=user_input,
            bot_response=response.text, 
            status="File and input processed successfully"
        )

    except Exception as e:
        # 打印错误信息进行调试
        print(f"Exception: {e}")
        app.logger.error(f"Error processing input and file: {e}")

        # 返回错误响应
        return jsonify(
            status="Error processing input and file",
            error=str(e)  # 将异常信息作为响应的一部分返回，方便调试
        ), 500  # 返回状态码 500 表示服务器内部错误


if __name__ == "__main__":
    app.run(debug=True,port=5000)