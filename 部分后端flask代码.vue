@app.route('/api/cartlist', methods=['POST'])

def get_cart_list():
	# current_user_id = get_jwt_identity()
	data = request.json
	user_id = data.get('user_id')

	cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	# 查询当前用户的购物车项
	# cart_items = Cart.query.filter_by(user_id=current_user_id).join(product).all()

	# 查询当前用户的购物车项
	cur.execute("""
		SELECT id, category_id,product_id, product_name,product_price,product_quantity,product_picture
		FROM cart WHERE user_id = %s
	""", (user_id,))

	cart_list = cur.fetchall()

	for item in cart_list:
		item['product_price'] = float(item['product_price'])

	return jsonify({'code': 200, 'msg': 'success', 'data': cart_list})


@app.route('/api/cart/remove/<int:Id>', methods=['DELETE'])

def remove_from_cart(Id):
	if not request.is_json:
		return jsonify({'code': 400, 'message': '请求必须包含JSON数据'}), 400
	data = request.get_json()  # 使用get_json()替代json属性
	user_id = data.get('user_id')
	# 验证user_id是否存在
	if not user_id or not Id:
		return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

	try:
		cur = mysql.connection.cursor()

		query = "DELETE FROM cart WHERE user_id = %s AND id = %s"
		params = (user_id, Id)

		print(f"Executing delete: {query} with values: {params}")
		cur.execute(query, params)

		# 提交事务
		mysql.connection.commit()

		# 检查是否删除了记录
		if cur.rowcount > 0:
			return jsonify({'code': 200, 'data':'', 'message': '删除成功'}), 200
		else:
			return jsonify({'code': 404, 'message': '未找到对应的课程'}), 404

	except Exception as e:
		mysql.connection.rollback()
		return jsonify({'code': 500, 'message': '服务器内部错误', 'error': str(e)}), 500

	finally:
		cur.close()


@app.route('/api/createOrder', methods=['POST'])
def create_order():
	data = request.json
	user_id = data.get('user_id')
	items = data.get('items')
	total_price = Decimal(str(data.get('totalPrice')))

	print(f"Raw data: {data}")

	if not user_id or not items or not total_price:
		return jsonify({"error": "Missing data"}), 400

	if not isinstance(items, list) or len(items) == 0:
		return jsonify({"error": "Invalid items data"}), 400

	try:
		cur = mysql.connection.cursor()
		# 插入订单信息到 orders 表
		cur.execute("""
			INSERT INTO orders (user_id, total_price, status)
			VALUES (%s, %s,%s)
		""", (user_id, total_price,'pending'))
		order_id = cur.lastrowid

		# 插入每个课程项到 order_items 表
		for item in items:
			if not all(k in item for k in ['category_id','product_id',  'product_name', 'product_price', 'product_quantity','product_picture']):
				mysql.connection.rollback()
				return jsonify({"error": "Invalid item structure"}), 400

			cur.execute("""
				INSERT INTO order_items (order_id, category_id, product_id, product_name, product_price, product_quantity,product_picture)
				VALUES (%s, %s, %s, %s, %s,%s,%s)
			""", (order_id, item['category_id'],item['product_id'],item['product_name'], item['product_price'], item['product_quantity'],item['product_picture']))

		mysql.connection.commit()
		cur.close()

		return jsonify({"message": "Order created successfully", "order_id": order_id}), 201

	except Exception as e:
		mysql.connection.rollback()
		return jsonify({"error": str(e)}), 500


@app.route('/api/getPaymentParams/<order_id>', methods=['GET'])

def get_payment_params(order_id):
	# 获取当前用户身份
	# data = request.json
	# user_id = data.get('user_id')

	# 获取订单信息
	try:

		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			# 获取订单信息
		cur.execute("""
			SELECT o.user_id, o.total_price 
			FROM orders o 
			WHERE o.id = %s AND o.status = 'pending'
		""", (order_id,))
		order = cur.fetchone()
		print(f"执行SQL查询: {order}")

		if not order:
			return jsonify({'error': 'Order not found or unauthorized'}), 404

		total_amount = format(order['total_price'])  # 确保保留2位小数
		# total_amount = format(order['total_price'], ".2f")
		# 验证订单金额
		try:
			print(f"订单金额: {total_amount}")
			if Decimal(total_amount) <= 0:
				return jsonify({'error': 'Invalid order amount'}), 400
			# return jsonify({'success': 'amount format success'}), 200
		except (ValueError, TypeError):
			return jsonify({'error': 'Invalid order amount format'}), 400

		# 构造订单参数
		subject = "buyproduct"  # 订单标题
		out_trade_no = str(order_id)  # 商户订单号
		# out_trade_no = f"ORDER{order_id}{random.randint(1000, 9999)}"

		print(f"构造订单参数 - 金额: {total_amount}, 订单号: {out_trade_no}")

		alipay = create_alipay_client()
		print(f"支付宝客户端配置: {alipay.__dict__}")
		# APP支付接口 alipay.trade.app.pay
		order_string = alipay.api_alipay_trade_page_pay(
			out_trade_no=out_trade_no,
			total_amount=total_amount,
			subject=subject,
			notify_url="http://127.0.0.1:5002/alipay/notify" # 支付结果异步通知地址
			  # 支付成功后同步跳转地址
			# APP支付不需要return_url参数
		)
		print(f"生成的支付字符串: {order_string}")

		# 网页支付需要构造支付页面的URL
		pay_url = "https://openapi.alipay.com/gateway.do?" + order_string

		# 构造返回给前端的支付参数
		payment_params = {
			'provider': 'alipay',
			'pay_url': pay_url,  # 前端需要跳转到这个URL
			'orderInfo': {
				'orderId': out_trade_no,
				'amount': total_amount,
				'description': subject
			}
		}

		# 以下是微信支付的示例参数结构
		# payment_params = {
		# 	'provider': 'wxpay',
		# 	'timeStamp': str(int(time.time())),
		# 	'nonceStr': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
		# 	'package': f'prepay_id=模拟的预支付ID',
		# 	'signType': 'MD5',
		# 	'paySign': '模拟的签名',  # 这里应该用微信支付SDK生成实际签名
		# 	'orderInfo': {
		# 		'orderId': str(order_id),
		# 		'amount': float(order['total_price']),
		# 		'description': '课程购买'
		# 	}
		# }

		return jsonify(payment_params), 200

	except Exception as e:
		app.logger.error(f"Payment params generation failed: {str(e)}")
		return jsonify({"error": "Failed to generate payment parameters"}), 500
	finally:
		cur.close()
		print("数据库游标已关闭")  # 调试信息


@app.route('/api/handlePayment', methods=['POST'])
def handle_payment():
	try:
		# 获取前端传来的支付参数
		payment_params = request.json

		# 这里调用支付宝的API获取支付链接
		# 以下是示例代码，实际需要根据支付宝文档实现
		alipay_url = "https://openapi.alipay.com/gateway.do"

		# 构造支付宝请求参数（根据支付宝文档填写实际参数）
		params = {
			"app_id": os.getenv('ALIPAY_APP_ID'),
			"method": "alipay.trade.app.pay",
			"charset": "utf-8",
			"sign_type": "RSA2",
			"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			"version": "1.0",
			"biz_content": json.dumps({
				"out_trade_no": payment_params.get('orderInfo', {}).get('orderId'),
				"product_code": "FAST_INSTANT_TRADE_PAY",
				"total_amount": str(payment_params.get('orderInfo', {}).get('amount')),
				"subject": payment_params.get('orderInfo', {}).get('description', '课程购买'),
				"body": payment_params.get('body', '课程购买')
			},separators=(',', ':'))
		}

		# 移除空值参数
		params = {k: v for k, v in params.items() if v is not None}
		# 生成签名（需要实现签名方法）
		params['sign'] = generate_signature(params)

		# 调用支付宝接口
		response = requests.get(alipay_url, params=params)

		# 返回支付页面URL给前端
		return jsonify({
			"status": "success",
			"payment_url": response.url  # 或者根据支付宝返回构造支付页面URL
		}),200

	except Exception as e:
		return jsonify({
			"status": "error",
			"message": str(e)
		}), 400


# 支付网关回调接口（支付宝/微信支付等会调用这个接口）
@app.route('/alipay/notify', methods=['POST'])
def alipay_notify():
	"""
    支付宝异步通知接口
    """
	try:
		data = request.form.to_dict()
		signature = data.pop("sign", None)
		print('zhifubaoData:',data)

		# 验证签名
		alipay = create_alipay_client()  # 获取配置好的支付宝客户端
		success = alipay.verify(data, signature)
		print('success', success)

		if success and data['trade_status'] in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
			# 更新订单状态为已支付
			order_id = data['out_trade_no']
			cur = mysql.connection.cursor()
			cur.execute("UPDATE orders SET status = 'paid' WHERE id = %s", (order_id,))
			mysql.connection.commit()

			return "success"  # 必须返回success告知支付宝已处理
		else:
			return "failure"
	except Exception as e:
		app.logger.error(f"Alipay notify error: {str(e)}")
		return "failure"

@app.route('/api/checkOrderStatus/<order_id>', methods=['GET'])
def check_order_status(order_id):
	"""
    检查订单支付状态接口
    参数:
        order_id: 订单ID
    返回:
        {
            "status": "paid"|"unpaid"|"expired",
            "order_id": str,
            "timestamp": str
        }
    """
	try:
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		# 获取订单信息
		cur.execute("""
			SELECT o.user_id, o.total_price, o.created_at,o.status
			FROM orders o 
			WHERE o.id = %s
		""", (order_id,))

		order = cur.fetchone()

		print(f"执行SQL查询: {order}")

		if not order:
			return jsonify({'error': 'Order not found or unauthorized'}), 404

		# 检查订单是否已支付
		if order['status'] == 'paid':
			return jsonify({
				"status": "paid",
				"order_id": order_id,
				"timestamp": datetime.now().isoformat()
			}), 200

		elif order['status'] == 'cancelled':
			return jsonify({
				"status": "cancelled",
				"order_id": order_id,
				"timestamp": datetime.now().isoformat()
			}), 201

		elif order['status'] == 'expired':
			return jsonify({
				"status": "expired",
				"order_id": order_id,
				"timestamp": datetime.now().isoformat()
			}), 202

		elif order['status'] == 'pending':
			# 检查订单是否已过期（假设订单30分钟未支付则过期）
			created_time = order['created_at']
			print(f'订单创建时间：{created_time}')
			if isinstance(created_time, str):  # 如果是字符串才转换
				created_time = datetime.fromisoformat(order['created_at'])
			if (datetime.now() - created_time).total_seconds() > 1200:  # 20分钟
				# 更新数据库状态为过期
				cur.execute("UPDATE orders SET status = 'expired' WHERE id = %s", (order_id,))
				mysql.connection.commit()  # 提交事务

				# 确认状态已更新
				cur.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
				updated_order = cur.fetchone()

				if updated_order and updated_order['status'] == 'expired':
					return jsonify({
						"status": "expired",
						"order_id": order_id,
						"timestamp": datetime.now().isoformat()
					}), 203
				else:
					# 更新失败，仍返回pending状态
					order['status'] = 'pending'
				return jsonify({
					"status": "expired",
					"order_id": order_id,
					"timestamp": datetime.now().isoformat()
				}), 204

		# 订单未支付且未过期
		return jsonify({
			"status": "unpaid",
			"order_id": order_id,
			"timestamp": datetime.now().isoformat()
		}), 205

	except Exception as e:
		return jsonify({
			"status": "error",
			"message": str(e)
		}), 500
	finally:
		cur.close()


@app.route('/add_to_my_products', methods=['POST'])
def add_to_my_products():
	data = request.json
	user_id = data.get['user_id']
	order_id = data.get['order_id']

	if not order_id:
		return jsonify({"error": "Missing order_id"}), 400

	try:
		cur = mysql.connection.cursor()

		# 验证订单是否属于当前用户且已支付
		cur.execute("""
			SELECT o.status 
			FROM orders o 
			WHERE o.id = %s AND o.user_id = %s AND o.status = 'paid'
		""", (order_id, user_id))
		order = cur.fetchone()

		if not order:
			return jsonify({"error": "Order not found or unauthorized"}), 404

		if order['status'] != 'paid':
			return jsonify({"error": "Order not paid yet"}), 400

		# 获取 order_items 信息
		cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
		order_items = cur.fetchall()

		if not order_items:
			return jsonify({"error": "No items in this order"}), 400

		# 将 order_items 插入到 my_products 表中
		for item in order_items:
			cur.execute("""
			   SELECT 1 FROM my_products 
			   WHERE user_id = %s AND category_id = %s AND product_id = %s
		   """, (user_id, item['category_id'],item['product_id']))
			if cur.fetchone():
				continue  # 如果课程已存在则跳过

			cur.execute("""
				INSERT INTO my_products (user_id, category_id, product_id, product_name, product_price, product_quantity,product_picture)
				VALUES (%s, %s, %s, %s, %s, %s,%s)
			""", (user_id, item['category_id'],item['product_id'], item['product_name'], item['product_price'], item['product_quantity'],item['product_picture']))

			# 更新订单状态为已完成
		cur.execute("""
			UPDATE orders SET status = 'completed' WHERE id = %s
		""", (order_id,))

		mysql.connection.commit()
		return jsonify({"status": "success", "message": "products added to my products successfully"})

	except Exception as e:
		mysql.connection.rollback()
		return jsonify({"status": "error", "message": str(e)})

	finally:
		cur.close()



@app.route('/get_my_products', methods=['GET'])
def get_my_products():
	user_id = request.args.get('user_id')

	cur = mysql.connection.cursor()

	try:
		# 获取用户的课程信息
		cur.execute("SELECT * FROM my_products WHERE user_id = %s", (user_id,))
		products = cur.fetchall()

		return jsonify({"status": "success", "orderproducts": products})

	except Exception as e:
		return jsonify({"status": "error", "message": str(e)})

	finally:
		cur.close()
		mysql.connection.close()