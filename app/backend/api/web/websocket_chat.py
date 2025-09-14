from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request, g
from models import db, User, Merchant, ChatRoom, ChatMessage
from datetime import datetime
from utils.TokenUtils import validate
import json

# 存储在线用户和商家
online_users = {}  # {user_id: session_id}
online_merchants = {}  # {merchant_id: session_id}

def require_auth(f):
    """WebSocket认证装饰器"""
    def decorated_function(*args, **kwargs):
        # 检查g和request中的认证信息
        merchant_id = None
        if hasattr(g, 'merchant_id') and g.merchant_id:
            merchant_id = g.merchant_id
        elif hasattr(request, 'merchant_id') and request.merchant_id:
            merchant_id = request.merchant_id
        
        if not merchant_id:
            emit('error', {'message': '认证失败，请重新连接'})
            return False
        return f(*args, **kwargs)
    return decorated_function

def init_websocket(socketio):
    """初始化WebSocket事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        """客户端连接事件"""
        print(f"Client connected: {request.sid}")
        
        # 从查询参数中获取authorization
        authorization = request.args.get('authorization')
        if not authorization:
            print(f"WebSocket连接失败: 缺少认证信息")
            emit('error', {'message': '缺少认证信息'})
            disconnect()
            return False
        
        # 验证authorization（格式：Bearer token）
        if not authorization.startswith('Bearer '):
            print(f"WebSocket连接失败: 认证格式错误")
            emit('error', {'message': '认证格式错误'})
            disconnect()
            return False
        
        # 提取token
        token = authorization[7:]  # 移除 'Bearer ' 前缀
        
        # 验证token
        merchant_id = validate(token)
        if merchant_id is None:
            print(f"WebSocket连接失败: 无效的认证token")
            emit('error', {'message': '认证失败，请重新登录'})
            disconnect()
            return False
        
        # 将认证信息存储到session中
        g.merchant_id = merchant_id
        # 将认证信息也存储到request中，以便后续访问
        request.merchant_id = merchant_id
        print(f"WebSocket认证成功: merchant_id={merchant_id}")
        return True
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接事件"""
        print(f"Client disconnected: {request.sid}")
        
        # 从在线列表中移除
        for user_id, session_id in list(online_users.items()):
            if session_id == request.sid:
                del online_users[user_id]
                break
                
        for merchant_id, session_id in list(online_merchants.items()):
            if session_id == request.sid:
                del online_merchants[merchant_id]
                break
    
    @socketio.on('user_join')
    @require_auth
    def handle_user_join(data):
        """用户加入聊天"""
        try:
            user_id = data.get('user_id')
            if not user_id:
                emit('error', {'message': '用户ID不能为空'})
                return
            
            # 验证用户是否存在
            user = User.query.get(user_id)
            if not user:
                emit('error', {'message': '用户不存在'})
                return
            
            # 记录在线用户
            online_users[user_id] = request.sid
            
            emit('user_joined', {'user_id': user_id, 'message': '用户已加入聊天'})
            print(f"User {user_id} joined chat")
            
        except Exception as e:
            emit('error', {'message': f'加入聊天失败: {str(e)}'})
    
    @socketio.on('merchant_join')
    @require_auth
    def handle_merchant_join(data):
        """商家加入聊天"""
        try:
            merchant_id = data.get('merchant_id')
            if not merchant_id:
                emit('error', {'message': '商家ID不能为空'})
                return
            
            # 验证商家是否存在
            merchant = Merchant.query.get(merchant_id)
            if not merchant:
                emit('error', {'message': '商家不存在'})
                return
            
            # 记录在线商家
            online_merchants[merchant_id] = request.sid
            
            emit('merchant_joined', {'merchant_id': merchant_id, 'message': '商家已加入聊天'})
            print(f"Merchant {merchant_id} joined chat")
            
        except Exception as e:
            emit('error', {'message': f'加入聊天失败: {str(e)}'})
    
    @socketio.on('join_chat_room')
    @require_auth
    def handle_join_chat_room(data):
        """加入聊天室"""
        try:
            user_id = data.get('user_id')
            merchant_id = data.get('merchant_id')
            
            if not user_id or not merchant_id:
                emit('error', {'message': '用户ID和商家ID不能为空'})
                return
            
            # 获取或创建聊天室
            chat_room = ChatRoom.query.filter_by(
                user_id=user_id, 
                merchant_id=merchant_id
            ).first()
            
            if not chat_room:
                chat_room = ChatRoom(
                    user_id=user_id,
                    merchant_id=merchant_id,
                    status='active'
                )
                db.session.add(chat_room)
                db.session.commit()
            
            # 加入房间
            room_name = f"chat_{chat_room.id}"
            join_room(room_name)
            
            emit('joined_chat_room', {
                'chat_room_id': chat_room.id,
                'room_name': room_name,
                'message': '已加入聊天室'
            })
            
            print(f"User {user_id} joined chat room {chat_room.id} with merchant {merchant_id}")
            
        except Exception as e:
            emit('error', {'message': f'加入聊天室失败: {str(e)}'})
    
    @socketio.on('send_message')
    @require_auth
    def handle_send_message(data):
        """发送消息"""
        try:
            chat_room_id = data.get('chat_room_id')
            sender_type = data.get('sender_type')  # 'user' or 'merchant'
            sender_id = data.get('sender_id')
            content = data.get('content')
            message_type = data.get('message_type', 'text')
            file_url = data.get('file_url')
            
            if not all([chat_room_id, sender_type, sender_id, content]):
                emit('error', {'message': '消息参数不完整'})
                return
            
            # 验证聊天室是否存在
            chat_room = ChatRoom.query.get(chat_room_id)
            if not chat_room:
                emit('error', {'message': '聊天室不存在'})
                return
            
            # 创建消息
            message = ChatMessage(
                chat_room_id=chat_room_id,
                sender_type=sender_type,
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                file_url=file_url
            )
            
            db.session.add(message)
            
            # 更新聊天室的最后消息时间
            chat_room.last_message_at = datetime.utcnow()
            
            db.session.commit()
            
            # 获取发送者信息
            if sender_type == 'user':
                sender = User.query.get(sender_id)
                sender_name = sender.username if sender else f"用户{sender_id}"
            else:
                sender = Merchant.query.get(sender_id)
                sender_name = sender.name if sender else f"商家{sender_id}"
            
            # 构建消息数据
            message_data = {
                'id': message.id,
                'chat_room_id': chat_room_id,
                'sender_type': sender_type,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'content': content,
                'message_type': message_type,
                'file_url': file_url,
                'created_at': message.created_at.isoformat(),
                'is_read': False
            }
            
            # 发送到聊天室
            room_name = f"chat_{chat_room_id}"
            emit('new_message', message_data, room=room_name)
            
            print(f"Message sent in room {chat_room_id}: {content[:50]}...")
            
        except Exception as e:
            emit('error', {'message': f'发送消息失败: {str(e)}'})
    
    @socketio.on('mark_message_read')
    @require_auth
    def handle_mark_message_read(data):
        """标记消息为已读"""
        try:
            message_id = data.get('message_id')
            if not message_id:
                emit('error', {'message': '消息ID不能为空'})
                return
            
            message = ChatMessage.query.get(message_id)
            if not message:
                emit('error', {'message': '消息不存在'})
                return
            
            message.is_read = True
            db.session.commit()
            
            emit('message_marked_read', {'message_id': message_id})
            
        except Exception as e:
            emit('error', {'message': f'标记消息已读失败: {str(e)}'})
    
    @socketio.on('get_chat_history')
    @require_auth
    def handle_get_chat_history(data):
        """获取聊天历史"""
        try:
            chat_room_id = data.get('chat_room_id')
            page = data.get('page', 1)
            per_page = data.get('per_page', 20)
            
            if not chat_room_id:
                emit('error', {'message': '聊天室ID不能为空'})
                return
            
            # 验证聊天室是否存在
            chat_room = ChatRoom.query.get(chat_room_id)
            if not chat_room:
                emit('error', {'message': '聊天室不存在'})
                return
            
            # 获取消息历史
            messages = ChatMessage.query.filter_by(chat_room_id=chat_room_id)\
                .order_by(ChatMessage.created_at.desc())\
                .paginate(page=page, per_page=per_page, error_out=False)
            
            message_list = []
            for message in messages.items:
                # 获取发送者信息
                if message.sender_type == 'user':
                    sender = User.query.get(message.sender_id)
                    sender_name = sender.username if sender else f"用户{message.sender_id}"
                else:
                    sender = Merchant.query.get(message.sender_id)
                    sender_name = sender.name if sender else f"商家{message.sender_id}"
                
                message_data = {
                    'id': message.id,
                    'sender_type': message.sender_type,
                    'sender_id': message.sender_id,
                    'sender_name': sender_name,
                    'content': message.content,
                    'message_type': message.message_type,
                    'file_url': message.file_url,
                    'is_read': message.is_read,
                    'created_at': message.created_at.isoformat()
                }
                message_list.append(message_data)
            
            emit('chat_history', {
                'messages': message_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': messages.total,
                    'pages': messages.pages
                }
            })
            
        except Exception as e:
            emit('error', {'message': f'获取聊天历史失败: {str(e)}'})
    
    @socketio.on('get_online_status')
    @require_auth
    def handle_get_online_status(data):
        """获取在线状态"""
        try:
            user_id = data.get('user_id')
            merchant_id = data.get('merchant_id')
            
            status = {
                'user_online': user_id in online_users if user_id else False,
                'merchant_online': merchant_id in online_merchants if merchant_id else False,
                'online_users_count': len(online_users),
                'online_merchants_count': len(online_merchants)
            }
            
            emit('online_status', status)
            
        except Exception as e:
            emit('error', {'message': f'获取在线状态失败: {str(e)}'})
