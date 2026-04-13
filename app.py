from flask import Flask, render_template_string
from utils.db import get_logs

app = Flask(__name__)

HTML = """
<h1>NovaX Mod Dashboard</h1>
<table border="1" cellpadding="5">
<tr>
<th>ID</th><th>User</th><th>Moderator</th><th>Action</th><th>Reason</th><th>Time</th>
</tr>
{% for log in logs %}
<tr>
<td>{{log[0]}}</td>
<td>{{log[1]}}</td>
<td>{{log[2]}}</td>
<td>{{log[3]}}</td>
<td>{{log[4]}}</td>
<td>{{log[5]}}</td>
</tr>
{% endfor %}
</table>
"""

@app.route("/")
def home():
    logs = get_logs()
    return render_template_string(HTML, logs=logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
