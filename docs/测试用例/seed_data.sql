-- ============================================================
-- AI 数字化人才平台 · 测试种子数据 (MySQL)
-- 字段依据：docs/design/数据库表设计.md (2026-09-27 真实 ORM 模型)
-- 加载：mysql -u<user> -p ai_talent < seed_data.sql
-- 说明：
--   * 仅含 §3~§8.3 已逐字段展开的表；candidates/projects/project_groups
--     等 §9 未展开表的列为"推断列"，若与 ORM 不符请按实际模型微调。
--   * 数据为脱敏测试样例，非真实个人隐私。
--   * 向量(Milvus)/图谱(Neo4j)需另行灌入，本 SQL 仅落 MySQL 主数据。
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ---------------- 系统 / 权限 (sys_) ----------------
INSERT INTO sys_departments (id, name, parent_id, leader, phone, sort, status, created_at) VALUES
(1, 'AI 平台部', NULL, '张总', '13800000001', 1, 'active', '2026-09-01 09:00:00'),
(2, '算法组', 1, '李工', '13800000002', 1, 'active', '2026-09-01 09:00:00'),
(3, '产品组', 1, '王经理', '13800000003', 2, 'active', '2026-09-01 09:00:00'),
(4, '人力资源部', NULL, '赵HR', '13800000004', 3, 'active', '2026-09-01 09:00:00');

INSERT INTO sys_users (id, username, real_name, password, email, phone, department_id, department_name, status, created_at) VALUES
(1, 'admin', '管理员', 'ENC:test_placeholder', 'admin@demo.com', '13800000001', 1, 'AI 平台部', 'active', '2026-09-01 09:00:00'),
(2, 'hr_zhao', '赵HR', 'ENC:test_placeholder', 'hr@demo.com', '13800000004', 4, '人力资源部', 'active', '2026-09-01 09:00:00'),
(3, 'pm_wang', '王经理', 'ENC:test_placeholder', 'pm@demo.com', '13800000003', 3, '产品组', 'active', '2026-09-01 09:00:00'),
(4, 'emp_chen', '陈宇', 'ENC:test_placeholder', 'chen@demo.com', '13800000005', 2, '算法组', 'active', '2026-09-01 09:00:00');

INSERT INTO sys_roles (id, code, name, description, data_scope, status, created_at) VALUES
(1, 'admin', '系统管理员', '全部权限', 'all', 'active', '2026-09-01 09:00:00'),
(2, 'hr', 'HR管理员', '招聘与候选人', 'dept', 'active', '2026-09-01 09:00:00'),
(3, 'biz', '业务负责人', '本门项目与缺口', 'dept', 'active', '2026-09-01 09:00:00'),
(4, 'employee', '普通员工', '本人数据', 'self', 'active', '2026-09-01 09:00:00');

INSERT INTO sys_user_roles (id, user_id, role_id) VALUES
(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4);

INSERT INTO sys_menus (id, parent_id, name, path, icon, permission_code, type, hidden, sort, status, created_at) VALUES
(1, NULL, '智能工作台', '/dashboard', 'home', 'dashboard:view', 'menu', 0, 1, 'active', '2026-09-01 09:00:00'),
(2, NULL, '简历智能筛选', '/resumes', 'doc', 'resume:view', 'menu', 0, 2, 'active', '2026-09-01 09:00:00'),
(3, NULL, '智能测评', '/exams', 'edit', 'exam:view', 'menu', 0, 3, 'active', '2026-09-01 09:00:00'),
(4, NULL, '岗位匹配', '/matching', 'match', 'match:view', 'menu', 0, 4, 'active', '2026-09-01 09:00:00'),
(5, NULL, '培训成长', '/training', 'book', 'train:view', 'menu', 0, 5, 'active', '2026-09-01 09:00:00'),
(6, NULL, '数据决策', '/decision', 'chart', 'decision:view', 'menu', 0, 6, 'active', '2026-09-01 09:00:00'),
(7, NULL, '知识库', '/kb', 'kb', 'kb:view', 'menu', 0, 7, 'active', '2026-09-01 09:00:00'),
(8, NULL, 'Agent编排', '/agent', 'bot', 'agent:view', 'menu', 0, 8, 'active', '2026-09-01 09:00:00'),
(9, NULL, '系统管理', '/system', 'setting', 'sys:view', 'menu', 0, 9, 'active', '2026-09-01 09:00:00');

INSERT INTO sys_role_permissions (id, role_id, menu_id, action, data_scope) VALUES
(1, 1, NULL, 'view', 'all'), (2, 1, NULL, 'create', 'all'), (3, 1, NULL, 'edit', 'all'), (4, 1, NULL, 'delete', 'all'), (5, 1, NULL, 'export', 'all'),
(6, 2, 2, 'view', 'dept'), (7, 2, 2, 'export', 'dept'),
(8, 3, 4, 'view', 'dept'),
(9, 4, 1, 'view', 'self'), (10, 4, 7, 'view', 'self');

-- ---------------- 岗位字典 / 岗位条件 ----------------
INSERT INTO positions (id, name) VALUES
(1, '高级算法工程师'), (2, 'AI 产品经理'), (3, '前端工程师'), (4, '数据工程师');

INSERT INTO job_profiles (id, name, prompt, conditions, score, score_rules, passing_threshold, status) VALUES
(3, '高级算法工程师(AI平台部)', '评估候选人算法与工程能力',
  '[{"key":"学历","op":">=","value":"硕士"},{"key":"技能","op":"contains","value":"PyTorch"},{"key":"工作年限","op":">=","value":3}]',
  0.0, '{"weights":{"education":0.3,"skills":0.4,"experience":0.3}}', 70, 'active'),
(2, 'AI 产品经理', '评估产品与业务理解',
  '[{"key":"技能","op":"contains","value":"需求分析"},{"key":"工作年限","op":">=","value":2}]',
  0.0, '{"weights":{"skills":0.5,"experience":0.5}}', 65, 'active');

-- ---------------- 候选人 (推断列：id,name,phone,email,position,status,created_at) ----------------
INSERT INTO candidates (id, name, phone, email, position, status, created_at) VALUES
(1, '陈宇', '13900000001', 'chenyu@demo.com', '高级算法工程师', 'active', '2026-09-10 10:00:00'),
(2, '王峰', '13900000002', 'wangfeng@demo.com', 'AI 产品经理', 'active', '2026-09-10 10:00:00'),
(3, '李娜', '13900000003', 'lina@demo.com', '前端工程师', 'active', '2026-09-10 10:00:00');

-- ---------------- 简历解析域 ----------------
INSERT INTO resume_files (id, filename, object_key, status, content_type, size_bytes, attachment_url, project_demand_id, job_profile_id, project_name, position, source_path) VALUES
(1, '陈宇_算法.pdf', 'resumes/chenyu.pdf', 'completed', 'application/pdf', 204800, 'https://minio.demo/resumes/chenyu.pdf', 12, 3, 'AI平台建设项目', '高级算法工程师', '/data/inbox/chenyu.pdf'),
(2, '王峰_产品.pdf', 'resumes/wangfeng.pdf', 'completed', 'application/pdf', 180000, 'https://minio.demo/resumes/wangfeng.pdf', 12, 2, 'AI平台建设项目', 'AI 产品经理', '/data/inbox/wangfeng.pdf');

INSERT INTO parse_tasks (id, resume_id, status, priority, attempts, error_message) VALUES
(1, 1, 'completed', 0, 1, NULL), (2, 2, 'completed', 0, 1, NULL);

INSERT INTO parsed_resumes (id, resume_id, project_demand_id, job_profile_id, name, phone, email, gender, age, education, major, skills, years_experience, strengths, attachment_url, photo_object_key, photo_url, resume_content, raw_json) VALUES
(1, 1, 12, 3, '陈宇', '13900000001', 'chenyu@demo.com', '男', 28, '硕士', '计算机科学',
  '["Python","PyTorch","NLP","分布式"]', 5, '大模型训练与推理优化经验丰富',
  'https://minio.demo/resumes/chenyu.pdf', 'photos/chenyu.jpg', 'https://minio.demo/photos/chenyu.jpg',
  '5年算法经验，主导推荐系统与大模型微调...',
  '{"name":"陈宇","education":"硕士","skills":["Python","PyTorch","NLP","分布式"],"years":5}'),
(2, 2, 12, 2, '王峰', '13900000002', 'wangfeng@demo.com', '男', 30, '本科', '信息管理',
  '["需求分析","项目管理","Axure"]', 6, 'B端产品规划与落地能力强',
  'https://minio.demo/resumes/wangfeng.pdf', 'photos/wangfeng.jpg', 'https://minio.demo/photos/wangfeng.jpg',
  '6年产品经验，负责AI平台产品设计...',
  '{"name":"王峰","education":"本科","skills":["需求分析","项目管理","Axure"],"years":6}');

-- ---------------- 匹配域 ----------------
INSERT INTO match_results (id, parsed_resume_id, job_profile_id, condition_detail, total_score, passed) VALUES
(1, 1, 3, '[{"key":"学历","ok":true},{"key":"技能","ok":true},{"key":"工作年限","ok":true}]', 88, 1),
(2, 2, 2, '[{"key":"技能","ok":true},{"key":"工作年限","ok":true}]', 79, 1);

INSERT INTO match_lists (id, resume_file_id, parsed_resume_id, job_profile_id, job_profile_name, attachment_url, photo_url, name, phone, email, gender, age, education, major, skills, years_experience, strengths, total_score, passing_threshold, passed, reason, candidate_id) VALUES
(1, 1, 1, 3, '高级算法工程师(AI平台部)', 'https://minio.demo/resumes/chenyu.pdf', 'https://minio.demo/photos/chenyu.jpg',
  '陈宇', '13900000001', 'chenyu@demo.com', '男', 28, '硕士', '计算机科学',
  '["Python","PyTorch","NLP","分布式"]', 5, '大模型训练与推理优化经验丰富', 88, 70, 1,
  '学历硕士、技能含PyTorch、工作年限5年，三项条件均满足，匹配度88分。', 1),
(2, 2, 2, 2, 'AI 产品经理', 'https://minio.demo/resumes/wangfeng.pdf', 'https://minio.demo/photos/wangfeng.jpg',
  '王峰', '13900000002', 'wangfeng@demo.com', '男', 30, '本科', '信息管理',
  '["需求分析","项目管理","Axure"]', 6, 'B端产品规划与落地能力强', 79, 65, 1,
  '技能含需求分析、工作年限6年，匹配度79分。', 2);

-- ---------------- 人才画像域 ----------------
INSERT INTO talent_tags (id, name, description, category, status) VALUES
(1, '大模型', '大模型相关能力', '技术', 'active'),
(2, '项目管理', '项目管理能力', '通用', 'active'),
(3, '沟通', '沟通表达', '通用', 'active');

INSERT INTO talent_profiles (id, candidate_id, candidate_name, position, project_group_id, project_id, project_group_name, project_name, profile_title, summary, strengths, weaknesses, abilities, dimensions, tag_ids, tag_quantify, data_sources, recommendation, status) VALUES
(1, 1, '陈宇', '高级算法工程师', NULL, NULL, '', 'AI平台建设项目', '算法骨干画像',
  '具备扎实的大模型训练与工程能力', '["大模型训练","推理优化"]', '["前端较弱"]',
  '{"算法":88,"工程":80,"沟通":70}', '["算法","工程","沟通"]', '[1]', '{"1":0.9}',
  '["resume","exam"]', '建议承担核心模型训练任务并补强前端协作。', 'active');

-- ---------------- 测评域 ----------------
INSERT INTO question_banks (id, name, description, total_questions, status) VALUES
(1, '算法基础题库', '覆盖数据结构与算法', 3, 'active');

INSERT INTO questions (id, bank_id, serial_no, question_type, content, options, answer, score, scoring_standard, analysis, knowledge_point, knowledge_category, knowledge_base_category, difficulty, subjective, operator, status) VALUES
(1, 1, 'Q001', 'single_choice', '时间复杂度 O(n log n) 的典型排序是？',
  '["冒泡排序","快速排序","选择排序","插入排序"]', '快速排序', 20, '选对得分', '快排平均O(nlogn)',
  '排序算法', '算法', '算法', 'medium', 0, 'admin', 'active'),
(2, 1, 'Q002', 'multi_choice', '以下哪些是深度学习框架？',
  '["PyTorch","TensorFlow","MySQL","Redis"]', 'PyTorch,TensorFlow', 20, '全对得分', 'PyTorch/TF为深度学习框架',
  '深度学习', '算法', '算法', 'easy', 0, 'admin', 'active'),
(3, 1, 'Q003', 'essay', '简述 Transformer 注意力机制。',
  '[]', '要点：Q/K/V、缩放点积、多头', 60, '按要点给分', '注意力的核心计算',
  'Transformer', '算法', '算法', 'hard', 1, 'admin', 'active');

INSERT INTO exams (id, name, category, description, bank_ids, question_ids, total_questions, total_score, pass_score, start_time, end_time, duration_minutes, status) VALUES
(1, '算法工程师内测', '内测', '考察算法基础', '[1]', '[1,2,3]', 3, 100, 60,
  '2026-09-20 09:00:00', '2026-09-30 18:00:00', 60, 'published');

INSERT INTO exam_submissions (id, exam_id, candidate_name, answers, score, max_score, pass_score, result, recommendation, detail) VALUES
(1, 1, '陈宇', '[{"question_id":1,"answer":"快速排序"},{"question_id":2,"answer":"PyTorch,TensorFlow"},{"question_id":3,"answer":"Q/K/V缩放点积多头"}]',
  92, 100, 60, 'passed', '算法基础扎实，建议进入下一轮。',
  '[{"question_id":1,"score":20},{"question_id":2,"score":20},{"question_id":3,"score":52}]');

INSERT INTO wrong_questions (id, exam_id, submission_id, question_id, bank_id, candidate_name, content, question_type, user_answer, standard_answer, analysis, score, max_score, status) VALUES
(1, 1, 1, 3, 1, '陈宇', '简述 Transformer 注意力机制。', 'essay', 'Q/K/V缩放点积多头', '要点：Q/K/V、缩放点积、多头',
  '注意力的核心计算', 52, 60, 'active');

INSERT INTO review_plans (id, wrong_question_id, question_id, candidate_name, content, question_type, review_time, reminder, status) VALUES
(1, 1, 3, '陈宇', '简述 Transformer 注意力机制。', 'essay', '2026-09-28 10:00:00', 1, 'scheduled');

-- ---------------- 培训域 ----------------
INSERT INTO training_courses (id, name, description, category, duration_hours, difficulty, instructor, content, status) VALUES
(1, '大模型微调实战', '从数据到部署的全流程', '算法', 4, 'hard', '李工', '覆盖SFT/RLHF与推理优化', 'active'),
(2, '产品需求分析方法', 'B端需求拆解', '产品', 2, 'medium', '王经理', '需求池管理与优先级', 'active');

INSERT INTO course_attachments (id, course_id, name, url, size, content_type, upload_failed, status) VALUES
(1, 1, '课件.pdf', 'https://minio.demo/courses/1.pdf', 102400, 'application/pdf', 0, 'active');

INSERT INTO prejob_plans (id, roster_id, candidate_id, candidate_name, position_name, plan_title, goal, total_weeks, phases, course_ids, mentor, status) VALUES
(1, NULL, 1, '陈宇', '高级算法工程师', '陈宇岗前培养方案', '补齐工程与协作短板',
  4, '[{"week":1,"goal":"环境熟悉"},{"week":2,"goal":"模型训练实战"},{"week":3,"goal":"推理优化"},{"week":4,"goal":"复盘"}]', '[1]', '李工', 'generated');

-- ---------------- 知识库域 ----------------
INSERT INTO knowledge_categories (id, name, description) VALUES
(1, '人事制度', '假期/薪酬/考勤制度'), (2, '技术规范', '研发规范与最佳实践');

INSERT INTO business_knowledge (id, category_id, category_name, title, filename, object_key, attachment_url, content_type, content_text, chunk_count, status, error_message, attempts, created_at) VALUES
(1, 1, '人事制度', '年假管理办法', 'leave.pdf', 'kb/leave.pdf', 'https://minio.demo/kb/leave.pdf', 'application/pdf',
  '员工累计工作满1年享受5天年假，满10年享受10天；年假按自然年清零。', 2, 'completed', NULL, 1, '2026-09-15 09:00:00');

INSERT INTO knowledge_chunks (id, knowledge_id, category_id, chunk_index, chunk_text, milvus_id, score) VALUES
(1, 1, 1, 0, '员工累计工作满1年享受5天年假。', 10001, NULL),
(2, 1, 1, 1, '年假按自然年清零，逾期作废。', 10002, NULL);

-- ---------------- 智能体 / 调度 / 模型 ----------------
INSERT INTO agent_registry (id, name, category, status, owner, endpoint, version, capabilities, description, success_rate, avg_latency_ms, registered_by, retired_at) VALUES
(1, '档案解析Agent', 'resume', 'active', 'admin', '/api/agent-management/1', '1.0.0',
  '["parse","extract"]', '简历解析与字段抽取', 0.99, 1200, 'admin', NULL),
(2, '岗位匹配Agent', 'matching', 'active', 'admin', '/api/agent-management/2', '1.0.0',
  '["match","score"]', '岗位-人才匹配评分', 0.95, 800, 'admin', NULL);

INSERT INTO agent_run_logs (id, agent_id, agent_name, task_name, status, latency_ms, message, started_at) VALUES
(1, 1, '档案解析Agent', 'parse:chenyu', 'success', 1150, '解析完成', '2026-09-20 10:00:00');

INSERT INTO task_schedule_rules (id, name, digital_worker, agent_name, trigger_rule, schedule_type, schedule_cron, interval_minutes, priority, status, retry_policy, owner, description, last_run_at, next_run_at, run_count, success_count, failure_count, config) VALUES
(1, '每日简历解析', '数字员工-小艾', '档案解析Agent', '每天凌晨拉取收件箱', 'cron', '0 2 * * *', 60, 5, 'enabled',
  '{"max_retry":3}', 'admin', '定时解析新增简历', '2026-09-27 02:00:00', '2026-09-28 02:00:00', 27, 26, 1,
  '{"source":"/data/inbox"}');

INSERT INTO model_providers (id, name, provider_type, base_url, api_key, model, description, status) VALUES
(1, '本地DeepSeek', 'deepseek', 'https://api.deepseek.com/v1', 'sk-test-placeholder', 'deepseek-chat', '主用推理模型', 'active'),
(2, '本地Ollama', 'ollama', 'http://localhost:11434', '', 'qwen2.5', '内网轻量模型', 'active');

-- ---------------- 项目需求 (§9 已知列) ----------------
INSERT INTO project_demands (id, project_name, project_group, position, headcount, expected_start_date, priority, remark, status) VALUES
(12, 'AI平台建设项目', 'AI平台群', '高级算法工程师', 2, '2026-10-01', 'high', '核心模型研发', 'active');

SET FOREIGN_KEY_CHECKS = 1;
