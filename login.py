from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import webbrowser
import logging
import os
import uuid  # 用于生成唯一的API密钥

# 设置 ANSI 转义序列，将输出设置为红色
RED_COLOR = '\033[91m'
RESET_COLOR = '\033[0m'

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app) 

# 设置日志记录的配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_login():
    return render_template("login.html")

def initialize_user_data():
    # 设置默认用户名和密码
    default_username = 'admin\n'
    default_password = 'admin\n'

    # 将默认用户名和密码写入到相应的文本文件中
    with open('user_data/user.txt', 'w') as user_file:
        user_file.write(default_username)
    with open('user_data/password.txt', 'w') as password_file:
        password_file.write(default_password)

def check_credentials(username, password):
    # 从文本文件中读取用户名和密码
    with open('user_data/user.txt', 'r') as user_file:
        saved_usernames = user_file.readlines()
    with open('user_data/password.txt', 'r') as password_file:
        saved_passwords = password_file.readlines()

    # 验证用户名和密码是否匹配任何一个用户
    for saved_username, saved_password in zip(saved_usernames, saved_passwords):
        if username == saved_username.strip() and password == saved_password.strip():
            return True

    return False

# 生成唯一的API密钥
def generate_api_key():
    return str(uuid.uuid4())

@app.route('/login', methods=['GET'])
def login():
    return show_login()

@app.route('/login', methods=['POST'])
def process_login():
    # 获取POST请求中的表单数据
    username = request.form.get('username')
    password = request.form.get('password')

    # 打印用户输入的账号和密码
    logger.info('username : User: %s, Password: %s', f"{RED_COLOR}{username}{RESET_COLOR}", f"{RED_COLOR}{password}{RESET_COLOR}")

    # 检查凭据是否有效
    if check_credentials(username, password):
        # 如果登录成功，生成并存储与用户相关的唯一API密钥
        api_key = generate_api_key()
        session['username'] = username
        session['api_key'] = api_key
        logger.info('Login successful for user: %s', username)
        return jsonify({'success': True, 'api_key': api_key})
    else:
        logger.warning('Login failed for user: %s', username)
        return jsonify({'success': False, 'message': '用户名或密码错误'})

@app.route('/')
def home():
    # 检查会话中是否存在用户名和API密钥
    if 'username' in session and 'api_key' in session:
        # 如果存在用户名和API密钥，则返回相应的对话窗口
        username = session['username']
        api_key = session['api_key']
        return render_template("Gemini-Pro-ui.html", username=username, api_key=api_key)
    else:
        # 如果不存在用户名或API密钥，则重定向到登录页面
        return redirect(url_for('login'))

if __name__ == '__main__':
    url = "http://127.0.0.1:5001/login"
    webbrowser.open(url)
    # initialize_user_data()
    print("用户数据初始化完成。")
    app.secret_key = os.urandom(24)  # 使用随机生成的密钥作为会话密钥
    app.run(debug=True, port=5001)
