<script setup lang="ts">
defineProps<{
  switches: string[];
}>()
</script>

<template>
  <div class="agent-switch-log">
    <h3>🔄 Agent 交接链路</h3>
    <div v-if="switches.length === 0" class="empty">暂无交接</div>
    <div v-else class="switch-path">
      <span v-for="(agent, index) in switches" :key="index" class="agent-node">
        <span class="agent-name">{{ agent }}</span>
        <span v-if="index < switches.length - 1" class="arrow">→</span>
      </span>
    </div>
  </div>
</template>

<style scoped>
.agent-switch-log {
  background: #2d2d2d;
  border-radius: 8px;
  padding: 16px;
  color: #eee;
  border: 2px solid #FFC72C;
}

.agent-switch-log h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #FFC72C;
}

.empty {
  color: #888;
  font-size: 12px;
}

.switch-path {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.agent-node {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.agent-name {
  background: #DA291C;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: bold;
}

.arrow {
  color: #FFC72C;
  font-size: 12px;
}
</style>