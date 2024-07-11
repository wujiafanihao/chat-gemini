document.addEventListener('DOMContentLoaded', function() {
    // 获取登录表单
    const loginForm = document.querySelector('#login-form');

    // 监听表单的submit事件
    loginForm.addEventListener('submit', function(event) {
        // 阻止表单默认提交行为
        event.preventDefault();

        // 获取表单数据
        const username = document.querySelector('#username').value;
        const password = document.querySelector('#password').value;

        // 构造要发送的数据对象
        const data = new FormData();
        data.append('username', username);
        data.append('password', password);

        // 发送 POST 请求到登录路由
        fetch('/login', {
            method: 'POST',
            body: data
        })
        .then(response => {
            if (response.redirected) {
                // 如果服务器返回重定向信息，重定向到对应页面
                window.location.href = response.url;
            } else {
                // 否则，将响应解析为 JSON
                return response.json();
            }
        })
        .then(data => {
            // 处理服务器响应
            if (data.success) {
                // 登录成功，重定向到对应页面
                window.location.href = 'http://127.0.0.1:5000'; // 修改重定向地址
            } else {
                // 登录失败，根据错误类型弹出相应的提示框
                if (data.message === '密码错误') {
                    alert('密码错误，请重新输入。');
                } else if (data.message === '账号不存在') {
                    alert('账号不存在，请重新输入或注册新账号。');
                } else {
                    alert('登录失败，请稍后再试。');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // 获取注册按钮
    const registerButton = document.querySelector('#register-button');

    // 监听注册按钮的点击事件
    registerButton.addEventListener('click', function(event) {
        // 阻止默认点击行为
        event.preventDefault();

        // 跳转到注册页面
        window.location.href = 'http://127.0.0.1:5000'; // 修改注册页面URL
    });
});