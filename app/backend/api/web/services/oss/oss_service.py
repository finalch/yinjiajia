import alibabacloud_oss_v2 as oss
from config import ali_oss_config
import uuid
import os
from datetime import datetime

from . import oss_utils


def init_oss_client() -> oss.Client:
    credentials_provider = oss.credentials.StaticCredentialsProvider(
        access_key_id=ali_oss_config.oss_key_id,
        access_key_secret=ali_oss_config.oss_key_secret
    )
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = 'cn-hangzhou'
    return oss.Client(cfg)


oss_client = init_oss_client()


def get_post_signature_for_oss_upload():
    return oss_utils.generate_upload_params()


def put_bucket():
    try:
        result = oss_client.put_bucket(
            oss.PutBucketRequest(ali_oss_config.oss_bucket,
                                 create_bucket_configuration=oss.CreateBucketConfiguration(
                                     storage_class='Standard'
                                 )))
        return result
    except Exception as e:
        print("put bucket error", e)
        raise Exception("put bucket failed")


def put_object(bucket_name: str, key: str, content: str):
    try:
        result = oss_client.put_object(oss.PutObjectRequest(
            bucket=bucket_name,
            key=key,
            body=content.encode('utf-8')))
        return result
    except Exception as e:
        print("put object error", e)
        raise Exception("put object failed")


def put_object_from_file(bucket_name: str, key: str, file_content: bytes):
    """上传文件内容到OSS"""
    try:
        result = oss_client.put_object(oss.PutObjectRequest(
            bucket=bucket_name,
            key=key,
            body=file_content))
        return result
    except Exception as e:
        print("put object from file error", e)
        raise Exception("put object from file failed")


def upload_image(file):
    """上传图片文件到OSS"""
    try:
        # 生成唯一的文件名
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 构建OSS key（路径）
        current_date = datetime.now().strftime('%Y/%m/%d')
        oss_key = f"{ali_oss_config.oss_prefix}/images/{current_date}/{unique_filename}"
        
        # 读取文件内容
        file_content = file.read()
        
        # 上传到OSS
        result = put_object_from_file(ali_oss_config.oss_bucket, oss_key, file_content)
        
        # 构建访问URL
        url = f"https://{ali_oss_config.oss_bucket}.{ali_oss_config.oss_endpoint}/{oss_key}"
        
        return url
        
    except Exception as e:
        print("upload image error", e)
        raise Exception("upload image failed")


def upload_video(file):
    """上传视频文件到OSS"""
    try:
        # 生成唯一的文件名
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.mp4'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 构建OSS key（路径）
        current_date = datetime.now().strftime('%Y/%m/%d')
        oss_key = f"{ali_oss_config.oss_prefix}/videos/{current_date}/{unique_filename}"
        
        # 读取文件内容
        file_content = file.read()
        
        # 上传到OSS
        result = put_object_from_file(ali_oss_config.oss_bucket, oss_key, file_content)
        
        # 构建访问URL
        url = f"https://{ali_oss_config.oss_bucket}.{ali_oss_config.oss_endpoint}/{oss_key}"
        
        return url
        
    except Exception as e:
        print("upload video error", e)
        raise Exception("upload video failed")
