<script setup lang="ts">
interface ToolCall {
  function_name: string;
  arguments: string;
}

interface CallLogEntry {
  agent: string;
  agent_instructions: string;
  request: any;
  response: any;
  tool_calls: ToolCall[];
}

defineProps<{
  callLog: CallLogEntry[];
}>()
</script>

<template>
  <div class="llm-call-details">
    <h3>📡 LLM 调用详情</h3>
    <div v-if="callLog.length === 0" class="empty">暂无调用记录</div>
    <div v-else class="calls">
      <details v-for="(call, index) in callLog" :key="index" class="call-entry">
        <summary>
          <span class="call-number">{{ index + 1 }}</span>
          <span class="agent-name">{{ call.agent }}</span>
          <span v-if="call.tool_calls.length > 0" class="tool-badge">
            {{ call.tool_calls.length }} tool(s)
          </span>
        </summary>
        <div class="call-content">
          <details>
            <summary>Request</summary>
            <pre>{{ JSON.stringify(call.request, null, 2) }}</pre>
          </details>
          <details>
            <summary>Response</summary>
            <pre>{{ JSON.stringify(call.response, null, 2) }}</pre>
          </details>
          <div v-if="call.tool_calls.length > 0" class="tool-calls">
            <strong>Tool Calls:</strong>
            <div v-for="tc in call.tool_calls" :key="tc.function_name" class="tool-call">
              {{ tc.function_name }}
            </div>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>

<style scoped>
.llm-call-details {
  background: #2d2d2d;
  border-radius: 8px;
  padding: 16px;
  color: #eee;
  max-height: 400px;
  overflow-y: auto;
  border: 2px solid #FFC72C;
}

.llm-call-details h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #FFC72C;
}

.empty {
  color: #888;
  font-size: 12px;
}

.calls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.call-entry {
  background: #1a1a1a;
  border-radius: 4px;
  padding: 8px;
  border: 1px solid #444;
}

.call-entry > summary {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.call-number {
  background: #FFC72C;
  color: #1a1a1a;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
}

.agent-name {
  font-weight: bold;
  color: #FFC72C;
}

.tool-badge {
  background: #DA291C;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.call-content {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #444;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.call-content details {
  background: #1a1a1a;
  border-radius: 4px;
  border: 1px solid #444;
}

.call-content details > summary {
  cursor: pointer;
  padding: 8px;
  font-size: 12px;
  color: #FFC72C;
}

.call-content pre {
  margin: 0;
  padding: 8px;
  font-size: 10px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  color: #aaa;
}

.tool-calls {
  font-size: 12px;
  color: #888;
}

.tool-call {
  background: #DA291C;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  margin-top: 4px;
  display: inline-block;
  margin-right: 4px;
}
</style>