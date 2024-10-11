import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, JobQueue, CallbackQueryHandler

# Token de acesso do bot
TOKEN = 'seu token aqui'  # Substitua pelo seu token

DATABASE = 'usuarios.db'  # Nome do arquivo do banco de dados

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def criar_banco_dados():
    """Cria o banco de dados e a tabela se eles não existirem."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER UNIQUE
        )
    ''')
    conn.commit()
    conn.close()


def adicionar_usuario(chat_id):
    """Adiciona um novo usuário ao banco de dados."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (chat_id) VALUES (?)", (chat_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ignora se o chat_id já existir
    finally:
        conn.close()


def obter_usuarios():
    """Retorna uma lista com os IDs de todos os usuários no banco de dados."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM usuarios")
    usuarios = [row[0] for row in cursor.fetchall()]
    conn.close()
    return usuarios


async def enviar_mensagem_apos_30_minutos(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem para o usuário após 30 minutos com a informação da BR4BET e botão para cadastro."""
    job = context.job
    chat_id = job.data  # Obtém o ID do chat do job
    mensagem = """
Como o mercado está mudando e agora é extremamente necessário apostar em Plataformas REGULAMENTADAS ✅

Pra você conseguir receber BANCAS, participar de alavancagens e usufruir 100% do que tenho pra te oferecer 🤑

Clique no botão abaixo e se cadastra-se na BR4BET, Casa de Aposta brasileira que já está regulamentada 😉
"""

    # Cria o botão
    keyboard = [
        [InlineKeyboardButton("CADASTRE-SE AQUI", url="#link do seu bot aqui")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text=mensagem, reply_markup=reply_markup, parse_mode='Markdown')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de boas-vindas com botões e adiciona o usuário ao banco de dados."""
    chat_id = update.effective_chat.id

    # Cria os botões
    keyboard = [
        [
            InlineKeyboardButton("RECEBER BANCA 🎁",
                                 url="#link do seu grupo aqui"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=
        "Olá, Seja bem vindo! 🎁🎁🎁 \n\nMeu nome é Karen Souza e vou te dar uma BANQUINHA GRÁTIS agora mesmo no meu CANAL! 🎁\n\nClique no botão abaixo ⬇",
        reply_markup=reply_markup)  # Envia a mensagem com os botões
    adicionar_usuario(chat_id)

    # Agenda o envio de mensagens periódicas (a cada 24 horas)
    context.job_queue.run_repeating(enviar_mensagem_personalizada,
                                   interval=24 * 60 * 60,
                                   first=0)
    # Agenda o envio da mensagem da BR4BET após 30 minutos
    context.job_queue.run_once(enviar_mensagem_apos_30_minutos, 30 * 60, data=chat_id)  # 30 minutos * 60 segundos/minuto = 1800 segundos


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ecoa a mensagem do usuário."""
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                    text=update.message.text)


async def enviar_mensagem_personalizada(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem personalizada para todos os usuários no banco de dados."""
    if update.effective_user.id == #id do adm1 or update.effective_user.id == #id do adm2:  # Substitua pelo seu ID
        mensagem = " ".join(context.args)
        for chat_id in obter_usuarios():
            await context.bot.send_message(chat_id=chat_id, text=mensagem)
    else:
        await update.message.reply_text(
            "Você não tem permissão para usar este comando.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manipula as ações dos botões."""
    query = update.callback_query
    await query.answer()

    if query.data == 'ofertas':
        await query.edit_message_text(text="Em breve, ofertas imperdíveis aqui!")
    elif query.data == 'contato':
        await query.edit_message_text(
            text="Entre em contato conosco pelo email: contato@exemplo.com")


def main() -> None:
    """Inicia o bot."""
    criar_banco_dados()  # Cria o banco de dados ao iniciar o bot
    application = ApplicationBuilder().token(TOKEN).build()
    job_queue = application.job_queue

    # Adiciona handlers para os comandos e mensagens
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                           echo))
    application.add_handler(CommandHandler("enviar",
                                          enviar_mensagem_personalizada))
    application.add_handler(CallbackQueryHandler(button))

    # Inicia o bot
    application.run_polling()


if __name__ == '__main__':
    main()
