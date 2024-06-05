import os
import boto3
from PIL import Image
import io
import subprocess

s3_client = boto3.client('s3')

def compress_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=70)  # Compress image
    output.seek(0)
    return output

def compress_video(file_path):
    compressed_file_path = '/tmp/compressed.mp4'
    command = f"ffmpeg -i {file_path} -vcodec libx265 -crf 28 {compressed_file_path}"
    subprocess.run(command, shell=True, check=True)
    return compressed_file_path

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_data = response['Body'].read()
        
        if key.lower().endswith(('.png', '.jpg', '.jpeg')):
            compressed_data = compress_image(file_data)
            compressed_key = f"compressed/{os.path.basename(key)}"
            s3_client.put_object(Bucket=bucket, Key=compressed_key, Body=compressed_data, ContentType='image/jpeg')
        elif key.lower().endswith(('.mp4', '.mov', '.avi')):
            with open('/tmp/input_video', 'wb') as f:
                f.write(file_data)
            compressed_file_path = compress_video('/tmp/input_video')
            compressed_key = f"compressed/{os.path.basename(key)}"
            with open(compressed_file_path, 'rb') as f:
                s3_client.put_object(Bucket=bucket, Key=compressed_key, Body=f, ContentType='video/mp4')
        else:
            print(f"Unsupported file type: {key}")
    
    return {
        'statusCode': 200,
        'body': 'Compression complete!'
    }
