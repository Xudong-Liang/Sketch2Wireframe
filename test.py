import paddlex as pdx
if __name__ == '__main__':
    model = pdx.load_model("./Ours")
    img = './e687de707be2742f.jpg'
    result = model.predict(img)
    pdx.det.visualize(img, result, save_dir='./')