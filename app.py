import streamlit as st
import requests
import json
import time

# 从 Secrets 获取配置
UPSTASH_URL = st.secrets["UPSTASH_REST_URL"]
UPSTASH_TOKEN = st.secrets["UPSTASH_REST_TOKEN"]
DEEPSEEK_KEY = st.secrets["DEEPSEEK_API_KEY"]

# --- 数据库读写函数 ---
def save_to_cloud(messages):
    url = f"{UPSTASH_URL}/set/alkaid_chat"
    headers = {"Authorization": f"Bearer {UPSTASH_TOKEN}"}
    requests.post(url, headers=headers, data=json.dumps(messages))

def load_from_cloud():
    url = f"{UPSTASH_URL}/get/alkaid_chat"
    headers = {"Authorization": f"Bearer {UPSTASH_TOKEN}"}
    resp = requests.get(url, headers=headers).json()
    if resp.get("result"):
        return json.loads(resp["result"])
    return None

# --- 初始化记忆 ---
if "messages" not in st.session_state:
    saved_history = load_from_cloud()
    if saved_history:
        st.session_state.messages = saved_history
    else:
        st.session_state.messages = [{"role": "assistant", "content": "学妹，好久不见。"}]

# --- UI 样式 (沿用之前的极简纯色) ---
st.markdown(f"""
    <style>
       /* --- 终极抹除底部所有 Streamlit 痕迹 (三重保险) --- */
    
    /* 1. 隐藏官方页脚和菜单 */
    footer {visibility: hidden !important; height: 0px !important; margin: 0px !important;}
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}

    /* 2. 暴力切断底部“Manage app”和“登录信息”容器 */
    /* 针对最新版 Streamlit Cloud 的悬浮工具栏 */
    div[data-testid="stStatusWidget"], 
    .stDeployButton,
    div[class*="viewerBadge"],
    div[class*="StreamlitToolbar"],
    div[class*="stStyledBox"] {
        display: none !important;
    }

    /* 3. 强制内容区撑满底部，不给那一横条留空间 */
    .block-container {
        padding-bottom: 0rem !important;
    }
    
    /* 针对某些安卓浏览器会在底部留白的修补 */
    .stApp {
        bottom: 0 !important;
        position: fixed !important;
        width: 100vw !important;
        height: 100vh !important;
    }
 
    /* 1. 基础清场：隐藏所有不需要的官方组件 */
    footer, #MainMenu {{ visibility: hidden !important; }}
    [data-testid="stHeader"], .stDeployButton {{ display: none !important; }}
    div[data-testid="stStatusWidget"] {{ display: none !important; }}

    /* 2. 【核心】自定义全局背景图片 */
    /* 请把下面的图片链接换成你自己的（支持在线链接或 Base64） */
    .stApp {{
        background-image: url("https://github.com/Alkaidshelter/sunshineRome/blob/main/QQ%E5%9B%BE%E7%89%8720260405174515.jpg"); 
        background-size: cover;
        background-position: center;
        background-attachment: fixed; /* 关键：背景固定，聊天气泡滚动 */
    }}

    /* 3. 复活“三条杠”菜单按钮 (奶油色微调) */
    header[data-testid="stHeader"] {{
        display: flex !important;
        background: transparent !important;
        height: 3.5rem !important;
        border: none !important;
        z-index: 99999 !important;
    }}
    header[data-testid="stHeader"] > div:first-child {{
        display: flex !important;
    }}
    button[kind="header"] {{
        color: #C0A080 !important; /* 金色菜单按钮 */
        background-color: rgba(255, 255, 255, 0.4) !important; /* 半透明底，衬托图片 */
        border-radius: 50% !important;
        margin-left: 10px !important;
    }}

    /* 4. 暴力隐藏气泡上方的 assistant/user 标签 */
    [data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] > p:first-child:has(+ *) {{
        display: none !important;
    }
    div[data-testid="chatAvatar"] + div {{
        display: flex;
        flex-direction: column;
    }}
    .stChatMessage [data-testid="stWidgetLabel"],
    .stChatMessage .st-ae,
    .stChatMessage code {{
        display: none !important;
    }}

    /* 5. 【核心】气泡整容：圆角长方形 + 你选的奶油色 */
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        padding: 0.8rem 0 !important;
        gap: 8px !important; /* 头像和气泡优雅间距 */
    }

    /* 路辰的气泡 (Assistant) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarAssistant"]) .stMarkdown {{
        background-color: #FBF2E2 !important; /* 老大选的路辰奶油黄 */
        border: 1px solid rgba(192, 160, 128, 0.2) !important; /* 超细金色描边 */
        border-radius: 4px 18px 18px 18px !important;
        padding: 12px 16px !important;
        color: #5D4037 !important; /* 深棕色文字，保护眼睛且更有质感 */
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    /* 修改默认头像颜色，防白 */
    div[data-testid="chatAvatarAssistant"] svg {{
        fill: #C0A080 !important;
    }}

    /* 你的气泡 (User) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarUser"]) {{
        flex-direction: row-reverse !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarUser"]) .stMarkdown {{
        background-color: #FFEFD7 !important; /* 老大选的用户奶油粉 */
        border: 1px solid rgba(255, 239, 215, 0.3) !important;
        border-radius: 18px 4px 18px 18px !important;
        padding: 10px 14px !important;
        color: #5D4037 !important; /* 深棕色文字 */
    }
    /* 修改用户头像颜色 */
    div[data-testid="chatAvatarUser"] svg {{
        fill: #5C5C5C !important;
    }}

    /* 6. 输入框美化 (浮动悬浮感) */
    .stChatInputContainer {{
        padding-bottom: 25px !important;
        background-color: transparent !important;
    }
    .stChatInput {{
        background-color: rgba(255, 255, 255, 0.8) !important; /* 半透明输入框 */
        border-radius: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }
</style>



""", unsafe_allow_html=True)

# 渲染历史
for msg in st.session_state.messages:
    # 这一行是关键！千万不要写成 with st.chat_message("路辰"):
    # 必须写 msg["role"] 或者 "assistant" / "user"
    with st.chat_message("assistant" / "user"):
        st.markdown(msg["content"])


# --- 聊天逻辑 ---
if user_input := st.chat_input("和路辰聊聊..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 立即调用 DeepSeek
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
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}] + st.session_state.messages
    }
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
        reply = resp.json()["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": reply})
        
        # 关键：对话更新后立刻存入云端
        save_to_cloud(st.session_state.messages)
        st.rerun()
    except Exception as e:
        st.error(f"路辰断网了: {e}")

# 侧边栏加个重置按钮
if st.sidebar.button("清空所有记忆"):
    st.session_state.messages = []
    save_to_cloud([])
    st.rerun()
