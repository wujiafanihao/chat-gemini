// 页面加载时初始化聊天框
document.addEventListener("DOMContentLoaded", initializeChat);

// 初始化聊天界面
function initializeChat() {
    const chatBox = document.getElementById('chat-box');
    displayWelcomeMessage(chatBox);

    // 给发送按钮和清除按钮添加事件监听器
    document.getElementById('send-button').addEventListener('click', sendMessage);
    document.getElementById('clear-button').addEventListener('click', clearChatHistory);
    // document.getElementById('file-input').addEventListener('change', handleFileSelect);
    // 图片预览容器初始时隐藏
    const imagePreviewContainer = document.getElementById('image-preview-container');
    if (imagePreviewContainer) {
        imagePreviewContainer.style.display = 'none';
    }
    // 给文件输入框添加事件监听器以处理文件选择事件
    document.getElementById('file-input').addEventListener('change', handleFileSelect);

    // 监听输入框的 input 事件
    const userInput = document.getElementById('user-input');
    const typingIndicator = document.getElementById('typing-indicator');
    userInput.addEventListener('input', function() {
        // 如果输入框中有文本，显示正在输入指示器，否则隐藏
        if (userInput.value.trim() !== '') {
            if (typingIndicator) {
                typingIndicator.style.display = 'block';
            }
        } else {
            if (typingIndicator) {
                typingIndicator.style.display = 'none';
            }
        }
    });

    // 监听输入框的 blur 事件（即失去焦点事件），隐藏正在输入指示器
    userInput.addEventListener('blur', function() {
        if (typingIndicator) {
            typingIndicator.style.display = 'none';
        }
    });
}

// 显示欢迎信息
function displayWelcomeMessage(chatBox) {
    const welcomeMessage = "你好，请问有什么需求吗？";
    
    setTimeout(function() {
        chatBox.appendChild(createMessageWithAvatar('bot', welcomeMessage, 'bot-message'));
        scrollChatToBottom(chatBox);
    }, 500);
}

// 清除聊天历史记录
function clearChatHistory() {
    const chatBox = document.getElementById('chat-box');
    const temporaryContainer = document.createElement('div');
    const headContainer = document.querySelector('.head_container');
    temporaryContainer.appendChild(headContainer.cloneNode(true));
    chatBox.innerHTML = '';
    chatBox.appendChild(temporaryContainer.firstChild);

    // 显示清理成功的提示
    showSuccessMessage('清理成功');

    initializeChat(); // 重新初始化聊天界面
}

// 创建提示元素
function showSuccessMessage(message) {
    const successMessage = document.createElement('div');
    successMessage.innerText = message;  // 设置提示文字
    successMessage.style.position = 'fixed';  // 设置提示元素的样式
    successMessage.style.bottom = '50%';
    successMessage.style.right = '50%';
    successMessage.style.color = 'black';
    successMessage.style.backgroundColor = 'rgb(190, 150, 97)';
    successMessage.style.padding = '5px';
    successMessage.style.borderRadius = '5px';
    successMessage.style.opacity = '1';  // 初始不透明
    successMessage.style.transition = 'opacity 1.5s';  // 透明过渡效果设置为1.5秒
    document.body.appendChild(successMessage);  // 将提示元素添加到页面上

    // 1.5秒后逐渐消失
    setTimeout(function() {
        successMessage.style.opacity = '0';
    }, 1500);

    // 1.5秒后从页面中删除元素
    setTimeout(function() {
        document.body.removeChild(successMessage);
    }, 3000);
}

// 发送消息的处理函数
function sendMessage(event) {
    event.preventDefault();  // 确保没有默认的表单提交行为
    console.log('Send button clicked');  // 控制台将输出该日志，确保每个点击仅触发一次
    showThinkingAnimation(); // 显示思考动画
    processUserInput();
}
// 显示正在思考动画
function showThinkingAnimation() {
    const chatBox = document.getElementById('chat-box');
    const thinkingAnimation = createThinkingAnimationElement();
    chatBox.appendChild(thinkingAnimation);
    scrollChatToBottom(chatBox);
}
// 创建正在思考动画元素
function createThinkingAnimationElement() {
    const thinkingAnimation = document.createElement('div');
    thinkingAnimation.classList.add('thinking-animation');
    thinkingAnimation.innerHTML = '<div class="loader"></div><p>正在思考...</p>'; // 这里使用了一个CSS动画，你需要在CSS中定义这个动画
    return thinkingAnimation;
}
// 隐藏思考动画的函数
function hideThinkingAnimation() {
    const chatBox = document.getElementById('chat-box');
    const thinkingAnimation = chatBox.querySelector('.thinking-animation');
    if (thinkingAnimation) {
        chatBox.removeChild(thinkingAnimation);
    }
}


// 处理用户输入
function processUserInput() {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input').value.trim();
    const fileInput = document.getElementById('file-input').files[0];
    let userMessageDiv;

    // 清空输入字段
    document.getElementById('user-input').value = '';
    document.getElementById('file-input').value = '';
    selectedFile = null; // 重置selectedFile状态

    // 如果用户只上传了图片
    if (!userInput && fileInput) {
        userMessageDiv = createMessageWithAvatar('user', '', 'user-message', URL.createObjectURL(fileInput));
        chatBox.appendChild(userMessageDiv); // 添加到聊天框
        scrollChatToBottom(chatBox);
        sendUserFileToServer(fileInput); // 假定这是您发送文件的函数
    }
    // 如果用户只输入了文本
    else if (userInput && !fileInput) {
        userMessageDiv = createMessageWithAvatar('user', userInput, 'user-message');
        chatBox.appendChild(userMessageDiv); // 添加到聊天框
        scrollChatToBottom(chatBox);
        sendUserInputToServer(userInput); // 发送文本到服务器
    }
    // 如果用户文本和图片一起发送
    else if (userInput && fileInput) {
        userMessageDiv = createMessageWithAvatar('user', userInput, 'user-message', URL.createObjectURL(fileInput));
        chatBox.appendChild(userMessageDiv); // 添加到聊天框
        scrollChatToBottom(chatBox);
        sendUserInputAndFileToServer(userInput, fileInput); // 同时发送文本和图片到服务器
    }
}

// 向服务器发送用户输入
function sendUserInputToServer(userInput) {
    showSuccessMessage('模型已切换为Gemini-pro');
    console.log('以切换到Gemini-pro');
    const chatBox = document.getElementById('chat-box');
    axios.post('/get_response', `user_input=${encodeURIComponent(userInput)}`)
    .then(response => {
        // AI 响应成功后，隐藏思考动画
        hideThinkingAnimation();
        chatBox.appendChild(createMessageWithAvatar('bot', response.data.bot_response, 'bot-message'));
        scrollChatToBottom(chatBox);
    })
    .catch(error => {
        // AI 响应成功后，隐藏思考动画
        hideThinkingAnimation();
        console.error('Error fetching response: ', error);
        handleErrorResponse();
    });
}

// 文件上传处理函数
function sendUserFileToServer(fileInput) {
    showSuccessMessage('模型已切换为Gemini-pro-vision');
    console.log('以切换到Gemini-pro-vision');
    const formData = new FormData();
    formData.append('file', fileInput);

    // 将文件上传的路径作为参数传递给后端
    const uploadUrl = '/upload_file?upload_path=' + encodeURIComponent('/dynamic/upload/folder');

    axios.post(uploadUrl, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
    .then(response => {
        // AI 响应成功后，隐藏思考动画
        hideThinkingAnimation();
        const chatBox = document.getElementById('chat-box');
        console.log('File uploaded successfully:', response);

        // 从响应中获取具体的内容
        const responseData = response.data;
        const responseContent = responseData.bot_response; // 修改此处，根据实际情况获取服务器响应的内容

        chatBox.appendChild(createMessageWithAvatar('bot', responseContent, 'bot-message'));
        scrollChatToBottom(chatBox);
    })
    .catch(error => {
        // AI 响应成功后，隐藏思考动画
        hideThinkingAnimation();
        console.error('Error uploading file: ', error);
        console.error('Error details: ', error.response.data); // 打印出具体的错误信息
        handleFileErrorResponse(); // 修改此处，根据实际情况调用错误处理函数
    });
}

// 向服务器发送用户输入和文件
function sendUserInputAndFileToServer(userInput, fileInput) {
    showSuccessMessage('模型已切换为Gemini-pro-vision');
    console.log('以切换到Gemini-pro-vision');
    // 创建 FormData 实例以便一起发送文本和文件
    const formData = new FormData();
    formData.append('user_input', userInput); // 将用户输入作为文本字段添加
    console.log('Sending text and file...');
    const file = fileInput; // 已经确保fileInput是有效的文件对象
    formData.append('file', file); // 将用户选中的文件作为文件字段添加

    // 定义服务器端接收文件和文本输入的 API 路径
    const uploadUrl = '/upload_with_input';

    axios.post(uploadUrl, formData)
    .then(response => {
        // AI 响应成功后，隐藏思考动画
        hideThinkingAnimation();
        // 成功响应的处理逻辑
        const chatBox = document.getElementById('chat-box');
        console.log('Text and file uploaded successfully:', response);

        // 从响应中获取具体的内容
        const responseData = response.data;
        const responseContent = responseData.bot_response; // 假设响应的内容位于bot_response字段中

        chatBox.appendChild(createMessageWithAvatar('bot', responseContent, 'bot-message'));
        scrollChatToBottom(chatBox);
    })
    .catch(error => {
        // AI 响应成功后，隐藏思考动画
        hideThinkingAnimation();
        // 错误处理逻辑
        console.error('Error uploading text and file: ', error);
        handleErrorResponse(); // 调用通用的错误处理函数
    });
}
// 处理错误响应
function handleErrorResponse() {
    const chatBox = document.getElementById('chat-box');
    chatBox.appendChild(createMessageWithAvatar('bot', "Sorry, there was an error.", 'bot-message'));
    scrollChatToBottom(chatBox);
}
function handleFileErrorResponse(){
    const chatBox = document.getElementById('chat-box');
    chatBox.appendChild(createMessageWithAvatar('bot', "Sorry, File upload error.", 'bot-message'));
    scrollChatToBottom(chatBox);
}

// 创建带头像的消息元素
function createMessageWithAvatar(author, text, className, imgSrc = null) {
    console.log('Creating message:', { author, text, imgSrc });
    const messageWithAvatarDiv = document.createElement('div');
    messageWithAvatarDiv.classList.add('message-container', author);

    // 添加头像元素
    const avatarElement = createAvatarElement(author);
    messageWithAvatarDiv.appendChild(avatarElement);

    // 创建消息内容元素
    const messageContentDiv = document.createElement('div');
    messageContentDiv.classList.add('message-content');

    if (text && imgSrc) {
        // 如果用户同时输入了文本和图片
        const textElement = document.createElement('div');
        textElement.classList.add(className);
        textElement.textContent = text;
        messageContentDiv.appendChild(textElement);

        const imageElement = document.createElement('img');
        imageElement.classList.add('message-image');
        imageElement.src = imgSrc;
        messageContentDiv.appendChild(imageElement);
    } else if (imgSrc) {
        // 如果用户只上传了图片
        const imageElement = document.createElement('img');
        imageElement.classList.add('message-image', className);
        imageElement.src = imgSrc;
        messageContentDiv.appendChild(imageElement);
    } else {
        // 如果用户只输入了文本
        const textElement = document.createElement('div');
        textElement.classList.add(className);
        textElement.textContent = text;
        messageContentDiv.appendChild(textElement);
    }

    messageWithAvatarDiv.appendChild(messageContentDiv);

    return messageWithAvatarDiv;
}


// 创建消息内容元素

function createContentElement(author, className, text, imgSrc) {
    const messageContentDiv = document.createElement('div');
    messageContentDiv.classList.add('message-content');

    // 如果有图片源，首先创建图片元素并添加到内容元素中
    if (imgSrc) {
        const imgElement = createImageElement(imgSrc);
        messageContentDiv.appendChild(imgElement);
    }

    // 创建并添加文本内容
    const messageDiv = document.createElement('div');
    messageDiv.className = className;
    messageDiv.innerHTML = text.includes('*') || text.includes('`') ? markdownToHTML(text) : text;
    messageContentDiv.appendChild(messageDiv);

    return messageContentDiv;
}

// 创建头像元素
function createAvatarElement(author) {
    const avatar = document.createElement('img');
    avatar.classList.add('avatar');
    avatar.src = author === 'user' ? '../static/img/user-avatar.png' : '../static/img/bot-avatar.png';
    avatar.alt = 'avatar';
    return avatar;
}

// 创建图片元素
function createImageElement(imgSrc) {
    const imgElement = document.createElement('img');
    imgElement.src = imgSrc;
    imgElement.classList.add('message-image');
    return imgElement;
}

// 文件选择处理函数
function handleFileSelect(event) {
    selectedFile = event.target.files[0]; // 获取并保存选择的文件

    // 显示文件预览（如果需要的话）
    const fileInput = event.target;
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const imagePreviewContainer = document.getElementById('image-preview-container');
            if (imagePreviewContainer) {
                imagePreviewContainer.style.display = 'block';
                const imagePreview = document.getElementById('image-preview');
                imagePreview.src = e.target.result;
            }
        }
        reader.readAsDataURL(fileInput.files[0]);
    }
}

// 滚动聊天内容到底部
function scrollChatToBottom(chatBox) {
    chatBox.scrollTop = chatBox.scrollHeight;
}

let selectedFile = null;  // 用来存放选择的文件

// Markdown文本转换为HTML的函数
function markdownToHTML(text) {
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
               .replace(/\*(.*?)\*/g, '<em>$1</em>')
               .replace(/`(.*?)`/g, '<code>$1</code>')
               .replace(/\n/g, '<br>');
}

