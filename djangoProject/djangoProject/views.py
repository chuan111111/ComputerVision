# djangoProject/views.py
import shutil

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .form import ImageUploadForm
from . import settings
import os
from deepface import DeepFace
from PIL import Image

import time
import tempfile


def upload_image(request):
    if request.method == 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    else:
        timestamp = int(time.time())
        return render(request, 'upload.html', {'timestamp': timestamp})


def upload_and_compare(request):
    if request.method == 'POST':
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        print(1)
        if not image1 or not image2:
            return JsonResponse({'error': 'Both images are required.'}, status=400)

        try:
            # 使用PIL打开图片
            img1 = Image.open(image1)
            img2 = Image.open(image2)

            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp1, tempfile.NamedTemporaryFile(
                    suffix='.png', delete=False) as temp2:
                # 将图片保存到临时文件
                img1.save(temp1, format='PNG')
                img2.save(temp2, format='PNG')

                temp1.flush()
                temp2.flush()

                # 使用DeepFace进行比较
                resp = DeepFace.verify(img1_path=temp1.name, img2_path=temp2.name, model_name='VGG-Face')

                return JsonResponse(resp)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def face_find(request):
    if request.method == 'POST':
        image = request.FILES.get('image')

        print(2)
        if not image :
            return JsonResponse({'error': 'image are required.'}, status=400)

        try:
            # image1_path = 'dataset/img.png'
            # resp = DeepFace.find(img_path=image1_path,
            #                      db_path="D:/Users/hasee/Documents/GitHub/ComputerVision/djangoProject/dataset",
            #                      model_name='VGG-Face', distance_metric='cosine')
            # print(resp)
            # 使用PIL打开图片
            img = Image.open(image)

            print('image ok')
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                # 将图片保存到临时文件
                img.save(temp, format='PNG')
                temp.flush()
                print('ok')

                # 使用DeepFace进行比较
                resp = DeepFace.find(img_path=temp.name, db_path="D:/Users/hasee/Documents/GitHub/ComputerVision/djangoProject/dataset",model_name='VGG-Face', distance_metric='cosine')
                print(resp[0]['identity'][0])
                print(len(resp[0]['identity']))
                if len(resp[0]['identity']) > 0:
                    matched = resp[0]['identity'][0]
                    # print(matched)
                    # return JsonResponse({'matched_image': matched})
                    filename = os.path.basename(matched)
                    media_path = os.path.join(settings.MEDIA_ROOT, filename)
                    shutil.copy(matched, media_path)

                    # 返回媒体文件的URL
                    matched_url = settings.MEDIA_URL + filename
                    return JsonResponse({'matched_image': matched_url})
                else:
                    return JsonResponse({'error': 'No matching faces found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def face_search(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        print(2)  # 调试信息
        if not image:
            return JsonResponse({'error': 'Image is required.'}, status=400)

        try:
            img = Image.open(image)

            print("Image opened successfully")  # 调试信息
            with tempfile.NamedTemporaryFile(dir='./media/images', suffix='.png', delete=False) as temp:
                img.save(temp, format='PNG')
                temp.flush()

                print(f"Image saved to temporary file: {temp.name}")  # 调试信息
                faces = DeepFace.extract_faces(img_path=temp.name, detector_backend='opencv')
                print(f"Faces detected: {len(faces)}")  # 调试信息

                face_num = len(faces)

                return JsonResponse({'face_num': face_num}, status=200)
        except Exception as e:
            print(f"Exception occurred: {e}")  # 调试信息
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def face_analyse(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        print(3)  # 调试信息
        if not image:
            return JsonResponse({'error': 'Image is required.'}, status=400)

        try:
            img = Image.open(image)

            print("Image opened successfully")  # 调试信息
            with tempfile.NamedTemporaryFile(dir='./media/images', suffix='.png', delete=False) as temp:
                img.save(temp, format='PNG')
                temp.flush()

                print(f"Image saved to temporary file: {temp.name}")  # 调试信息
                faces = DeepFace.analyze(img_path=temp.name, detector_backend='opencv')

                return JsonResponse(
                    {'age': faces[0]['age'], 'gender': max(faces[0]['gender'], key=lambda k: faces[0]['gender'][k]),
                     'emotion': max(faces[0]['emotion'], key=lambda k: faces[0]['emotion'][k]),
                     'race': max(faces[0]['race'], key=lambda k: faces[0]['race'][k])}, status=200)
        except Exception as e:
            print(f"Exception occurred: {e}")  # 调试信息
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def show_dataset(request):
    test_dataset_dir = os.path.join(settings.VGG2_FACE_DIR, 'vggface2_test/test/')
    test_dataset_dir1 = os.path.join(test_dataset_dir, 'n000001/')
    images = [f for f in os.listdir(test_dataset_dir1) if os.path.isfile(os.path.join(test_dataset_dir1, f))]
    DeepFace.analyze()
    # 将图片路径传递到模板
    context = {
        'images': images,
        'dataset_dir': test_dataset_dir1
    }
    return render(request, 'show_dataset.html', context)
