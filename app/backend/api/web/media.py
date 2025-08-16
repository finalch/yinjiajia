from flask import Blueprint, jsonify, request
web_media_api = Blueprint('media_api', __name__, url_prefix='/api/web/media')

@web_media_api.route('/upload-image', methods=['POST'])
def upload_image():
    # Mock实现，实际存储逻辑后续补充
    return jsonify({
        "code": 200,
        "message": "上传成功",
        "data": {
            "url": "https://img12.360buyimg.com/n5/s720x720_jfs/t1/110781/9/39729/35768/6630b66eF7b8cbb65/a9cfa77aa778f872.jpg"
        }
    }), 200

@web_media_api.route('/upload-video', methods=['POST'])
def upload_video():
    # Mock实现，实际存储逻辑后续补充
    return jsonify({
        "code": 200,
        "message": "上传成功",
        "data": {
            "url": "https://vod.300hu.com/24/4c1f7a6atransbjngwcloud1oss/46291626964916957953441793/1097_5000_1_ab24dad66_f.mp4?source=1&h265=1088_3000_1_8e6f5c602_f.mp4"
        }
    }), 200
