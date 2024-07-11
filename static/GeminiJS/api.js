
// 弹窗相关函数
function openApiKeyModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "block";
}

function closeModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
}

function saveApiKey() {
    var apiKey = document.getElementById("apiKeyInput").value;

    // 构造要发送的数据对象
    const data = new FormData();
    data.append('gemini_api_key', apiKey);

    // 发送 POST 请求到设置 Gemini API 密钥的路由
    fetch('/set_gemini_api_key', {
        method: 'POST',
        body: data
    })
    .then(response => {
        // 检查响应状态
        if (response.ok) {
            console.log("API Key saved successfully:", apiKey);
        } else {
            console.error("Failed to save API Key:", response.statusText);
        }
        closeModal();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('出现错误，请稍后再试。');
    });
}


// 点击页面其他地方关闭弹窗
window.onclick = function(event) {
    var modal = document.getElementById("myModal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
}