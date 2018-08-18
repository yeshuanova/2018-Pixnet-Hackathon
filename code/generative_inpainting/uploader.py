import argparse

import cv2
import numpy as np
import tensorflow as tf
import neuralgym as ng

from skimage import img_as_ubyte, img_as_float
import skimage.io as ski_io
import skimage.morphology as ski_morph

import pdb
from pdb import set_trace

from inpaint_model import InpaintCAModel
from pixnet_inpainting import get_image, submit_image


parser = argparse.ArgumentParser()
parser.add_argument('--output', default='output.png', type=str,
                    help='Where to write output.')
parser.add_argument('--checkpoint_dir', default='', type=str,
                    help='The directory of tensorflow checkpoint.')

def fetch_image(qid):
    quiz = get_image(qid)

    raw_image = quiz.raw_image.copy()
    bbox = quiz.bbox
    mean_color = quiz.raw_image.mean(axis=(0, 1))  # shape: (3,)

    raw_roi = raw_image[bbox['y']:bbox['y']+bbox['h'], bbox['x']:bbox['x']+bbox['w'], :]

    mask = np.zeros(raw_image.shape[:2])
    mask_roi = mask[bbox['y']:bbox['y']+bbox['h'], bbox['x']:bbox['x']+bbox['w']]

    to_filling = (raw_roi[:, :, 1] == 255) & (raw_roi[:, :, 0] < 10) & (raw_roi[:, :, 2] < 10)
    mask_roi[to_filling] = 1

    mask = ski_morph.dilation(mask, ski_morph.square(7))
    mask = np.repeat(mask, 3).reshape(256, 256, 3)
    # ski_io.imsave('/tmp/mask.jpg', mask)
    # pdb.set_trace()
    return raw_image, mask

def make_image(image, mask):
    print(image.shape, mask.shape)
    assert image.shape == mask.shape

    h, w, _ = image.shape
    grid = 8
    image = image[:h//grid*grid, :w//grid*grid, :]
    mask = mask[:h//grid*grid, :w//grid*grid, :]
    print('Shape of image: {}'.format(image.shape))

    image = np.expand_dims(image, 0)
    mask = np.expand_dims(mask, 0)
    concated = np.concatenate([image, mask], axis=2)
    return concated

if __name__ == "__main__":
    ng.get_gpus(1, dedicated=False)
    args = parser.parse_args()

    model = InpaintCAModel()


    sess_config = tf.ConfigProto()
    sess_config.gpu_options.allow_growth = True
    sess = tf.Session(config=sess_config)

    input_image = tf.placeholder(tf.float32 , (1, 256, 512, 3), name='123')

    output = model.build_server_graph(input_image)

    output = (output + 1.) * 127.5
    output = tf.reverse(output, [-1])
    output = tf.saturate_cast(output, tf.uint8)

    # load pretrained model
    vars_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES)
    assign_ops = []


    for var in vars_list:
        vname = var.name
        from_name = vname
        var_value = tf.contrib.framework.load_variable(args.checkpoint_dir, from_name)
        assign_ops.append(tf.assign(var, var_value))
    sess.run(assign_ops)

    print('Model loaded.')

    cont = True
    while cont:
        try:
            question_id = input('question_id: ')
            image, mask = fetch_image(question_id)

            image = image[:, :, ::-1]
            mask = img_as_ubyte(mask)

            concated = make_image(image, mask)

            cv2.imwrite('/concated.jpg', concated[0])

            result = sess.run(output, feed_dict={input_image: concated})[0]
            ski_io.imsave(args.output, result, format_str='jpeg')
            cv2.imwrite('/out.jpg', result[:, :, ::-1] )
            submit_image(result, question_id)
        except KeyboardInterrupt:
            sess.close()
            cont = False
        except KeyError:
            pass
