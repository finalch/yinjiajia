from flask import Blueprint, jsonify, request

from services.oss import oss_service

web_media_api = Blueprint('media_api', __name__, url_prefix='/api/web/media')


@web_media_api.route('/get_post_signature_for_oss_upload', methods=['GET'])
def get_post_signature_for_oss_upload():
    return jsonify({
        "code": 200,
        "message": "获取成功",
        "data": oss_service.get_post_signature_for_oss_upload()
    }), 200


@web_media_api.route('/create-oss-bucket', methods=['GET'])
def create_oss_bucket():
    return jsonify({
        "code": 200,
        "message": "获取成功",
        "data": oss_service.put_bucket()
    }), 200


@web_media_api.route('/upload-image', methods=['POST'])
def upload_image():
    file = request.files.get('file')
    if not file:
        return jsonify({"code": 400, "message": "请选择要上传的文件"}), 400

    try:
        url = oss_service.upload_image(file)
        return jsonify({
            "code": 200,
            "message": "上传成功",
            "data": {
                "url": url
            }
        }), 200
    except Exception as e:
        print("Upload image error:", e)
        return jsonify({"code": 500, "message": "上传失败"}), 500


@web_media_api.route('/upload-video', methods=['POST'])
def upload_video():
    file = request.files.get('file')
    if not file:
        return jsonify({"code": 400, "message": "请选择要上传的文件"}), 400

    try:
        url = oss_service.upload_video(file)
        return jsonify({
            "code": 200,
            "message": "上传成功",
            "data": {
                "url": url
            }
        }), 200
    except Exception as e:
        print("Upload video error:", e)
        return jsonify({"code": 500, "message": "上传失败"}), 500
