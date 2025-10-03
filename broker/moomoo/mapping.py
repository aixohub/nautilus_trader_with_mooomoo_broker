from nautilus_trader.model.enums import OrderType, TimeInForce, OrderStatus, OrderSide

FUTU_MAP_ORDER_TYPE: dict[int | tuple[int, int], str] = {
    OrderType.LIMIT: "NORMAL",
    OrderType.LIMIT_IF_TOUCHED: "MARKET_IF_TOUCHED",
    OrderType.MARKET: "MARKET",
    OrderType.MARKET_IF_TOUCHED: "LIMIT_IF_TOUCHED",
    OrderType.MARKET_TO_LIMIT: "MTL",
    OrderType.STOP_LIMIT: "STOP_LIMIT",
    OrderType.STOP_MARKET: "STOP",
    OrderType.TRAILING_STOP_LIMIT: "TRAILING_STOP_LIMIT",
    OrderType.TRAILING_STOP_MARKET: "TRAILING_STOP",
    (OrderType.MARKET, TimeInForce.AT_THE_CLOSE): "MOC",
    (OrderType.LIMIT, TimeInForce.AT_THE_CLOSE): "LOC",
}

FUTU_MAP_ORDER_STATUS = {
    "WAITING_SUBMIT": OrderStatus.SUBMITTED,
    "SUBMITTING": OrderStatus.SUBMITTED,
    "PendingCancel": OrderStatus.PENDING_CANCEL,
    "SUBMITTED": OrderStatus.ACCEPTED,
    "DISABLED": OrderStatus.CANCELED,
    "FILLED_ALL": OrderStatus.FILLED,
    "FAILED": OrderStatus.DENIED,
}

FUTU_MAP_TIME_IN_FORCE = {
    "DAY": TimeInForce.DAY,
    "GTC": TimeInForce.GTC,
}

FUTU_MAP_ORDER_ACTION = {
    "BUY": OrderSide.BUY,
    "SELL": OrderSide.SELL,
    "BUY_BACK": OrderSide.BUY,
    "SELL_SHORT": OrderSide.SELL,
}
