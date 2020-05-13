import boto3
import colorsys


configuration = json.loads(
    boto3.client("secretsmanager").get_secret_value(
        SecretId=os.environ.get("SECRET_ARN")
        ).get("SecretString")
    )
team="TUTSYURT3",
channel="G012HLGCNKY",

def label(self, kind, value):
    def color(string):
        golden_ratio = 5 ** .5 * .5 + .5
        number = sum(hashlib.sha256(string.encode("utf-8")).digest()) / 256 * 32
        color = colorsys.hsv_to_rgb((number + golden_ratio) % 1, 0.5, 0.95)
        return "#{:x}{:x}{:x}".format(*color)
    labels = workstreams.labels.fetch_team_labels(
        ws_user_id=self.user,
        team_id=self.team
        )
    matches = [
        item["labelId"]
        for item in labels
        if [item["kind"], item["textValue"]] == [kind, value]
        ]
    return matches[0] if matches else workstreams.labels.create(
        ws_user_id=self.user,
        team_id=self.team,
        data={
            "color": color(kind),
            "teamId": self.team,
            "textValue": value,
            "kind": kind
            })["labelId"]


def task(self, title, labels, description):
    labels = [self.label("pragma", "once")] + [
        self.label(*item) for item in labels
        ]
    data = {
        "title": title,
        "labels": labels,
        "description": description
        }
    tasks = workstreams.tasks.fetch_user_tasks(
        ws_user_id=self.user,
        user_id=self.user,
        team_id=self.team
        )
    matches = [
        item["taskId"]
        for item in tasks
        if self.label("pragma", "once") in item.get("labels", [])
        ]
    if matches:
        return workstreams.tasks.update(
            task_id=matches[0],
            ws_user_id=self.user,
            data=data
            )["taskId"]
    else:
        return workstreams.tasks.create(
            data={**data, "assignee": self.user},
            channel_id=self.channel,
            ws_user_id=self.user,
            team_id=self.team
            )["taskId"]
