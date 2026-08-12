// 徽州 · 水墨国风 设计令牌
// 参考传统徽州色彩体系：宣纸米白 / 墨黑 / 桥木褐 / 土壤橙 / 河川蓝 / 朱砂红
export const INK = {
  paper: '#f3ece3',        // 宣纸米白（页面底色）
  paperLight: '#faf5ec',   // 新宣纸
  paperDark: '#e3d5bf',    // 旧宣纸 / 深底
  paperEdge: '#d9c7aa',    // 纸缘
  ink: '#241b15',          // 墨黑（主文字）
  inkSoft: '#4a3a2a',      // 淡墨
  inkLine: '#9a8470',      // 枯笔线
  inkFaint: '#c8b69c',     // 极淡墨（网格）
  brown: '#6a4735',        // 桥木褐
  orange: '#c57b3a',       // 土壤橙（强调）
  blue: '#4f7681',         // 河川蓝
  red: '#a03a2e',          // 朱砂红（印章）
  gold: '#b08a4a',         // 鎏金
  cream: '#efe5d4',        // 米汤色
}

// 柱状图渐变（墨韵递进）
export const inkBarGradient = (opacity = 0.85) => ({
  type: 'linear',
  x: 0, y: 0, x2: 0, y2: 1,
  colorStops: [
    { offset: 0, color: `rgba(106, 71, 53, ${opacity})` },
    { offset: 1, color: `rgba(36, 27, 21, ${opacity * 0.55})` },
  ],
})

// 文字样式速写
export const inkAxisLabel = (color = INK.inkSoft) => ({
  color,
  fontSize: 13,
  fontFamily: '"Kaiti SC","STKaiti","KaiTi","楷体",serif',
})

export default INK
