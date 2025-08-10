from flask import Blueprint, jsonify
from datetime import datetime

web_health_api = Blueprint('web_health_api', __name__, url_prefix='/api/web/health')

@web_health_api.route('/ping', methods=['GET'])
def ping():
    """健康检查接口"""
    return jsonify({
        'code': 200,
        'message': 'pong',
        'data': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'healthy'
        }
    }), 200

@web_health_api.route('/status', methods=['GET'])
def status():
    """系统状态接口"""
    return jsonify({
        'code': 200,
        'message': '系统运行正常',
        'data': {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'environment': 'development'
        }
    }), 200
