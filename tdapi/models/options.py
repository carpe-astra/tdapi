"""Models for auth option chain objects"""

from typing import List, Optional

from pydantic import BaseModel

from tdapi.constants.options import (
    ExchangeName,
    IncludeQuotes,
    PutCall,
    Range,
    Strategy,
    Type,
)


class ExpirationDate(BaseModel):
    date: str


class OptionDeliverables(BaseModel):
    symbol: str
    assetType: str
    deliverableUnits: str
    currencyType: str


class StrikePriceMap(dict):
    pass


class Option(BaseModel):
    putCall: PutCall
    symbol: str
    description: str
    exchangeName: str
    bidPrice: Optional[float]
    askPrice: Optional[float]
    lastPrice: Optional[float]
    markPrice: Optional[float]
    bidSize: float
    askSize: float
    lastSize: float
    highPrice: float
    lowPrice: float
    openPrice: float
    closePrice: float
    totalVolume: float
    quoteTimeInLong: float
    tradeTimeInLong: float
    netChange: float
    volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    timeValue: float
    openInterest: float
    isInTheMoney: Optional[bool]
    theoreticalOptionValue: float
    theoreticalVolatility: float
    isMini: Optional[bool]
    isNonStandard: Optional[bool]
    optionDeliverablesList: Optional[List[OptionDeliverables]]
    strikePrice: float
    expirationDate: str
    expirationType: str
    multiplier: float
    settlementType: str
    deliverableNote: str
    isIndexOption: Optional[bool]
    percentChange: float
    markChange: float
    markPercentChange: float


class Underlying(BaseModel):
    ask: float
    askSize: float
    bid: float
    bidSize: float
    change: float
    close: float
    delayed: bool
    description: str
    exchangeName: ExchangeName
    fiftyTwoWeekHigh: float
    fiftyTwoWeekLow: float
    highPrice: float
    last: float
    lowPrice: float
    mark: float
    markChange: float
    markPercentChange: float
    openPrice: float
    percentChange: float
    quoteTime: float
    symbol: str
    totalVolume: float
    tradeTime: float


class OptionChain(BaseModel):
    symbol: str
    status: str
    underlying: Underlying
    strategy: Strategy
    interval: float
    isDelayed: bool
    isIndex: bool
    daysToExpiration: float
    interestRate: float
    underlyingPrice: float
    volatility: float
    callExpDateMap: StrikePriceMap
    putExpDateMap: StrikePriceMap
