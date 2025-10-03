from futu import TrdMarket, SecurityFirm, TrdEnv
from nautilus_trader.common.config import InstrumentProviderConfig

from nautilus_trader.live.config import LiveExecClientConfig


class FutuBrokersInstrumentProviderConfig(InstrumentProviderConfig, frozen=True):
    """
    Configuration for instances of `InteractiveBrokersInstrumentProvider`.

    Specify either `load_ids`, `load_contracts`, or both to dictate which instruments the system loads upon start.
    It should be noted that the `InteractiveBrokersInstrumentProviderConfig` isn't limited to the instruments
    initially loaded. Instruments can be dynamically requested and loaded at runtime as needed.

    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FutuBrokersInstrumentProviderConfig):
            return False

        return (
                self.load_ids == other.load_ids
                and self.load_contracts == other.load_contracts
                and self.min_expiry_days == other.min_expiry_days
                and self.max_expiry_days == other.max_expiry_days
                and self.build_options_chain == other.build_options_chain
                and self.build_futures_chain == other.build_futures_chain
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.load_ids,
                self.load_contracts,
                self.build_options_chain,
                self.build_futures_chain,
                self.min_expiry_days,
                self.max_expiry_days,
                self.convert_exchange_to_mic_venue,
                (
                    tuple(sorted(self.symbol_to_mic_venue.items()))
                    if self.symbol_to_mic_venue
                    else None
                ),
                self.cache_validity_days,
                self.pickle_path,
            ),
        )

    load_contracts: frozenset[str] | None = None
    build_options_chain: bool | None = None
    build_futures_chain: bool | None = None
    min_expiry_days: int | None = None
    max_expiry_days: int | None = None
    convert_exchange_to_mic_venue: bool = False
    symbol_to_mic_venue: dict = {}

    cache_validity_days: int | None = None
    pickle_path: str | None = None


class FutuBrokersExecClientConfig(LiveExecClientConfig, frozen=True):
    """
    Configuration for ``InteractiveBrokersExecClient`` instances.

    Parameters
    ----------
    ibg_host : str, default "127.0.0.1"
        The hostname or ip address for the IB Gateway (IBG) or Trader Workstation (TWS).
    ibg_port : int
        The port for the gateway server. ("paper"/"live" defaults: IBG 4002/4001; TWS 7497/7496)
    ibg_client_id: int, default 1
        The client_id to be passed into connect call.
    account_id : str
        Represents the account_id for the Interactive Brokers to which the TWS/Gateway is logged in.
        It's crucial that the account_id aligns with the account for which the TWS/Gateway is logged in.
        If the account_id is `None`, the system will fallback to use the `TWS_ACCOUNT` from environment variable.
    dockerized_gateway : DockerizedIBGatewayConfig, Optional
        The client's gateway container configuration.
    connection_timeout : int, default 300
        The timeout (seconds) to wait for the client connection to be established.
    fetch_all_open_orders : bool, default False
        If True, uses reqAllOpenOrders to fetch orders from all API clients and TWS GUI.
        If False, uses reqOpenOrders to fetch only orders from current client ID session.
        Note: When using reqAllOpenOrders with client ID 0, it can see orders from all
        sources including TWS GUI, but cannot see orders from other non-zero client IDs.
    track_option_exercise_from_position_update : bool, default False
        If True, subscribes to real-time position updates to track option exercises.

    """
    host: str = "127.0.0.1"
    port: int = 11111
    client_id: int = 1
    account_id: str | None = None
    trade_market: TrdMarket | None = None
    trade_env: TrdEnv = TrdEnv.SIMULATE
    trade_pwd: str | None = None
    fill_outside_rth: bool = False
    security_firm: SecurityFirm = SecurityFirm.FUTUSECURITIES
    connection_timeout: int = 300
    fetch_all_open_orders: bool = False
    track_option_exercise_from_position_update: bool = False
