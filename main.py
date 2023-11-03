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
element_list = []

@app.route('/upload', methods=['POST'])
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
    pdx.det.visualize(img, result, save_dir='./test')
    global data
    data = []

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
    root = {'category': 'container', 'bbox': [x, y, w, h], 'area': w * h, 'child': data}
    global element_list
    element_list = deepcopy([root])
    return json.dumps([root], ensure_ascii=False)


@app.route('/draft', methods=['POST'])
def draft():
    global element_list
    return json.dumps(element_list, ensure_ascii=False)


@app.route('/heuristics', methods=['POST'])
def heuristics():
    from copy import deepcopy
    global data
    dropdown_rate = 0.304

    data.sort(key=lambda x: x['bbox'][1])
    i = 1
    c1 = [data[0]]
    while i < len(data):
        if data[i]['category'] in ['linebreak']:
            for e in c1:
                for x in data:
                    if e == x:
                        if e['child']:
                            delta_y = x['bbox'][1] - c1[0]['bbox'][1]
                            for child in e['child']:
                                child['bbox'][1] -= delta_y
                        x['bbox'][1] = c1[0]['bbox'][1]
            i += 1
            c1 = [data[i]]
        if data[i]['bbox'][1] - data[i - 1]['bbox'][1] < min(data[i]['bbox'][3], data[i - 1]['bbox'][3]) / 4:
         
            if abs(data[i]['bbox'][3] - data[i - 1]['bbox'][3]) < min(data[i]['bbox'][3], data[i - 1]['bbox'][3]) / 2:
                data[i]['bbox'][3] = min(data[i]['bbox'][3], data[i - 1]['bbox'][3])
                data[i - 1]['bbox'][3] = min(data[i]['bbox'][3], data[i - 1]['bbox'][3])
                data[i]['area'] = data[i]['bbox'][2] * data[i]['bbox'][3]
                data[i - 1]['area'] = data[i - 1]['bbox'][2] * data[i - 1]['bbox'][3]
            c1.append(data[i])
        else:
            for e in c1:
                for x in data:
                    if e == x:
                        if e['child']:
                            delta_y = x['bbox'][1] - c1[0]['bbox'][1]
                            for child in e['child']:
                                child['bbox'][1] -= delta_y
                        x['bbox'][1] = c1[0]['bbox'][1]
            c1 = [data[i]]
        i += 1
 
    data.sort(key=lambda x: x['bbox'][0])
    i = 1
    c1 = [data[0]]
    while i < len(data):
        if data[i]['bbox'][0] - data[i - 1]['bbox'][0] < min(data[i]['bbox'][2], data[i - 1]['bbox'][2]) / 4:
          
            if abs(data[i]['bbox'][2] - data[i - 1]['bbox'][2]) < min(data[i]['bbox'][2], data[i - 1]['bbox'][2]) / 2:
                data[i]['bbox'][2] = min(data[i]['bbox'][2], data[i - 1]['bbox'][2])
                data[i - 1]['bbox'][2] = min(data[i]['bbox'][2], data[i - 1]['bbox'][2])
                data[i]['area'] = data[i]['bbox'][2] * data[i]['bbox'][3]
                data[i - 1]['area'] = data[i - 1]['bbox'][2] * data[i - 1]['bbox'][3]
            c1.append(data[i])
        else:
            for e in c1:
                for x in data:
                    if e == x:
                        if e['child']:
                            delta_x = x['bbox'][0] - c1[0]['bbox'][0]
                            for child in e['child']:
                                child['bbox'][0] -= delta_x
                        x['bbox'][0] = c1[0]['bbox'][0]
            c1 = [data[i]]
        i += 1

    length = len(data)
    for i in range(0, length):
        for j in range(i + 1, length):
            if data[i]['category'] == data[j]['category'] and data[i]['category'] != 'container':
                """if 0.8 < e1['bbox'][2]/ e2['bbox'][2] < 1.25 and 0.8 < e1['bbox'][3]/ e2['bbox'][3] < 1.25:"""
                if 0.8 < e1['area'] / e2['area'] < 1.25:
                    if data[i]['area'] > data[j]['area']:
                        data[i]['bbox'][2], data[i]['bbox'][3] = data[j]['bbox'][2], data[j]['bbox'][3]
                        data[i]['area'] = data[j]['area']
                    else:
                        data[j]['bbox'][2], data[j]['bbox'][3] = data[i]['bbox'][2], data[i]['bbox'][3]
                        data[j]['area'] = data[i]['area']
    """data1 = deepcopy(data)
    for e1 in data:
        for e2 in data1:
            if e1['category'] == e2['category']:
                if min(e1['area'], e2['area']) / max(e1['area'], e2['area']) > 0.8:
                    if e1['area'] > e2['area']:
                        e1['bbox'][2] = e2['bbox'][2]
                        e1['bbox'][3] = e2['bbox'][3]
                        e1['area'] = e2['area']"""
    """for e1 in data:
        for e2 in data:
            if e1['category'] == e2['category']:
                if e2['category'] == 'linebreak':
                    if abs(e1['bbox'][2] - e2['bbox'][2]) < min(e1['bbox'][2], e2['bbox'][2]) / 2 and abs(
                            e1['bbox'][0] - e2['bbox'][0]) < min(e1['bbox'][2], e2['bbox'][2]):
                        e1['bbox'][0] = e2['bbox'][0]
                        e1['bbox'][2] = min(e1['bbox'][2], e2['bbox'][2])
                        e2['bbox'][2] = min(e1['bbox'][2], e2['bbox'][2])
                        e1['area'], e2['area'] = e1['bbox'][2] * e1['bbox'][3], e2['bbox'][2] * e2['bbox'][3]
                elif e1['bbox'][0] == e2['bbox'][0] or e1['bbox'][1] == e2['bbox'][1]:
                    if abs(e1['area'] - e2['area']) <= min(e1['area'], e2['area']):
                        if e1['area'] < e2['area']:
                            e2['bbox'][2], e2['bbox'][3], e2['area'] = e1['bbox'][2], e1['bbox'][3], e1['area']
                            if e2['child'] != []:
                                for child in e2['child']:
                                    overlap, w, h = isContain(e2, child)
                                    if overlap != 0:
                                        child['bbox'][2], child['bbox'][3], child['area'] = w, h, w * h
                        else:
                            e1['bbox'][2], e1['bbox'][3], e1['area'] = e2['bbox'][2], e2['bbox'][3], e2['area']
                            if e1['child'] != []:
                                for child in e1['child']:
                                    overlap, w, h = isContain(e1, child)
                                    if overlap != 0:
                                        child['bbox'][2], child['bbox'][3], child['area'] = w, h, w * h"""


    """i = 1
    data1 = deepcopy(data)
    for e1 in data1:
        for e2 in data1:
            overlap, w, h = isContain(e1, e2)
            if overlap == 0.5:
                delta_h, t = downSeparate(data1[i], data1[i - 1])
                for e in data:
                    if e['bbox'][1] >= t:
                        if e['child'] != []:
                            for child in e['child']:
                                child['bbox'][1] += delta_h
                        e['bbox'][1] += delta_h"""
    i = 1
    data.sort(key=lambda x: (x['bbox'][0], x['bbox'][1]))
    while i < len(data):
        overlap, w, h = isContain(data[i], data[i - 1])
        if overlap == 0.5:
            delta_h, t = downSeparate(data[i], data[i - 1])
            for e in data:
                if e['bbox'][1] >= t:
                    if e['child']:
                        for child in e['child']:
                            child['bbox'][1] += (delta_h + 5)
                    e['bbox'][1] += (delta_h + 5)
        i += 1
    for e1 in data:
        for e2 in data:
            overlap, w, h = isContain(e1, e2)
            if overlap == 0.5:
                delta_h, t = downSeparate(e1, e2)
                for e in data:
                    if e['bbox'][1] >= t:
                        if e['child']:
                            for child in e['child']:
                                child['bbox'][1] += (delta_h + 5)
                        e['bbox'][1] += (delta_h + 5)


    i = 1
    data.sort(key=lambda x: (x['bbox'][1], x['bbox'][0]))
    while i < len(data):
        overlap, w, h = isContain(data[i], data[i - 1])
        if overlap == 0.5:
            delta_w, t = rightSeparate(data[i], data[i - 1])
            for e in data:
                if e['bbox'][0] >= t:
                    if e['child']:
                        for child in e['child']:
                            child['bbox'][0] += (delta_w + 5)
                    e['bbox'][0] += (delta_w + 5)
        i += 1

    for e in data:
        if e['category'] == 'dropdown':
            e['bbox'][2] = e['bbox'][3] / dropdown_rate
            e['area'] = e['bbox'][2] * e['bbox'][3]

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
    root = {'category': 'container', 'bbox': [x, y, w, h], 'area': w * h, 'child': data}
    return json.dumps([root], ensure_ascii=False)


@app.route('/ipOptimizer', methods=['POST'])
def ipOptimizer():
    from HybOptimizer import optimizer
    from HybOptimizer.tools import JSONLoader
    import HybOptimizer.model.SolutionManager as SolutionManager
    from HybOptimizer.model import FlexiFixPlacement
    global element_list
    structure_list = optimizer.layout_structure(element_list)
    data = JSONLoader.load_json_file(structure_list)
    sol_mgr = SolutionManager.SolutionManager()
    sol_mgr.add_solution_handler(SolutionManager.json_handler)
    model = FlexiFixPlacement(data, sol_mgr)
    return json.dumps(model, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
