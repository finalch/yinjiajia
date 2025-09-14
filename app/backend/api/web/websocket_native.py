import json
import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from flask import request, g
from models import db, User, Merchant, ChatRoom, ChatMessage
from datetime import datetime
from utils.TokenUtils import validate
import threading
import logging

# 存储在线连接
active_connections = {}  # {session_id: websocket}
online_users = {}  # {user_id: session_id}
online_merchants = {}  # {merchant_id: session_id}

logger = logging.getLogger(__name__)

class WebSocketHandler:
    def __init__(self):
        self.server = None
        self.loop = None
        self.thread = None
    
    def start_server(self, host='0.0.0.0', port=8002):
        """启动WebSocket服务器"""
        def run_server():
            try:
                # 创建新的事件循环
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                
                # 创建WebSocket服务器
                async def create_server():
                    return await websockets.serve(
                        self.handle_connection,
                        host,
                        port,
                        ping_interval=20,
                        ping_timeout=10
                    )
                
                # 启动服务器
                self.server = self.loop.run_until_complete(create_server())
                logger.info(f"WebSocket服务器启动在 {host}:{port}")
                
                # 运行事件循环
                self.loop.run_forever()
            except Exception as e:
                logger.error(f"WebSocket服务器启动失败: {e}")
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
    
    async def handle_connection(self, websocket: WebSocketServerProtocol):
        """处理WebSocket连接"""
        session_id = id(websocket)
        logger.info(f"新的WebSocket连接: {session_id}")
        
        try:
            # 从请求头获取查询参数
            # 在websockets库中，查询参数通常通过request_headers传递
            query_string = ""
            
            # 尝试从不同的地方获取查询参数
            if hasattr(websocket, 'request_headers'):
                # 检查是否有query头
                query_string = websocket.request_headers.get('query', '')
            
            # 如果没有找到查询参数，尝试从其他方式获取
            if not query_string and hasattr(websocket, 'path'):
                # 从path中获取查询参数
                if '?' in websocket.path:
                    query_string = websocket.path.split('?')[1]
            
            if not query_string:
                await websocket.close(code=1008, reason="缺少认证信息")
                return
            
            # 解析查询参数
            auth_params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    auth_params[key] = value
            
            authorization = auth_params.get('authorization')
            if not authorization:
                await websocket.close(code=1008, reason="缺少认证信息")
                return
            
            # 验证authorization（格式：Bearer token）
            if not authorization.startswith('Bearer '):
                await websocket.close(code=1008, reason="认证格式错误")
                return
            
            # 提取token
            token = authorization[7:]  # 移除 'Bearer ' 前缀
            
            # 验证token
            merchant_id = validate(token)
            if merchant_id is None:
                await websocket.close(code=1008, reason="认证失败")
                return
            
            # 存储连接
            active_connections[session_id] = websocket
            logger.info(f"WebSocket认证成功: session_id={session_id}, merchant_id={merchant_id}")
            
            # 发送认证成功消息
            await self.send_message(websocket, {
                'type': 'auth_success',
                'data': {'merchant_id': merchant_id, 'message': '认证成功'}
            })
            
            # 处理消息
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, session_id, merchant_id, data)
                except json.JSONDecodeError:
                    await self.send_error(websocket, "消息格式错误")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
                    await self.send_error(websocket, f"处理消息失败: {str(e)}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket连接关闭: {session_id}")
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            # 清理连接
            if session_id in active_connections:
                del active_connections[session_id]
            
            # 从在线列表中移除
            for user_id, sid in list(online_users.items()):
                if sid == session_id:
                    del online_users[user_id]
                    break
            
            for merchant_id, sid in list(online_merchants.items()):
                if sid == session_id:
                    del online_merchants[merchant_id]
                    break
    
    async def handle_message(self, websocket, session_id, merchant_id, data):
        """处理接收到的消息"""
        message_type = data.get('type')
        message_data = data.get('data', {})
        
        logger.info(f"收到消息: {message_type}, 数据: {message_data}")
        
        if message_type == 'user_join':
            await self.handle_user_join(websocket, session_id, message_data)
        elif message_type == 'merchant_join':
            await self.handle_merchant_join(websocket, session_id, message_data)
        elif message_type == 'join_chat_room':
            await self.handle_join_chat_room(websocket, session_id, message_data)
        elif message_type == 'send_message':
            await self.handle_send_message(websocket, session_id, message_data)
        elif message_type == 'mark_message_read':
            await self.handle_mark_message_read(websocket, session_id, message_data)
        elif message_type == 'get_chat_history':
            await self.handle_get_chat_history(websocket, session_id, message_data)
        elif message_type == 'get_online_status':
            await self.handle_get_online_status(websocket, session_id, message_data)
        else:
            await self.send_error(websocket, f"未知的消息类型: {message_type}")
    
    async def handle_user_join(self, websocket, session_id, data):
        """用户加入聊天"""
        try:
            user_id = data.get('user_id')
            if not user_id:
                await self.send_error(websocket, "用户ID不能为空")
                return
            
            # 验证用户是否存在
            user = User.query.get(user_id)
            if not user:
                await self.send_error(websocket, "用户不存在")
                return
            
            # 记录在线用户
            online_users[user_id] = session_id
            
            await self.send_message(websocket, {
                'type': 'user_joined',
                'data': {'user_id': user_id, 'message': '用户已加入聊天'}
            })
            
            logger.info(f"用户 {user_id} 加入聊天")
            
        except Exception as e:
            await self.send_error(websocket, f"加入聊天失败: {str(e)}")
    
    async def handle_merchant_join(self, websocket, session_id, data):
        """商家加入聊天"""
        try:
            merchant_id = data.get('merchant_id')
            if not merchant_id:
                await self.send_error(websocket, "商家ID不能为空")
                return
            
            # 验证商家是否存在
            merchant = Merchant.query.get(merchant_id)
            if not merchant:
                await self.send_error(websocket, "商家不存在")
                return
            
            # 记录在线商家
            online_merchants[merchant_id] = session_id
            
            await self.send_message(websocket, {
                'type': 'merchant_joined',
                'data': {'merchant_id': merchant_id, 'message': '商家已加入聊天'}
            })
            
            logger.info(f"商家 {merchant_id} 加入聊天")
            
        except Exception as e:
            await self.send_error(websocket, f"加入聊天失败: {str(e)}")
    
    async def handle_join_chat_room(self, websocket, session_id, data):
        """加入聊天室"""
        try:
            user_id = data.get('user_id')
            merchant_id = data.get('merchant_id')
            
            if not user_id or not merchant_id:
                await self.send_error(websocket, "用户ID和商家ID不能为空")
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
            
            await self.send_message(websocket, {
                'type': 'joined_chat_room',
                'data': {
                    'chat_room_id': chat_room.id,
                    'message': '已加入聊天室'
                }
            })
            
            logger.info(f"用户 {user_id} 加入聊天室 {chat_room.id} 与商家 {merchant_id}")
            
        except Exception as e:
            await self.send_error(websocket, f"加入聊天室失败: {str(e)}")
    
    async def handle_send_message(self, websocket, session_id, data):
        """发送消息"""
        try:
            chat_room_id = data.get('chat_room_id')
            sender_type = data.get('sender_type')  # 'user' or 'merchant'
            sender_id = data.get('sender_id')
            content = data.get('content')
            message_type = data.get('message_type', 'text')
            file_url = data.get('file_url')
            
            if not all([chat_room_id, sender_type, sender_id, content]):
                await self.send_error(websocket, "消息参数不完整")
                return
            
            # 验证聊天室是否存在
            chat_room = ChatRoom.query.get(chat_room_id)
            if not chat_room:
                await self.send_error(websocket, "聊天室不存在")
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
            
            # 发送消息给所有相关连接
            await self.broadcast_to_chat_room(chat_room_id, {
                'type': 'new_message',
                'data': message_data
            })
            
            logger.info(f"消息已发送到聊天室 {chat_room_id}: {content[:50]}...")
            
        except Exception as e:
            await self.send_error(websocket, f"发送消息失败: {str(e)}")
    
    async def handle_mark_message_read(self, websocket, session_id, data):
        """标记消息为已读"""
        try:
            message_id = data.get('message_id')
            if not message_id:
                await self.send_error(websocket, "消息ID不能为空")
                return
            
            message = ChatMessage.query.get(message_id)
            if not message:
                await self.send_error(websocket, "消息不存在")
                return
            
            message.is_read = True
            db.session.commit()
            
            await self.send_message(websocket, {
                'type': 'message_marked_read',
                'data': {'message_id': message_id}
            })
            
        except Exception as e:
            await self.send_error(websocket, f"标记消息已读失败: {str(e)}")
    
    async def handle_get_chat_history(self, websocket, session_id, data):
        """获取聊天历史"""
        try:
            chat_room_id = data.get('chat_room_id')
            page = data.get('page', 1)
            per_page = data.get('per_page', 20)
            
            if not chat_room_id:
                await self.send_error(websocket, "聊天室ID不能为空")
                return
            
            # 验证聊天室是否存在
            chat_room = ChatRoom.query.get(chat_room_id)
            if not chat_room:
                await self.send_error(websocket, "聊天室不存在")
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
            
            await self.send_message(websocket, {
                'type': 'chat_history',
                'data': {
                    'messages': message_list,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': messages.total,
                        'pages': messages.pages
                    }
                }
            })
            
        except Exception as e:
            await self.send_error(websocket, f"获取聊天历史失败: {str(e)}")
    
    async def handle_get_online_status(self, websocket, session_id, data):
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
            
            await self.send_message(websocket, {
                'type': 'online_status',
                'data': status
            })
            
        except Exception as e:
            await self.send_error(websocket, f"获取在线状态失败: {str(e)}")
    
    async def send_message(self, websocket, data):
        """发送消息"""
        try:
            await websocket.send(json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
    
    async def send_error(self, websocket, message):
        """发送错误消息"""
        await self.send_message(websocket, {
            'type': 'error',
            'data': {'message': message}
        })
    
    async def broadcast_to_chat_room(self, chat_room_id, data):
        """向聊天室广播消息"""
        # 这里可以实现向特定聊天室的所有成员广播消息
        # 目前简化实现，只发送给当前连接
        pass

# 创建全局WebSocket处理器实例
websocket_handler = WebSocketHandler()
