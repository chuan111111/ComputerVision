# djangoProject/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .form import ImageUploadForm
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