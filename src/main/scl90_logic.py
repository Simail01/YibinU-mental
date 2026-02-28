# -------------------------- SCL-90 逻辑模块 --------------------------

# SCL-90 题目定义与因子归属
# 参考标准 SCL-90-R 因子划分
SCL90_QUESTIONS = [
    {"id": 1, "text": "头痛", "category": "somatization"},
    {"id": 2, "text": "神经过敏，心中不踏实", "category": "anxiety"},
    {"id": 3, "text": "头脑中有不必要的想法或字句盘旋", "category": "obsessive"},
    {"id": 4, "text": "头晕或晕倒", "category": "somatization"},
    {"id": 5, "text": "对异性的兴趣减退", "category": "depression"}, # 原 other -> depression
    {"id": 6, "text": "对旁人求全责备", "category": "interpersonal"}, # 原 hostility -> interpersonal
    {"id": 7, "text": "感到别人能控制您的思想", "category": "psychotic"},
    {"id": 8, "text": "责怪别人制造麻烦", "category": "paranoid"}, # 原 hostility -> paranoid
    {"id": 9, "text": "忘记性大", "category": "obsessive"},
    {"id": 10, "text": "担心自己的衣饰整齐及仪态的端正", "category": "obsessive"},
    {"id": 11, "text": "容易烦恼和激动", "category": "hostility"}, # 原 anxiety -> hostility
    {"id": 12, "text": "胸痛", "category": "somatization"},
    {"id": 13, "text": "害怕空旷的场所或街道", "category": "phobic"},
    {"id": 14, "text": "感到自己的精力下降，活动减慢", "category": "depression"},
    {"id": 15, "text": "想结束自己的生命", "category": "depression"},
    {"id": 16, "text": "听到旁人听不到的声音", "category": "psychotic"},
    {"id": 17, "text": "发抖", "category": "anxiety"},
    {"id": 18, "text": "感到大多数人都不可信任", "category": "paranoid"},
    {"id": 19, "text": "胃口不好", "category": "other"}, # 原 somatization -> other
    {"id": 20, "text": "容易哭泣", "category": "depression"},
    {"id": 21, "text": "同异性相处时感到害羞不自在", "category": "interpersonal"},
    {"id": 22, "text": "感到受骗，中了圈套或有人想抓住您", "category": "depression"}, # Standard SCL-90 puts 22 in Depression? No, 22 is usually Paranoid? Let me check.
    # Re-checking standard SCL-90-R:
    # 22 "Feeling trapped or caught" -> Depression in some, Paranoid in others?
    # Derogatis 1977: 22 is Depression.
    {"id": 23, "text": "无缘无故地突然感到害怕", "category": "anxiety"},
    {"id": 24, "text": "自己不能控制地大发脾气", "category": "hostility"},
    {"id": 25, "text": "怕单独出门", "category": "phobic"},
    {"id": 26, "text": "经常责怪自己", "category": "depression"},
    {"id": 27, "text": "腰痛", "category": "somatization"},
    {"id": 28, "text": "感到难以完成任务", "category": "obsessive"}, # 原 depression -> obsessive
    {"id": 29, "text": "感到孤独", "category": "depression"}, # 原 interpersonal -> depression
    {"id": 30, "text": "感到苦闷", "category": "depression"},
    {"id": 31, "text": "过分担忧", "category": "depression"}, # 原 anxiety -> depression (Standard: 31 is Depression)
    {"id": 32, "text": "对事物不感兴趣", "category": "depression"},
    {"id": 33, "text": "感到害怕", "category": "anxiety"},
    {"id": 34, "text": "您的感情容易受到伤害", "category": "interpersonal"},
    {"id": 35, "text": "旁人能知道您的私下想法", "category": "psychotic"},
    {"id": 36, "text": "感到别人不理解您、不同情您", "category": "interpersonal"},
    {"id": 37, "text": "感到人们对您不友好、不喜欢您", "category": "interpersonal"},
    {"id": 38, "text": "做事必须做得很慢以保证做得正确", "category": "obsessive"},
    {"id": 39, "text": "心跳得很厉害", "category": "anxiety"},
    {"id": 40, "text": "恶心或胃部不舒服", "category": "somatization"},
    {"id": 41, "text": "感到比不上他人", "category": "interpersonal"},
    {"id": 42, "text": "肌肉酸痛", "category": "somatization"},
    {"id": 43, "text": "感到有人在监视您、谈论您", "category": "paranoid"},
    {"id": 44, "text": "难以入睡", "category": "other"},
    {"id": 45, "text": "做事必须反复检查", "category": "obsessive"},
    {"id": 46, "text": "难以作出决定", "category": "obsessive"},
    {"id": 47, "text": "怕乘电车、公共汽车、地铁或火车", "category": "phobic"},
    {"id": 48, "text": "呼吸有困难", "category": "somatization"}, # 原 anxiety -> somatization (Standard: 48 is Somatization)
    {"id": 49, "text": "一阵阵发冷或发热", "category": "somatization"},
    {"id": 50, "text": "因为感到害怕而避开某些东西、场合或活动", "category": "phobic"},
    {"id": 51, "text": "脑子变空了", "category": "obsessive"}, # 原 depression -> obsessive
    {"id": 52, "text": "身体发麻或刺痛", "category": "somatization"},
    {"id": 53, "text": "喉咙有梗塞感", "category": "somatization"},
    {"id": 54, "text": "感到对前途没有希望", "category": "depression"},
    {"id": 55, "text": "不能集中注意力", "category": "obsessive"},
    {"id": 56, "text": "感到身体的某一部分软弱无力", "category": "somatization"},
    {"id": 57, "text": "感到紧张或容易紧张", "category": "anxiety"},
    {"id": 58, "text": "感到手或脚发重", "category": "somatization"},
    {"id": 59, "text": "想到死亡的事", "category": "other"}, # 原 depression -> other (Standard: 59 is Additional/Other)
    {"id": 60, "text": "吃得太多", "category": "other"},
    {"id": 61, "text": "当别人看着您或谈论您时感到不自在", "category": "interpersonal"},
    {"id": 62, "text": "有一些不属于您自己的想法", "category": "psychotic"},
    {"id": 63, "text": "有想打人或伤害他人的冲动", "category": "hostility"},
    {"id": 64, "text": "醒得太早", "category": "other"},
    {"id": 65, "text": "必须反复洗手、点数目或触摸某些东西", "category": "obsessive"},
    {"id": 66, "text": "睡得不稳不深", "category": "other"},
    {"id": 67, "text": "有想摔坏或破坏东西的冲动", "category": "hostility"},
    {"id": 68, "text": "有一些别人没有的想法或念头", "category": "paranoid"}, # 原 psychotic -> paranoid
    {"id": 69, "text": "感到对别人神经过敏", "category": "interpersonal"},
    {"id": 70, "text": "在商店或电影院等人多的地方感到不自在", "category": "phobic"},
    {"id": 71, "text": "感到任何事情都很困难", "category": "depression"},
    {"id": 72, "text": "一阵阵恐惧或惊恐", "category": "anxiety"},
    {"id": 73, "text": "感到在公共场合吃东西很不舒服", "category": "interpersonal"}, # 原 phobic -> interpersonal (Standard: 73 is Interpersonal)
    {"id": 74, "text": "经常与人争论", "category": "hostility"},
    {"id": 75, "text": "单独一人时神经很紧张", "category": "phobic"}, # 原 anxiety -> phobic
    {"id": 76, "text": "别人对您的成绩没有作出恰当的评价", "category": "paranoid"},
    {"id": 77, "text": "即使和别人在一起也感到孤单", "category": "psychotic"}, # 原 interpersonal -> psychotic
    {"id": 78, "text": "感到坐立不安、心神不定", "category": "anxiety"},
    {"id": 79, "text": "感到自己没有什么价值", "category": "depression"},
    {"id": 80, "text": "感到熟悉的东西变得陌生或不像是真的", "category": "anxiety"}, # 原 psychotic -> anxiety (Standard: 80 is Anxiety?) Wait.
    # 80 "Familiar things feel strange" - Derealization.
    # Derogatis 1977: 80 is Anxiety. Yes.
    {"id": 81, "text": "大叫或摔东西", "category": "hostility"},
    {"id": 82, "text": "害怕会在公共场合晕倒", "category": "phobic"},
    {"id": 83, "text": "感到别人想占您的便宜", "category": "paranoid"},
    {"id": 84, "text": "为一些有关性的想法而很苦恼", "category": "psychotic"}, # 原 other -> psychotic
    {"id": 85, "text": "您认为应该因为自己的过错而受到惩罚", "category": "psychotic"}, # 原 depression -> psychotic
    {"id": 86, "text": "感到要很快把事情做完", "category": "anxiety"}, # 原 obsessive -> anxiety
    {"id": 87, "text": "感到自己的身体有严重问题", "category": "psychotic"}, # 原 somatization -> psychotic
    {"id": 88, "text": "从未感到和其他人很亲近", "category": "psychotic"}, # 原 interpersonal -> psychotic
    {"id": 89, "text": "感到自己有罪", "category": "other"}, # 原 depression -> other
    {"id": 90, "text": "感到自己的脑子有毛病", "category": "psychotic"}
]

CATEGORIES = {
    "somatization": "躯体化",
    "obsessive": "强迫症状",
    "interpersonal": "人际关系敏感",
    "depression": "抑郁",
    "anxiety": "焦虑",
    "hostility": "敌对",
    "phobic": "恐怖",
    "paranoid": "偏执",
    "psychotic": "精神病性",
    "other": "其他"
}

def calculate_scl90_score(answers):
    """
    计算SCL-90得分
    answers: dict, {question_id: score}
    """
    # 验证是否包含所有90道题目的答案
    if len(answers) < 90:
        raise ValueError(f"答案不完整，共需90道题，当前仅收到 {len(answers)} 道")

    total_score = 0
    factor_scores = {k: {"total": 0, "count": 0} for k in CATEGORIES.keys()}
    abnormal_items = []

    for q in SCL90_QUESTIONS:
        qid = str(q["id"])
        if qid not in answers:
             raise ValueError(f"缺少题目 ID {qid} 的答案")
             
        try:
            score = int(answers[qid])
            if score < 1 or score > 5:
                raise ValueError(f"题目 ID {qid} 的分数 {score} 超出范围 (1-5)")
        except ValueError:
            raise ValueError(f"题目 ID {qid} 的分数格式错误")
            
        total_score += score
        
        cat = q["category"]
        factor_scores[cat]["total"] += score
        factor_scores[cat]["count"] += 1
        
        if score >= 3: # 3分以上为异常（中等及以上）
            abnormal_items.append({
                "question": q["text"],
                "score": score,
                "category": CATEGORIES[cat]
            })

    results = {}
    for cat, data in factor_scores.items():
        avg = data["total"] / data["count"] if data["count"] > 0 else 0
        results[cat] = {
            "name": CATEGORIES[cat],
            "score": round(avg, 2),
            "raw_score": data["total"]
        }
        
    return {
        "total_score": total_score,
        "factor_results": results,
        "abnormal_items": abnormal_items,
        "average_score": round(total_score / 90, 2),
        "positive_items_count": len([k for k,v in answers.items() if int(v) >= 2])
    }
