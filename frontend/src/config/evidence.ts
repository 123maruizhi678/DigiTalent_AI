export const candidateEvidence = {
  id: 'DEMO-C001',
  name: '陈 * 宇',
  resume: '示例简历 v1，第 1–2 页；已移除联系方式、住址与证件信息。',
  original: '硕士，6 年算法研发经验。参与知识库检索与模型调优项目。',
  fields: '学历：硕士；工作年限：6 年；目标方向：算法研发',
  skills: 'Python、PyTorch、RAG（简历第 1 页技能段）',
  work: '示例科技企业：算法研发，负责模型训练与检索优化（第 1 页工作经历）',
  project: '知识库检索项目：负责召回与重排（第 2 页项目经历）',
  anomaly: '项目起止月份缺失；分布式训练规模缺少证据，需人工核实。',
  matching: [
    {
      requirement: '硕士及以上',
      experience: '简历第 1 页教育经历：硕士',
      basis: '学历符合要求',
      gap: '学历凭证尚未验证',
      score: '20 / 20',
    },
    {
      requirement: '5 年算法经验',
      experience: '简历第 1 页工作经历：6 年',
      basis: '年限符合要求',
      gap: '任职月份待核实',
      score: '28 / 30',
    },
    {
      requirement: 'LLM / RAG 项目',
      experience: '简历第 2 页知识库检索项目',
      basis: '具备召回与重排经验',
      gap: '业务规模缺少量化证据',
      score: '25 / 30',
    },
    {
      requirement: '分布式训练',
      experience: '未提供对应项目记录',
      basis: '证据不足',
      gap: '需面试补充验证',
      score: '8 / 20',
    },
  ],
  sources: [
    { source: '简历', locator: 'DEMO-C001 / v1 / 第 1 页', excerpt: '硕士；6 年算法研发经验' },
    {
      source: '项目经历',
      locator: 'DEMO-C001 / v1 / 第 2 页 / 项目 1',
      excerpt: '负责知识库召回与重排',
    },
    {
      source: '工作经历',
      locator: 'DEMO-C001 / v1 / 第 1 页 / 经历 1',
      excerpt: '模型训练与检索优化',
    },
    {
      source: '技能标签',
      locator: 'DEMO-C001 / 简历技能段',
      excerpt: 'Python、PyTorch、RAG；提取结果待复核',
    },
    {
      source: '测评记录',
      locator: 'DEMO-AS001 / 题组 A / 技术题 1–10',
      excerpt: '技术题答对 9 / 10；模拟评分 90 分',
    },
    {
      source: '面试评价',
      locator: 'DEMO-IV001 / 技术面 / 评价 1',
      excerpt: '能说明检索方案；训练规模需补充验证',
    },
  ],
}
