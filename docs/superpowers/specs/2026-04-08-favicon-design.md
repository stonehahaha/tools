# Data Processing Favicon Design

Date: 2026-04-08

## Goal

为 `data.ebaking.cn` 设计一个新的浏览器标签页图标，用于替换当前过于复杂、缩小后识别度不足的图标。

## Chosen Direction

- Base concept: `流程线`
- Visual metaphor: `数据进入 -> 处理 -> 输出`
- Shape style: `适配 favicon 的简化小图标`
- Color direction: `站内一致的蓝紫渐变`

## Visual Rules

- 使用圆角方形底板，提升浏览器标签页中的稳定识别度
- 主体采用高对比度流程线结构，不使用复杂细节
- 保留 3 个主要节点，避免缩小时糊成一团
- 节点与主线保持较粗笔画，优先保证 `16x16` 可辨识
- 使用蓝紫渐变背景，与站内品牌区视觉一致
- 使用白色主线，配一个暖色强调节点，增强记忆点

## Constraints

- 这是专用 favicon，不追求大尺寸海报效果
- 优先适配浏览器标签页，而不是站内插图
- 不复用当前复杂 SVG 主体造型
- 输出应兼容 `index.html` 中的 favicon 引用方式

## Out of Scope

- 站内品牌区 logo 联动改造
- 应用内大图标系统重做
- 多套品牌方案并行维护

## Next Step

基于以上方向直接生成并替换 favicon 资源，然后更新 `index.html` 引用并做本地构建验证。
