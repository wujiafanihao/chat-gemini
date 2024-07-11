from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import webbrowser
import logging
import os
import uuid  # 用于生成唯一的API密钥
from werkzeug.utils import secure_filename
import pathlib
import PIL.Image
from PIL import Image
import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown

# 设置 ANSI 转义序列，将输出设置为红色
RED_COLOR = '\033[91m'  # 定义ANSI转义序列为红色
RESET_COLOR = '\033[0m'  # 定义ANSI转义序列为重置颜色

app = Flask(__name__)  # 创建Flask应用实例
app.secret_key = os.urandom(24)  # 生成密钥用于session加密
CORS(app)  # 启用CORS，允许跨域请求
app.config['JSON_AS_ASCII'] = False  # 设置JSON响应中文显示
logging.basicConfig(level=logging.INFO)  # 配置日志记录器，设置日志级别为INFO
logger = logging.getLogger(__name__)  # 获取logger对象

text_model = genai.GenerativeModel('gemini-pro')
img_model = genai.GenerativeModel('gemini-pro-vision')

# 显示登录页面
def show_login():
    return render_template("login.html")

# 初始化用户数据
def initialize_user_data():
    default_username = 'admin\n'  # 默认用户名
    default_password = 'admin\n'  # 默认密码
    with open('user_data/user.txt', 'w') as user_file:
        user_file.write(default_username)  # 写入默认用户名到文件中
    with open('user_data/password.txt', 'w') as password_file:
        password_file.write(default_password)  # 写入默认密码到文件中

# 检查用户凭据
def check_credentials(username, password):
    with open('user_data/user.txt', 'r') as user_file:
        saved_usernames = user_file.readlines()  # 读取保存的用户名列表
    with open('user_data/password.txt', 'r') as password_file:
        saved_passwords = password_file.readlines()  # 读取保存的密码列表

    for saved_username, saved_password in zip(saved_usernames, saved_passwords):
        if username == saved_username.strip() and password == saved_password.strip():
            return True  # 验证通过
    return False  # 验证失败

# 生成唯一的API密钥
def generate_api_key():
    return str(uuid.uuid4())  # 生成UUID作为API密钥

# 登录页面路由，GET请求用于显示登录页面，POST请求用于处理登录表单提交
@app.route('/login', methods=['GET'])
def login():
    return show_login()

@app.route('/login', methods=['POST'])
def process_login():
    username = request.form.get('username')  # 获取表单中的用户名
    password = request.form.get('password')  # 获取表单中的密码
    logger.info('username : User: %s, Password: %s', f"{RED_COLOR}{username}{RESET_COLOR}", f"{RED_COLOR}{password}{RESET_COLOR}")  # 记录登录尝试信息到日志
    if check_credentials(username, password):  # 验证用户凭据
        if 'api_key' not in session:  # 检查是否已经设置了Gemini API密钥
            api_key = generate_api_key()  # 生成API密钥
            session['api_key'] = api_key  # 将API密钥存储到会话中
            logger.info('Generated API key for user: %s', username)  # 记录API密钥生成信息到日志
        else:
            api_key = session['api_key']  # 从会话中获取API密钥
            logger.info('Reusing existing API key for user: %s', username)  # 记录重用API密钥信息到日志
        session['username'] = username  # 将用户名存储到会话中
        logger.info('Login successful for user: %s', username)  # 记录登录成功信息到日志
        return redirect(url_for('home'))  # 修改这里，登录成功后重定向到home路由
    else:
        logger.warning('Login failed for user: %s', username)  # 记录登录失败信息到日志
        return jsonify({'success': False, 'message': '用户名或密码错误'})  # 返回登录失败响应

gemini_key = None

# 定义一个函数来检查用户是否已经设置了 Gemini API 密钥
def check_api_key(username):
    # 根据用户名检查是否存在对应的 Gemini API 密钥文件
    key_file_path = f"user_data/{username}_api_key.txt"
    return os.path.exists(key_file_path)

# 将 API 密钥与用户名相关联并保存到持久性存储中
def save_api_key(username, api_key):
    # 这里可以将 API 密钥存储到文件中，使用用户名作为文件名，或者存储到数据库中
    key_file_path = f"user_data/{username}_api_key.txt"
    with open(key_file_path, "w") as key_file:
        key_file.write(api_key)

# 用于接收用户 Gemini API 密钥的路由
@app.route("/set_gemini_api_key", methods=["POST"])
def set_gemini_api_key():
    global gemini_key  # 声明 gemini_key 是全局变量
    try:
        # 获取用户名
        username = session.get("username")
        
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
        save_api_key(username, gemini_api_key)
        
        print("Gemini API Key saved for user:", username)
        gemini_key = genai.configure(api_key=gemini_api_key)
        app.logger.log(20, "User API key saved")
        return jsonify(status="Gemini API key saved successfully")
    except Exception as e:
        app.logger.error(f"Error setting Gemini API key: {e}")
        return jsonify(status="Error setting Gemini API key"), 500


# 主页路由，根据会话中的用户状态返回相应页面
@app.route("/home")
def home():
    if 'username' in session:  # 检查会话中是否包含用户名
        username = session['username']  # 获取会话中的用户名
        api_key = session.get('api_key')  # 获取会话中的API密钥
        if not api_key:  # 如果会话中没有API密钥，则重定向到设置Gemini API密钥的页面
            return redirect(url_for('set_gemini_api_key'))
        return render_template("Gemini-Pro-ui.html", username=username, api_key=api_key)  # 渲染主页模板，并传递用户名和API密钥
    else:
        return redirect(url_for('login'))  # 如果会话中不包含用户名，则重定向到登录页面

# 获取模型的响应路由
@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        user_input = request.form.get("user_input")  # 获取用户输入
        response = text_model.generate_content(user_input,stream=True)  # 生成模型响应
        response.resolve()  # 解析模型响应
        return jsonify(bot_response=response.text)  # 返回模型响应
    except Exception as e:
        app.logger.error(f"Error generating response: {e}")  # 记录生成响应出错的消息到日志
        return jsonify(bot_response="I'm sorry, there was an error processing your request."), 500  # 返回处理请求出错响应

# 上传文件路由
@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['file']  # 获取上传的文件
        upload_path = request.args.get('upload_path', '/default/upload/folder')  # 获取上传路径，默认为'/default/upload/folder'
        file_path = os.path.join(app.root_path, upload_path)  # 构建文件保存路径
        os.makedirs(file_path, exist_ok=True)  # 确保路径存在
        file_path = os.path.join(file_path, secure_filename(uploaded_file.filename))  # 构建文件完整路径
        uploaded_file.save(file_path)  # 保存上传的文件
        img = Image.open(file_path)  # 打开上传的图片文件
        response = img_model.generate_content(img, stream=True)  # 生成图片模型响应
        response.resolve()  # 解析模型响应
        return jsonify(bot_response=response.text, status="File uploaded successfully")  # 返回文件上传成功响应
    except Exception as e:
        app.logger.error(f"Error uploading file: {e}")  # 记录上传文件出错的消息到日志
        return jsonify(status="Error uploading file"), 500  # 返回上传文件出错响应

# 上传文件和文本路由
@app.route('/upload_with_input', methods=['POST'])
def upload_with_input():
    try:
        user_input = request.form['user_input']  # 获取用户输入
        uploaded_file = request.files['file']  # 获取上传的文件
        upload_path = '/dynamic/upload/folder'  # 设置上传路径为'/dynamic/upload/folder'
        file_path = os.path.join(app.root_path, upload_path)  # 构建文件保存路径
        os.makedirs(file_path, exist_ok=True)  # 确保路径存在
        file_path = os.path.join(file_path, secure_filename(uploaded_file.filename))  # 构建文件完整路径
        uploaded_file.save(file_path)  # 保存上传的文件
        img = PIL.Image.open(file_path)  # 打开上传的图片文件
        response = img_model.generate_content([user_input, img], stream=True)  # 生成图片模型响应，包括用户输入
        response.resolve()  # 解析模型响应
        return jsonify(
            user_input=user_input,  # 返回用户输入
            bot_response=response.text,  # 返回模型响应
            status="File and input processed successfully"  # 返回处理成功的状态信息
        )
    except Exception as e:
        print(f"Exception: {e}")
        app.logger.error(f"Error processing input and file: {e}")  # 记录处理输入和文件出错的消息到日志
        return jsonify(
            status="Error processing input and file",  # 返回处理输入和文件出错的状态信息
            error=str(e)  # 返回错误信息
        ), 500

# 运行应用
if __name__ == "__main__":
    url = "http://127.0.0.1:5001/login"  # 定义登录页面URL
    webbrowser.open(url)  # 在默认浏览器中打开登录页面
    print("用户数据初始化完成。")  # 打印用户数据初始化完成的消息
    app.secret_key = os.urandom(24)  # 生成新的密钥用于session加密
    app.run(debug=True, port=5001)  # 运行应用，启动调试模式，监听5001端口