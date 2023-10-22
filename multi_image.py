from botocore.client import Config
from PIL import Image
import boto3
import ast
import sys
import uuid
import os
import time
import shutil
import json
import glob
from Queue import Queue
from threading import Thread

s3_client = boto3.client(
        's3',
        config=Config(signature_version='s3v4')
        )

file_size = 0

class Images(object):
    def __init__(self, local_path = None, bucket = None, s3_path = None, pri = None):
        self.local_path = local_path
        self.bucket = bucket
        self.s3_path = s3_path
        self.pri = pri

max_jobs = 1000
max_workers = 12
queue_s3 = Queue(max_jobs)

class Resolution(object):
    def __init__(self, id = None, height = None, width = None, dstPath = None):
        self.id = id
        self.height = height
        self.width = width
        self.dstPath = dstPath

def resize_image(image_path, resized_path, height, width):
    with Image.open(image_path) as image:
        size = (height, width)
        #image.thumbnail(size, Image.ANTIALIAS)
        temp = image.resize(size, Image.ANTIALIAS)
        temp.save(resized_path, 'JPEG', quality = 100)

def process_crops(image_path, crop_size, X, Y):
    with Image.open(image_path) as image:
        width, height = image.size
        for i in range(X):
            for j in range(Y):
                temp1 = (j+1) * crop_size
                if(temp1 > width):
                    temp1 = width
                temp2 = (i+1) * crop_size
                if(temp2 > height):
                    temp2 = height
                box = (j * crop_size, i * crop_size, temp1, temp2)
                yield image.crop(box)

def crop_image(image_path, crop_path, crop_size, X, Y):
    start_num = 0
    for k, piece in enumerate(process_crops(image_path, crop_size, X, Y), start_num):
        img = Image.new('RGB', (piece.size), 255)
        img.paste(piece)
        path = os.path.join(crop_path, "X%sY%s.webp" % (k % Y, int(k / Y)))
        img.save(path, 'webp', quality = 100)

def s3_uploader(q):
    while True:
        temp = q.get()
        try:
            s3_client.upload_file(temp.local_path, temp.bucket, temp.s3_path, ExtraArgs={'ACL': temp.pri, 'ContentType': 'image/jpeg', 'CacheControl': 'max-age=31536000'})
        except:
            print (temp.s3_path)
        q.task_done()

def upload(images_path, dst_s3, bucket, orig, event, pri):
    try:
        os.remove(images_path+"2.jpg")
    except OSError:
        print("image 2 not found")
    try:
        os.remove(images_path+"3.jpg")
    except OSError:
        print("image 3 not found")
    try:
        os.remove(images_path+"4.jpg")
    except OSError:
        print("image 4 not found")
    img = Image.open(orig)
    try:
        os.remove(orig)
    except OSError:
        print("original image not found")
    for root, dirs, files in os.walk(images_path):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, images_path)
            s3_path = os.path.join(dst_s3, relative_path)
            queue_s3.put(Images(local_path, bucket, s3_path, pri))
    
    for i in range(max_workers):
        worker = Thread(target=s3_uploader, args=(queue_s3,))
        worker.setDaemon(True)
        worker.start()
    queue_s3.join()

def handler(event, context):
    base_destination_path = "/tmp/" + str(uuid.uuid4()) + "/"
    if not os.path.exists(base_destination_path):
        os.makedirs(base_destination_path)

    bucket = event["bucketName"]
    dst_s3 = event["writePath"]
    key = event["loadPath"]
    pri = event["acl"]

    infile = base_destination_path + 'original'+key[key.rfind('.'):]
    s3_client.download_file(bucket, key, infile)
    resolutions = []
    temp = ast.literal_eval(event["res"])
    file_size = os.stat(infile).st_size
    for i in range(0, len(temp)):
        resolutions.append(Resolution(i + 2, temp[i] / 2, temp[i], base_destination_path + "level-"+str(i + 2)))
    with Image.open(infile) as im:
        width, height = im.size

    for i in range(0, len(resolutions)):
        save_path = base_destination_path + str(resolutions[i].id)+ '.jpg'
        resize_image(infile, save_path, resolutions[i].width, resolutions[i].height)
        dst_path = base_destination_path + "level-" + str(resolutions[i].id)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        X = resolutions[i].height / 512
        if(resolutions[i].height % 512 > 0):
            X = X + 1
        Y = resolutions[i].width / 512
        if(resolutions[i].width % 512 > 0):
            Y = Y + 1
        crop_image(save_path, dst_path, 512, X, Y)
    upload(base_destination_path, dst_s3, bucket, infile, event, pri) 
    shutil.rmtree(base_destination_path)
    message = {
	'message': 'Execution started successfully!',
	'file_size': file_size
    }
    return {
            'statusCode': 200,
	    'headers': {'Content-Type': 'application/json'},
	    'body': json.dumps(message)
            }