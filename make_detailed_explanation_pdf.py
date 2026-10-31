from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors

out = "Forgettable_Athlete_DetailedExplanation.pdf"

doc = SimpleDocTemplate(
    out, pagesize=A4,
    leftMargin=1.6 * cm, rightMargin=1.6 * cm,
    topMargin=1.4 * cm, bottomMargin=1.4 * cm,
)

styles = getSampleStyleSheet()
title = ParagraphStyle("title", parent=styles["Title"], fontSize=18,
                       spaceAfter=10, textColor=HexColor("#1f3a93"))
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13,
                    spaceBefore=12, spaceAfter=5, textColor=HexColor("#1f3a93"))
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=11,
                    spaceBefore=8, spaceAfter=3, textColor=HexColor("#2c5cb8"))
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10.2,
                      leading=14, spaceAfter=5)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=4)
note = ParagraphStyle("note", parent=body, textColor=HexColor("#444444"),
                      fontSize=9.5, leading=12)

story = []

# ---------- HEADER ----------
story.append(Paragraph("Forgettable Athlete — Detailed Explanation", title))
story.append(Paragraph(
    "Why Logistic Regression won, what the SHAP graphs mean, how SISA works, "
    "and how to read the correlation heatmap.", note))
story.append(Spacer(1, 10))

# ---------- 1. MODEL RANKING ----------
story.append(Paragraph("1. The Model Ranking (by ROC-AUC)", h2))

data = [
    ["Rank", "Model", "Accuracy", "F1", "ROC-AUC", "Fit time (s)"],
    ["1st", "Logistic Regression", "0.9500", "0.9500", "0.9961", "0.021"],
    ["2nd", "Random Forest",       "0.9563", "0.9560", "0.9925", "0.649"],
    ["3rd", "LightGBM",             "0.9187", "0.9161", "0.9881", "0.152"],
    ["4th", "XGBoost",              "0.9375", "0.9359", "0.9848", "0.131"],
]
t = Table(data, hAlign="LEFT",
          colWidths=[1.2*cm, 4.5*cm, 2.2*cm, 1.8*cm, 2.2*cm, 2.6*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1f3a93")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("BACKGROUND", (0, 1), (-1, 1), HexColor("#dfe9ff")),
    ("ROWBACKGROUNDS", (0, 2), (-1, -1), [colors.white, HexColor("#f4f4f4")]),
]))
story.append(t)
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Random Forest has slightly higher raw accuracy, but <b>ROC-AUC is the primary metric</b> "
    "because in injury prediction both false positives (unnecessary rest) and false negatives "
    "(missed injury) matter. ROC-AUC measures probability-ranking quality across every "
    "threshold, not just hard predictions at 0.5.", body))

# ---------- 2. WHY LOGISTIC REGRESSION WON ----------
story.append(Paragraph("2. Why Logistic Regression Wins — the Theory", h2))
story.append(Paragraph(
    "Logistic Regression draws a <b>straight line (hyperplane) through the feature space</b> "
    "and says: everyone on this side is at injury risk, everyone on the other side is safe. "
    "It only works well when the signal in the data is roughly linear.", body))

story.append(Paragraph("A. Your engineered features pre-cooked the non-linearity.", h3))
story.append(Paragraph(
    "You manually built four features:", body))
story.append(Paragraph("• <b>ACWR</b> = training load relative to a rolling 5-row mean (a ratio).", bullet))
story.append(Paragraph("• <b>Recovery_Score</b> = weighted blend of sleep + nutrition + warmup minus stress.", bullet))
story.append(Paragraph("• <b>Fatigue_Index</b> = blend of training load + matches minus recovery.", bullet))
story.append(Paragraph("• <b>Injury_Frequency_Score</b> = previous injuries divided by age.", bullet))
story.append(Paragraph(
    "These are already non-linear combinations of the raw columns (ratios, weighted sums). "
    "By the time the linear model sees them, the hard work is done — it just needs to draw a "
    "line through them. Tree models (RF, XGBoost, LightGBM) try to <b>rediscover</b> these "
    "patterns from scratch by splitting raw columns repeatedly, which on only 640 training "
    "rows wastes capacity and risks overfitting.", body))

story.append(Paragraph("B. Small dataset (n = 640 train).", h3))
story.append(Paragraph(
    "Boosting algorithms shine with tens of thousands of rows. On small tabular data with "
    "strong linear signals, the simpler model usually wins — this is a textbook "
    "<b>bias-variance tradeoff</b> outcome. Trees have high variance; linear models have low "
    "variance. Less data means variance hurts more.", body))

story.append(Paragraph("C. Calibrated, smooth probabilities.", h3))
story.append(Paragraph(
    "Logistic outputs smooth probabilities via the sigmoid function. ROC-AUC rewards good "
    "probability <i>ranking</i>, which is exactly what logistic regression is mathematically "
    "optimised for.", body))

story.append(Paragraph("Why the others ranked where they did", h3))
story.append(Paragraph(
    "• <b>Random Forest (2nd)</b> — Averages many decision trees, so variance drops vs a "
    "single tree. It found most of the signal but slightly overfits because trees can't "
    "represent a smooth ratio like ACWR cleanly — they approximate it with many step-function splits.", bullet))
story.append(Paragraph(
    "• <b>LightGBM (3rd)</b> — Uses <i>leaf-wise</i> growth (always splits the leaf with "
    "highest loss reduction). Very aggressive — great on big data, but on 640 rows it overfits noisy splits.", bullet))
story.append(Paragraph(
    "• <b>XGBoost (4th, worst)</b> — Similar to LightGBM but with level-wise growth. "
    "Without hyper-parameter tuning, its defaults didn't help on a dataset this small.", bullet))
story.append(Paragraph(
    "<b>In short:</b> the dataset is small + linear-friendly + already feature-engineered → "
    "linear model wins.", note))

story.append(PageBreak())

# ---------- 3. FEATURES ----------
story.append(Paragraph("3. Which Features Did the Heavy Lifting", h2))
story.append(Paragraph(
    "From the top-10 correlations and SHAP, the dominant features are:", body))
story.append(Paragraph("1. <b>Fatigue_Index</b> — workload pressure offset by recovery. Higher → more injury.", bullet))
story.append(Paragraph("2. <b>Recovery_Score</b> — sleep + nutrition + warmup. Higher → less injury.", bullet))
story.append(Paragraph("3. <b>Previous_Injury_Count</b> — past injuries predict future injuries.", bullet))
story.append(Paragraph("4. <b>Injury_Frequency_Score</b> — chronic injury-prone players, age-adjusted.", bullet))
story.append(Paragraph("5. <b>Training_Hours_Per_Week</b> and <b>ACWR</b> — workload spikes are dangerous.", bullet))
story.append(Paragraph("6. <b>Sleep_Hours_Per_Night</b> and <b>Stress_Level_Score</b> — recovery quality.", bullet))
story.append(Paragraph(
    "The <b>engineered features did most of the predicting</b> — that is why logistic "
    "regression worked so well. Raw features like BMI, height, or position alone carried "
    "little signal.", body))

# ---------- 4. CORRELATION HEATMAP ----------
story.append(Paragraph("4. The Correlation Heatmap — Simple Explanation", h2))
story.append(Paragraph(
    "A correlation heatmap shows how each pair of variables moves together, with values from "
    "<b>-1 to +1</b>:", body))
story.append(Paragraph("• <b>+1 (deep red):</b> when one goes up, the other goes up. Perfect positive link.", bullet))
story.append(Paragraph("• <b>0 (white):</b> no relationship.", bullet))
story.append(Paragraph("• <b>-1 (deep blue):</b> when one goes up, the other goes down. Perfect negative link.", bullet))
story.append(Paragraph("How to read your heatmap", h3))
story.append(Paragraph(
    "1. <b>Look at the Injury_Next_Season row/column</b> — that's your target. The cells there "
    "tell you which feature is the strongest predictor. The notebook says <i>no single feature "
    "dominates</i>, meaning all correlations with the target are modest (under 0.3 each). "
    "This is normal for injury data — injuries are multi-causal.", body))
story.append(Paragraph(
    "2. <b>Big red blocks among physical tests</b> — features like Knee_Strength_Score, "
    "Balance_Test_Score, Agility_Score, Sprint_Speed_10m_s are correlated with each other. "
    "That means they carry overlapping information (a strong athlete is strong on all of them). "
    "Models will use one and ignore the others — this is called <b>multicollinearity</b>.", body))
story.append(Paragraph(
    "3. <b>Fatigue_Index and Recovery_Score show stronger correlation with the target</b> than "
    "the raw features — proof that feature engineering added real signal.", body))
story.append(Paragraph(
    "4. <b>BMI is essentially flat with the target</b> — your EDA confirmed this; the BMI "
    "distributions overlap fully across injured vs non-injured players.", body))
story.append(Paragraph(
    "<b>One-line takeaway:</b> No single feature is a smoking gun — injury comes from a "
    "<i>combination</i> of fatigue, prior injuries, and poor recovery, which is why the "
    "engineered composite features beat the raw ones.", note))

story.append(PageBreak())

# ---------- 5. SHAP ----------
story.append(Paragraph("5. SHAP Analysis — What the Graphs Mean", h2))
story.append(Paragraph(
    "<b>SHAP (SHapley Additive exPlanations)</b> comes from game theory. Imagine each feature "
    "is a player on a team, and the team's job is to predict whether a footballer will get "
    "injured. SHAP fairly distributes the 'credit' for the prediction across all features — "
    "for every single prediction.", body))
story.append(Paragraph(
    "For each prediction, SHAP says: 'the model would normally predict X (the baseline), but "
    "for this specific player, feature A pushed the prediction up by +0.15, feature B pushed "
    "it down by -0.08…' and so on.", body))

story.append(Paragraph("The Summary Plot (beeswarm — first SHAP graph)", h3))
story.append(Paragraph("This is the dot-cloud chart. Read it like this:", body))
story.append(Paragraph("• <b>Y-axis</b> = features, sorted from most important (top) to least.", bullet))
story.append(Paragraph(
    "• <b>X-axis</b> = SHAP value. Right of zero pushes prediction toward 'Injury'; "
    "left pushes toward 'No injury'.", bullet))
story.append(Paragraph("• <b>Each dot</b> = one player in the test set.", bullet))
story.append(Paragraph(
    "• <b>Dot colour</b> = the actual value of that feature for that player. "
    "<b>Red = high value, Blue = low value.</b>", bullet))
story.append(Paragraph("<b>How to interpret a row:</b>", body))
story.append(Paragraph(
    "If red dots cluster on the <b>right</b> and blue on the <b>left</b>, then high values of "
    "that feature increase injury risk (positive relationship). For Fatigue_Index, red dots "
    "will sit on the right → high fatigue → more injury risk. For Recovery_Score, you'll see "
    "the opposite: red on the left → good recovery protects players.", body))

story.append(Paragraph("The Bar Plot (second SHAP graph)", h3))
story.append(Paragraph(
    "Just the <b>average absolute SHAP value</b> per feature — a clean ranking of 'how much "
    "does this feature move predictions, on average?' The top bars are your most influential "
    "features overall.", body))

story.append(Paragraph("The Waterfall Plot (third SHAP graph — for one player)", h3))
story.append(Paragraph("Explains ONE specific injured player's prediction:", body))
story.append(Paragraph(
    "• Starts at the model's <b>baseline probability</b> (about 50% in your balanced dataset).", bullet))
story.append(Paragraph(
    "• Each <b>red bar</b> = a feature pushing the prediction up toward 'Injury'.", bullet))
story.append(Paragraph(
    "• Each <b>blue bar</b> = a feature pushing the prediction down toward 'No injury'.", bullet))
story.append(Paragraph(
    "• Ends at the model's <b>final prediction</b> for that player.", bullet))
story.append(Paragraph(
    "<b>Why this matters:</b> A team doctor can look at this plot and say 'We're resting this "
    "player because his Fatigue_Index is +0.18, his Previous_Injury_Count contributes +0.12, "
    "and his low Recovery_Score adds another +0.09 — here's the receipt.' That's auditable "
    "medicine, not a black box.", note))

story.append(PageBreak())

# ---------- 6. SISA ----------
story.append(Paragraph("6. SISA — Machine Unlearning Explained Simply", h2))
story.append(Paragraph(
    "<b>SISA = Sharded, Isolated, Sliced, Aggregated.</b> It's a clever trick for handling "
    "'right to be forgotten' requests (GDPR) without retraining your whole model.", body))

story.append(Paragraph("The Problem It Solves", h3))
story.append(Paragraph(
    "A footballer leaves the club and says 'delete my data.' Normally you would:", body))
story.append(Paragraph("1. Remove their rows from the training data.", bullet))
story.append(Paragraph("2. <b>Retrain the entire model from scratch.</b>", bullet))
story.append(Paragraph(
    "On big datasets this is expensive — hours, possibly days. SISA shortens it.", body))

story.append(Paragraph("How SISA Works (4 Steps)", h3))
story.append(Paragraph(
    "1. <b>Shard</b> — Split your training data into N independent chunks (you used N=5 "
    "shards of 128 players each).", bullet))
story.append(Paragraph(
    "2. <b>Isolate</b> — Train <b>one separate model per shard</b>. Each model only ever sees "
    "its own 128 players, nothing else.", bullet))
story.append(Paragraph(
    "3. <b>Slice</b> (optional) — Inside each shard, save intermediate checkpoints so you can "
    "roll back to a midpoint instead of starting over.", bullet))
story.append(Paragraph(
    "4. <b>Aggregate</b> — At prediction time, all 5 shard-models vote (average their "
    "probabilities). That's your ensemble prediction.", bullet))

story.append(Paragraph("Why It's Fast for Deletions", h3))
story.append(Paragraph("When a player asks to be forgotten:", body))
story.append(Paragraph("• Find which shard contains them.", bullet))
story.append(Paragraph(
    "• <b>Retrain only that one shard.</b> The other shards never saw them, so they don't "
    "need to change.", bullet))
story.append(Paragraph("• Cost = 1/N of a full retrain (in the best case).", bullet))

story.append(Paragraph("Your Notebook's Result", h3))
data2 = [
    ["Method",           "Accuracy", "ROC-AUC", "Time (s)"],
    ["Full retraining",  "0.9563",   "0.9922",  "0.148"],
    ["SISA unlearning",  "0.9375",   "0.9855",  "0.116"],
]
t2 = Table(data2, hAlign="LEFT",
           colWidths=[4.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1f3a93")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, HexColor("#f4f4f4")]),
]))
story.append(t2)
story.append(Spacer(1, 6))
story.append(Paragraph(
    "• 54 players requested deletion in the training set.", bullet))
story.append(Paragraph(
    "• <b>Time saving: 21.9%</b> — and post-unlearning ROC-AUC is virtually identical "
    "to full retraining.", bullet))
story.append(Paragraph(
    "The 22% saving looks small here because the dataset is tiny (640 rows, total time "
    "0.15 seconds). In a real club with <b>100,000+ rows and gradient-boosted models</b>, "
    "full retraining takes minutes-to-hours, and SISA gives massive time savings (often "
    "80%+). In your specific run, all 5 shards happened to contain at least one deletion "
    "request, so you retrained all 5 anyway — with luckier sharding or more shards, the "
    "saving grows.", body))

story.append(Paragraph("The Tradeoff", h3))
story.append(Paragraph(
    "• <b>Pro:</b> Cheap deletions, provable forgetting.", bullet))
story.append(Paragraph(
    "• <b>Con:</b> Each shard sees less data → individual shards are weaker (your shards "
    "each got about 89–91% accuracy vs the 95% full model). The ensemble averaging mostly "
    "recovers performance, but there's a small permanent accuracy cost.", bullet))

# ---------- 7. BIG PICTURE ----------
story.append(Paragraph("7. The Big Picture", h2))
story.append(Paragraph(
    "Your pipeline elegantly combines three things that are usually separate:", body))
story.append(Paragraph(
    "1. <b>Sports science</b> — workload, recovery, fatigue features grounded in real injury research.", bullet))
story.append(Paragraph(
    "2. <b>Explainable AI</b> — SHAP makes the model auditable for medical staff.", bullet))
story.append(Paragraph(
    "3. <b>Privacy compliance</b> — SISA gives you GDPR-style 'right to be forgotten' without burning compute.", bullet))
story.append(Paragraph(
    "<b>The reason Logistic Regression won is not that it's a 'better algorithm' in general "
    "— it's that for this particular setup (small dataset + well-engineered linear-friendly "
    "features + the need for calibrated probabilities), it fits the problem perfectly.</b> "
    "Had you doubled the dataset and skipped feature engineering, LightGBM or XGBoost would "
    "likely have overtaken it.", body))

doc.build(story)
print(f"Created {out}")
