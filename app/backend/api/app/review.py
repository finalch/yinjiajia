from flask import Blueprint, jsonify, request

app_review_api = Blueprint('app_review_api', __name__, url_prefix='/api/app/review')

@app_review_api.route('/', methods=['POST'])
def add_review():
    """APP端-用户添加评价接口"""
    # TODO: 添加评价
    return jsonify({'message': 'APP端-添加评价接口'}), 201
