import base64
from io import BytesIO
from flask import Flask, render_template, request
import matplotlib
import matplotlib.pyplot as plt
from textblob import TextBlob

matplotlib.use("Agg")

app = Flask(__name__)

history_log = []


def generate_chart(pos, neg, neu):
  labels = ["Positive", "Negative", "Neutral"]
  values = [pos, neg, neu]
  colors = ["#28a745", "#dc3545", "#ffc107"]

  fig, ax = plt.subplots(figsize=(4, 4))
  ax.pie(
      values,
      labels=labels,
      colors=colors,
      autopct="%1.1f%%",
      startangle=140,
      textprops={"fontsize": 10},
  )
  ax.axis("equal")

  buffer = BytesIO()
  plt.savefig(buffer, format="png", bbox_inches="tight", transparent=True)
  buffer.seek(0)
  image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
  plt.close(fig)
  return image_base64


@app.route("/", methods=["GET", "POST"])
def home():
  result = None
  polarity = None
  subjectivity = None
  chart_url = None
  user_text = ""

  pos_count = sum(1 for item in history_log if item["sentiment"] == "Positive")
  neg_count = sum(1 for item in history_log if item["sentiment"] == "Negative")
  neu_count = sum(1 for item in history_log if item["sentiment"] == "Neutral")

  if request.method == "POST":
    user_text = request.form.get("user_text", "")
    if user_text.strip():
      blob = TextBlob(user_text)
      polarity = round(blob.sentiment.polarity, 3)
      subjectivity = round(blob.sentiment.subjectivity, 3)

      if polarity > 0:
        result = "Positive"
      elif polarity < 0:
        result = "Negative"
      else:
        result = "Neutral"

      history_log.insert(
          0,
          {
              "text": user_text,
              "sentiment": result,
              "polarity": polarity,
              "subjectivity": subjectivity,
          },
      )

      pos_count = sum(
          1 for item in history_log if item["sentiment"] == "Positive"
      )
      neg_count = sum(
          1 for item in history_log if item["sentiment"] == "Negative"
      )
      neu_count = sum(
          1 for item in history_log if item["sentiment"] == "Neutral"
      )

  if history_log:
    chart_url = generate_chart(pos_count, neg_count, neu_count)

  return render_template(
      "index.html",
      result=result,
      polarity=polarity,
      subjectivity=subjectivity,
      user_text=user_text,
      history=history_log[:5],  
      chart_url=chart_url,
  )


if __name__ == "__main__":
  app.run(debug=True)