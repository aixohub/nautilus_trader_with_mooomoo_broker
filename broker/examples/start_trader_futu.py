from datetime import datetime

from futu import TrdMarket, TrdEnv, SecurityFirm
from nautilus_trader.adapters.interactive_brokers.common import IB
from nautilus_trader.adapters.interactive_brokers.config import IBMarketDataTypeEnum
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers.config import SymbologyMethod
from nautilus_trader.adapters.interactive_brokers.factories import InteractiveBrokersLiveDataClientFactory
from nautilus_trader.adapters.interactive_brokers.factories import InteractiveBrokersLiveExecClientFactory
from nautilus_trader.config import LiveDataEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import RoutingConfig
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.examples.strategies.subscribe import SubscribeStrategy
from nautilus_trader.examples.strategies.subscribe import SubscribeStrategyConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.identifiers import InstrumentId

from broker.moomoo.common import FUTU
from broker.moomoo.config import FutuBrokersExecClientConfig
from broker.moomoo.factories import FutuBrokersLiveExecClientFactory
from MACDStrategy import MACDStrategy, MACDConfig


# fmt: on

# *** THIS IS A TEST STRATEGY WITH NO ALPHA ADVANTAGE WHATSOEVER. ***
# *** IT IS NOT INTENDED TO BE USED TO TRADE LIVE WITH REAL MONEY. ***

# *** THIS INTEGRATION IS STILL UNDER CONSTRUCTION. ***
# *** CONSIDER IT TO BE IN AN UNSTABLE BETA PHASE AND EXERCISE CAUTION. ***

class TraderWorkstation:

    def __init__(self, instrument_id, strategy, account_id):
        self.instrument_id = instrument_id
        self.strategy = strategy
        self.account_id = account_id

        print("")

    def start(self):
        instrument_provider = InteractiveBrokersInstrumentProviderConfig(
            symbology_method=SymbologyMethod.IB_SIMPLIFIED,
            load_ids=frozenset(
                [
                    self.instrument_id,

                ],
            ),
        )

        # Configure the trading node

        config_node = TradingNodeConfig(
            trader_id="TESTER-001",

            logging=LoggingConfig(
                log_level="INFO",
                log_level_file="INFO",
                log_file_name=datetime.strftime(
                    datetime.utcnow(),
                    "%Y-%m-%d_%H-%M",
                ) + f"_order_{self.instrument_id}.log",
                log_directory="./logs/",
                print_config=True,
            ),
            data_clients={
                IB: InteractiveBrokersDataClientConfig(
                    ibg_host="127.0.0.1",
                    ibg_port=4002,
                    ibg_client_id=2,
                    handle_revised_bars=False,
                    use_regular_trading_hours=True,  # Include extended hours
                    market_data_type=IBMarketDataTypeEnum.REALTIME,  # Real-time data
                    instrument_provider=instrument_provider,
                ),
            },
            exec_clients={
                FUTU: FutuBrokersExecClientConfig(
                    host="127.0.0.1",
                    port=11111,
                    client_id=2,
                    account_id=self.account_id,
                    security_firm=SecurityFirm.FUTUINC,
                    trade_pwd='',
                    trade_market=TrdMarket.US,
                    trade_env=TrdEnv.SIMULATE,
                    fill_outside_rth=True,
                    routing=RoutingConfig(
                        default=True,
                    ),
                ),
            },
            data_engine=LiveDataEngineConfig(
                time_bars_timestamp_on_close=False,  # Will use opening time as `ts_event` (same like IB)
                validate_data_sequence=True,  # Will make sure DataEngine discards any Bars received out of sequence
            ),
            timeout_connection=90.0,
            timeout_reconciliation=5.0,
            timeout_portfolio=5.0,
            timeout_disconnection=5.0,
            timeout_post_stop=2.0,
        )

        # Instantiate the node with a configuration
        node = TradingNode(config=config_node)

        # Add your strategies and modules
        node.trader.add_strategy(self.strategy)

        # Register your client factories with the node (can take user-defined factories)
        node.add_data_client_factory(IB, InteractiveBrokersLiveDataClientFactory)
        node.add_exec_client_factory(FUTU, FutuBrokersLiveExecClientFactory)

        node.build()
        return node


# Stop and dispose of the node with SIGINT/CTRL+C
if __name__ == "__main__":
    # instrument_id_str = "TSLA.NASDAQ"
    # instrument_id_str = "NVDA.NASDAQ"
    instrument_id_str = "APP.NASDAQ"
    # instrument_id_str = "CRCL.NASDAQ"
    #instrument_id_str = "QUBT.NASDAQ"
    # instrument_id_str = "IONQ.NASDAQ"
    # instrument_id_str = "HL.NASDAQ"
    # Configure your strategy      instrument_id=InstrumentId.from_str("EUR/USD.IDEALPRO"),
    strategy_config = SubscribeStrategyConfig(
        instrument_id=InstrumentId.from_str(instrument_id_str),
        trade_ticks=False,
        quote_ticks=True,
        bars=True,
    )
    # Instantiate your strategy
    strategy = SubscribeStrategy(config=strategy_config)

    macd_strategy_config = MACDConfig(
        instrument_id=InstrumentId.from_str(instrument_id_str),
    )
    # 添加策略
    strategy3 = MACDStrategy(macd_strategy_config)

    account_id = "U8889990"

    node = TraderWorkstation(instrument_id_str, strategy3, account_id).start()
    try:
        node.run()
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            node.stop()
        finally:
            node.dispose()
