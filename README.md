# Universal Whisper Dictation (通用语音输入法) 🎤

> A portable, user-friendly voice dictation system with smart formatting for Chinese, English, and mixed-language input.
> 
> 一个便携、易用的语音输入系统，支持中英文混合输入及智能格式化。

## ✨ 核心功能 / Key Features

### 🌍 多语言支持 / Multi-Language Support
- **中文 (Chinese)**: 自动标点 (，。！？)、智能分段。
- **英文 (English)**: 自动标点、句首大写、智能分句。
- **混合 (Mixed)**: 自动优化中英文之间的空格 (Auto-spacing between Chinese & English)。

### ✨ AI 润色 (AI Polish) - **NEW!**
- **语法修正 (Grammar Fix)**: 瞬间修复口语中的语法错误。
- **语气调整 (Tone Adjustment)**: 将原本的话改为“商务风”、“地道口语”或“简洁模式”。
- **翻译 (Translation)**:哪怕你说的是中文，也能直接输出英文。
- **兼容性 (BYO Key)**: 支持 OpenAI, DeepSeek, Google Gemini 等所有兼容 API。
- *English:* Integrate LLM support to refine grammar, tone, or translate text instantly.

### 🎮 游戏兼容模式 / Game Compatibility
- **Smart Latch**: **轻按 (Tap)** 快捷键切换录音开关（解决游戏屏蔽长按的问题）；**长按 (Hold)** 保持对讲机模式。
- **WASAPI**: 使用共享音频模式，完美兼容《最终幻想7 重制版》、《赛博朋克 2077》等独占音频的游戏。

### 🚀 通用性 / Universal Compatibility
- **无需管理员权限 (No Admin Needed)**: 在任何文件夹解压即用。
- **自动检测 (Auto-Detect)**: 自动识别 NVIDIA GPU 加速，无显卡自动切换 CPU 模式。

---

## 🚀 快速开始 / Quick Start

### 首次安装 / First Time Setup
1. **下载** 项目文件夹。
2. **双击** `portable-setup.bat`。
3. **等待** 安装完成 (约 5-10 分钟)。
4. **双击** `start-universal.bat`。
5. **跟随** 交互式向导完成设置。

### 日常使用 / Daily Use
只需运行 `start-universal.bat`，然后：
- **按住 (HOLD)** 快捷键 (默认 F15)
- **说话 (SPEAK)** (中英文混合皆可)
- **松开 (RELEASE)** 即可上屏
- **轻按 (TAP)** 快捷键可切换为“长录音模式” (再次轻按停止)

---

## ⚙️ 配置说明 / Configuration

### 设置向导 / Setup Wizard
首次运行时会自动启动向导，引导你设置：
- **语言偏好**: 中文/英文/混合
- **文本风格**: 聊天/正式/商务
- **快捷键**: 自定义触发键 (推荐 F15-F20)

### AI 润色设置 / AI Polish Setup
在托盘图标右键 -> **Settings** -> **AI Polish** 页签：
- **Enable AI Polish**: 开启功能
- **API Key**: 填入你的 LLM API Key
- **Prompt Template**: 选择预设模板 (如 Grammar Fix) 或自定义

### 配置文件 / User Config
所有设置保存在 `user-config.json` 中：
```json
{
  "hotkey": "f15",
  "ai_polish_enabled": true,
  "ai_model": "gpt-4o-mini",
  "language": null,      // null = Auto-detect
  "device": "auto"       // auto / cuda / cpu
}
```

---

## 📝 效果示例 / Examples

### 中文输入 (Chinese)
```
输入:  今天天气真好啊我要去公园玩然后回家吃饭
输出:  今天天气真好啊！我要去公园玩，然后回家吃饭。
```

### 英文输入 (English)
```
Input:  hello today is a great day i want to go to the park
Output: Hello. Today is a great day. I want to go to the park.
```

### 混合输入 (Mixed)
```
输入:  我有5个apple和3个banana today is great
输出:  我有 5 个 apple 和 3 个 banana. Today is great.
```

### AI 润色 (AI Polish)
```
语音: "I want open window let wind come."
输出: "I would like to open the window to let in some fresh air." (Native Speaker Mode)
```

---

## 🖱️ 鼠标侧键设置 / Mouse Button Setup

推荐使用 **X-Mouse Button Control** 将鼠标侧键映射为 F15-F24 虚拟键：
1. 打开 X-Mouse Button Control。
2. 选择侧键 (Mouse Button 4/5)。
3. 选择 "Simulated Keys" (模拟按键)。
4. 输入 `{F15}`。
5. 模式选择 "During (press on down, release on up)"。

---

## 📁 文件结构 / File Structure

```
whisper-dictation/
├── dictation-universal.py      # 主程序 (Main Program)
├── ai_helper.py                # AI 润色模块 (AI Module)
├── start-universal.bat         # 启动脚本 (Launcher)
├── portable-setup.bat          # 安装脚本 (Installer)
├── settings_gui.py             # 设置界面 (Settings UI)
├── user-config.json            # 用户配置 (User Config)
├── AGENT_GUIDE.md              # 开发者指南 (Developer Guide)
└── .venv/                      # Python 环境 (Python Env)
```

---

## 🔒 隐私与安全 / Privacy & Security

✅ **100% 本地化 (Local)**
- 语音识别完全在本地运行 (Faster-Whisper)。
- 不上传录音数据。

⚠️ **AI 功能 (AI Feature)**
- *仅当开启 AI Polish 时*，文本会被发送到你配置的 API 提供商 (如 OpenAI)。
- *Only when AI Polish is enabled*, text is sent to your configured API provider.

---

## 📄 许可证 / License
MIT License

**Made with ❤️ for effortless voice typing.**
