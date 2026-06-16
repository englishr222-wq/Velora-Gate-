import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعدادات التسجيل لمراقبة الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- النصوص الترحيبية والمعلوماتية (تعديل سهل) ---
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
    "🍏 *حسابات Apple ID & iCloud:*\n"
    "• تم إنشاؤها عبر سيرفرات مخصصة لضمان الاستقرار.\n"
    "• خالية تماماً من مشاكل القفل المفاجئ وتدعم كامل خدمات المزامنة.\n"
    "• نوفر معلومات الأمان الكاملة (الأسئلة السريّة أو التحقق الثنائي).\n\n"
    "📧 *حسابات Gmail:*\n"
    "• حسابات قديمة وجديدة تم إنشاؤها بـ IPs نظيفة.\n"
    "• موثقة ومقاومة لطلبات التحقق التعجيزية.\n\n"
    "👑 *شعارنا:* الاستدامة والأمان قبل كل شيء."
)

EXCHANGE_RATE_INFO = (
    "💱 *أسعار الصرف المعتمدة اليوم:*\n\n"
    "• 1 USDT (BEP20) ↔️ 15,000 ليرة سورية\n"
    "• سيراتيل كاش و شام كاش يعاملان بنفس القيمة الرسمية للمتجر.\n\n"
    "⚠️ *ملاحظة:* يتم تحديث الأسعار بشكل دوري بناءً على تقلبات السوق."
)

DEPOSIT_INFO = (
    "💳 *طرق شحن الرصيد المتاحة* 💳\n\n"
    "لإتمام عملية الشحن، يرجى التحويل إلى أحد الحسابات التالية ثم إرسال الإيصال للدعم:\n\n"
    "📱 *سيراتيل كاش (Syriatel Cash):*\n"
    "`0912345678`\n\n"
    "📱 *شام كاش (Cham Cash):*\n"
    "`0987654321`\n\n"
    "🌐 *USDT (Network: BEP20):*\n"
    "`0xYourCryptoWalletAddressGoesHere`\n\n"
    "📥 بعد التحويل، اضغط على زر '📧 التواصل مع الدعم' وأرسل لقطة شاشة للإيصال ليتم تفعيل رصيدك فوراً."
)

SUPPORT_INFO = (
    "🤝 *الدعم الفني والخدمات الفورية*\n\n"
    "فريق Velora Gate في خدمتك دائماً للاستفسارات، حل المشاكل، أو لتثبيت عمليات الشحن.\n\n"
    "اضغط على الرابط أدناه للتواصل المباشر مع المطور:"
)

# --- دالة إنشاء القائمة الرئيسية ---
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛍️ منتجاتنا", callback_data='products')],
        [InlineKeyboardButton("💳 شحن الرصيد", callback_data='deposit'), InlineKeyboardButton("💱 سعر الصرف 💱", callback_data='exchange')],
        [InlineKeyboardButton("🔗 رابط الإحالة", callback_data='referral'), InlineKeyboardButton("🌟 جودة المنتجات", callback_data='quality')],
        [InlineKeyboardButton("📧 التواصل مع الدعم", callback_data='support')]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- معالجة الأوامر ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عند إرسال /start تظهر الرسالة الترحيبية الفخمة"""
    await update.message.reply_text(
        text=WELCOME_MESSAGE,
        reply_markup=main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الضغط على الأزرار المرنة"""
    query = update.callback_query
    await query.answer()
    
    data = query.data

    # زر العودة للقائمة الرئيسية
    back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data='main_menu')]])

    if data == 'main_menu':
        await query.edit_message_text(text=WELCOME_MESSAGE, reply_markup=main_menu_keyboard(), parse_mode='Markdown')
        
    elif data == 'quality':
        await query.edit_message_text(text=QUALITY_INFO, reply_markup=back_keyboard, parse_mode='Markdown')
        
    elif data == 'exchange':
        await query.edit_message_text(text=EXCHANGE_RATE_INFO, reply_markup=back_keyboard, parse_mode='Markdown')
        
    elif data == 'deposit':
        await query.edit_message_text(text=DEPOSIT_INFO, reply_markup=back_keyboard, parse_mode='Markdown')
        
    elif data == 'referral':
        user_id = query.from_user.id
        # توليد رابط إحالة فريد بناءً على الـ ID الخاص بالمستخدم
        ref_link = f"https://t.me/{(context.bot.username)}?start=ref_{user_id}"
        ref_text = (
            "🔗 *نظام الإحالة وكسب الأرباح:*\n\n"
            "شارك الرابط الخاص بك مع أصدقائك، وعند قيامهم بأي عملية شراء ستحصل على عمولة تضاف لرصيدك تلقائياً!\n\n"
            f"رابط الإحالة الخاص بك:\n`{ref_link}`"
        )
        await query.edit_message_text(text=ref_text, reply_markup=back_keyboard, parse_mode='Markdown')
        
    elif data == 'support':
        support_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👨‍💻 مراسلة الدعم المباشر", url="https://t.me/YourSupportUsername")], # ضع يوزر الدعم هنا
            [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data='main_menu')]
        ])
        await query.edit_message_text(text=SUPPORT_INFO, reply_markup=support_keyboard, parse_mode='Markdown')
        
    elif data == 'products':
        products_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🍏 Apple ID / iCloud", callback_data='prod_apple')],
            [InlineKeyboardButton("📧 Gmail Accounts", callback_data='prod_gmail')],
            [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data='main_menu')]
        ])
        await query.edit_message_text(text="📦 *قائمة المنتجات المتاحة:* \nإختر القسم الذي تريد التصفح منه:", reply_markup=products_keyboard, parse_mode='Markdown')

    elif data in ['prod_apple', 'prod_gmail']:
        # تفريغ الأقسام لعرضها للعميل
        prod_type = "Apple ID & iCloud" if data == 'prod_apple' else "Gmail"
        prod_details = (
            f"📦 *قسم حسابات {prod_type}*\n\n"
            "• الحسابات المتوفرة حالياً جاهزة للتسليم التلقائي.\n"
            "• السعر: يتم تحديثه برمجياً عند ربط قاعدة البيانات.\n\n"
            "⚠️ _ملاحظة: السكريبت حالياً واجهة ذكية، يمكنك ربطه لاحقاً بقاعدة بيانات لتسليم الحسابات فوراً._"
        )
        await query.edit_message_text(text=prod_details, reply_markup=back_keyboard, parse_mode='Markdown')

def main() -> None:
    # ضع التوكن الخاص بالبوت الذي حصلت عليه من BotFather هنا
    BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    # بدء تشغيل البوت
    print("🔋 Velora Gate Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()

python-telegram-bot==21.1.1

# Ignore environment variables and tokens
config.py
.env
__pycache__/
