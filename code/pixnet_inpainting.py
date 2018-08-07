import os
import numpy as np
import argparse
import warnings
import requests
from io import BytesIO
import base64
import attr
import skimage.io as ski_io
import skimage.color as ski_color
import skimage.morphology as ski_morph
import subprocess

@attr.s
class FoodQuiz:
    question_id = attr.ib()
    raw_image = attr.ib()
    bbox = attr.ib()
    description = attr.ib()


# 從 PIXNET 拿到比賽題目
def get_image(question_id, img_header=True):
    endpoint = 'http://pixnethackathon2018-competition.events.pixnet.net/api/question'
    payload = dict(question_id=question_id, img_header=img_header)
    print('Step 1: 從 PIXNET 拿比賽題目\n')
    response = requests.get(endpoint, params=payload)

    try:
        data = response.json()['data']
        question_id = data['question_id']
        description = data['desc']
        bbox = data['bounding_area']
        encoded_image = data['image']
        raw_image = ski_io.imread(
            BytesIO(base64.b64decode(encoded_image[encoded_image.find(',')+1:]))
        )

        header = encoded_image[:encoded_image.find(',')]
        if 'bmp' not in header:
            raise ValueError('Image should be BMP format')

        print('題號：', question_id)
        print('文字描述：', description)
        print('Bounding Box:', bbox)
        print('影像物件：', type(raw_image), raw_image.dtype, ', 影像大小：', raw_image.shape)

        quiz = FoodQuiz(question_id, raw_image, bbox, description)

    except Exception as err:
        # Catch exceptions here...
        print(data)
        raise err

    print('=====================')

    return quiz


# 使用你的模型，補全影像
def inpainting(quiz, debug=True):

    print('Step 2: 使用你的模型，補全影像\n')
    print('...')
    
    # 1. Generate mask image from source image
    
    raw_image = quiz.raw_image.copy()
    bbox = quiz.bbox
    mean_color = quiz.raw_image.mean(axis=(0, 1))  # shape: (3,)

    raw_roi = raw_image[bbox['y']:bbox['y']+bbox['h'], bbox['x']:bbox['x']+bbox['w'], :]

    mask = np.zeros(raw_image.shape[:2])
    mask_roi = mask[bbox['y']:bbox['y']+bbox['h'], bbox['x']:bbox['x']+bbox['w']]

    to_filling = (raw_roi[:, :, 1] == 255) & (raw_roi[:, :, 0] < 10) & (raw_roi[:, :, 2] < 10)
    mask_roi[to_filling] = 1

    mask = ski_morph.dilation(mask, ski_morph.square(7))
    mask = np.expand_dims(mask, axis=-1)

    # 2. save to png file
    img_path = f'output/{quiz.question_id}_raw_image.png'
    mask_path = f'output/{quiz.question_id}_mask.png'
    
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=UserWarning)
        os.makedirs('output', exist_ok=True)
        ski_io.imsave(img_path, raw_image, quality=100)
        ski_io.imsave(mask_path, mask[:, :, 0], quality=100)    

    # 3. Call generative_inpainting model from CLI, this model will complete image and save to png file.    
    os.makedirs('output', exist_ok=True)
    output_path = f'output/{quiz.question_id}_gen_image.png'
    model_path = 'generative_inpainting/models_logs/20180806124027737769_6c140319b0ee_pixfood20_NORMAL_wgan_gp_pixfood20/'
    
    cli = ['python', './generative_inpainting/test.py',
           '--image', img_path,
           '--mask', mask_path,
           '--output', output_path,
           '--checkpoint', model_path]
    
    res = subprocess.call(cli)
    
    # 4. Load completed file and return gen_image array date type 
    if res == 0:
        print('run DeepFillv1 successfully.')
        gen_image = ski_io.imread(output_path)
    else:v
        gen_image = quiz.raw_image
        print('Run DeepFillv1 error!')
        
    print('=====================')

    return gen_image


# 上傳答案到 PIXNET
def submit_image(image, question_id):
    print('Step 3: 上傳答案到 PIXNET\n')

    endpoint = 'http://pixnethackathon2018-competition.events.pixnet.net/api/answer'

    key = os.environ.get('PIXNET_FOODAI_KEY')

    # Assign image format
    image_format = 'jpeg'
    with BytesIO() as f:
        ski_io.imsave(f, image, format_str=image_format)
        f.seek(0)
        data = f.read()
        encoded_image = base64.b64encode(data)
    image_b64string = 'data:image/{};base64,'.format(image_format) + encoded_image.decode('utf-8')

    payload = dict(question_id=question_id,
                   key=key,
                   image=image_b64string)
    response = requests.post(endpoint, json=payload)
    try:
        rdata = response.json()
        if response.status_code == 200 and not rdata['error']:
            print('上傳成功')
        print('題號：', question_id)
        print('回答截止時間：', rdata['data']['expired_at'])
        print('所剩答題次數：', rdata['data']['remain_quota'])

    except Exception as err:
        print(rdata)
        raise err
    print('=====================')


parser = argparse.ArgumentParser(
    description='''
    PIXNET HACKATHON 競賽平台測試 0731 版.
    測試流程： `get_image` --> `inpainting` --> `submit_image`
    1. `get_image`: 取得測試題目，必須指定題目編號。
    2. `inpainting`: 參賽者的補圖邏輯實作在這一個 stage
    3. `submit_image`: 將補好的圖片與題號，提交回server，透過 PIXNET 核發的 API token 識別身份，故 token 請妥善保存。

    執行範例1：
        $ bash -c "export PIXNET_FOODAI_KEY=<YOUR-API-TOKEN>; python api_test_0731.py --qid 1"

    執行範例2:
        a. 將 API-TOKEN 如以下形式寫入某檔案，例如 .secrets.env 並存檔。
            export PIXNET_FOODAI_KEY=<YOUR-API-TOKEN>
        b. 執行:
        $ bash -c "source .secrets.env; python api_test_0731.py --qid 1"

    API 文件：https://github.com/pixnet/2018-pixnet-hackathon/blob/master/opendata/food.competition.api.md
    競賽平台位置：http://pixnethackathon2018-competition.events.pixnet.net/''',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('--qid', metavar='qid', nargs='?', type=int, default=1, help='題目編號(int)')

if __name__ == '__main__':
    args = parser.parse_args()
    quiz = get_image(args.qid)
    gen_image = inpainting(quiz)
    submit_image(gen_image, quiz.question_id)
    print('Done... Waiting for next round.')
