<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 暂时不想动数据库只要详细的 md 方案文档

```markdown
# UniThrive / Mindful Campus Demo 技术规划文档（无数据库实现版）

> 目标：在现有 Emergent Agent Landing Page 前端基础上，为 UniThrive / Mindful Campus 做一个“可讲解、可扩展”的后端与批处理（batch）方案，只交付架构与步骤，不要求你现在就落地数据库或模型代码。前端只需要调用少量 REST API 即可完成 demo 演示。 [file:4]

---

## 1. 产品及 Demo 场景概述

### 1.1 产品愿景（对齐 Pitch Deck）

UniThrive 想解决的问题：高校学生并不缺课程、活动和心理资源，但缺少一个把“学业、身心健康、机会”整合到一起的**个性化智能系统**。 [file:4]  

Pitch Deck 中的关键体验：  
- 三个 **Activity Rings（三环仪表盘）**：Mental / Psychological / Physical，分别跟踪学习进展、心理状态和身体生活。 [file:4]  
- 学生通过**匿名或实名 check-in** 汇报状态，系统用 AI 分析，给出“当下建议 + 后续资源推荐”。 [file:4]  
- 每周生成 **Weekly Summary + Spotlight Opportunity + Weekly Achievement**。 [file:4]  
- 当系统检测到**持续高压 / 风险**，会触发升级路径，引导到学校现有辅导资源。 [file:4]  

### 1.2 Demo 要展示的完整故事线

在 Demo 中，我们希望做到：  
1. 用户（Maya）在 landing page 上登录/进入，完成每日 check-in（情绪、压力、睡眠、运动等简单问卷）。 [file:4]  
2. 后端记录这些数据，通过 **批处理任务** 每隔一段时间计算：  
   - 三环当天/本周得分；  
   - 过去一周 Weekly Summary + 一个 Spotlight 机会 + 一个 Achievement 徽章；  
   - 如果检测到风险（例如压力高、情绪持续降低），生成 Alert。 [file:4]  
3. 用户刷新 Dashboard 后，可以看到：  
   - 三环仪表盘（环形进度条 + 得分）；  
   - Weekly Summary 文本；  
   - 推荐卡片（活动/工作坊/心理资源等）；  
   - 如有需要，弹出“你似乎有点压力高，要不要看看学校提供的资源？”提示。 [file:4]  

---

## 2. 总体技术架构（不落地 DB，仅说明层次）

### 2.1 组件划分

- **前端（已存在）**：Emergent Agent 生成的 landing page，增加少量 JS 调用 REST API（登录、check-in、获取 dashboard）。  
- **API 层**：FastAPI + Pydantic（与你 Unithrive backend 规划一致，方便之后重用栈）。 [file:2]  
- **领域服务层（Services）**：处理业务逻辑（check-in 写入、dashboard 拼装、从缓存/内存结构读取周总结与推荐）。  
- **批处理（Batch Job）**：定期运行的 Python 脚本，  
  - 从**数据源（可先模拟数据结构内存/JSON 文件）**读取过去 7 天记录，  
  - 计算三环得分、Weekly Summary、推荐与风险，  
  - 把结果写入缓存或 JSON 文件，供 API 直接读取。  
- **AI / 决策模块（轻量版）**：基于 `neural_network_plan_33` 的思想，保留“多模块输入 + 核心评分模块 + 排名”的接口结构，先用规则+线性打分实现；将来可以无缝替换成 Transformer + ListMLE 等真正模型。 [file:3]  

> 重要：本版本**不要求**真实数据库，可以通过 “in-memory + JSON 文件” 模拟持久层，只要接口设计好，你后续换成 SQLite / PostgreSQL / Supabase 时不需要动上层逻辑。  

### 2.2 分层示意（逻辑视图）

- `frontend (Emergent Agent landing page)`  
  - 与 `/api/checkins`, `/api/dashboard`, `/api/weekly-summary` 通讯。  

- `FastAPI app`  
  - `routers`: 定义 HTTP 路由；  
  - `schemas`: 定义请求/响应 Pydantic 模型； [file:2]  
  - `services`: 聚合业务逻辑（调用“存储接口 + AI / 决策模块 + 缓存读写”）。  

- `storage (abstract)`  
  - `load_checkins(user_id, date_range)`  
  - `save_checkin(record)`  
  - `load_aggregates(user_id, week)`  
  - `save_aggregates(...)`  
  - 初期实现：基于 JSON 文件或 Python 字典（程序运行时驻留内存）；后期替换成 ORM + 真实数据库。  

- `batch_job`  
  - 使用 storage 抽象读写数据；  
  - 调用 `decision_engine` 生成 summary、推荐、风险。  

- `decision_engine`（对应 neural_network_plan 的“Cognitive Core + Neural Core”理念） [file:3]  
  - `feature_extractor`：从原始 check-in / 活动数据中提取特征（平均分、趋势、方差等）；  
  - `multi_perspective_modules`：仿照 Six Thinking Hats / MBTI 多视角，对 solution / 机会做多维度评分； [file:3]  
  - `core_ranker`：综合多视角的结果，输出最终排序分数列表。  

---

## 3. 数据与领域模型（不绑定具体 DB）

此处只定义**概念模型**与字段，实际存储可以是 JSON / 内存结构；后期落地到数据库时可以直接映射。  

### 3.1 用户与画像

#### User（用户）

- `id: string` – 用户唯一标识，可用 UUID 或匿名 ID。  
- `email: string | null` – 匿名模式下可为空。 [file:4]  
- `display_name: string` – 用于前端展示，如 “Maya”。 [file:4]  
- `created_at: datetime`  

#### Profile（个人画像）

- `user_id: string`  
- `major: string` – 专业，如 “Physics / Green Energy”。  
- `year: int` – 年级。  
- `campus: string` – 学校/校区，便于推荐本校资源。 [file:4]  
- `goals: list[string]` – 个人目标，如 “提高 GPA”、“改善睡眠”等。  

### 3.2 Check-in 与日常活动

#### Checkin（每日状态）

- `id: string`  
- `user_id: string`  
- `timestamp: datetime`  
- `mood_score: int (1–5)`  
- `stress_score: int (1–5)`  
- `sleep_hours: float`  
- `exercise_minutes: int`  
- `social_interactions: int` – 当天与同学/朋友交互次数（自己感知）；  
- `notes_text: string | null` – 自由文本。  

#### Activity（活动记录，可选）

对 Pitch Deck 里的 “Course Engagement、Skill Development、Exercise Tracker、Social Events” 做抽象。 [file:4]  

- `id: string`  
- `user_id: string`  
- `date: date`  
- `type: string` – `"course" | "skill" | "exercise" | "social" | "event"`； [file:4]  
- `duration_minutes: int`  
- `tag_ring: string` – `"mental" | "psychological" | "physical"`，标记主要贡献到哪一环。 [file:4]  

### 3.3 三环与周总结

#### DailyRingScore（日三环得分）

由 batch 根据当天所有 check-in + activity 计算得出。 [file:4]  

- `user_id: string`  
- `date: date`  
- `mental_score: float` – 反映课程参与度、技能发展和学业相关的完成度。 [file:4]  
- `psychological_score: float` – 反映压力水平、情绪、正念/冥想次数等。 [file:4]  
- `physical_score: float` – 反映运动时间、睡眠质量、作息平衡。 [file:4]  

#### WeeklySummary（周总结）

- `id: string`  
- `user_id: string`  
- `week_start: date`  
- `week_end: date`  
- `mental_summary: string` – 如 “你本周完成了 3 次课程相关任务，总时长 6 小时。” [file:4]  
- `psych_summary: string` – 如 “你记录了 4 次正念练习，压力在周中稍有升高。” [file:4]  
- `physical_summary: string` – 如 “你平均每天睡眠 6.5 小时，运动 3 次。” [file:4]  
- `spotlight_opportunity: string` – 推荐下周的重点机会（写作工作坊/瑜伽课/职业讲座等）。 [file:4]  
- `achievement_badge: string` – 如 “Balance Seeker”、“Stress Fighter”等游戏化勋章。 [file:4]  

### 3.4 风险预警与机会推荐

#### Alert（风险提示）

- `id: string`  
- `user_id: string`  
- `created_at: datetime`  
- `risk_level: string` – `"low" | "medium" | "high"`；  
- `reason: string` – “连续 5 天压力评分 ≥4 且情绪下降”；  
- `escalated_to_counselor: bool` – 是否已由学校辅导员接手。 [file:4]  

#### Opportunity（机会资源库）

- `id: string`  
- `title: string` – “Writing Workshop for Final Week”等； [file:4]  
- `type: string` – `"workshop" | "event" | "counselling" | "community"`； [file:4]  
- `tags: list[string]` – 如 `["stress", "exam", "sleep"]`；  
- `campus: string` – 学校/校区；  
- `start_time: datetime`  
- `end_time: datetime`  

#### Recommendation（推荐记录）

- `id: string`  
- `user_id: string`  
- `created_at: datetime`  
- `opportunity_id: string`  
- `ring_target: string` – 推荐主要帮助哪一环：`"mental" | "psychological" | "physical"`； [file:4]  
- `score: float` – 由决策引擎计算的综合得分； [file:3]  
- `explanation: string` – 人类可读解释，“你最近压力较高且缺乏运动，这个校内瑜伽课可以帮助你放松身心。” [file:4]  

---

## 4. API 设计（面向前端，无数据库实现细节）

### 4.1 身份与会话（极简）

> Demo 为主，可以只实现“假登录”（前端存一个 pseudo user_id），暂时不做完整 OAuth2 / JWT。  

- `POST /api/auth/mock-login`  
  - Request：`{ "email": "maya@example.com" }` 或空（匿名模式）；  
  - Response：`{ "user_id": "some-uuid-or-random-id", "is_anonymous": true/false }`。  

### 4.2 Check-in 与活动采集

- `POST /api/checkins`  
  - Request：  
    ```json
    {
      "user_id": "uuid",
      "mood_score": 3,
      "stress_score": 4,
      "sleep_hours": 6.5,
      "exercise_minutes": 30,
      "social_interactions": 2,
      "notes_text": "有点焦虑，但今天和朋友聊天稍微好了一点"
    }
    ```  
  - Response：`{"status": "ok"}`  

- `POST /api/activities`（可选）  
  - Request：  
    ```json
    {
      "user_id": "uuid",
      "date": "2026-03-03",
      "type": "course",
      "duration_minutes": 90,
      "tag_ring": "mental"
    }
    ```  

### 4.3 Dashboard & Weekly Summary

- `GET /api/dashboard/{user_id}`  
  - Response 示例：  
    ```json
    {
      "ring_scores": {
        "mental": 0.72,
        "psychological": 0.55,
        "physical": 0.63
      },
      "streak_days": 5,
      "unread_alerts": 1,
      "recommendation_preview": [
        {
          "id": 1,
          "title": "Exam Week Mindfulness Session",
          "ring_target": "psychological",
          "explanation": "你本周压力评分偏高，推荐你参加一次 30 分钟正念练习。"
        }
      ]
    }
    ``` [file:4]  

- `GET /api/weekly-summary/{user_id}`  
  - Response 示例：  
    ```json
    {
      "week_start": "2026-02-24",
      "week_end": "2026-03-02",
      "mental_summary": "你完成了 3 次课程任务，总学习时长约 8 小时。",
      "psych_summary": "你记录了 4 次正念练习，周中压力升高但周末略有缓解。",
      "physical_summary": "你平均每天睡眠 6.4 小时，完成了 2 次中等强度运动。",
      "spotlight_opportunity": "根据你的目标和压力趋势，推荐你报名下周的 Writing Workshop。",
      "achievement_badge": "Balance Seeker"
    }
    ``` [file:4]  

### 4.4 Alerts & Recommendations

- `GET /api/alerts/{user_id}`  
  - 返回最近 N 条风险提示，用于前端显示 “我们注意到你最近压力有点高”。 [file:4]  

- `GET /api/recommendations/{user_id}`  
  - 返回当前周的完整推荐列表，前端可以做卡片列表。 [file:3][file:4]  

---

## 5. 批处理（Batch Processing）详细设计

### 5.1 运行方式（无 DB 版本）

- 数据源：  
  - 可以是一个 `data/checkins.json`, `data/activities.json` 等文件；  
  - 或者是启动时载入到内存的 Python 结构，并在 batch 结束时回写 JSON。  
- 触发方式：  
  - 本地 Demo：手动 `python batch_job.py`；  
  - 或使用简单定时调度（如每 5 分钟跑一次，用 `while True + sleep(300)` 即可）。  

### 5.2 批任务的主要步骤

以“对所有在过去 7 天内出现过的用户”为单位：  

1. **拉取原始数据**  
   - 读取该用户过去 7 天的 checkins 与 activities。  
2. **计算日三环得分**  
   - 根据简单的规则函数，将原始指标映射为 [0,1] 的分数：  
     - mental：学习时长、课程/技能型 activity，目标：每周 X 小时为 1.0； [file:4]  
     - psychological：压力评分越低越好、正念/社交次数越多越好； [file:4]  
     - physical：运动分钟和睡眠时长接近健康目标区间时得分高。 [file:4]  
   - 计算每日 score，写入 `DailyRingScore`（在本版本中可以是 `aggregates/daily_{user_id}.json`）。  
3. **生成 Weekly Summary**  
   - 聚合一周的日得分和原始事件：  
     - mentally：统计课程/学习次数与总时长；  
     - psychologically：绘制压力/情绪趋势，用自然语言归纳 “压力在周中升高/周末下降”；  
     - physically：计算平均睡眠、运动符合多少天目标。 [file:4]  
   - 决定一个 Spotlight 机会：  
     - 如果 psychological 得分最低，则从 `Opportunity` 列表中挑选与压力/焦虑标签相关的活动； [file:4]  
     - 如果 physical 得分最低，则推荐运动类活动；  
     - 如果 mental 得分最低，则推荐学习/技能工作坊。  
   - 决定 Achievement 徽章：  
     - 如 “Balance Seeker”（三环都在 0.6 以上）； [file:4]  
     - “Comeback Kid”（前半周较低、后半周有明显提升）。  
   - 把结果写入 `aggregates/weekly_{user_id}.json` 或内存结构。  
4. **生成推荐（Recommendation）**  
   - 通过 `decision_engine`：  
     - 输入：  
       - 用户画像、目标；  
       - 一周的三环统计（均值、标准差、趋势斜率）；  
       - 候选 Opportunity 列表。 [file:3][file:4]  
     - 处理流程对齐 `neural_network_plan_33` 的设计：  
       - 多视角模块（例如 “效率视角”、“心理安全视角”、“身体恢复视角”），各自对机会打分； [file:3]  
       - 核心整合器（可理解为简化版 Transformer / attention），将多视角分数线性组合； [file:3]  
       - 排行模块（模拟 ListNet / ListMLE，按分数排序取前 K 条）。 [file:3]  
     - Demo 阶段可用简单线性权重实现：  
       - 如果 psychological 分最低，心理相关标签的机会在心理视角下加权更高，最终排序靠前。  
   - 写入 `aggregates/recommendations_{user_id}.json`。  
5. **评估风险并写入 Alert**  
   - 规则示例：  
     - 连续 5 天 stress_score ≥ 4；  
     - 或 7 天内 mood_score 总体呈持续下降趋势；  
     - 或 check-in 文本中出现 “suicidal”、“cannot cope” 等高危关键词（可后期用 NLP 模型）。 [file:4]  
   - 生成 Alert，对应 risk_level & reason。  

### 5.3 决策引擎模块结构（对齐 Neural Network Plan）

以模块接口形式保留未来升级空间，结合 `neural_network_plan_33` 的“多模块 + Transformer 核心”思想： [file:3]  

- `feature_extractor(user_week_data) -> FeatureVector`  
  - 输出如：  
    - `avg_mental`, `trend_mental`  
    - `avg_psych`, `trend_psych`  
    - `avg_physical`, `trend_physical`  
- `perspective_scorers`：  
  - `efficiency_perspective(feature, opportunity)` – 看这个机会对学业/时间管理的帮助； [file:3]  
  - `wellbeing_perspective(feature, opportunity)` – 看对心理健康的帮助； [file:3]  
  - `physical_perspective(feature, opportunity)` – 看对睡眠/运动/身体活力的帮助。 [file:3][file:4]  
- `core_ranker(perspective_scores) -> final_score`  
  - 将多视角分数整合成一个最终得分；  
  - 目前可用线性加权，之后替换为 Transformer + ranking loss（ListNet/ListMLE + AdamW）。 [file:3]  

---

## 6. 代码结构规划（目录与文件）

即使暂时不实现数据库，也建议按下面方式组织代码，方便后续直接填充：  

- `app/`  
  - `main.py` – FastAPI 入口，挂载路由。  
  - `routers/`  
    - `auth.py` – mock 登录路由。  
    - `checkins.py` – check-in、activities 相关路由。  
    - `dashboard.py` – dashboard、weekly summary、alerts、recommendations 路由。  
  - `schemas.py` – Pydantic 模型。 [file:2]  
  - `services/`  
    - `checkin_service.py` – 写入/读取 check-in 数据；  
    - `dashboard_service.py` – 汇总 Dashboard 响应；  
    - `summary_service.py` – 读取 batch 生成的 weekly summary 与推荐。  
  - `storage/`  
    - `memory_storage.py` – 用 Python dict/JSON 文件模拟持久化；  
    - 未来可以新增 `db_storage.py`，实现同样接口但使用数据库。  
  - `decision_engine/`  
    - `features.py` – 特征抽取； [file:3]  
    - `perspectives.py` – 多视角评分模块； [file:3]  
    - `ranker.py` – 核心打分与排序模块。 [file:3]  

- `batch_job.py` – 批处理主脚本，import `storage` 与 `decision_engine`。  
- `seed_data.py` – 人工生成学生/活动/机会等假数据，填满一周，用于演示。  

---

## 7. 人工数据（Fake Data）生成建议

### 7.1 学生与机会假数据

- 学生：  
  - Maya – 二年级、主修 Business + minor in Psychology； [file:4]  
  - Shadow – 物理 + Green Energy；  
  - Adrian – CS / Fintech。  

- 机会（Opportunity）：  
  - “Exam Week Mindfulness Group”（标签：`["stress", "exam", "mindfulness"]`）； [file:4]  
  - “Campus Yoga Session”（标签：`["exercise", "sleep"]`）；  
  - “Career CV Clinic”（标签：`["career", "skill", "confidence"]`）； [file:4]  
  - “Peer Support Circle”（标签：`["loneliness", "social"]`）。 [file:4]  

### 7.2 行为与 check-in 假数据模式

根据 Pitch Deck 中提到的“压力、孤独、运动不足”的统计趋势，构造有故事线的假数据： [file:4]  

- Maya：  
  - 考试周：压力高（4–5），睡眠偏少（5–6 小时），运动少，社交少；  
  - 周末：压力下降一点，补觉和运动。  
- Shadow：  
  - 学业、项目多，mental 得分偏高但 physical 偏低（长时间久坐）。  
- Adrian：  
  - 活动多、社交高，但心理波动较大（情绪起伏）。  

用 `seed_data.py` 随机生成带趋势的数据，可以更好地演示 Weekly Summary 与推荐。  

---

## 8. 与未来数据库 & 真·模型接轨的路径

虽然本 md 方案不实现数据库，但已经为以后扩展留了明确路径：  

1. **Storage 抽象接口稳定后**，只需新增数据库实现，不需要改服务层和 API：  
   - 把目前 JSON / dict 替换为 SQLAlchemy + PostgreSQL / Supabase，字段映射对应本文件中的“概念模型”。 [file:2]  
2. **Decision Engine 升级**：  
   - 目前是规则 + 线性权重；  
   - 未来可以根据 `neural_network_plan_33`：  
     - 使用 Transformers 库（Python 3.11 + PyTorch + FastAPI 等栈已在 plan 中建议）， [file:3]  
     - 加入多值逻辑、MBTI 认知功能等输入，丰富特征空间； [file:3]  
     - 采用 ranking loss（ListNet / ListMLE）和 AdamW 优化训练一个专门排序模型。 [file:3]  

---

## 9. 下一步落地建议（按优先级）

1. 在本 md 基础上，新建 `docs/demo_plan.md`，复制此内容作为项目官方设计文档。  
2. 创建基础 FastAPI 项目，仅实现：  
   - `POST /api/checkins`（写入内存或 JSON）；  
   - `GET /api/dashboard/{user_id}`（返回固定假数据）。  
3. 用 `seed_data.py` 构造一周的假数据，手动运行 `batch_job.py` 产生 Weekly Summary 与推荐 JSON。  
4. 在 landing page 中，用少量 JS 调 API，渲染：  
   - 三个环形进度条（可以根据 ring_scores 映射到百分比）；  
   - 一个 Weekly Summary 卡片；  
   - 一条 Spotlight Opportunity 卡片。  

到这一步，你已经有一个“看起来完整”的 UniThrive / Mindful Campus demo 流程，可以在 hackathon / pitch 中演示 end-to-end 的体验，而不需要真正上线数据库或复杂模型。  

```markdown
```

<span style="display:none">[^1][^2][^3][^4]</span>

<div align="center">⁂</div>

[^1]: The-Linux-Programming-Interface.pdf

[^2]: Unithrive-Backend-Brainstorming-and-plans.pdf

[^3]: neural_network_plan_33.md

[^4]: ZC10_A-STARS_Final-Pitch-Deck.pdf

