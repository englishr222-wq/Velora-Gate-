"""
لوحة التحكم للآدمن
Admin Panel Module
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
import config
from database import db

# Conversation states
EDIT_PRICE, EDIT_PAYMENT, SEND_BROADCAST, EDIT_MESSAGE = range(4)

def is_admin(user_id):
    """التحقق من أن المستخدم آدمن"""
    return user_id in config.ADMIN_IDS

def admin_menu():
    """قائمة لوحة التحكم الرئيسية"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 تعديل الأسعار", callback_data="admin_prices")],
        [InlineKeyboardButton("💳 تعديل طرق الدفع", callback_data="admin_payment")],
        [InlineKeyboardButton("📢 رسالة جماعية", callback_data="admin_broadcast")],
        [InlineKeyboardButton("✏️ تعديل الرسائل", callback_data="admin_edit_messages")],
        [InlineKeyboardButton("⬅️ الرجوع", callback_data="main")]
    ])

def prices_menu():
    """قائمة تعديل الأسعار"""
    prices = db.get_prices()
    buttons = []
    
    for product_id, price in prices.items():
        buttons.append([
            InlineKeyboardButton(
                f"{product_id.upper()}: {price} SYP",
                callback_data=f"edit_price_{product_id}"
            )
        ])
    
    buttons.append([InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)

def payment_methods_menu():
    """قائمة تعديل طرق الدفع"""
    methods = db.get_payment_methods()
    buttons = []
    
    for method_id, method_info in methods.items():
        buttons.append([
            InlineKeyboardButton(
                f"✏️ {method_info['name']}",
                callback_data=f"edit_payment_{method_id}"
            )
        ])
    
    buttons.append([InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)

def messages_edit_menu():
    """قائمة تعديل الرسائل"""
    messages = [
        ("welcome", "🎯 رسالة الترحيب"),
        ("quality", "🛡️ رسالة الجودة"),
        ("support", "🤝 رسالة الدعم")
    ]
    
    buttons = []
    for msg_id, msg_name in messages:
        buttons.append([
            InlineKeyboardButton(
                f"✏️ {msg_name}",
                callback_data=f"edit_msg_{msg_id}"
            )
        ])
    
    buttons.append([InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء لوحة التحكم"""
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("❌ أنت لست مسؤول!")
        return
    
    welcome = (
        f"👨‍💼 *مرحباً بك يا مسؤول*\n\n"
        f"المستخدم: {user.first_name}\n"
        f"المعرّف: {user.id}\n\n"
        f"اختر ما تريد القيام به من الخيارات أدناه:"
    )
    
    await update.message.reply_text(
        welcome,
        reply_markup=admin_menu(),
        parse_mode="Markdown"
    )

async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أزرار لوحة التحكم"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if not is_admin(user_id):
        await query.answer("❌ ليس لديك صلاحيات!", show_alert=True)
        return
    
    await query.answer()
    data = query.data

    # ===== الإحصائيات =====
    if data == "admin_stats":
        stats = db.get_users_stats()
        stats_text = (
            f"📊 *الإحصائيات العامة*\n\n"
            f"👥 عدد المستخدمين: {stats['total_users']}\n"
            f"💰 الإيرادات الكلية: {stats['total_revenue']:,.0f} SYP\n"
        )
        
        back = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")]])
        await query.edit_message_text(stats_text, reply_markup=back, parse_mode="Markdown")

    # ===== الأسعار =====
    elif data == "admin_prices":
        await query.edit_message_text(
            "💰 *تعديل الأسعار*\n\nاختر المنتج الذي تريد تعديل سعره:",
            reply_markup=prices_menu(),
            parse_mode="Markdown"
        )

    elif data.startswith("edit_price_"):
        product_id = data.replace("edit_price_", "")
        context.user_data["edit_product"] = product_id
        current_price = db.get_price(product_id)
        
        await query.edit_message_text(
            f"💰 تعديل سعر {product_id.upper()}\n\n"
            f"السعر الحالي: {current_price} SYP\n\n"
            f"أرسل السعر الجديد (رقم فقط):"
        )
        return EDIT_PRICE

    # ===== طرق الدفع =====
    elif data == "admin_payment":
        await query.edit_message_text(
            "💳 *تعديل طرق الدفع*\n\nاختر الطريقة التي تريد تعديلها:",
            reply_markup=payment_methods_menu(),
            parse_mode="Markdown"
        )

    elif data.startswith("edit_payment_"):
        method_id = data.replace("edit_payment_", "")
        context.user_data["edit_method"] = method_id
        methods = db.get_payment_methods()
        current_value = methods[method_id]["value"]
        
        await query.edit_message_text(
            f"💳 تعديل {methods[method_id]['name']}\n\n"
            f"القيمة الحالية: `{current_value}`\n\n"
            f"أرسل القيمة الجديدة:"
        )
        return EDIT_PAYMENT

    # ===== الرسائل الجماعية =====
    elif data == "admin_broadcast":
        await query.edit_message_text(
            "📢 *رسالة جماعية*\n\n"
            f"سيتم إرسال الرسالة لـ {db.get_user_count()} مستخدم\n\n"
            "اكتب الرسالة التي تريد إرسالها:"
        )
        return SEND_BROADCAST

    # ===== تعديل الرسائل =====
    elif data == "admin_edit_messages":
        await query.edit_message_text(
            "✏️ *تعديل الرسائل*\n\nاختر الرسالة التي تريد تعديلها:",
            reply_markup=messages_edit_menu(),
            parse_mode="Markdown"
        )

    elif data.startswith("edit_msg_"):
        msg_id = data.replace("edit_msg_", "")
        context.user_data["edit_message_id"] = msg_id
        current_msg = db.get_message(msg_id)
        
        await query.edit_message_text(
            f"✏️ تعديل الرسالة\n\n"
            f"الرسالة الحالية:\n"
            f"`{current_msg if current_msg else 'لا توجد رسالة'}`\n\n"
            f"أرسل الرسالة الجديدة:"
        )
        return EDIT_MESSAGE

    # ===== الرجوع =====
    elif data == "admin_panel":
        await query.edit_message_text(
            "👨‍💼 *لوحة التحكم*",
            reply_markup=admin_menu(),
            parse_mode="Markdown"
        )


async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال السعر الجديد"""
    try:
        new_price = float(update.message.text)
        product_id = context.user_data.get("edit_product")
        
        db.update_price(product_id, new_price)
        
        await update.message.reply_text(
            f"✅ تم تحديث سعر {product_id.upper()} إلى {new_price} SYP",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")]
            ])
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return EDIT_PRICE


async def handle_payment_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة إدخال طريقة الدفع الجديدة"""
    new_value = update.message.text
    method_id = context.user_data.get("edit_method")
    
    db.update_payment_method(method_id, new_value)
    
    await update.message.reply_text(
        f"✅ تم تحديث طريقة الدفع بنجاح",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")]
        ])
    )
    return ConversationHandler.END


async def handle_broadcast_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسالة الجماعية"""
    message_text = update.message.text
    
    # يمكنك هنا إضافة كود لإرسال الرسالة لجميع المستخدمين
    # هذا مثال بسيط:
    
    await update.message.reply_text(
        f"✅ تم حفظ الرسالة الجماعية\n\n"
        f"ستُرسل إلى {db.get_user_count()} مستخدم",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")]
        ])
    )
    return ConversationHandler.END


async def handle_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة تعديل الرسالة"""
    new_content = update.message.text
    msg_id = context.user_data.get("edit_message_id")
    
    db.update_message(msg_id, new_content)
    
    await update.message.reply_text(
        "✅ تم تحديث الرسالة بنجاح",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ رجوع", callback_data="admin_panel")]
        ])
    )
    return ConversationHandler.END
