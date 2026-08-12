<template>
  <section class="ink-panel">
    <!-- 四角墨迹 -->
    <i class="corner tl"></i><i class="corner tr"></i>
    <i class="corner bl"></i><i class="corner br"></i>
    <header class="ink-panel-title">
      <span class="seal-dot"></span>
      <span class="title-text"><slot name="title">面板</slot></span>
      <span class="title-rule"></span>
    </header>
    <div class="ink-panel-body">
      <slot name="content"></slot>
    </div>
  </section>
</template>

<script setup></script>

<style lang="scss" scoped>
.ink-panel {
  position: relative;
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0) 42%),
    linear-gradient(340deg, rgba(150, 120, 80, 0.10), rgba(255, 255, 255, 0) 55%),
    rgba(248, 243, 234, 0.92);
  border: 1px solid rgba(106, 71, 53, 0.35);
  box-shadow:
    0 2px 14px rgba(74, 58, 42, 0.10),
    inset 0 0 0 3px rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.corner {
  position: absolute;
  width: 16px;
  height: 16px;
  pointer-events: none;
  opacity: 0.75;
}
.corner.tl { top: 0; left: 0; border-top: 2px solid #6a4735; border-left: 2px solid #6a4735; }
.corner.tr { top: 0; right: 0; border-top: 2px solid #6a4735; border-right: 2px solid #6a4735; }
.corner.bl { bottom: 0; left: 0; border-bottom: 2px solid #6a4735; border-left: 2px solid #6a4735; }
.corner.br { bottom: 0; right: 0; border-bottom: 2px solid #6a4735; border-right: 2px solid #6a4735; }

.ink-panel-title {
  position: relative;
  height: 44px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  background: linear-gradient(90deg, rgba(106, 71, 53, 0.14), rgba(106, 71, 53, 0.02));
  border-bottom: 1px solid rgba(106, 71, 53, 0.18);
}
.seal-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a03a2e;
  box-shadow: 0 0 0 3px rgba(160, 58, 46, 0.18);
}
.title-text {
  font-family: 'STKaiti', 'KaiTi', '楷体', 'Kaiti SC', serif;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 3px;
  color: #241b15;
}
.title-rule {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(106, 71, 53, 0.4), transparent);
}
.ink-panel-body {
  flex: 1;
  min-height: 0;
  padding: 10px 14px 12px;
  box-sizing: border-box;
}
</style>
