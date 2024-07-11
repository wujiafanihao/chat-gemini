from flask import Flask, render_template, request, jsonify, redirect, url_for, session  # 导入Flask模块中的相关类和函数
from flask_cors import CORS  # 导入CORS类，用于处理跨域请求
import os  # 导入os模块，用于文件和目录操作
import webbrowser  # 导入webbrowser模块，用于在浏览器中打开URL
import logging  # 导入logging模块，用于日志记录
import uuid  # 导入uuid模块，用于生成唯一的API密钥
from werkzeug.utils import secure_filename  # 导入secure_filename函数，用于安全处理文件名
import PIL.Image  # 导入PIL.Image模块，用于处理图像文件
from PIL import Image  # 导入Image类
import google.generativeai as genai  # 导入生成式AI模块
import socks
import socket
import requests

# # 设置SOCKS代理
# socks.set_default_proxy(socks.SOCKS5, addr="8.219.245.23", port=1080, username="wIwnLB2xoi", password="mbKF7wq7FJ")
# socket.socket = socks.socksocket

# 设置 ANSI 转义序列，将输出设置为红色
RED_COLOR = '\033[91m'  # 定义ANSI转义序列为红色
RESET_COLOR = '\033[0m'  # 定义ANSI转义序列为重置颜色

app = Flask(__name__)  # 创建Flask应用实例
app.secret_key = os.urandom(24)  # 生成应用的密钥，用于session加密
CORS(app)  # 启用CORS，允许跨域请求
app.config['JSON_AS_ASCII'] = False  # 设置JSON响应中文显示
logging.basicConfig(level=logging.INFO)  # 配置日志记录器，设置日志级别为INFO
logger = logging.getLogger(__name__)  # 获取logger对象

text_model = genai.GenerativeModel('gemini-pro')  # 初始化文本生成模型
img_model = genai.GenerativeModel('gemini-pro-vision')  # 初始化图像生成模型

user_database = {}  # 用户数据库，用于存储用户名和密码

def initialize_user_database():
    """
    初始化用户数据库。
    """
    if not os.path.exists('user_data'):  # 如果'user_data'文件夹不存在，则创建它
        os.makedirs('user_data')

    if not os.path.exists('user_data/user.txt'):  # 如果'user.txt'文件不存在，则创建一个空文件
        open('user_data/user.txt', 'w').close()
    if not os.path.exists('user_data/password.txt'):  # 如果'password.txt'文件不存在，则创建一个空文件
        open('user_data/password.txt', 'w').close()

    with open('user_data/user.txt', 'r') as f_user, open('user_data/password.txt', 'r') as f_password:
        users = f_user.readlines()  # 读取用户文件中的内容
        passwords = f_password.readlines()  # 读取密码文件中的内容
    for user, password in zip(users, passwords):  # 遍历用户和密码列表
        user_database[user.strip()] = password.strip()  # 将用户名和密码存储到用户数据库中

def save_user_data(username, password):
    """
    将用户数据保存到文件和数据库中。
    """
    user_database[username] = password  # 将用户名和密码存储到用户数据库中
    with open('user_data/user.txt', 'a') as f_user:  # 将用户名追加到'user.txt'文件中
        f_user.write(username + '\n')
        f_user.flush()  # 刷新文件缓冲区
        f_user.close()  # 关闭文件对象
    with open('user_data/password.txt', 'a') as f_password:  # 将密码追加到'password.txt'文件中
        f_password.write(password + '\n')
        f_password.flush()  # 刷新文件缓冲区
        f_password.close()  # 关闭文件对象

def check_credentials(username, password):
    """
    检查用户凭据是否正确。
    """
    with open('user_data/user.txt', 'r') as user_file:  # 打开用户文件以读取保存的用户名列表
        saved_usernames = user_file.readlines()
    with open('user_data/password.txt', 'r') as password_file:  # 打开密码文件以读取保存的密码列表
        saved_passwords = password_file.readlines()

    for saved_username, saved_password in zip(saved_usernames, saved_passwords):
        if username == saved_username.strip() and password == saved_password.strip():  # 如果用户名和密码匹配
            return True  # 返回验证通过
    return False  # 返回验证失败

def generate_api_key():
    """
    生成唯一的API密钥。
    """
    return str(uuid.uuid4())  # 生成UUID作为API密钥

def check_api_key(username):
    # 根据用户名检查是否存在对应的 Gemini API 密钥文件
    key_file_path = f"user_data/{username}_api_key.txt"
    return os.path.exists(key_file_path)


def save_api_key(username, api_key):
    # 这里可以将 API 密钥存储到文件中，使用用户名作为文件名，或者存储到数据库中
    key_file_path = f"user_data/{username}_api_key.txt"
    with open(key_file_path, "w") as key_file:
        key_file.write(api_key)
@app.route('/')  # 根路由，渲染注册页面
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])  # 处理注册请求
def register():
    username = request.form['username']  # 获取表单中的用户名
    password = request.form['password']  # 获取表单中的密码

    if username in user_database:  # 检查用户名是否已被注册
        return jsonify({'success': False, 'message': '用户名已被注册，请选择其他用户名'})

    save_user_data(username, password)  # 保存用户数据到文件中

    return jsonify({'success': True, 'message': '注册成功！'})  # 返回注册成功响应

@app.route('/login', methods=['GET'])  # 渲染登录页面
def login():
    if 'username' in session:  # 如果用户已登录，则重定向到主页
        return redirect(url_for('home'))
    return render_template("login.html")  # 否则渲染登录页面

@app.route('/login', methods=['POST'])  # 处理登录请求
def process_login():
    username = request.form.get('username')  # 获取表单中的用户名
    password = request.form.get('password')  # 获取表单中的密码
    logger.info('username : User: %s, Password: %s', username, password)  # 记录用户名和密码

    if check_credentials(username, password):  # 检查用户凭据是否正确
        if 'api_key' not in session:  # 如果用户未设置API密钥
            api_key = generate_api_key()  # 生成新的API密钥
            session['api_key'] = api_key  # 将API密钥存储到session中
            logger.info('Generated API key for user: %s', username)  # 记录已生成API密钥的用户
        else:
            api_key = session['api_key']  # 使用现有的API密钥
            logger.info('Reusing existing API key for user: %s', username)  # 记录已重用API密钥的用户
        session['username'] = username  # 将用户名存储到session中
        logger.info('Login successful for user: %s', username)  # 记录用户登录成功
         # 打印用户输入的账号和密码
        logger.info('username : User: %s, Password: %s', f"{RED_COLOR}{username}{RESET_COLOR}", f"{RED_COLOR}{password}{RESET_COLOR}")
        return redirect(url_for('home'))  # 重定向到主页
    else:
        logger.warning('Login failed for user: %s', username)  # 记录用户登录失败
        return jsonify({'success': False, 'message': '用户名或密码错误'})  # 返回登录失败响应

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
        
        print("Gemini API Key saved for user:", f"{RED_COLOR}{username}{RESET_COLOR}")
        print("Gemini API Key saved:", f"{RED_COLOR}{gemini_api_key}{RESET_COLOR}")
        gemini_key = genai.configure(api_key=gemini_api_key)
        app.logger.log(20, "User API key saved")
        return jsonify(status="Gemini API key saved successfully")
    except Exception as e:
        app.logger.error(f"Error setting Gemini API key: {e}")
        return jsonify(status="Error setting Gemini API key"), 500

@app.route("/home")  # 主页路由
def home():
    if 'username' in session:  # 如果用户已登录
        username = session['username']  # 获取当前登录用户的用户名
        api_key = session.get('api_key')  # 获取当前登录用户的API密钥
        if not api_key:  # 如果用户未设置API密钥
            return redirect(url_for('set_gemini_api_key'))  # 重定向到设置API密钥页面
        return render_template("Gemini-Pro-ui.html", username=username, api_key=api_key)  # 渲染主页
    else:
        return redirect(url_for('login'))  # 如果用户未登录，则重定向到登录页面

@app.route("/get_response", methods=["POST"])  # 获取模型响应路由
def get_response():
    try:
        user_input = request.form.get("user_input")  # 获取用户输入
        response = text_model.generate_content(user_input, stream=True)  # 使用文本生成模型生成响应
        response.resolve()  # 解析响应
        return jsonify(bot_response=response.text)  # 返回模型生成的响应
    except Exception as e:
        app.logger.error(f"Error generating response: {e}")  # 记录生成响应时出错的消息
        return jsonify(bot_response="I'm sorry, there was an error processing your request."), 500  # 返回错误响应

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


if __name__ == '__main__':
    url = "http://127.0.0.1:5000/login"  # 设置URL
    webbrowser.open(url)  # 在浏览器中打开URL
    print("用户数据初始化完成。")  # 打印用户数据初始化完成的消息
    app.run(debug=True, port=5000)  # 运行Flask应用
