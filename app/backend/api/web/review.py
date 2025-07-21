from flask import Blueprint, jsonify, request

web_review_api = Blueprint('web_review_api', __name__, url_prefix='/api/web/review')

@web_review_api.route('/', methods=['GET'])
def get_reviews():
    """WEB端-评价管理接口"""
    # TODO: 查询评价
    return jsonify({'message': 'WEB端-评价管理接口'}), 200
