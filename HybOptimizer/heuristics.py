from flask import Flask, request
import json
import cv2
import numpy as np

app = Flask(__name__)


def isContain(e1, e2):
    w = min(e2["bbox"][0] + e2["bbox"][2], e1["bbox"][0] + e1["bbox"][2]) - max(e1["bbox"][0], e2["bbox"][0])
    h = min(e2["bbox"][1] + e2["bbox"][3], e1["bbox"][1] + e1["bbox"][3]) - max(e1["bbox"][1], e2["bbox"][1])
    if w <= 0 or h <= 0:
        return 0, w, h
    elif w * h / e2['area'] > 0.8:
        return 1, w, h
    else:
        return 0.5, w, h


def downSeparate(e1, e2):
    if e1['bbox'][1] < e2['bbox'][1]:
        delta_h = e1['bbox'][3] - abs(e1['bbox'][1] - e2['bbox'][1])
        t = e2['bbox'][1]
    elif e1['bbox'][1] > e2['bbox'][1]:
        delta_h = e2['bbox'][3] - abs(e1['bbox'][1] - e2['bbox'][1])
        t = e1['bbox'][1]
    else:
        delta_h = 0
        t = e1['bbox'][1]
    return delta_h, t


def rightSeparate(e1, e2):
    if e1['bbox'][0] < e2['bbox'][0]:
        delta_w = e1['bbox'][2] - abs(e1['bbox'][0] - e2['bbox'][0])
        t = e2['bbox'][0]
    elif e1['bbox'][0] > e2['bbox'][0]:
        delta_w = e2['bbox'][2] - abs(e1['bbox'][0] - e2['bbox'][0])
        t = e1['bbox'][0]
    else:
        delta_w = 0
        t = e1['bbox'][0]
    return delta_w, t


data = []


@app.route('/sketch', methods=['POST'])
def register():
    import paddlex as pdx
    from copy import deepcopy
    model = pdx.load_model("./model")
    data0 = request.stream.read()
    img1 = np.frombuffer(data0, np.uint8)
    img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)
    cv2.imwrite('./test/test.jpg', img_cv)
    img = './test/test.jpg'
    result = model.predict(img)
    print('result=', result)
    pdx.det.visualize(img, result, save_dir='./test')
    global data
    data = []
    # 预处理
    for obj in result:
        element = {}
        if obj['score'] > 0.5:
            if obj['category'] == 'linebreak':
                x, y, w, h = round(obj['bbox'][0]), round(obj['bbox'][1]), round(obj['bbox'][2]), 6
            else:
                x, y, w, h = round(obj['bbox'][0]), round(obj['bbox'][1]), round(obj['bbox'][2]), round(
                    obj['bbox'][3])
            element['category'] = obj['category']
            element['bbox'] = [x, y, w, h]
            element['area'] = element['bbox'][2] * element['bbox'][3]
            data.append(element)
            cv2.rectangle(img_cv, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
    cv2.imwrite('./test/bbox.jpg', img_cv)
    # 1.容器划分
    data.sort(key=lambda x: x['area'])
    if data[-1]['category'] == 'container':
        data.remove(data[-1])
    sectioned = []
    for e1 in data:
        sectioned_copy = deepcopy(sectioned)
        contains = []
        for e2 in sectioned:
            overlap, w, h = isContain(e1, e2)
            if overlap == 1 and e2['area'] < e1['area']:
                for e3 in sectioned_copy:
                    if e3 == e2:
                        break
                if e2['bbox'][0] < e1['bbox'][0]:
                    e2['bbox'][0] = e1['bbox'][0]
                if e2['bbox'][1] < e1['bbox'][1]:
                    e2['bbox'][1] = e1['bbox'][1]
                e2['bbox'][2], e2['bbox'][3], e2['area'] = w, h, w * h
                contains.append(e2)
                sectioned_copy.remove(e3)
        sectioned = sectioned_copy
        e1["child"] = contains
        sectioned.append(e1)
    data = deepcopy(sectioned)
    container = 0
    for e in data:
        if e['child']:
            container += 1
    print('容器划分：', data)
    print('容器个数：', container)
    # 生成root节点
    data1 = deepcopy(data)
    data1.sort(key=lambda x: x['bbox'][0])
    x = data1[0]['bbox'][0] - 40
    data1.sort(key=lambda x: x['bbox'][1])
    y = data1[0]['bbox'][1] - 40
    y_h = []
    x_w = []
    for e in data1:
        x_w.append(e['bbox'][0] + e['bbox'][2])
        y_h.append(e['bbox'][1] + e['bbox'][3])
    w, h = max(x_w) + 40 - x, max(y_h) + 40 - y
    for e in data:
        if e['bbox'][2] / (w - 40) > 0.8:
            e['bbox'][2] = w - 80
            e['area'] = e['bbox'][0] * e['bbox'][1]
    print('最终：', data)
    root = {'category': 'container'}
    root['bbox'] = [x, y, w, h]
    root['area'] = w * h
    root['child'] = data
    print('[root]=', data)
    return json.dumps([root], ensure_ascii=False)


@app.route('/optimiser', methods=['POST'])
def optimiser():
    dropdown_rate = 0.304
    import paddlex as pdx
    from copy import deepcopy
    model = pdx.load_model("./MSA_model")
    data0 = request.stream.read()
    img1 = np.frombuffer(data0, np.uint8)
    img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)
    cv2.imwrite('./test/test.jpg', img_cv)
    img = './test/test.jpg'
    result = model.predict(img)
    print('result=', result)
    pdx.det.visualize(img, result, save_dir='./test')
    global data
    data = []
    # 预处理
    for obj in result:
        element = {}
        if obj['score'] > 0.5:
            if obj['category'] == 'linebreak':
                x, y, w, h = round(obj['bbox'][0]), round(obj['bbox'][1]), round(obj['bbox'][2]), 6
            else:
                x, y, w, h = round(obj['bbox'][0]), round(obj['bbox'][1]), round(obj['bbox'][2]), round(
                    obj['bbox'][3])
            element['category'] = obj['category']
            element['bbox'] = [x, y, w, h]
            element['area'] = element['bbox'][2] * element['bbox'][3]
            data.append(element)
            cv2.rectangle(img_cv, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
    cv2.imwrite('./test/bbox.jpg', img_cv)
    # 1.容器划分
    data.sort(key=lambda x: x['area'])
    if data[-1]['category'] == 'container':
        data.remove(data[-1])
    sectioned = []
    for e1 in data:
        sectioned_copy = deepcopy(sectioned)
        contains = []
        for e2 in sectioned:
            overlap, w, h = isContain(e1, e2)
            if overlap == 1 and e2['area'] < e1['area']:
                for e3 in sectioned_copy:
                    if e3 == e2:
                        break
                if e2['bbox'][0] < e1['bbox'][0]:
                    e2['bbox'][0] = e1['bbox'][0]
                if e2['bbox'][1] < e1['bbox'][1]:
                    e2['bbox'][1] = e1['bbox'][1]
                e2['bbox'][2], e2['bbox'][3], e2['area'] = w, h, w * h
                contains.append(e2)
                sectioned_copy.remove(e3)
        sectioned = sectioned_copy
        e1["child"] = contains
        sectioned.append(e1)
    data = deepcopy(sectioned)
    container = 0
    for e in data:
        if e['child']:
            container += 1
    print('容器划分：', data)
    print('容器个数：', container)

    return json.dumps(container, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
