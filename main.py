import asyncio
import logging
import os
from stellar_sdk import Server, Asset
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ASSET_CODE = "ORANGE"
ASSET_ISSUER = "GAHJE75PMXWFSCGE7HMG2OFEXSC2IEEF7FTWHPDRLKRT6ERE6GYZTEPC"

server = Server("https://horizon.stellar.org")
asset_token = Asset(ASSET_CODE, ASSET_ISSUER)
asset_xlm = Asset.native()
cursor = "now"

logging.basicConfig(level=logging.INFO)

async def send_buy_alert(bot, xlm_amount, token_amount, buyer):
    message = (
        f"🚀 *Buy Alert!*\n"
        f"💸 {xlm_amount:.2f} XLM → {token_amount:,.0f} ${ASSET_CODE}\n"
        f"👤 By: `{buyer}`"
    )
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

async def monitor_trades():
    global cursor
    bot = Bot(token=BOT_TOKEN)
    while True:
        try:
            trades = server.trades() \
                .for_asset_pair(asset_xlm, asset_token) \
                .cursor(cursor) \
                .limit(10) \
                .order(desc=False) \
                .call()

            for trade in trades["_embedded"]["records"]:
                cursor = trade["paging_token"]

                if trade["base_asset_type"] == "native" and trade.get("counter_asset_code") == ASSET_CODE:
                    buyer = trade.get("base_account", "unknown")
                    xlm_amount = float(trade["base_amount"])
                    token_amount = float(trade["counter_amount"])

                elif trade["counter_asset_type"] == "native" and trade.get("base_asset_code") == ASSET_CODE:
                    buyer = trade.get("counter_account", "unknown")
                    xlm_amount = float(trade["counter_amount"])
                    token_amount = float(trade["base_amount"])

                else:
                    continue

                if xlm_amount >= 10:
                    await send_buy_alert(bot, xlm_amount, token_amount, buyer)

            await asyncio.sleep(5)

        except Exception as e:
            logging.error(f"[ERROR] {e}")
            await asyncio.sleep(10)

async def main():
    logging.info(f"🔍 Memantau pembelian token {ASSET_CODE}...")
    await monitor_trades()

if __name__ == "__main__":
    asyncio.run(main())
