from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import text
from redis import StrictRedis

import json
import random
import datetime
import auth
from config import BaseConfig

# 初始化 Flask 应用
app = Flask(__name__)
app.config.from_object(BaseConfig)

# 初始化数据库连接（SQLAlchemy ORM）
db = SQLAlchemy(app)

# 初始化 Redis，作为缓存/临时存储使用
redis_store = StrictRedis(
    host=BaseConfig.REDIS_HOST,
    port=BaseConfig.REDIS_PORT,
    decode_responses=True
)

# 启用跨域支持
CORS(app)

# 检查数据库连接是否正常
with app.app_context():
    with db.engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(result.fetchone())


def get_status_desc(status_code):
    # 建议缓存到 Redis，或查数据库
    status_dict = {
        0: '未派单',
        1: '已揽单',
        2: '商家备货中',
        3: '已发货',
        4: '派送中',
        5: '已送达'
    }
    return status_dict.get(status_code, '未知状态')

# 用户登录接口
@app.route("/api/user/login", methods=["POST"])
@cross_origin()
def user_login():
    print(request.json)
    userortel = request.json.get("userortel", "").strip()
    password = request.json.get("password", "").strip()

    # 查询用户信息
    sql = (
        'SELECT * FROM user '
        'WHERE telephone = "{0}" AND password = "{1}"'
    ).format(userortel, password)
    data = db.session.execute(text(sql)).first()
    print(data)

    if data:
        user = {
            'id': data[0],
            'username': data[1],
            'password': data[2],
            'telephone': data[3]
        }
        token = auth.encode_func(user)
        print(token)
        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "token": token,
            "role": data[4]
        })
    else:
        return jsonify({
            "code": 1000,
            "msg": "用户名或密码错误"
        })


# 用户获取所有店铺信息
@app.route("/api/user/shop", methods=["GET"])
@cross_origin()
def user_get_shop():
    result = db.session.execute(text('SELECT * FROM fastfood_shop')).fetchall()
    shop_list = []

    for row in result:
        shop = {
            "shop_name": row[0],
            "price": row[1],
            "sale": row[2]
        }
        shop_list.append(shop)

    print(shop_list)
    return jsonify(status=200, tabledata=shop_list)


# 用户提交订单
# 用户提交订单
@app.route("/api/user/addorder", methods=["POST"])
@cross_origin()
def user_addorder():
    data = request.json

    shop_name = data.get("shop_name")
    order_money = data.get("order_money")
    order_way = data.get("order_way")
    cons_name = data.get("cons_name")
    cons_address = data.get("cons_addre")

    # 从 token 中解析出手机号
    token = request.headers.get('token')
    cons_phone = get_token_phone(token)

    create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 插入订单记录
    sql_order = '''
        INSERT INTO oorder(
            shop_name, order_money, order_way,
            cons_phone, cons_name, cons_addre, create_time
        ) VALUES (:shop_name, :order_money, :order_way, :cons_phone, :cons_name, :cons_addre, :create_time)
    '''
    db.session.execute(
        text(sql_order),
        {
            "shop_name": shop_name,
            "order_money": order_money,
            "order_way": order_way,
            "cons_phone": cons_phone,
            "cons_name": cons_name,
            "cons_addre": cons_address,
            "create_time": create_time
        }
    )
    db.session.commit()

    # 查询刚插入订单的 ID
    order_id_result = db.session.execute(
        text("SELECT LAST_INSERT_ID()")
    ).first()
    order_id = order_id_result[0] if order_id_result else None

    # 插入物流记录（配送员写死为 D001，预计时间写死为“25分钟”）

    sql_logistics = '''
        INSERT INTO wuliu(
            order_id, cons_phone, disp_id, deliver_time, ended
        ) VALUES (:order_id, :cons_phone, :disp_id, :deliver_time, :ended)
    '''
    db.session.execute(
        text(sql_logistics),
        {
            "order_id": order_id,
            "cons_phone": cons_phone,
            "disp_id": "D001",
            "deliver_time": "25分钟",
            "ended": 0
        }
    )
    db.session.commit()

    return jsonify(status=200, msg="成功下单")

# 从 token 中提取用户手机号
def get_token_phone(token):
    data = auth.decode_func(token)
    return data.get('telephone')
# 查询/修改/删除 未派送订单
@app.route("/api/user/unsend", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_unsend():
    if request.method == 'GET':
        # 获取当前用户的未派送订单
        phone = get_token_phone(request.headers.get('token'))
        print(phone)
        result = db.session.execute(
            text('SELECT * FROM oorder WHERE checked=0 AND cons_phone="%s"' % phone)
        ).fetchall()

        order_list = []
        for row in result:
            order = {
                "order_id": row[0],
                "shop_name": row[1],
                "price": row[2],
                "orderway": row[3],
                "cons_name": row[5],
                "cons_addre": row[6],
                "create_time": row[8],
                "status_desc": get_status_desc(row[7])  # row[7] 是 checked

            }
            order_list.append(order)
        return jsonify(status=200, tabledata=order_list)

    elif request.method == 'POST':
        # 修改未派送订单的收件人信息
        data = request.json
        order_id = data.get("order_id")
        cons_name = data.get("cons_name")
        cons_addre = data.get("cons_addre")

        db.session.execute(
            text('UPDATE oorder SET cons_name="%s", cons_addre="%s" WHERE order_id=%d' %
                 (cons_name, cons_addre, order_id))
        )
        db.session.commit()
        return jsonify(status=200, msg="修改成功")

    elif request.method == 'DELETE':
        # 删除指定订单
        order_id = request.json.get("delete_id")
        db.session.execute(
            text('DELETE FROM oorder WHERE order_id=%d' % order_id)
        )
        db.session.commit()
        return jsonify(status=200, msg="删除成功")


# 查询 派送中订单
@app.route("/api/user/sending", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_sending():
    if request.method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        result = db.session.execute(
            text('SELECT * FROM sending_order WHERE cons_phone="%s"' % phone)
        ).fetchall()

        sending_list = []
        for row in result:
            order = {
                "order_id": row[0],
                "shop_name": row[1],
                "order_money": row[2],
                "order_way": row[3],
                "cons_phone": row[4],
                "cons_name": row[5],
                "cons_addre": row[6],
                "disp_id": row[7],
                "deliver_time": row[8],
                "disp_phone": row[9]
            }
            sending_list.append(order)

        return jsonify(status=200, tabledata=sending_list)


# 查询 已派送订单
@app.route("/api/user/sended", methods=["POST", "GET", "DELETE"])
@cross_origin()
def user_sended():
    if request.method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        result = db.session.execute(
            text('SELECT * FROM sended_order WHERE cons_phone="%s"' % phone)
        ).fetchall()

        sended_list = []
        for row in result:
            order = {
                "order_id": row[0],
                "shop_name": row[1],
                "order_money": row[2],
                "order_way": row[3],
                "cons_phone": row[4],
                "cons_name": row[5],
                "cons_addre": row[6],
                "disp_id": row[7],
                "deliver_time": row[8],
                "disp_phone": row[9]

            }
            sended_list.append(order)

        return jsonify(status=200, tabledata=sended_list)

# 获取用户个人信息
@app.route("/api/user/usermsg", methods=["POST", "GET"])
@cross_origin()
def usermsg():
    if request.method == 'GET':
        phone = get_token_phone(request.headers.get('token'))
        result = db.session.execute(
            text('SELECT * FROM user_msg WHERE phone="%s"' % phone)
        ).fetchall()

        if not result:
            return jsonify(status=1000, msg="用户信息不存在")

        info = {
            "real_name": result[0][1],
            "sex": result[0][2],
            "age": result[0][3],
            "mail": result[0][4],
            "phone": result[0][5],
            "user_name": result[0][6]
        }

        return jsonify(status=200, data=info)


# 修改密码
@app.route("/api/user/pwd_chg", methods=["POST"])
@cross_origin()
def user_pwd_chg():
    if request.method == 'POST':
        new_pwd = request.json.get('new_pwd')
        old_pwd = request.json.get('old_pwd')
        phone = get_token_phone(request.headers.get('token'))

        # 校验旧密码
        result = db.session.execute(
            text('SELECT * FROM user WHERE telephone="%s" AND password="%s"' % (phone, old_pwd))
        ).fetchall()

        if not result:
            return jsonify(status=1000, msg="原始密码错误")

        # 更新为新密码
        db.session.execute(
            text('UPDATE user SET password="%s" WHERE telephone="%s"' % (new_pwd, phone))
        )
        db.session.commit()
        return jsonify(status=200, msg="修改成功")


# 管理员管理店铺（增删改查）
@app.route("/api/manager/shop", methods=["POST", "GET", "DELETE"])
@cross_origin()
def manager_shop():
    if request.method == 'GET':
        result = db.session.execute(text('SELECT * FROM fastfood_shop')).fetchall()
        shop_list = []
        for row in result:
            shop = {
                "shop_name": row[0],
                "price": row[1],
                "sale": row[2]
            }
            shop_list.append(shop)
        return jsonify(status=200, tabledata=shop_list)

    elif request.method == 'POST':
        action = request.json.get('action')

        if action == "add":
            data = request.json
            shop_name = data.get('shop_name')
            price = int(data.get('price'))
            m_sale_v = int(data.get('m_sale_v'))

            exist = db.session.execute(
                text('SELECT * FROM fastfood_shop WHERE shop_name="%s"' % shop_name)
            ).fetchall()

            if not exist:
                db.session.execute(
                    text('INSERT INTO fastfood_shop(shop_name, price, m_sale_v) VALUES("%s", %d, %d)' %
                         (shop_name, price, m_sale_v))
                )
                db.session.commit()
                return jsonify(status=200, msg="添加成功")
            else:
                return jsonify(status=1000, msg="该店铺已存在")

        elif action == "change":
            data = request.json
            shop_name = data.get('shop_name')
            price = int(data.get('price'))
            m_sale_v = int(data.get('m_sale_v'))

            db.session.execute(
                text('UPDATE fastfood_shop SET price=%d, m_sale_v=%d WHERE shop_name="%s"' %
                     (price, m_sale_v, shop_name))
            )
            db.session.commit()
            return jsonify(status=200, msg="修改成功")

    elif request.method == 'DELETE':
        shop_name = request.json.get('want_delete')
        db.session.execute(
            text('DELETE FROM fastfood_shop WHERE shop_name="%s"' % shop_name)
        )
        db.session.commit()
        return jsonify(status=200, msg="删除成功")
# 管理员管理服务员信息（增删查）
@app.route("/api/manager/server", methods=["POST", "GET", "DELETE"])
@cross_origin()
def manager_server():
    if request.method == 'GET':
        # 查询所有服务员信息
        result = db.session.execute(text('SELECT * FROM server')).fetchall()
        server_list = []
        for row in result:
            server_list.append({
                "service_id": row[0],
                "service_name": row[1],
                "fastfood_shop_name": row[2]
            })

        # 获取所有店铺，用于服务员绑定选项
        shop_result = db.session.execute(text('SELECT shop_name FROM fastfood_shop')).fetchall()
        shop_list = [{"shop_name": row[0]} for row in shop_result]

        print(shop_list)
        return jsonify(status=200, tabledata=server_list, shop_range=shop_list)

    elif request.method == 'POST':
        data = request.json
        service_id = data.get('service_id')
        service_name = data.get('service_name')
        shop_name = data.get('fastfood_shop_name')

        exist = db.session.execute(
            text('SELECT * FROM server WHERE service_id="%s"' % service_id)
        ).fetchall()

        if not exist:
            db.session.execute(
                text('INSERT INTO server(service_id, service_name, fastfood_shop_name) '
                     'VALUES ("%s", "%s", "%s")' %
                     (service_id, service_name, shop_name))
            )
            db.session.commit()
            return jsonify(status=200, msg="添加成功")
        else:
            return jsonify(status=1000, msg="该编号已存在")

    elif request.method == 'DELETE':
        service_id = request.json.get('want_delete')
        db.session.execute(
            text('DELETE FROM server WHERE service_id="%s"' % service_id)
        )
        db.session.commit()
        return jsonify(status=200, msg="解雇成功")


# 管理员管理配送员信息（增删查）
@app.route("/api/manager/dispatcher", methods=["POST", "GET", "DELETE"])
@cross_origin()
def manager_dispatcher():
    if request.method == 'GET':
        result = db.session.execute(text('SELECT * FROM dispatcher')).fetchall()
        dispatcher_list = []
        for row in result:
            dispatcher_list.append({
                "dispatcher_id": row[0],
                "dispatcher_name": row[1],
                "dispatcher_phone": row[2]
            })
        return jsonify(status=200, tabledata=dispatcher_list)

    elif request.method == 'POST':
        data = request.json
        dispatcher_id = data.get('dispatcher_id')
        dispatcher_name = data.get('dispatcher_name')
        dispatcher_phone = data.get('dispatcher_phone')

        exist = db.session.execute(
            text('SELECT * FROM dispatcher WHERE dispatcher_id="%s"' % dispatcher_id)
        ).fetchall()

        if not exist:
            db.session.execute(
                text('INSERT INTO dispatcher(dispatcher_id, dispatcher_name, dispatcher_phone) '
                     'VALUES ("%s", "%s", "%s")' %
                     (dispatcher_id, dispatcher_name, dispatcher_phone))
            )
            db.session.commit()
            return jsonify(status=200, msg="添加成功")
        else:
            return jsonify(status=1000, msg="该编号已存在")

    elif request.method == 'DELETE':
        dispatcher_id = request.json.get('want_delete')
        db.session.execute(
            text('DELETE FROM dispatcher WHERE dispatcher_id="%s"' % dispatcher_id)
        )
        db.session.commit()
        return jsonify(status=200, msg="解雇成功")
# 查询物流记录：根据是否已完成
@app.route("/api/manager/wuliu", methods=["GET"])
@cross_origin()
def manager_wuliu():
    ended = request.args.get('id')  # 0 表示未完成，1 表示已完成

    query = 'SELECT * FROM wuliu WHERE ended=%s' % ended
    result = db.session.execute(text(query)).fetchall()

    logistics_list = []
    for row in result:
        logistics_list.append({
            "order_id": row[0],
            "cons_phone": row[1],
            "disp_id": row[2],
            "deliver_time": row[3]
        })

    return jsonify(status=200, tabledata=logistics_list)


# 管理员查看未派单订单，并执行派单
@app.route("/api/manager/unsend", methods=["GET", "POST"])
@cross_origin()
def manager_unsend():
    if request.method == 'GET':
        # 获取所有未派单订单
        result = db.session.execute(text('SELECT * FROM oorder WHERE checked=0')).fetchall()
        order_list = []
        for row in result:
            order_list.append({
                "order_id": row[0],
                "shop_name": row[1],
                "price": row[2],
                "orderway": row[3],
                "cons_phone": row[4],
                "cons_name": row[5],
                "cons_addre": row[6],
                "create_time": row[8]
            })

        # 获取所有配送员供前端选择
        disp_result = db.session.execute(text('SELECT * FROM dispatcher')).fetchall()
        dispatcher_range = [{"disp_id": row[0]} for row in disp_result]

        return jsonify(status=200, tabledata=order_list, disp_range=dispatcher_range)

    elif request.method == 'POST':
        data = request.json
        order_id = int(data.get('order_id'))
        dispatcher_id = data.get('dispatcher_id')
        deliver_time = data.get('deliver_time')

        # 获取对应订单的用户手机号
        cons_phone = db.session.execute(
            text('SELECT cons_phone FROM oorder WHERE order_id=%d' % order_id)
        ).first()

        # 插入物流表进行派单
        db.session.execute(
            text('INSERT INTO wuliu(order_id, cons_phone, disp_id, deliver_time) '
                 'VALUES(%d, "%s", "%s", "%s")' %
                 (order_id, cons_phone[0], dispatcher_id, deliver_time))
        )
        db.session.commit()
        return jsonify(status=200, msg="成功派发")

# 更新订单状态接口（所有用户通用）
@app.route("/api/order/update_status", methods=["POST"])
@cross_origin()
def update_order_status():
    data = request.json
    order_id = int(data.get("order_id"))
    new_status = int(data.get("checked"))  # 1~5

    #token = request.headers.get('token')
    token = request.headers.get('Authorization')
    user_info = auth.decode_func(token)
    role = user_info.get("role")

    # 只有顾客(0)、商家(2)、配送员(3)能更新状态
    #if role not in [0, 2, 3]:
        #return jsonify(status=1001, msg="无权限更新订单状态")

    # 更新数据库
    db.session.execute(
        text('UPDATE oorder SET checked = :new_status WHERE order_id = :oid'),
        {"new_status": new_status, "oid": order_id}
    )
    db.session.commit()
    return jsonify(status=200, msg="订单状态已更新")



# 管理员查看正在配送的订单
@app.route("/api/manager/sending", methods=["GET"])
@cross_origin()
def manager_sending():
    result = db.session.execute(text('SELECT * FROM sending_order')).fetchall()
    sending_list = []
    for row in result:
        sending_list.append({
            "order_id": row[0],
            "shop_name": row[1],
            "order_money": row[2],
            "order_way": row[3],
            "cons_phone": row[4],
            "cons_name": row[5],
            "cons_addre": row[6],
            "disp_id": row[7],
            "deliver_time": row[8]
        })
    return jsonify(status=200, tabledata=sending_list)

@app.route("/api/dispatcher/orders/count", methods=["GET"])
@cross_origin()
def dispatcher_order_count():
    #token = request.headers.get('token')
    token = request.headers.get('Authorization')
    user_info = auth.decode_func(token)

    #if user_info.get("role") != 3:
        #return jsonify(status=1001, msg="无权限访问")

    phone = user_info.get("telephone")

    # 根据手机号查配送员 ID
    dispatcher = db.session.execute(
        text('SELECT dispatcher_id FROM dispatcher WHERE dispatcher_phone = :phone'),
        {"phone": phone}
    ).first()

    if not dispatcher:
        return jsonify(status=1002, msg="未找到对应配送员账号")

    dispatcher_id = dispatcher[0]

    # 查询配送中订单数量（checked = 4）
    count = db.session.execute(
        text('SELECT COUNT(*) FROM wuliu '
             'JOIN oorder ON wuliu.order_id = oorder.order_id '
             'WHERE wuliu.disp_id = :did'),
        {"did": dispatcher_id}
    ).scalar()

    return jsonify(status=200, data={"dispatcher_id": dispatcher_id, "current_orders": count})



# 管理员查看已配送订单
@app.route("/api/manager/sended", methods=["GET"])
@cross_origin()
def manager_sended():
    result = db.session.execute(text('SELECT * FROM sended_order')).fetchall()
    sended_list = []
    for row in result:
        sended_list.append({
            "order_id": row[0],
            "shop_name": row[1],
            "order_money": row[2],
            "order_way": row[3],
            "cons_phone": row[4],
            "cons_name": row[5],
            "cons_addre": row[6],
            "disp_id": row[7],
            "deliver_time": row[8]
        })
    return jsonify(status=200, tabledata=sended_list)


@app.route("/api/dispatcher/orders/list", methods=["GET"])
@cross_origin()
def list_all_dispatcher_orders():
    # 查询所有配送员及其派送中订单数量（checked ∈ 1~4）
    result = db.session.execute(text("""
        SELECT 
            d.dispatcher_id,
            d.dispatcher_name,
            d.dispatcher_phone,
            COUNT(o.order_id) AS current_orders
        FROM dispatcher d
        LEFT JOIN wuliu w ON d.dispatcher_id = w.disp_id
        LEFT JOIN oorder o ON w.order_id = o.order_id AND o.checked IN (1, 2, 3, 4)
        GROUP BY d.dispatcher_id, d.dispatcher_name, d.dispatcher_phone
    """)).fetchall()

    # 构造返回数据
    data = []
    for row in result:
        data.append({
            "dispatcher_id": row[0],
            "dispatcher_name": row[1],
            "dispatcher_phone": row[2],
            "current_orders": row[3]
        })

    return jsonify(status=200, data=data)


# 启动应用
if __name__ == '__main__':
    # 启动 Flask 应用，启用 debug 模式
    app.run(debug=True, host='127.0.0.1', port=5000)
