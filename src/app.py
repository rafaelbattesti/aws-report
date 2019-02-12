import os, boto3, requests, json
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

@app.route('/aws/ec2/doTag', methods=['GET'])
def do_tag():
    account_id = request.args.get('account_id')
    return jsonify({"Response": account_id})

@app.route('/aws/ec2/doReap', methods=['GET'])
def do_reap():
    return jsonify({"Response" : [{"InstanceId" : "i-ue8376sbu", "Status" : "Stopped"}]})

@app.route('/aws/ec2/report', methods=['GET'])
def report():
    do_validate(request)
    return post_response(build_report())

@app.errorhandler(404)
def not_found(error):
    return jsonify({"Status": "Not found"})

@app.errorhandler(401)
def custom_401(error):
    return jsonify({"Status": "Not unauthorized"})

def do_validate(request):
    token = request.form['token']
    if token != os.getenv('SLACK_TOKEN'):
        abort(401)

def post_response(text):
    slack_data = {}
    slack_data['text'] = text
    requests.post(
        os.getenv('SLACK_URL'), data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

def get_instances():
    ec2 = boto3.resource('ec2')
    return ec2.instances.all()

def get_volumes():
    ec2 = boto3.resource('ec2')
    return ec2.volumes.all()

def get_regions():
    ec2 = boto3.client('ec2')
    return ec2.describe_regions

def get_tag(tags, tag_name):
    for tag in tags:
        k = tag['Key']
        v = tag['Value']
        if (k == tag_name):
            return v

def get_instance_map(instances):
    i_map = {}
    for i in instances:
        iid = i.instance_id
        iname = get_tag(i.tags, 'Name')
        itype = i.instance_type
        i_map[iid] = iname + ',' + itype
    return i_map

def get_volume_map(volumes):
    v_map = {}
    for v in volumes:
        att = v.attachments
        type = v.volume_type
        size = str(v.size)
        for a in att:
            if a:
                iid = a['InstanceId']
                v_map[iid] = type + ',' + size
    return v_map

def build_report():
    i_map = get_instance_map(get_instances())
    v_map = get_volume_map(get_volumes())
    text = ''
    for k, v in i_map.items():
        if k in v_map:
            text = text + v + ',' + v_map[k] + '\n'
    return text

if __name__ == '__main__':
    app.run(debug=True)