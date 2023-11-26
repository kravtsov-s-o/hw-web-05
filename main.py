import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta


async def fetch_exchange_rates(date, session):
    url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
    try:
        async with session.get(url) as response:
            data = await response.json()
            return data['exchangeRate']
    except aiohttp.ClientError as ce:
        print(f"Aiohttp ClientError: {ce}")
        return []


async def get_currency_rates(days):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_exchange_rates((datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y'), session) for i in
                 range(days)]
        results = await asyncio.gather(*tasks)

        formatted_results = []
        for i in range(days):
            formatted_date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')

            formatted_result = {}

            for r in results[i]:
                if r['currency'] in ['USD', 'EUR']:
                    formatted_result[r['currency']] = {'sale': r['saleRateNB'], 'purchase': r['purchaseRateNB']}

            formatted_results.append({formatted_date: formatted_result})

        return formatted_results


def main():
    if len(sys.argv) != 2:
        sys.argv.append(1)

    try:
        days = int(sys.argv[1])
        if days <= 0 or days > 10:
            raise ValueError("Number of days should be between 1 and 10.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_currency_rates(days))
    print(result)


if __name__ == "__main__":
    main()
