import os
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import kube
import data_parsers

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN")
)
kube_api = kube.Kube_api()

@app.message("start")
def message_hello(message, say):
    say(
        blocks=[
            {
                "type": "actions",
                "elements": [
                    {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Dashboard count"},
                    "action_id": "dashboard_count"
                    },
                    {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "List dashboards"},
                    "action_id": "dashboard_list"
                    },
                    {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Alerts missing notif channels"},
                    "action_id": "dashboard_alerts"
                    },
                    {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Alerts missing runbook link"},
                    "action_id": "dashboard_runbook"
                    }
                ]
            }
        ],
        text=f"Action selector"
    )

@app.action("dashboard_count")
def action_dashboard_count(ack, say):
    res = len(data_parsers.get_object_names(kube_api.list_custom_objects_all()))
    ack()
    say(f"Dashboard count: {res}")

@app.action("dashboard_list")
def action_dashboard_list(ack):
    res = data_parsers.get_object_names(kube_api.list_custom_objects_all())
    with open('data.txt', 'w') as f:
        for item in res:
            f.write(item + "\n")
    ack()
    app.client.files_upload(
        channels="dashboard-checker",
        file="data.txt",
        filename="data.txt",
        filetype="text"
    )

@app.action("dashboard_alerts")
def action_dashboard_alerts(ack):
    res = kube_api.list_custom_objects_all()
    dashboard_dict = data_parsers.generate_dashboard_dict(res)

    with open('data.txt', 'w') as f:
        for key in dashboard_dict:
            for a in data_parsers.find_json_key("alert", dashboard_dict[key]):
                if  len(a['notifications']) < 3 and len(a['notifications']) != 0:
                    if (len(a['notifications']) == 1) and (a['notifications'][0]['uid'] in ['iot_alerts_slack', 'stream_performance_alerts_slack', 'operational_intelligence_alerts_slack', 'p3_alert', 'opslegends_slack', 'alerts_critical_production']):
                        continue
                    f.write("-- " + a['name'] + " --" + "\n")
                    for notif in a['notifications']:
                        f.write(str(notif['uid']) + " ")
                    f.write("\n")
                    if "alertRuleTags" in a:
                        f.write(str(a['alertRuleTags']))
                    f.write("\n")

    ack()
    app.client.files_upload(
        channels="dashboard-checker",
        file="data.txt",
        filename="data.txt",
        filetype="text"
    )

@app.action("dashboard_runbook")
def action_dashboard_runbook(ack):
    res = kube_api.list_custom_objects_all()
    dashboard_dict = data_parsers.generate_dashboard_dict(res)

    with open('data.txt', 'w') as f:
        for key in dashboard_dict:
            for a in data_parsers.find_json_key("alert", dashboard_dict[key]):
                for notifier in a['notifications']:
                    if  ('jira_notifier' in notifier['uid']):
                        try:
                            if 'https' not in a['message']:
                                # f.write("-- " + a['name'] + " -- " + a['message'] + "\n")
                                f.write("-- " + a['name'] + "\n")
                        except KeyError:
                            f.write("-- " + a['name'] + " -- " + 'no message' + "\n")

    ack()
    app.client.files_upload(
        channels="dashboard-checker",
        file="data.txt",
        filename="data.txt",
        filetype="text"
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
