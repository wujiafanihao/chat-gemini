document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#register-form').onsubmit = function() {
        // 获取表单数据
        const username = document.querySelector('#username').value;
        const password = document.querySelector('#password').value;
        const confirm_password = document.querySelector('#confirm_password').value;

        // 检查密码和确认密码是否一致
        if (password !== confirm_password) {
            // 如果密码和确认密码不一致，则显示错误消息并阻止表单提交
            alert('密码和确认密码不一致，请重新输入。');
            return false;
        }

        // 构造要发送的数据对象
        const data = new FormData();
        data.append('username', username);
        data.append('password', password);

        // 发送 POST 请求到注册路由
        fetch('/register', {
            method: 'POST',
            body: data
        })
        .then(response => response.json())
        .then(data => {
            // 处理服务器响应
            console.log(data);
            if (data.success) {
                // 如果注册成功，则显示注册成功的提示框
                alert('注册成功！');
                // 注册成功后跳转到登录页面
                window.location.href = 'http://127.0.0.1:5000/login'; // 修改为登录页面的 URL
            } else {
                // 如果注册失败，则弹出注册失败的提示框
                alert('注册失败：' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('注册失败：' + error);
        });

        // 防止表单提交导致页面刷新
        return false;
    };
});
