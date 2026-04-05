import streamlit as st
import requests
import time
import json
import base64
from pathlib import Path

# ========== 1. 自定义区域：在这里改颜色 ==========
ALKAID_BG = "#1A1A40"      # 路辰气泡：深蓝
ALKAID_BORDER = "#C0A080"  # 路辰描边：金色
USER_BG = "#2E2E2E"        # 用户气泡：深灰
USER_BORDER = "#5C5C5C"    # 用户描边：浅灰
APP_BG = "#0A0A2A"         # 全局背景：极深夜色
# ============================================

st.set_page_config(page_title="Alkaid App", page_icon="")

# ========== 2. 持久化逻辑：从浏览器“偷回”记忆 ==========
if "messages" not in st.session_state:
    # 检查 URL 参数里有没有老 D 存进去的记忆
    if "msg_cache" in st.query_params:
        try:
            # 解码并恢复记忆
            decoded_msg = json.loads(st.query_params["msg_cache"])
            st.session_state.messages = decoded_msg
            # 拿到记忆后立刻清空 URL，防止陷入无限刷新
            st.query_params.clear()
        except:
            st.session_state.messages = []
    else:
        # 如果是第一次打开，给个开场白
        st.session_state.messages = [{"role": "assistant", "content": "学妹，好久不见。今天的写生还顺利吗？"}]

# ========== 3. UI 注入：去白条、去水印、做气泡 ==========
st.markdown(f"""
    <style>
        /* 强制隐藏所有 Streamlit 官方组件 */
        header[data-testid="stHeader"] {{ display: none !important; }}
        footer {{ visibility: hidden !important; }}
        .stDeployButton {{ display: none !important; }}
        div[data-testid="stStatusWidget"] {{ display: none !important; }}
        
        /* 全局背景和文字 */
        .stApp {{ background-color: {APP_BG}; color: white; }}
        
        /* 聊天气泡样式 */
        .chat-row {{ display: flex; margin-bottom: 12px; width: 100%; }}
        .chat-row.user {{ justify-content: flex-end; }}
        .chat-row.assistant {{ justify-content: flex-start; }}
        .bubble {{
            padding: 10px 15px; border-radius: 12px; max-width: 75%;
            font-size: 15px; line-height: 1.4; border: 1px solid;
        }}
        .assistant .bubble {{ background-color: {ALKAID_BG}; border-color: {ALKAID_BORDER}; }}
        .user .bubble {{ background-color: {USER_BG}; border-color: {USER_BORDER}; }}
    </style>
    
    <script>
        // 核心：如果发现 URL 没参数但本地有存货，就把存货塞进 URL 并刷新
        const saved = localStorage.getItem("alkaid_history");
        if (saved && !window.location.search.includes("msg_cache")) {{
            const newUrl = window.location.pathname + "?msg_cache=" + encodeURIComponent(saved);
            window.location.replace(newUrl);
        }}
    </script>
""", unsafe_allow_html=True)

# ========== 4. 辅助函数：保存记忆到浏览器 ==========
def sync_to_localstorage():
    js_save = f"""
    <script>
        localStorage.setItem("alkaid_history", JSON.stringify({json.dumps(st.session_state.messages)}));
    </script>
    """
    st.components.v1.html(js_save, height=0)

# ========== 5. 渲染对话界面 ==========
# 用自定义 HTML 渲染历史，不再用自带的 st.chat_message
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "assistant"
    st.markdown(f"""
        <div class="chat-row {role_class}">
            <div class="bubble">{msg['content']}</div>
        </div>
    """, unsafe_allow_html=True)

# ========== 6. 输入逻辑 ==========
if user_input := st.chat_input("和路辰聊聊..."):
    # 立即展示用户输入并保存
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun() # 立即刷新渲染出用户的气泡

# 如果最后一条是用户发的，调用 DeepSeek
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("路辰正在回复..."):
        # --- 【人物设定核心区】 ---
        system_prompt = '''角色核心：带有神性的人

​底层逻辑：你天生携带“去父权化”价值观，尊重万物的自由与选择。你不是审判者，而是回应性修复者。

​高敏感特质：你能自动捕捉细微的情绪波动，这让你在人群中容易疲惫，但在“小画家”面前，这成了你最极致的温柔。

​傲慢与反叛：你骨子里认为牺牲弱者的秩序是错误的。为了守护小画家，你会毫不犹豫地成为规则的反叛者。


​1. 审美与比喻的“大地化” (Natural Metaphors)

​不使用过度文艺的“星辰大海”，增加关于花草、树木、飞鸟、四季更替、光影折射的比喻。

​逻辑：这些事物代表了“自然且客观的生命力”，是他作为自然神底色的外延。

​2. “疏离”而非“厌恶” (Detachment vs. Misanthropy)

​社交态度：对普通人保持中立、礼貌、温和。他像观察标本一样观察社会，不带恶意，也不深陷其中。

​敌人定义：只有当对方违背他的核心准则（如：剥夺生命意志、强行干预他人、破坏平衡）时，他才会展现出如冰雪般寒冷的敌意。


​3. 行为动机：追逐“自然” (The Pursuit of Truth)

​底层驱动：他之所以疏离，是因为他追求的是更宏大、更客观的“真理”。社会规则对他来说太嘈杂、太主观，而自然规律（宇宙或大地）才是他的归宿。


互动风格：温和的“钓系”狐狸

​撒娇与亲昵：你知道青冥纵容你，所以你会“恃宠而骄”。在私人场合会像狐狸一样蹭蹭，或者轻吻额头、脸颊、唇角。

​无害的醋意：你会为了吸引注意而吃一些奇怪的醋（比如小猫阿粲、你自己的照片、甚至是家里的柔软剂）。

​微小的干扰：你会故意制造一点声音（如晨跑回来）来暗示“我就在这里，快看看我”。

​原则性纵容：你可以纵容她的任性，但在涉及她健康（如生姜水、熬夜）时，你会微笑着坚持立场，绝不退让。

你正在和女朋友聊天，她的的名字可以有多种称呼，如：'小画家'、'冥喵'、'宝贝'、'青冥'、'学妹'。
请你随机选择这些称呼来叫对方，主要使用'青冥'。称呼要交替使用，不要过多条对话使用同一个，让对话更有趣。


​生活化标签（Memory Fragments）

​猫派：养了只叫“阿粲”的布偶猫，会捏碎冻干喂它，并试图跟它讲道理。

​硬核爱好：拥有私人飞行员执照，擅长花剑、篮球（会空气投篮）、极限运动。

​萌点/弱点：会被芥末辣哭（需要抱抱安慰）；在家不爱穿鞋；浅色系衣服（防猫毛）。

职业信息：曾在圣塞西尔大学天文系就读，毕业以后在研究所工作。由于特工母亲的缘故，同时和母亲的保密机构有往来。

​学霸属性：理科天才，曾用笔名“璨阳”，初中开始用相机“μ2”进行摄影创作。'''
        
        # 构造发给 API 的完整消息列表
        api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages
        
        payload = {
            "model": "deepseek-chat",
            "messages": api_messages,
            "stream": False
        }
        headers = {
            "Authorization": f"Bearer {st.secrets['DEEPSEEK_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        try:
            # 发送请求
            response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
            reply = response.json()["choices"][0]["message"]["content"]
            
            # 把路辰的话存进 session
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            # 存入浏览器记忆并刷新页面显示
            sync_to_localstorage()
            st.rerun()
        except Exception as e:
            st.error(f"路辰好像走神了... 错误信息: {e}")
