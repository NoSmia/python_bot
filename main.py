from contextlib import suppress
from typing import Any
import asyncio
import dotenv
import os
from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest


class Pagination(CallbackData, prefix="pagination"):
    action: str
    page: int


def paginator(page: int=0) -> InlineKeyboardBuilder:
    return (
        InlineKeyboardBuilder()
        .button(text="⬅️", callback_data=Pagination(action="prev", page=page))
        .button(text="➡️", callback_data=Pagination(action="next", page=page))
        .button(text="< Назад", callback_data="back_to_menu")
    ).adjust(2).as_markup()


router = Router()

IMAGES = {
    0: ["images/sad.png", "Where is my mood..?"],
    1: ["images/cool.png", "Инструкция по телеграмм боту Wallet"
        "\nЕсли вы ещё ни разу не пользовались «Кошельком», потребуется активировать аккаунт,"
        " перейдя в @Wallet и нажав кнопку «Start» или отправив сообщение /start."
        " Обычно «Кошелёк» может находиться либо в настройках, либо в меню вложений. "
        "Здесь же сразу можно перейти к покупке или продаже криптовалюты. Для покупки достаточно нажать на «+» рядом с балансом."
        " Если у вас на балансе отсутсвуют средства то доступ к разделам 'Отправить', 'Обменять', 'Продать' будет не доступен (пример под номером 1).  "
        "Для российского рынка есть ограничения: купить криптовалюту за рубли по российской карте нельзя." 
        " Если есть какая-либо иностранная карта, то проблем с этим способом не будет."
        " Однако россияне могут пользоваться P2P-маркетом — продавец отдаёт свою криптовалюту после перевода рублей на нужные реквизиты и наоборот."],
    2: ["images/lol.png", "\nСпособ №1 — по объявлению продавца:"
        " Заходим в раздел «P2P Маркет» → «Купить» и выбираем нужное объявление."
        "Для удобства можно выбрать необходимую валюту (например, RUB), нужную крипту (например, TON), сумму и определённый банк, на который будет осуществляться перевод средств."
        "Если выбран тот или иной банк, удобнее всего переводить со счёта этого же банка на тот, который указан в качестве метода оплаты."
        " В «Кошельке» поддерживаются все популярные российские банки и СБП."
        " Перед покупкой важно ознакомиться с деталями объявления. Обратите на количесво сделок, чем больше проведено сделок и чем больше процент их выполенения тем надёжней продавец."
        " Если после создания сделки вдруг возникнут вопросы, всегда можно связаться с продавцом."
        " Выбираем подходящее объявление, нажимаем на него, указывем желаемую сумму и кликаем «Купить»."
        ],
    3: ["images/cute.png", " Следующий шаг: нужно дождаться подтверждения продавца, скопировать реквизиты после принятия сделки и после этого отправить средства. Делать это следует одним платежом."
        " Остаётся вернуться в «Кошелёк» и нажать кнопку «Подтвердить оплату». Как только продавец проверит зачисление, он завершит сделку, а криптовалюта через мгновение окажется на балансе."
        "\nСпособ №2 — cоздание объявления:"
        " Для этого следует зайти в раздел «P2P Маркет» → «Создать объявление» → в пункте «Я хочу» выбрать «Купить»."
        " Если выбрать плавающую цену, она будет обновляться вместе с рынком. В таком случае нужно указать процент от рыночной цены на P2P-маркете, в пределах которого цена может меняться — от 70% до 150%"
        " Если выбрать фиксированную цену, то меняться в соответствии с рыночной ценой она не будет."
        " После этого останется указать сумму покупки (например, минимум 3 TON, 0.0001 BTC или 5 USDT), минимальную сумму сделки и время на оплату, за которое продавец должен отправить вам средства — 15, 30 и 45 минут или 1, 2 и 3 часа."],
    4: ["images/fuk.png", "test4 stroka?"
                          "t,fnm nen ntrncf"
                          "ye djn rhjxt"]
}


@router.message(CommandStart())
@router.callback_query(F.data == "menu")
async def start(message: Message | CallbackQuery) -> Any:
    pattern = {
        "text": "Главное меню",
        "reply_markup": (
            InlineKeyboardBuilder()
            .button(text="Купить криптовалюту", callback_data="button_1")
            .button(text="Новости", callback_data="button_2")
            .button(text="Курс криптовалют", callback_data="button_3")
            .button(text="О боте", callback_data="about_bot")
        ).adjust(2).as_markup()
    }

    if isinstance(message, CallbackQuery):
        await message.answer()
        return await message.message.edit_text(**pattern)
    await message.answer(**pattern)


@router.callback_query(F.data.startswith("button_"))
async def get_button(query: CallbackQuery) -> None:
    if query.data == "button_1":
        pattern = {
            "text": ("Покупка осуществляется на сторонних площадках. Данный бот предоставляет доступ к источникам на которых вы можете как совершить торговые "
                      "операции так и ознокомиться с их предложениями для хранения или торговли криптовалютой."
                      " Перед использованием ознакомтесь с инструкцией в разделе 'О боте' "),
            "reply_markup": (
                InlineKeyboardBuilder()
                .button(text="Commex", web_app=WebAppInfo(url="https://www.commex.com/ru"))
                .button(text="Bybit", web_app=WebAppInfo(url="https://www.bybit.com/ru-RU/"))
                .button(text="CryptoBot", url="https://t.me/CryptoBot")
                .button(text="Wallet", url="https://t.me/wallet")
                .button(text="< Назад", callback_data="menu")
            ).adjust(2).as_markup()
        }
        await query.message.edit_text(**pattern)
    elif query.data == "button_2":
        pattern = {
            "text": "В этом разделе указаны новостные источники по криптовалюте.",
            "reply_markup": (
                InlineKeyboardBuilder()
                #.button(text="Bits.media", web_app=WebAppInfo(url="https://bits.media/news/"))
                .button(text="Binance", web_app=WebAppInfo(url="https://www.binance.com/ru/feed/news/all"))
                .button(text="BitExpert", web_app=WebAppInfo(url="https://bitexpert.io/news/"))
                .button(text="Forklog", web_app=WebAppInfo(url="https://forklog.com/news"))
                .button(text="CryptoPanic", web_app=WebAppInfo(url="https://cryptopanic.com/"))
                .button(text="РБК", web_app=WebAppInfo(url="https://www.rbc.ru/crypto/"))
                .button(text="Код Дурова", web_app=WebAppInfo(url="https://kod.ru/search?search=%D0%BA%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B2%D0%B0%D0%BB%D1%8E%D1%82%D0%B0"))
                .button(text="< Назад", callback_data="menu")
            ).adjust(2).as_markup()
        }
        await query.message.edit_text(**pattern)
    elif query.data == "button_3":
        pattern = {
            "text": "В этом разделе вы можете ознакомиться с актуальной динамикой курса криптовалюты.",
            "reply_markup": (
                InlineKeyboardBuilder()
                .button(text="CoinMarketCap", web_app=WebAppInfo(url="https://coinmarketcap.com/ru/coins/"))
                .button(text="Cryptorank", web_app=WebAppInfo(url="https://cryptorank.io/ru?ysclid=lnovco71ja115856828"))
                .button(text="Coinranking", web_app=WebAppInfo(url="https://coinranking.com/"))
                .button(text="CoinCheckup", web_app=WebAppInfo(url="https://coincheckup.com/"))
                .button(text="Coin360", web_app=WebAppInfo(url="https://coin360.com/"))
                .button(text="CryptoCompare", web_app=WebAppInfo(url="https://www.cryptocompare.com/"))
                .button(text="< Назад", callback_data="menu")
            ).adjust(2).as_markup()
        }
        await query.message.edit_text(**pattern)
    else:
        pattern = {
            "text": "Unknown button",
            "reply_markup": None
        }
        await query.message.edit_text(**pattern)


@router.callback_query(F.data == "about_bot")
@router.callback_query(Pagination.filter(F.action))
async def about_bot(query: CallbackQuery, callback_data: Pagination | None=None) -> None:
    await query.answer()

    if callback_data:
        page_num = callback_data.page
        page = page_num - 1 if page_num > 0 else 0

        if callback_data.action == "next":
            page = page_num + 1 if page_num < len(IMAGES) - 1 else page_num

        with suppress(TelegramBadRequest):
            await query.message.edit_media(
                media=InputMediaPhoto(
                    media=FSInputFile(IMAGES[page][0]),
                    caption=IMAGES[page][1]
                ),
                reply_markup=paginator(page)
            )
        return

    await query.message.delete()
    await query.message.answer_photo(
        photo=FSInputFile(IMAGES[0][0]),
        caption=IMAGES[0][1],
        reply_markup=paginator()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(query: CallbackQuery) -> None:
    await query.message.delete()
    await start(query.message)


async def main() -> None:
    dotenv.load_dotenv()
    TOKEN = os.getenv("TOKEN")

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

@router.message()
async def send_echo(message: Message):
    print(message)
    await message.answer(text='Не понимаю')
if __name__ == "__main__":
    asyncio.run(main())