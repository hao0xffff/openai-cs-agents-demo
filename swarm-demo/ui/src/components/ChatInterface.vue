<script setup lang="ts">
import { ref } from 'vue'
import AgentSwitchLog from './AgentSwitchLog.vue'
import LlmCallDetails from './LlmCallDetails.vue'

interface Message {
  role: string;
  content: string;
  agent?: string;
}

interface CallLogEntry {
  agent: string;
  agent_instructions: string;
  request: any;
  response: any;
  tool_calls: { function_name: string; arguments: string }[];
}

const messages = ref<Message[]>([])
const currentAgent = ref('迎宾员')
const callLog = ref<CallLogEntry[]>([])
const agentSwitchLog = ref<string[]>(['迎宾员'])
const userInput = ref('')
const loading = ref(false)

const API_BASE = 'http://localhost:8000'

async function sendMessage() {
  if (!userInput.value.trim() || loading.value) return

  const input = userInput.value.trim()
  userInput.value = ''
  loading.value = true

  // 添加用户消息
  messages.value.push({ role: 'user', content: input })

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: input,
        model: 'mimo-v2.5-pro'
      })
    })

    const data = await response.json()

    // 更新 call log
    callLog.value = data.call_log

    // 从 call log 中提取 agent 交接链路
    const switches = ['迎宾员']
    for (const entry of data.call_log) {
      if (entry.tool_calls && entry.tool_calls.length > 0) {
        // 检查是否有交接
        for (const tc of entry.tool_calls) {
          if (tc.function_name.startsWith('transfer_to_')) {
            // 从函数名提取目标 agent
            const target = tc.function_name.replace('transfer_to_', '')
            // 转换为中文
            const targetMap: Record<string, string> = {
              'order': '点餐员',
              'fries': '炸薯条师傅',
              'chicken': '炸鸡师傅',
              'cola': '倒可乐专员'
            }
            const targetName = targetMap[target] || target
            switches.push(targetName)
          }
        }
      }
    }
    agentSwitchLog.value = switches

    // 更新当前 agent
    currentAgent.value = data.current_agent

    // 添加 assistant 消息，使用后端返回的 agent 字段
    for (const msg of data.messages) {
      if (msg.role === 'assistant' && msg.content) {
        messages.value.push({
          role: 'assistant',
          content: msg.content,
          agent: msg.agent
        })
      }
    }
  } catch (error) {
    messages.value.push({ role: 'assistant', content: `错误: ${error}` })
  } finally {
    loading.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div class="chat-container">
    <div class="sidebar">
      <AgentSwitchLog :switches="agentSwitchLog" />
      <LlmCallDetails :callLog="callLog" />
    </div>

    <div class="main">
      <div class="current-agent">
        当前 Agent: <span class="agent-badge">{{ currentAgent }}</span>
      </div>

      <div class="messages">
        <div v-if="messages.length === 0" class="empty-state">
          🍔 开始和 Agent 对话吧！
        </div>
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <span class="role">{{ msg.role === 'user' ? '顾客' : (msg.agent || currentAgent) }}</span>
          <span class="content">{{ msg.content }}</span>
        </div>
        <div v-if="loading" class="loading">🤔 思考中...</div>
      </div>

      <div class="input-area">
        <textarea
          v-model="userInput"
          @keydown="handleKeydown"
          placeholder="输入消息..."
          :disabled="loading"
        ></textarea>
        <button @click="sendMessage" :disabled="loading || !userInput.trim()">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  gap: 16px;
  padding: 16px;
  box-sizing: border-box;
  background: #1a1a1a;
}

.sidebar {
  width: 350px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.current-agent {
  padding: 12px 16px;
  background: #DA291C;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.agent-badge {
  background: #FFC72C;
  color: #DA291C;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: bold;
}

.messages {
  flex: 1;
  background: #2d2d2d;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 2px solid #FFC72C;
}

.empty-state {
  color: #FFC72C;
  text-align: center;
  margin-top: 40%;
  font-size: 18px;
}

.message {
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
}

.message.user {
  background: #DA291C;
  flex-direction: row-reverse;
  text-align: right;
}

.message.user .content {
  color: white;
}

.message.assistant {
  background: #3d3d3d;
}

.role {
  color: #FFC72C;
  font-size: 11px;
  min-width: 70px;
  font-weight: bold;
}

.message.user .role {
  color: #FFC72C;
}

.content {
  color: #ffffff;
  font-size: 14px;
  white-space: pre-wrap;
}

.loading {
  color: #FFC72C;
  text-align: center;
  font-style: italic;
}

.input-area {
  display: flex;
  gap: 8px;
}

.input-area textarea {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  border: 2px solid #FFC72C;
  background: #2d2d2d;
  color: white;
  resize: none;
  font-size: 14px;
}

.input-area textarea:focus {
  outline: none;
  border-color: #DA291C;
}

.input-area textarea::placeholder {
  color: #888;
}

.input-area button {
  padding: 12px 24px;
  background: #DA291C;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
}

.input-area button:hover {
  background: #b22222;
}

.input-area button:disabled {
  background: #666;
  cursor: not-allowed;
}
</style>