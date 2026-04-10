<script setup lang="ts">
type HostsAction = "modify" | "backup" | "restore" | "open" | "save-domain";

const store = useMtgaStore();
const { runningAction, runAction } = usePendingAction<HostsAction>();
const hostsDomain = computed({
  get: () => store.hostsDomain.value,
  set: (value) => {
    store.hostsDomain.value = value;
  },
});

const hostsDomainTooltip = [
  "可自定义写入 hosts 的目标域名",
  "默认：api.openai.com",
  "修改 hosts 按钮会把该域名指向 127.0.0.1 与 ::1",
].join("\n");

const handleSaveDomain = async () => {
  await runAction("save-domain", async () => {
    const ok = await store.saveConfig();
    if (ok) {
      store.appendLog("hosts 域名设置已保存");
    } else {
      store.appendLog("hosts 域名设置保存失败");
    }
    return ok;
  });
};

const handleModify = async () => {
  await runAction("modify", () => store.runHostsModify("add"));
};

const handleBackup = async () => {
  await runAction("backup", () => store.runHostsModify("backup"));
};

const handleRestore = async () => {
  await runAction("restore", () => store.runHostsModify("restore"));
};

const handleOpen = async () => {
  await runAction("open", () => store.runHostsOpen());
};
</script>

<template>
  <div class="mtga-soft-panel space-y-3">
    <div>
      <div class="text-sm font-semibold text-slate-900">hosts 文件</div>
      <div class="text-xs text-slate-500">自定义域名映射、快速修改与备份恢复</div>
    </div>
    <div class="space-y-2">
      <div
        class="tooltip mtga-tooltip w-full"
        :data-tip="hostsDomainTooltip"
        style="--mtga-tooltip-max: 360px"
      >
        <MtgaInput v-model="hostsDomain" label="hosts 目标域名" placeholder="api.openai.com" />
      </div>
      <MtgaLoadingButton
        class="mtga-btn-outline"
        :loading="runningAction === 'save-domain'"
        :disabled="Boolean(runningAction)"
        @click="handleSaveDomain"
      >
        保存域名设置
      </MtgaLoadingButton>
      <MtgaLoadingButton
        class="mtga-btn-primary"
        :loading="runningAction === 'modify'"
        :disabled="Boolean(runningAction)"
        @click="handleModify"
      >
        修改hosts文件
      </MtgaLoadingButton>
      <div class="grid grid-cols-2 gap-2">
        <MtgaLoadingButton
          class="mtga-btn-outline"
          :loading="runningAction === 'backup'"
          :disabled="Boolean(runningAction)"
          @click="handleBackup"
        >
          备份hosts
        </MtgaLoadingButton>
        <MtgaLoadingButton
          class="mtga-btn-outline"
          :loading="runningAction === 'restore'"
          :disabled="Boolean(runningAction)"
          @click="handleRestore"
        >
          还原hosts
        </MtgaLoadingButton>
      </div>
      <MtgaLoadingButton
        class="mtga-btn-outline"
        :loading="runningAction === 'open'"
        :disabled="Boolean(runningAction)"
        @click="handleOpen"
      >
        打开hosts文件
      </MtgaLoadingButton>
    </div>
  </div>
</template>
