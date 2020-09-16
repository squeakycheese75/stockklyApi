import pandas as pd
from json import loads
import logging
from api.repositories.products_repo import get_product
from api.repositories.prices_repo import get_price_trend, get_price_latest

log = logging.getLogger(__name__)


def get_historical(ticker, span) -> list:
    try:
        price_list = clean_price_list(ticker, span)
        if not price_list:
            return []
        converted_price_list = convert_price_list(price_list)
        return converted_price_list
    except (KeyError, TypeError, ValueError, AttributeError) as error_ee:
        log.error("Could not connect extract historical prices: %s" % error_ee)
        return []


def get_price(ticker) -> dict:
    response = get_price_latest(ticker)
    product = get_product(ticker)
    if product:
        response['symbol'] = product['quote']['symbol']
        response['displayTicker'] = product['displayTicker']
    return response


def clean_price_list(ticker: str, span: int) -> list:
    price_history = get_price_trend(ticker, span)

    price_list = []
    for price_item in price_history:
        if type(price_item['price']) is float:
            price_list.append(price_item)
    return price_list


def convert_price_list(price_list: list) -> dict:
    # convert to dataframe and format for the chart
    df = pd.DataFrame(price_list)
    df = df.set_index(pd.DatetimeIndex(df['priceDate']).strftime("%Y-%m-%d"))
    # drop the priceDate column
    target_column = 'priceDate'
    resval = df.drop(target_column, axis=1)

    r = resval.to_json(date_format='iso')
    rv = loads(r)
    return rv['price']
