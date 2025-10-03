from nautilus_trader.common.enums import LogColor
from nautilus_trader.core.message import Event
from nautilus_trader.core.nautilus_pyo3 import TimeInForce
from nautilus_trader.indicators import MovingAverageConvergenceDivergence
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Position
from nautilus_trader.model import QuoteTick, Quantity, Price
from nautilus_trader.model.data import Bar
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import PositionSide
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.events import PositionOpened
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.trading.strategy import StrategyConfig


class MACDConfig(StrategyConfig):
    instrument_id: InstrumentId
    fast_period: int = 12
    slow_period: int = 26
    trade_size: int = 100
    entry_threshold: float = 0.00010


class MACDStrategy(Strategy):
    def __init__(self, config: MACDConfig):
        super().__init__(config=config)
        # Our "trading signal"
        self.macd = MovingAverageConvergenceDivergence(
            fast_period=config.fast_period, slow_period=config.slow_period, price_type=PriceType.MID
        )

        self.trade_size = config.trade_size

        # Convenience
        self.position: Position | None = None

        self.buy_order_price = 99999

        self.can_buy = True
        self.can_sell = False
        self.position_flag = False

    def on_start(self):
        self.subscribe_quote_ticks(instrument_id=self.config.instrument_id)

    def on_stop(self):
        self.close_all_positions(self.config.instrument_id)
        self.unsubscribe_quote_ticks(instrument_id=self.config.instrument_id)

    def on_quote_tick(self, tick: QuoteTick):
        # You can register indicators to receive quote tick updates automatically,
        # here we manually update the indicator to demonstrate the flexibility available.
        # self.log.info(str(tick))
        self.macd.handle_quote_tick(tick)

        if not self.macd.initialized:
            return  # Wait for indicator to warm up

        # self._log.info(f"{self.macd.value=}:%5d")
        self.check_for_entry(tick.bid_price.as_double())
        self.check_for_exit(tick.bid_price.as_double())

    def on_bar(self, bar: Bar) -> None:
        self.log.info(str(bar))

    def on_event(self, event: Event):
        if isinstance(event, PositionOpened):
            self.position = self.cache.position(event.position_id)

    def check_for_entry(self, current_price):
        # If MACD line is above our entry threshold, we should be LONG
        if self.macd.value > self.config.entry_threshold:
            if self.position and self.position.side == PositionSide.LONG:
                return  # Already LONG

            self.execute_buy(current_price=current_price)
        # If MACD line is below our entry threshold, we should be SHORT
        elif self.macd.value < -self.config.entry_threshold:
            if self.position and self.position.side == PositionSide.SHORT:
                return  # Already SHORT

            self.execute_sell(current_price=current_price)

    def check_for_exit(self, current_price):
        # If MACD line is above zero then exit if we are SHORT
        if self.macd.value >= 0.0:
            if self.position_flag == True:
                self.execute_sell(current_price=current_price)
        # If MACD line is below zero then exit if we are LONG
        else:
            if self.position_flag == True:
                self.execute_sell(current_price=current_price)

    def execute_buy(self, current_price):
        """执行买入操作"""
        if self.position and self.position.side == OrderSide.BUY:
            self.log.info("已有买入持仓，跳过")
            return

        if not self.can_buy:
            return

        if self.position_flag == True:
            return

            # 开多头仓位
        order = self.order_factory.limit(
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.BUY,
            price=Price(current_price, 2),
            quantity=Quantity.from_int(self.trade_size),
            time_in_force=TimeInForce.GTC,
        )

        self.submit_order(order)
        self.buy_order_price = current_price
        self.can_buy = False
        self.can_sell = True
        self.log.info(f"提交买入订单: {order}")

    def execute_sell(self, current_price):
        """执行卖出操作"""
        if self.position and self.position.side == OrderSide.SELL:
            self.log.info("已有卖出持仓，跳过")

        if self.buy_order_price > current_price:
            self.log.info("已有 current_price < buy_order_price + 3 ，跳过")
            return

        if not self.can_sell:
            return

        if self.buy_order_price + 3 < current_price:
            # 开空头仓位
            order = self.order_factory.limit(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.SELL,
                price=Price(current_price, 2),
                quantity=Quantity.from_int(self.trade_size),
                time_in_force=TimeInForce.GTC,
            )

            self.submit_order(order)
            self.buy_order_price = 9999
            self.can_buy = True
            self.can_sell = False
            self.log.info(f"提交卖出订单: {order}")

    def on_order_filled(self, order):
        """订单成交时调用"""
        self.log.info(f"订单成交: {order}", color=LogColor.CYAN)

        # 更新仓位信息
        self.position = self.cache.position_for_order(order.client_order_id)

        if order.order_side == "BUY":
            self.position_flag = True
        else:
            self.position_flag = False

        if self.position:
            self.log.info(f"当前仓位: {self.position}")

    def on_dispose(self):
        pass  # Do nothing else