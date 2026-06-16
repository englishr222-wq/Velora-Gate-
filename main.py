import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)
import config
from database import db
import admin_panel

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Conversation states
EDIT_PRICE, EDIT_PAYMENT, SEND_BROADCAST, EDIT_MESSAGE = range(4)

WELCOME_MESSAGE = (
    "✨ *مرحباً بك في بوابة Velora Gate الرقمية* ✨\n\n"
    "يسعدنا تلبية احتياجاتك لأرقى الحسابات والخدمات الرقمية بجودة واستقرار لا مثيل لهما.\n\n"
    "💡 *ماذا نقدم؟*\n"
    "• حسابات Apple ID و iCloud مجهزة ومؤمنة بأعلى المعايير.\n"
    "• حسابات Gmail موثقة وجاهزة للاستخدام الفوري.\n\n"
    "🚀 تصفح القائمة أدناه واكتشف الجودة الفائقة بنفسك!"
)

QUALITY_INFO = (
    "🛡️ *ضمان الجودة والأمان في Velora Gate* 🛡️\n\n"
    "🍏 *Apple ID & iCloud:*\n"
    "• استقرار عالي\n"
    "• حماية قوية\n\n"
    "📧 *Gmail:*\n"
    "• IPs نظيفة\n"
    "• موثقة\n"
)

SUPPORT_INFO = "🤝 *الدعم الفني*"

def get_exchange_rate_info():
    """الحصول على معلومات سعر الصرف"""
    return f"💱 *أسعار الصرف:*\n\n• 1 USDT = {config.EXCHANGE_RATE} SYP\n"

def get_deposit_info():
    """الحصول على معلومات طرق الدفع"""
    methods = db.get_payment_methods()
    text = "💳 *طرق الشحن*\n\n"
    
    for method_id, method_info in methods.items():
        text += f"{method_info['name']}: `{method_info['value']}`\n"
    
    return text

def get_prices_info():
    """الحصول على معلومات الأسعار"""
    prices = db.get_prices()
    text = "💰 *الأسعار:*\n\n"
    
    for product, price in prices.items():
        text += f"• {product.upper()}: {price:,.0f} SYP\n"
    
    return text

def main_menu():
    """القائمة الرئيسية"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ منتجاتنا", callback_data="products")],
        [
            InlineKeyboardButton("💳 شحن", callback_data="deposit"),
            InlineKeyboardButton("💱 سعر الصرف", callback_data="exchange")
        ],
        [
            InlineKeyboardButton("🌟 جودة", callback_data="quality"),
            InlineKeyboardButton("🤝 دعم", callback_data="support")
        ]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء البوت"""
    user = update.effective_user
    
    # إضافة المستخدم إلى قاعدة البيانات
    db.add_user(user.id, user.username or "Unknown", user.first_name or "User")
    
    # التحقق إذا كان الآدمن
    if admin_panel.is_admin(user.id):
        # إظهار قائمة خاصة للآدمن
        admin_buttons = main_menu().inline_keyboard.copy()
        admin_buttons.append([InlineKeyboardButton("👨‍💼 لوحة التحكم", callback_data="admin_panel")])
        special_menu = InlineKeyboardMarkup(admin_buttons)
        
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=special_menu,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    back = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ رجوع", callback_data="main")]
    ])

    # ===== قائمة الآدمن =====
    if data == "admin_panel":
        if admin_panel.is_admin(user_id):
            await query.edit_message_text(
                "👨‍💼 *لوحة التحكم*",
                reply_markup=admin_panel.admin_menu(),
                parse_mode="Markdown"
            )
        else:
            await query.answer("❌ ليس لديك صلاحيات!", show_alert=True)
        return

    # ===== القائمة الرئيسية =====
    if data == "main":
        user = update.effective_user
        if admin_panel.is_admin(user_id):
            admin_buttons = main_menu().inline_keyboard.copy()
            admin_buttons.append([InlineKeyboardButton("👨‍💼 لوحة التحكم", callback_data="admin_panel")])
            special_menu = InlineKeyboardMarkup(admin_buttons)
            await query.edit_message_text(WELCOME_MESSAGE, reply_markup=special_menu, parse_mode="Markdown")
        else:
            await query.edit_message_text(WELCOME_MESSAGE, reply_markup=main_menu(), parse_mode="Markdown")

    # ===== المحتوى العام =====
    elif data == "quality":
        await query.edit_message_text(QUALITY_INFO, reply_markup=back, parse_mode="Markdown")

    elif data == "exchange":
        await query.edit_message_text(get_exchange_rate_info(), reply_markup=back, parse_mode="Markdown")

    elif data == "deposit":
        await query.edit_message_text(get_deposit_info(), reply_markup=back, parse_mode="Markdown")

    elif data == "support":
        await query.edit_message_text(SUPPORT_INFO, reply_markup=back, parse_mode="Markdown")

    elif data == "products":
        prices_text = get_prices_info()
        await query.edit_message_text(
            f"📦 *المنتجات:*\n\n{prices_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Apple ID", callback_data="apple")],
                [InlineKeyboardButton("Gmail", callback_data="gmail")],
                [InlineKeyboardButton("⬅️ رجوع", callback_data="main")]
            ]),
            parse_mode="Markdown"
        )

    elif data in ["apple", "gmail"]:
        price = db.get_price(data)
        await query.edit_message_text(
            f"📦 قسم {data.upper()}\n\n"
            f"السعر: {price:,.0f} SYP",
            reply_markup=back
        )

    # ===== معالجات الآدمن =====
    elif admin_panel.is_admin(user_id):
        await admin_panel.admin_button_handler(update, context)

def main():
    """بدء البوت"""
    app = Application.builder().token(config.BOT_TOKEN).build()

    # معالجات أساسية
    app.add_handler(CommandHandler("start", start))
    
    # معالج الآدمن
    app.add_handler(CommandHandler("admin", admin_panel.admin_start))
    
    # مجموعة محادثة تعديل الأسعار
    price_conv_handler = ConversationHandler(
        entry_points=[],
        states={
            EDIT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_panel.handle_price_input)],
        },
        fallbacks=[],
    )
    app.add_handler(price_conv_handler)
    
    # مجموعة محادثة تعديل طرق الدفع
    payment_conv_handler = ConversationHandler(
        entry_points=[],
        states={
            EDIT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_panel.handle_payment_input)],
        },
        fallbacks=[],
    )
    app.add_handler(payment_conv_handler)
    
    # مجموعة محادثة الرسائل الجماعية
    broadcast_conv_handler = ConversationHandler(
        entry_points=[],
        states={
            SEND_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_panel.handle_broadcast_input)],
        },
        fallbacks=[],
    )
    app.add_handler(broadcast_conv_handler)
    
    # مجموعة محادثة تعديل الرسائل
    message_conv_handler = ConversationHandler(
        entry_points=[],
        states={
            EDIT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_panel.handle_message_input)],
        },
        fallbacks=[],
    )
    app.add_handler(message_conv_handler)
    
    # معالج الأزرار
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 تم تشغيل البوت بنجاح...")
    print(f"👨‍💼 معرفات الآدمن: {config.ADMIN_IDS}")
    app.run_polling()

if __name__ == "__main__":
    main()
