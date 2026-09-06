
import re
import streamlit as st

st.set_page_config(
    page_title="문장 성분 서·논술형 실전 연습",
    page_icon="✍️",
    layout="wide",
)

# -----------------------------
# 기본 설정 / 스타일
# -----------------------------
st.markdown("""
<style>
    .block-container {max-width: 980px; padding-top: 1.6rem; padding-bottom: 3rem;}
    .hero {
        padding: 1.5rem 1.6rem;
        border-radius: 18px;
        background: #f7f9fc;
        border: 1px solid #e7ebf0;
        margin-bottom: 1rem;
    }
    .source-box {
        background: #eef6ff;
        border: 1px solid #cfe5ff;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin: .6rem 0 1rem 0;
    }
    .condition-box {
        background: #f4f4f4;
        border: 1px solid #dedede;
        border-radius: 12px;
        padding: .9rem 1.1rem;
        margin: .6rem 0 1rem 0;
    }
    .feedback-pass {
        background: #eefaf2;
        border-left: 6px solid #37a866;
        border-radius: 10px;
        padding: .9rem 1rem;
        margin-top: .8rem;
    }
    .feedback-revise {
        background: #fff8e8;
        border-left: 6px solid #e8a317;
        border-radius: 10px;
        padding: .9rem 1rem;
        margin-top: .8rem;
    }
    .feedback-retry {
        background: #fff0f0;
        border-left: 6px solid #d9534f;
        border-radius: 10px;
        padding: .9rem 1rem;
        margin-top: .8rem;
    }
    .small-note {color:#667085; font-size:.92rem;}
    .qtitle {margin-top:.3rem; margin-bottom:.2rem;}
</style>
""", unsafe_allow_html=True)

QUESTION_TITLES = {
    "q11": "실전 적용 1-1 · 문장 성분 명칭 쓰기",
    "q12": "실전 적용 1-2 · ‘대표가’가 보어인 까닭",
    "q13": "실전 적용 1-3 · 잘못된 분석 고치기",
    "q21": "실전 적용 2-1 · 해당 표현 찾아 쓰기",
    "q22": "실전 적용 2-2 · 주어와 보어 비교 설명",
    "q23": "실전 적용 2-3 · 조건에 맞게 문장 만들기",
    "q31": "실전 적용 3-1 · 문장 성분에 해당하는 표현 찾기",
    "q32": "실전 적용 3-2 · 관형어와 부사어 비교 설명",
    "q33": "실전 적용 3-3 · 잘못된 분석 고치기",
}

for qid in QUESTION_TITLES:
    st.session_state.setdefault(f"result_{qid}", None)
    st.session_state.setdefault(f"attempted_{qid}", False)

def norm(text):
    """띄어쓰기·문장부호 차이를 줄여 비교한다."""
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = re.sub(r"[\s\.,!?·'\"“”‘’()\[\]{}:;<>/\\_\-]+", "", text)
    return text

def contains_any(text, terms):
    n = norm(text)
    return any(norm(t) in n for t in terms)

def all_groups(text, groups):
    return all(contains_any(text, group) for group in groups)

def make_result(status, good="", improve="", hint=""):
    return {"status": status, "good": good, "improve": improve, "hint": hint}

def save_result(qid, result):
    st.session_state[f"result_{qid}"] = result
    st.session_state[f"attempted_{qid}"] = True

def feedback_html(result):
    if not result:
        return
    status = result["status"]
    if status == "pass":
        css, title = "feedback-pass", "🟢 통과"
    elif status == "revise":
        css, title = "feedback-revise", "🟡 거의 다 왔어요"
    else:
        css, title = "feedback-retry", "🔴 다시 생각해 보세요"

    parts = [f"<div class='{css}'><b>{title}</b>"]
    if result.get("good"):
        parts.append(f"<br><br>✓ <b>잘한 점</b><br>{result['good']}")
    if result.get("improve"):
        parts.append(f"<br><br>△ <b>보완할 점</b><br>{result['improve']}")
    if result.get("hint"):
        parts.append(f"<br><br>💡 <b>힌트</b><br>{result['hint']}")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)

def progress_panel():
    passed = sum(
        1 for qid in QUESTION_TITLES
        if st.session_state.get(f"result_{qid}", {}).get("status") == "pass"
    )
    st.progress(passed / 9)
    st.caption(f"현재 통과: {passed} / 9문항")
    return passed

def source_box(html_text):
    st.markdown(f"<div class='source-box'>{html_text}</div>", unsafe_allow_html=True)

def condition_box(items):
    lines = "<br>".join([f"• {x}" for x in items])
    st.markdown(f"<div class='condition-box'><b>조건</b><br>{lines}</div>", unsafe_allow_html=True)

# -----------------------------
# 채점 함수
# -----------------------------
def grade_q11(vals):
    answers = ["독립어", "관형어", "부사어", "보어", "목적어"]
    oks = [norm(v) == norm(a) for v, a in zip(vals, answers)]
    if all(oks):
        return make_result("pass", "다섯 문장 성분을 모두 정확하게 구별했습니다.")
    wrong = [f"㉠㉡㉢㉣㉤"[i] for i, ok in enumerate(oks) if not ok]
    good_count = sum(oks)
    return make_result(
        "revise" if good_count else "retry",
        f"{good_count}개 항목은 정확합니다." if good_count else "",
        f"{', '.join(wrong)} 항목을 다시 확인해 보세요.",
        "조사 모양만 보지 말고, 문장 속에서 어떤 역할을 하는지와 서술어와의 관계를 살펴보세요."
    )

def grade_q12(ans):
    has_boeo = contains_any(ans, ["보어"])
    has_doeda = contains_any(ans, ["되다", "되었다", "되었", "된다", "되는", "될"])
    has_subject = contains_any(ans, ["주어", "민지"])
    has_supp = contains_any(ans, ["보충", "보완", "채워", "채우", "내용을설명", "내용설명"])
    if not has_boeo:
        return make_result(
            "retry",
            "",
            "‘대표가’의 문장 성분부터 다시 판단해 보세요.",
            "‘가’가 붙었다는 사실만 보지 말고, 뒤의 서술어 ‘되었다’와의 관계를 확인해 보세요."
        )
    missing = []
    if not has_doeda:
        missing.append("서술어 ‘되었다’와의 관계")
    if not (has_subject and has_supp):
        missing.append("주어의 내용을 보충하는 역할")
    if not missing:
        return make_result("pass", "‘대표가’를 보어로 판단하고, ‘되었다’와의 관계 및 역할까지 설명했습니다.")
    return make_result(
        "revise",
        "‘대표가’가 보어라는 판단은 정확합니다.",
        " / ".join(missing) + " 설명이 빠졌습니다.",
        "보어는 ‘되다/아니다’ 앞에서 주어의 내용을 보충합니다."
    )

def independent_reason(text):
    return contains_any(text, ["감탄사", "독립", "직접관계를맺지", "관계가없", "따로쓰", "따로떨어"])

def adverb_reason(text, verb_terms):
    has_target = contains_any(text, verb_terms + ["서술어", "용언"])
    has_modify = contains_any(text, ["꾸미", "수식"])
    return has_target and has_modify

def grade_correction_pairs(pairs, target_a, target_b):
    """
    pairs: [(wrong, right, reason), ...]
    target_a/b: {"wrong":, "right":, "reason_fn": callable}
    """
    targets = [target_a, target_b]
    matched = []
    for t in targets:
        found = None
        for wrong, right, reason in pairs:
            correction_ok = contains_any(wrong, [t["wrong"]]) and contains_any(right, [t["right"]])
            if correction_ok:
                found = (True, t["reason_fn"](reason))
                break
        matched.append(found or (False, False))
    corr_count = sum(1 for c, r in matched if c)
    full_count = sum(1 for c, r in matched if c and r)

    if full_count == 2:
        return make_result("pass", "잘못된 두 부분을 모두 바르게 고치고, 판단 근거까지 정확하게 설명했습니다.")
    if corr_count == 2:
        return make_result(
            "revise",
            "잘못된 두 문장 성분은 모두 정확하게 고쳤습니다.",
            "각 문장 성분을 그렇게 판단한 근거가 충분하지 않습니다.",
            "각 표현이 다른 문장 성분과 어떤 관계를 맺거나 무엇을 꾸미는지 설명해 보세요."
        )
    if corr_count == 1:
        return make_result(
            "revise",
            "잘못된 부분 한 곳은 정확하게 찾았습니다.",
            "아직 다른 한 곳의 잘못된 분석도 찾아야 합니다.",
            "제시된 학생 분석에서 문장 성분의 기능이 맞는지 하나씩 다시 확인해 보세요."
        )
    return make_result(
        "retry",
        "",
        "잘못된 분석 두 곳을 다시 찾아보세요.",
        "‘우와’처럼 홀로 쓰이는 말과, 다른 말을 꾸미는 성분의 차이를 확인해 보세요."
    )

def grade_q21(vals):
    allowed = [
        ["와", "어머나"],
        ["공을", "새공을"],
        ["중학생이"],
        ["새"],
        ["정말"],
    ]
    oks = [norm(v) in [norm(x) for x in a] for v, a in zip(vals, allowed)]
    if all(oks):
        return make_result("pass", "설명에 해당하는 표현을 글에서 모두 정확하게 찾았습니다.")
    wrong = [f"㉠㉡㉢㉣㉤"[i] for i, ok in enumerate(oks) if not ok]
    if any(norm(v) in ["독립어","목적어","보어","관형어","부사어","주어","서술어"] for v in vals):
        hint = "이 문제는 문장 성분의 이름이 아니라, 글 속의 실제 표현을 찾아 쓰는 문제입니다."
    else:
        hint = "설명에 해당하는 표현이 글 속 어디에 있는지 다시 찾아보세요."
    return make_result(
        "revise",
        f"{sum(oks)}개 항목은 정확합니다." if any(oks) else "",
        f"{', '.join(wrong)} 항목을 다시 확인해 보세요.",
        hint
    )

def association_q22(text):
    n = norm(text)
    first_boeo = bool(re.search(r"(㉠|첫번째|첫째|1번)[^㉡]{0,30}보어", n))
    second_jueo = bool(re.search(r"(㉡|두번째|둘째|2번)[^㉠]{0,30}주어", n))
    # 흔한 자연어 표현 보완
    if "㉠의중학생이는보어" in n or "첫번째중학생이는보어" in n:
        first_boeo = True
    if "㉡의중학생이는주어" in n or "두번째중학생이는주어" in n:
        second_jueo = True
    return first_boeo, second_jueo

def grade_q22(ans):
    n = norm(ans)
    if "둘다주어" in n or ("이가" in n and "붙" in n and "주어" in n and "보어" not in n):
        return make_result(
            "retry",
            "",
            "조사 ‘이/가’만으로 두 표현을 모두 주어라고 판단할 수 없습니다.",
            "‘이/가’는 주어뿐 아니라 보어에도 쓰일 수 있습니다. 뒤의 서술어와의 관계를 확인하세요."
        )
    first_boeo, second_jueo = association_q22(ans)
    reason1 = contains_any(ans, ["아니다"]) and contains_any(ans, ["주어", "지민"]) and contains_any(ans, ["보충", "보완", "채워", "채우"])
    reason2 = contains_any(ans, ["달린다", "달리다", "달리는"]) and contains_any(ans, ["주체", "주인", "행동하는사람", "동작하는사람"])
    if first_boeo and second_jueo and reason1 and reason2:
        return make_result("pass", "㉠과 ㉡의 문장 성분을 정확하게 구별하고, 각각의 근거까지 설명했습니다.")
    if first_boeo and second_jueo:
        missing = []
        if not reason1:
            missing.append("㉠에서 ‘아니다’와 보어의 관계")
        if not reason2:
            missing.append("㉡이 ‘달린다’의 동작 주체라는 근거")
        return make_result(
            "revise",
            "㉠은 보어, ㉡은 주어라는 판단은 정확합니다.",
            " / ".join(missing) + "가 부족합니다.",
            "문장 성분의 이름만 쓰지 말고, 뒤의 서술어와 어떤 관계인지 설명해 보세요."
        )
    return make_result(
        "retry",
        "",
        "㉠과 ㉡의 문장 성분 구별부터 다시 확인해 보세요.",
        "㉠은 ‘아니다’ 앞에 있고, ㉡은 ‘달린다’라는 동작의 주체입니다."
    )

ADVERB_COMMON = [
    "천천히","조용히","열심히","빨리","오늘","지금","이제","매우","정말","아주","절대",
    "같이","함께","좀","도서관에서","교실에서","집에서","학교에서","운동장에서"
]
INDEPENDENT_COMMON = ["아","와","우와","어머나","아이고","얘들아","선생님","친구야","야","오"]

def is_independent_word(word):
    w = norm(word)
    if w in [norm(x) for x in INDEPENDENT_COMMON]:
        return True
    # 호격 표현의 대표 형태
    return len(w) >= 2 and (w.endswith("아") or w.endswith("야"))

def is_adverbial_word(word):
    w = norm(word)
    if w in [norm(x) for x in ADVERB_COMMON]:
        return True
    endings = ["에서","에게","으로","로부터","까지","부터","에게서","께서","에","로","와","과","게","도록"]
    return any(w.endswith(norm(e)) for e in endings)

def grade_q23(sentence, indep, adnom, adverb, obj):
    ns = norm(sentence)
    checks = {}
    checks["base"] = "학생이" in ns and "읽는다" in ns

    ni, na, nb, no = map(norm, [indep, adnom, adverb, obj])
    checks["in_sentence"] = all(x and x in ns for x in [ni, na, nb, no])
    checks["indep"] = is_independent_word(indep) and ni in ns
    checks["obj"] = (no.endswith("을") or no.endswith("를")) and no in ns and ns.find(no) < ns.find("읽는다")
    checks["adverb"] = is_adverbial_word(adverb) and nb in ns and ns.find(nb) < ns.find("읽는다")
    # 관형어는 학생이 적은 목적어 바로 앞에서 그 체언을 꾸미는 구조를 우선 인정
    checks["adnom"] = na in ns and no in ns and (na + no) in ns and na != nb

    if all(checks.values()):
        return make_result("pass", "기본 문장을 유지하면서 독립어·관형어·부사어·목적어를 모두 넣고, 자기 분석까지 정확하게 했습니다.")

    missing = []
    if not checks["base"]:
        missing.append("‘학생이’와 ‘읽는다’를 그대로 사용하기")
    if not checks["indep"]:
        missing.append("독립어")
    if not checks["obj"]:
        missing.append("‘읽는다’의 대상이 되는 목적어")
    if not checks["adnom"]:
        missing.append("목적어를 꾸미는 관형어")
    if not checks["adverb"]:
        missing.append("‘읽는다’를 꾸미는 부사어")
    if not checks["in_sentence"]:
        missing.append("성분표에 적은 표현을 실제 문장에도 사용하기")

    status = "revise" if checks["base"] and sum(checks.values()) >= 3 else "retry"
    return make_result(
        status,
        "조건 중 일부는 잘 충족했습니다." if status == "revise" else "",
        "다음 조건을 다시 확인하세요: " + ", ".join(dict.fromkeys(missing)),
        "관형어는 체언을 꾸미고, 부사어는 주로 용언을 꾸밉니다. 이 문항의 자동 검사는 수업에서 배운 대표 형태를 중심으로 작동합니다."
    )

def grade_q31(vals):
    allowed = [
        ["선생님", "아"],
        ["과학자가"],
        ["훌륭한", "어려운", "이"],
        ["책을"],
        ["미래에", "오늘", "도서관에서", "천천히", "정말"],
    ]
    oks = [norm(v) in [norm(x) for x in a] for v, a in zip(vals, allowed)]
    if all(oks):
        return make_result("pass", "각 문장 성분에 해당하는 표현을 모두 정확하게 찾았습니다.")
    wrong_names = ["독립어","보어","관형어","목적어","부사어"]
    wrong = [wrong_names[i] for i, ok in enumerate(oks) if not ok]
    return make_result(
        "revise",
        f"{sum(oks)}개 항목은 정확합니다." if any(oks) else "",
        "다시 확인할 항목: " + ", ".join(wrong),
        "답이 여러 개인 항목도 있습니다. 제시문에서 해당 역할을 하는 표현 하나를 찾아 쓰면 됩니다."
    )

def association_q32(text):
    n = norm(text)
    future_adv = bool(re.search(r"미래에[^.]{0,25}부사어", n))
    excellent_adnom = bool(re.search(r"훌륭한[^.]{0,25}관형어", n))
    return future_adv, excellent_adnom

def grade_q32(ans):
    future_adv, excellent_adnom = association_q32(ans)
    has_future_target = contains_any(ans, ["될거예요", "되다", "될", "된다"]) and contains_any(ans, ["꾸미", "수식"])
    has_excellent_target = contains_any(ans, ["과학자"]) and contains_any(ans, ["꾸미", "수식"])
    has_diff = (
        contains_any(ans, ["관형어"]) and contains_any(ans, ["체언"]) and
        contains_any(ans, ["부사어"]) and contains_any(ans, ["용언"]) and
        contains_any(ans, ["꾸미", "수식"])
    )

    n = norm(ans)
    if ("미래에는관형어" in n or "미래에관형어" in n) and ("훌륭한은부사어" in n or "훌륭한부사어" in n):
        return make_result(
            "retry",
            "",
            "관형어와 부사어가 서로 바뀌었습니다.",
            "각 표현이 실제로 무엇을 꾸며 주는지 먼저 확인해 보세요."
        )

    if future_adv and excellent_adnom and has_future_target and has_excellent_target and has_diff:
        return make_result("pass", "두 표현의 문장 성분과 꾸밈 관계, 관형어·부사어의 차이까지 정확하게 설명했습니다.")

    if future_adv and excellent_adnom:
        missing = []
        if not has_future_target:
            missing.append("‘미래에’가 무엇을 꾸미는지")
        if not has_excellent_target:
            missing.append("‘훌륭한’이 무엇을 꾸미는지")
        if not has_diff:
            missing.append("관형어와 부사어의 일반적인 차이")
        return make_result(
            "revise",
            "‘미래에’는 부사어, ‘훌륭한’은 관형어라는 판단은 정확합니다.",
            " / ".join(missing) + " 설명이 빠졌습니다.",
            "관형어는 체언을 꾸미고, 부사어는 주로 용언을 꾸밉니다."
        )
    return make_result(
        "retry",
        "",
        "‘미래에’와 ‘훌륭한’의 문장 성분부터 다시 판단해 보세요.",
        "각 표현이 무엇을 꾸미는지 확인하면 관형어와 부사어를 구별할 수 있습니다."
    )

def q33_today_reason(text):
    return (
        (contains_any(text, ["읽습니다","읽다","서술어","용언"]) and contains_any(text, ["꾸미","수식"]))
        or contains_any(text, ["읽는때","시간","언제"])
    )

def q33_difficult_reason(text):
    return (
        contains_any(text, ["책","체언"])
        and contains_any(text, ["꾸미","수식"])
    )

# -----------------------------
# 화면
# -----------------------------
st.markdown("""
<div class="hero">
<h1 style="margin:0 0 .4rem 0;">✍️ 문장 성분 서·논술형 실전 연습</h1>
<div style="font-size:1.06rem;">아는 문법을, <b>조건에 맞는 답안</b>으로 표현해 보자.</div>
</div>
""", unsafe_allow_html=True)

passed = progress_panel()

tabs = st.tabs(["시작하기", "실전 적용 1", "실전 적용 2", "실전 적용 3", "복습할 내용"])

# -----------------------------
# 시작하기
# -----------------------------
with tabs[0]:
    st.subheader("이 앱에서 연습할 내용")
    st.write("지금까지 배운 **주어·서술어·목적어·보어·관형어·부사어·독립어**를 활용하여 서·논술형 답안을 작성합니다.")
    st.info("총 3세트, 9문항입니다. 정답을 한 번에 맞히지 않아도 됩니다. 피드백을 확인하고 답안을 고쳐 다시 제출하세요.")
    st.markdown("""
    **연습 순서**
    1. 문제의 발문과 조건을 끝까지 읽기  
    2. 답안 작성하기  
    3. `답안 확인하기` 누르기  
    4. 피드백에서 빠진 조건 확인하기  
    5. 답안을 고쳐 다시 제출하기
    """)
    st.caption("이 앱은 형성평가용 규칙 기반 자동 피드백 앱입니다. 자유 서술형의 모든 가능한 표현을 완벽하게 판정하는 용도는 아닙니다.")

# -----------------------------
# 실전 적용 1
# -----------------------------
with tabs[1]:
    st.header("실전 적용 1")

    st.subheader("서·논술형 1")
    source_box("""
    <b>오늘 우리 반에서는 발표 수업이 있다.</b><br>
    얘들아, 민지는 새 교실에서 발표를 한다.<br>
    민지는 새로운 대표가 되었다.<br>
    우와, 친구들이 박수를 크게 친다.
    """)
    st.write("다음 표현의 문장 성분 명칭을 쓰시오.")
    with st.form("form_q11"):
        cols = st.columns(5)
        labels = ["㉠ 얘들아", "㉡ 새", "㉢ 교실에서", "㉣ 대표가", "㉤ 박수를"]
        vals = [cols[i].text_input(labels[i], key=f"q11_{i}") for i in range(5)]
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            save_result("q11", grade_q11(vals))
    feedback_html(st.session_state["result_q11"])

    st.divider()

    st.subheader("서·논술형 2")
    source_box("민지는 새로운 <b>대표가</b> 되었다.")
    st.write("‘대표가’의 문장 성분이 무엇인지 밝히고, 그 까닭을 조건에 맞게 서술하시오.")
    condition_box([
        "‘대표가’의 문장 성분을 정확하게 밝힐 것.",
        "서술어 ‘되었다’와의 관계를 설명할 것.",
        "해당 문장 성분이 하는 역할을 포함할 것."
    ])
    with st.form("form_q12"):
        ans = st.text_area("답안", height=120, key="q12_ans", label_visibility="collapsed")
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            save_result("q12", grade_q12(ans))
    feedback_html(st.session_state["result_q12"])

    st.divider()

    st.subheader("서·논술형 3")
    source_box("""
    <b>문장</b>: 우와, 친구들이 박수를 크게 친다.<br><br>
    <b>학생의 분석</b><br>
    우와 → 부사어<br>
    친구들이 → 주어<br>
    박수를 → 목적어<br>
    크게 → 관형어<br>
    친다 → 서술어
    """)
    st.write("잘못 분석한 부분 두 곳을 찾아 바르게 고치고, 각각의 근거를 쓰시오.")
    condition_box([
        "잘못된 분석 두 곳을 모두 찾을 것.",
        "바른 문장 성분의 명칭을 쓸 것.",
        "다른 말을 꾸미는지 여부 또는 다른 문장 성분과의 관계를 근거로 설명할 것."
    ])
    with st.form("form_q13"):
        c1, c2 = st.columns(2)
        with c1:
            w1 = st.text_input("잘못된 표현 ①", key="q13_w1")
            r1 = st.text_input("바른 문장 성분 ①", key="q13_r1")
            rs1 = st.text_area("근거 ①", height=90, key="q13_rs1")
        with c2:
            w2 = st.text_input("잘못된 표현 ②", key="q13_w2")
            r2 = st.text_input("바른 문장 성분 ②", key="q13_r2")
            rs2 = st.text_area("근거 ②", height=90, key="q13_rs2")
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            pairs = [(w1, r1, rs1), (w2, r2, rs2)]
            result = grade_correction_pairs(
                pairs,
                {"wrong":"우와","right":"독립어","reason_fn": independent_reason},
                {"wrong":"크게","right":"부사어","reason_fn": lambda x: adverb_reason(x, ["친다","치다"])},
            )
            save_result("q13", result)
    feedback_html(st.session_state["result_q13"])

# -----------------------------
# 실전 적용 2
# -----------------------------
with tabs[2]:
    st.header("실전 적용 2")

    st.subheader("서·논술형 1")
    source_box("""
    와, 서준이는 오늘 운동장에서 새 공을 힘껏 찼다.<br>
    지민이는 중학생이 아니다.<br>
    어머나, 새 가방이 정말 예쁘다.
    """)
    st.write("윗글에서 다음 설명에 해당하는 표현을 찾아 쓰시오.")
    descriptions = [
        "㉠ 다른 문장 성분과 직접적인 관계를 맺지 않는 성분",
        "㉡ ‘찼다’의 동작 대상을 나타내는 성분",
        "㉢ ‘아니다’ 앞에서 주어의 내용을 보충하는 성분",
        "㉣ ‘가방’을 꾸며 주는 성분",
        "㉤ ‘예쁘다’를 꾸며 주는 성분",
    ]
    with st.form("form_q21"):
        vals = []
        for i, d in enumerate(descriptions):
            vals.append(st.text_input(d, key=f"q21_{i}"))
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            save_result("q21", grade_q21(vals))
    feedback_html(st.session_state["result_q21"])

    st.divider()

    st.subheader("서·논술형 2")
    source_box("""
    ㉠ 지민이는 <b>중학생이</b> 아니다.<br>
    ㉡ <b>중학생이</b> 운동장에서 달린다.
    """)
    st.write("㉠과 ㉡의 ‘중학생이’가 각각 어떤 문장 성분인지 비교하여 설명하시오.")
    condition_box([
        "㉠과 ㉡의 문장 성분을 각각 밝힐 것.",
        "㉠은 ‘아니다’와의 관계를 근거로 설명할 것.",
        "㉡은 동작이나 상태의 주체라는 점을 근거로 설명할 것."
    ])
    with st.form("form_q22"):
        ans = st.text_area("답안", height=140, key="q22_ans", label_visibility="collapsed",
                           placeholder="예: ㉠은 …, ㉡은 …")
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            save_result("q22", grade_q22(ans))
    feedback_html(st.session_state["result_q22"])

    st.divider()

    st.subheader("서·논술형 3")
    source_box("<b>기본 문장</b>: 학생이 읽는다.")
    st.write("기본 문장을 조건에 맞게 바꾸어 쓰시오.")
    condition_box([
        "‘학생이’와 ‘읽는다’는 그대로 사용할 것.",
        "목적어 1개를 추가할 것.",
        "목적어를 꾸미는 관형어 1개 이상을 추가할 것.",
        "‘읽는다’를 꾸미는 부사어 1개 이상을 추가할 것.",
        "문장 앞에 독립어 1개를 추가할 것.",
        "완성한 뒤 자신이 추가한 문장 성분을 각각 밝힐 것."
    ])
    with st.form("form_q23"):
        sentence = st.text_input("완성한 문장", key="q23_sentence")
        c1, c2, c3, c4 = st.columns(4)
        indep = c1.text_input("독립어", key="q23_indep")
        adnom = c2.text_input("관형어", key="q23_adnom")
        adverb = c3.text_input("부사어", key="q23_adverb")
        obj = c4.text_input("목적어", key="q23_obj")
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            save_result("q23", grade_q23(sentence, indep, adnom, adverb, obj))
    feedback_html(st.session_state["result_q23"])

# -----------------------------
# 실전 적용 3
# -----------------------------
with tabs[3]:
    st.header("실전 적용 3")

    source_text_3 = """
    선생님, 저는 미래에 훌륭한 과학자가 될 거예요.<br>
    저는 오늘 도서관에서 <b>어려운 책을</b> 천천히 읽습니다.<br>
    아, 이 책은 정말 재미있습니다.
    """

    st.subheader("서·논술형 1")
    source_box(source_text_3)
    st.write("윗글에서 다음 문장 성분에 해당하는 표현을 하나씩 찾아 쓰시오.")
    names = ["독립어", "보어", "관형어", "목적어", "부사어"]
    with st.form("form_q31"):
        vals = []
        cols = st.columns(5)
        for i, name in enumerate(names):
            vals.append(cols[i].text_input(name, key=f"q31_{i}"))
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            save_result("q31", grade_q31(vals))
    feedback_html(st.session_state["result_q31"])

    st.divider()

    st.subheader("서·논술형 2")
    source_box("저는 <b>미래에</b> <b>훌륭한</b> 과학자가 될 거예요.")
    st.write("‘미래에’와 ‘훌륭한’의 문장 성분과 기능을 비교하여 설명하시오.")
    condition_box([
        "‘미래에’와 ‘훌륭한’의 문장 성분을 각각 밝힐 것.",
        "각각 무엇을 꾸미는지 밝힐 것.",
        "관형어와 부사어의 차이가 드러나도록 서술할 것."
    ])
    with st.form("form_q32"):
        ans = st.text_area("답안", height=150, key="q32_ans", label_visibility="collapsed")
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            save_result("q32", grade_q32(ans))
    feedback_html(st.session_state["result_q32"])

    st.divider()

    st.subheader("서·논술형 3")
    source_box("""
    <b>문장</b>: 저는 오늘 도서관에서 어려운 책을 천천히 읽습니다.<br><br>
    <b>학생의 분석</b><br>
    저는 → 주어<br>
    오늘 → 관형어<br>
    도서관에서 → 부사어<br>
    어려운 → 부사어<br>
    책을 → 목적어<br>
    천천히 → 부사어<br>
    읽습니다 → 서술어
    """)
    st.write("학생의 분석에서 잘못된 부분을 모두 찾아 바르게 고치고, 각각의 근거를 쓰시오.")
    condition_box([
        "잘못된 부분을 모두 찾을 것.",
        "바른 문장 성분의 명칭을 제시할 것.",
        "해당 표현이 어떤 말을 꾸미는지 반드시 밝힐 것."
    ])
    with st.form("form_q33"):
        c1, c2 = st.columns(2)
        with c1:
            w1 = st.text_input("잘못된 표현 ①", key="q33_w1")
            r1 = st.text_input("바른 문장 성분 ①", key="q33_r1")
            rs1 = st.text_area("근거 ①", height=90, key="q33_rs1")
        with c2:
            w2 = st.text_input("잘못된 표현 ②", key="q33_w2")
            r2 = st.text_input("바른 문장 성분 ②", key="q33_r2")
            rs2 = st.text_area("근거 ②", height=90, key="q33_rs2")
        submit = st.form_submit_button("답안 확인하기")
        if submit:
            pairs = [(w1, r1, rs1), (w2, r2, rs2)]
            result = grade_correction_pairs(
                pairs,
                {"wrong":"오늘","right":"부사어","reason_fn": q33_today_reason},
                {"wrong":"어려운","right":"관형어","reason_fn": q33_difficult_reason},
            )
            save_result("q33", result)
    feedback_html(st.session_state["result_q33"])

# -----------------------------
# 복습 탭
# -----------------------------
with tabs[4]:
    st.header("복습할 내용")

    failed = []
    for qid, title in QUESTION_TITLES.items():
        res = st.session_state.get(f"result_{qid}")
        attempted = st.session_state.get(f"attempted_{qid}", False)
        if attempted and res and res["status"] != "pass":
            failed.append((qid, title, res))

    unattempted = [
        title for qid, title in QUESTION_TITLES.items()
        if not st.session_state.get(f"attempted_{qid}", False)
    ]

    if passed == 9:
        st.success("🎉 9문항을 모두 통과했습니다! 문장 성분을 찾는 것뿐 아니라 근거를 들어 설명하고 조건에 맞게 답안을 쓰는 연습까지 완료했습니다.")
    elif not failed:
        st.info("아직 복습 목록이 없습니다. 실전 적용 문제를 풀면 보완이 필요한 문항이 여기에 모입니다.")
    else:
        st.write(f"현재 **{len(failed)}개 문항**을 다시 확인하면 좋습니다.")
        for qid, title, res in failed:
            with st.expander(title, expanded=True):
                feedback_html(res)
                st.caption("해당 실전 적용 탭으로 돌아가 답안을 수정한 뒤 다시 제출하세요.")

    if unattempted:
        st.markdown("#### 아직 풀지 않은 문항")
        for title in unattempted:
            st.write("• " + title)

st.divider()
c1, c2 = st.columns([4,1])
with c1:
    st.caption("모든 문제를 제출하면 ‘복습할 내용’ 탭에서 아직 통과하지 못한 개념을 확인할 수 있어요.")
with c2:
    if st.button("처음부터 다시 풀기", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
