GOOGLE_API_KEY = "AIzaSyAdATybFV0tHQlXQBaPwps32U5ojliM4tM"

# 用于接收用户 Gemini API 密钥的路由
@app.route("/set_gemini_api_key", methods=["POST"])
def set_gemini_api_key():
    global gemini_key  # 声明 gemini_key 是全局变量
    try:
        # 从请求中获取用户提供的 Gemini API 密钥
        gemini_api_key = request.form.get("gemini_api_key")
        
        # 检查是否提供了 API 密钥
        if not gemini_api_key:
            return jsonify(status="Please provide a Gemini API key"), 400
        
        # 在这里可以将 API 密钥存储到数据库或其他地方
        # 这里只是简单地打印 API 密钥到终端
        print("Gemini API Key saved:", gemini_api_key)
        gemini_key = genai.configure(api_key=gemini_api_key)
        app.logger.log(20, "User API key saved")
        return jsonify(status="Gemini API key saved successfully")
    except Exception as e:
        app.logger.error(f"Error setting Gemini API key: {e}")
        return jsonify(status="Error setting Gemini API key"), 500