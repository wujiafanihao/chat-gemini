from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import webbrowser

app = Flask(__name__)
CORS(app) 

# 假设这是一个用户数据库，用于保存注册用户的信息
user_database = {}

def initialize_user_database():
    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists('user_data'):
        os.makedirs('user_data')

    # 检查用户文件和密码文件是否存在，如果不存在则创建一个空文件
    if not os.path.exists('user_data/user.txt'):
        open('user_data/user.txt', 'w').close()
    if not os.path.exists('user_data/password.txt'):
        open('user_data/password.txt', 'w').close()

    # 读取用户文件和密码文件中的数据
    with open('user_data/user.txt', 'r') as f_user, open('user_data/password.txt', 'r') as f_password:
        users = f_user.readlines()
        passwords = f_password.readlines()
    for user, password in zip(users, passwords):
        user_database[user.strip()] = password.strip()

def save_user_data(username, password):
    # 将新用户信息保存到数据库中
    user_database[username] = password

    # 将用户名和密码分别写入到对应文件中
    with open('user_data/user.txt', 'a') as f_user:
        f_user.write(username + '\n')
        f_user.flush()  # 刷新文件缓冲区
        f_user.close()  # 关闭文件对象
    with open('user_data/password.txt', 'a') as f_password:
        f_password.write(password + '\n')
        f_password.flush()  # 刷新文件缓冲区
        f_password.close()  # 关闭文件对象


@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # 获取注册表单中输入的用户名和密码
    username = request.form['username']
    password = request.form['password']

    # 检查用户名是否已被注册
    if username in user_database:
        return jsonify({'success': False, 'message': '用户名已被注册，请选择其他用户名'})

    # 保存用户数据到文件中
    save_user_data(username, password)

    # 注册成功后，无需重定向到登录页面，由前端 JavaScript 处理跳转
    return jsonify({'success': True, 'message': '注册成功！'})

if __name__ == '__main__':
    # initialize_user_database()
    app.run(debug=True, port=5002)
