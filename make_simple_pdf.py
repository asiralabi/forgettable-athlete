from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors

out = "Forgettable_Athlete_SimpleExplainer.pdf"

doc = SimpleDocTemplate(
    out, pagesize=A4,
    leftMargin=1.6 * cm, rightMargin=1.6 * cm,
    topMargin=1.4 * cm, bottomMargin=1.4 * cm,
)

styles = getSampleStyleSheet()
title = ParagraphStyle("title", parent=styles["Title"], fontSize=18, spaceAfter=10, textColor=HexColor("#1f3a93"))
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=4, textColor=HexColor("#1f3a93"))
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10.2, leading=14, spaceAfter=5)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=4)
note = ParagraphStyle("note", parent=body, textColor=HexColor("#444444"), fontSize=9.5, leading=12)

story = []

story.append(Paragraph("Forgettable Athlete — Simple Explainer", title))
story.append(Paragraph("A noob-friendly guide to the injury prediction project: model ranking, ROC-AUC vs accuracy, correlation heatmap, SHAP, and machine unlearning (SISA).", note))
story.append(Spacer(1, 8))

# Section 1
story.append(Paragraph("1. Which model won, and the ranking", h2))
data = [
    ["Rank", "Model", "Accuracy", "F1", "ROC-AUC"],
    ["1", "Logistic Regression", "0.9500", "0.9500", "0.9961"],
    ["2", "Random Forest", "0.9563", "0.9560", "0.9925"],
    ["3", "LightGBM", "0.9187", "0.9161", "0.9881"],
    ["4", "XGBoost", "0.9375", "0.9359", "0.9848"],
]
t = Table(data, hAlign="LEFT", colWidths=[1.2*cm, 4.5*cm, 2.5*cm, 2.0*cm, 2.5*cm])
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
    "Logistic Regression took first place on ROC-AUC. Random Forest is right behind it and even beats it on raw accuracy. "
    "LightGBM came third and XGBoost was fourth.", body))

# Section 2
story.append(Paragraph("2. Why ROC-AUC instead of Accuracy?", h2))
story.append(Paragraph(
    "<b>Accuracy</b> only asks: did the model pick the right label at a 50% threshold? It treats a 51% confident guess and a 99% confident guess the same.", body))
story.append(Paragraph(
    "<b>ROC-AUC</b> asks something deeper: across <i>every</i> possible cutoff, how well does the model separate injured from healthy players? A score of 1.0 means perfect ranking; 0.5 means random.", body))
story.append(Paragraph("<b>Why this matters here:</b>", body))
story.append(Paragraph("• In sports medicine, the cost of missing an injury (false negative) is different from over-resting a player (false positive). A coach may want to use a stricter or looser threshold than 50%.", bullet))
story.append(Paragraph("• ROC-AUC tells us how good the model is at <i>ranking</i> risk — useful no matter where the coach sets the threshold.", bullet))
story.append(Paragraph("• It is also threshold-independent and works well even if classes are imbalanced.", bullet))
story.append(Paragraph(
    "Think of accuracy as 'did you pass the test?' and ROC-AUC as 'how confidently were your answers right?'", note))

# Section 3
story.append(Paragraph("3. Why Logistic Regression won (the simple version)", h2))
story.append(Paragraph(
    "Before training, we created smart features by hand: <b>ACWR</b> (workload ratio), <b>Recovery_Score</b>, <b>Fatigue_Index</b>, and <b>Injury_Frequency_Score</b>. "
    "These already mix sleep, stress, workload, and prior injuries into meaningful numbers.", body))
story.append(Paragraph("Other reasons Logistic Regression came out on top:", body))
story.append(Paragraph("• <b>Small dataset (800 players).</b> Simple models beat complex ones when data is limited — fewer parameters means less overfitting.", bullet))
story.append(Paragraph("• <b>Calibrated probabilities.</b> Logistic Regression outputs natural probabilities (0 to 1), which is exactly what ROC-AUC rewards.", bullet))
story.append(Paragraph("• <b>Pre-cooked features.</b> The non-linear patterns were already baked into the engineered columns, so a straight-line decision was enough.", bullet))
story.append(Paragraph("• <b>Stable training.</b> Linear models are not picky about hyperparameters; trees and boosting need careful tuning we didn't do.", bullet))
story.append(Paragraph("• <b>Less noise sensitivity.</b> With only 640 training rows, boosting models started fitting noise — logistic regression ignored it.", bullet))

story.append(PageBreak())

# Section 4
story.append(Paragraph("4. Correlation Analysis — reading the heatmap", h2))
story.append(Paragraph(
    "A correlation heatmap is a grid of colored squares. Each square shows how strongly two features move together. The numbers go from -1 to +1.", body))
story.append(Paragraph("<b>How to read the colors:</b>", body))
story.append(Paragraph("• <b>Deep red (+1):</b> when one feature goes up, the other goes up too.", bullet))
story.append(Paragraph("• <b>Deep blue (-1):</b> when one goes up, the other goes down.", bullet))
story.append(Paragraph("• <b>Near white (0):</b> no relationship.", bullet))
story.append(Paragraph("• The diagonal is always +1 because every feature perfectly correlates with itself.", bullet))
story.append(Paragraph("<b>What we learned from our heatmap:</b>", body))
story.append(Paragraph("• <b>No single feature is a giveaway.</b> The biggest correlations with Injury_Next_Season are modest (around 0.1 to 0.3). That tells us injury is a combination story, not a one-cause story.", bullet))
story.append(Paragraph("• <b>Our engineered features lead.</b> Fatigue_Index and Injury_Frequency_Score top the list, proving the feature engineering added real signal.", bullet))
story.append(Paragraph("• <b>Physical tests cluster together.</b> Knee strength, hamstring flexibility, balance, agility — fit athletes score well across the board, so these features overlap. Models will pick one and ignore the redundant ones.", bullet))
story.append(Paragraph(
    "Quick rule of thumb: |corr| > 0.7 = strong, 0.3 to 0.7 = moderate, < 0.3 = weak.", note))

# Section 5
story.append(Paragraph("5. SHAP / Shapley values — explained simply", h2))
story.append(Paragraph(
    "Imagine the model is a team and each feature is a teammate. After the team scores (makes a prediction), Shapley values fairly split the credit: how much did each teammate contribute? "
    "This idea comes from game theory and Nobel laureate Lloyd Shapley.", body))
story.append(Paragraph("<b>The math in one line:</b> Final prediction = average risk + sum of every feature's SHAP value.", body))
story.append(Paragraph("<b>The summary (beeswarm) plot:</b>", body))
story.append(Paragraph("• Y-axis: features ranked by importance (top = most important).", bullet))
story.append(Paragraph("• X-axis: SHAP value — right of zero = pushes toward 'injured', left = pushes toward 'healthy'.", bullet))
story.append(Paragraph("• Color: red dot = high feature value, blue dot = low feature value.", bullet))
story.append(Paragraph("• Each dot = one player.", bullet))
story.append(Paragraph(
    "Example: in the Previous_Injury_Count row, red dots cluster on the right — meaning a high prior-injury count pushes the model to predict injury. "
    "In Recovery_Score, red dots cluster on the left — high recovery protects the player.", body))
story.append(Paragraph("<b>The bar plot:</b> the same info, but only shows the average size of impact per feature — pure importance ranking.", body))
story.append(Paragraph("<b>The waterfall plot:</b> for one single player, it stacks each feature's contribution from the base rate up to the final risk number. Red bars push risk up, blue bars push it down. This is what a medic would show a player to justify a recommendation.", body))
story.append(Paragraph(
    "Why this matters: it turns the model from a black box into an auditable decision-maker. Useful for GDPR, useful for coaches.", note))

story.append(PageBreak())

# Section 6
story.append(Paragraph("6. Machine Unlearning (SISA) — explained simply", h2))
story.append(Paragraph(
    "Under GDPR, a player can say: <i>'Delete my data and remove my influence from your model.'</i> "
    "Retraining the whole model from scratch every time someone asks is slow and expensive. SISA solves this.", body))
story.append(Paragraph("<b>SISA = Sharded, Isolated, Sliced, Aggregated.</b>", body))
story.append(Paragraph("• <b>Sharded:</b> Split the training data into N small chunks (we used 5 chunks).", bullet))
story.append(Paragraph("• <b>Isolated:</b> Train one separate mini-model on each chunk. No chunk shares data with another.", bullet))
story.append(Paragraph("• <b>Sliced:</b> (optional) save checkpoints inside each chunk so you can rewind quickly.", bullet))
story.append(Paragraph("• <b>Aggregated:</b> When predicting, average the answers from all mini-models.", bullet))
story.append(Paragraph("<b>The unlearning trick:</b> If player X wants to be forgotten, only the chunk they belonged to needs retraining. Other chunks stay untouched. Expected speedup: roughly N times faster.", body))

data2 = [
    ["Method", "Accuracy", "ROC-AUC", "Time (s)"],
    ["Full retraining", "0.9563", "0.9922", "0.148"],
    ["SISA unlearning", "0.9375", "0.9855", "0.116"],
]
t2 = Table(data2, hAlign="LEFT", colWidths=[4.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
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
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Result:</b> SISA was about 22% faster while losing almost no accuracy. The speedup was modest because 54 deletion requests were spread across all 5 chunks — every chunk needed retraining. "
    "If deletion requests were grouped in fewer chunks, the speedup would be much bigger.", body))
story.append(Paragraph(
    "<b>The trade-off:</b> Each mini-model sees less data, so the ensemble is slightly weaker than one giant model — but in return we get fast, provable forgetting.", body))

# Final TL;DR
story.append(Paragraph("7. TL;DR", h2))
story.append(Paragraph("• Logistic Regression won (ROC-AUC = 0.9961). Random Forest 2nd, LightGBM 3rd, XGBoost 4th.", bullet))
story.append(Paragraph("• ROC-AUC was preferred over accuracy because it measures ranking quality across all thresholds.", bullet))
story.append(Paragraph("• The smart engineered features (Fatigue, Recovery, ACWR, Injury Frequency) gave Logistic Regression an edge.", bullet))
story.append(Paragraph("• The heatmap showed no single feature dominates — injury is a multi-factor story.", bullet))
story.append(Paragraph("• SHAP makes individual predictions explainable using a game-theory credit-splitting idea.", bullet))
story.append(Paragraph("• SISA lets us delete a player's influence quickly without retraining everything from scratch.", bullet))

doc.build(story)
print(f"Created {out}")
