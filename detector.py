from pprint import pprint
import cv2
import os
ROOT = '/root/Desktop/pictures'# путь к лицам
FACES = '/root/Desktop/faces'# место где сохранять обработаные фото
TRAIN = '/root/Desktop/training'# мозг обнаружения лиц


def detect(srcdir=ROOT, tgtdir=FACES, train_dir=TRAIN):
    for fname in os.listdir(srcdir):  # перебираем имена картинок директории
        if not fname.upper().endswith('.JPG'): # если файл не оканчивается на .JPG пропускаем файл
            continue
        fullname = os.path.join(srcdir, fname) # полный путь к фото
        newname = os.path.join(tgtdir, fname) # место куда мы его сохраним
        img = cv2.imread(fullname) # превращаем фото в массив пикселей и храним в оперативной памяти
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # делаем картинку черно-белой
        training = os.path.join(train_dir, 'haarcascade_frontalface_alt.xml')
        cascade = cv2.CascadeClassifier(training) # создаем мозг обнаружения лиц
        rects = cascade.detectMultiScale(gray, 1.3, 5) # сканируем картинку возвращает x y ширина высота
        try:
            if rects.any():
                print('got a face')
                rects[:, 2:] += rects[:, :2] # в ширину и высоты добавляет x и y для двух точек сверху справа и снизу слева
        except AttributeError:
            print(f'No faces found in {fname}')
            continue
            # highlight the faces in the image
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2) # делаем обводку в цвете
        cv2.imwrite(newname, img) # и сохраняем в цветном изображении

if __name__ == '__main__':
    detect()
