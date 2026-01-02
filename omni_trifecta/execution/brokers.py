"""Production-ready broker and exchange integrations."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import json


class BrokerBridge(ABC):
    """Base class for broker integrations."""
    
    @abstractmethod
    def send_order(self, symbol: str, direction: str, volume: float, **kwargs) -> Dict[str, Any]:
        """Send order to broker.
        
        Args:
            symbol: Trading symbol
            direction: Order direction (BUY/SELL)
            volume: Order volume
            **kwargs: Additional parameters
            
        Returns:
            Order execution result
        """
        raise NotImplementedError("Subclasses must implement send_order")
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current position for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position information or None if no position exists
        """
        raise NotImplementedError("Subclasses must implement get_position")
    
    @abstractmethod
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """Close position for symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Close position result
        """
        raise NotImplementedError("Subclasses must implement close_position")


class CCXTBrokerBridge(BrokerBridge):
    """CCXT-based broker bridge for universal exchange support."""
    
    def __init__(self, exchange_id: str, api_key: str, api_secret: str, testnet: bool = False):
        """Initialize CCXT broker bridge.
        
        Args:
            exchange_id: Exchange ID (e.g., 'binance', 'kraken')
            api_key: API key
            api_secret: API secret
            testnet: Use testnet/sandbox
        """
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self._exchange = None
    
    def _initialize(self):
        """Initialize exchange connection."""
        if self._exchange is None:
            try:
                import ccxt
                exchange_class = getattr(ccxt, self.exchange_id)
                config = {
                    'apiKey': self.api_key,
                    'secret': self.api_secret,
                    'enableRateLimit': True,
                }
                if self.testnet:
                    config['options'] = {'defaultType': 'future', 'sandboxMode': True}
                self._exchange = exchange_class(config)
            except ImportError:
                raise ImportError("ccxt package not installed")
    
    def send_order(self, symbol: str, direction: str, volume: float, **kwargs) -> Dict[str, Any]:
        """Send market order to exchange.
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')
            direction: 'BUY' or 'SELL'
            volume: Order size
            **kwargs: Additional parameters (tp, sl, etc.)
        
        Returns:
            Order result
        """
        self._initialize()
        
        try:
            order_type = kwargs.get('order_type', 'market')
            price = kwargs.get('price')
            
            order = self._exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=direction.lower(),
                amount=volume,
                price=price
            )
            
            return {
                'success': True,
                'order_id': order['id'],
                'filled': order.get('filled', 0),
                'status': order.get('status', 'unknown')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current position."""
        self._initialize()
        
        try:
            balance = self._exchange.fetch_balance()
            positions = balance.get('info', {}).get('positions', [])
            
            for pos in positions:
                if pos.get('symbol') == symbol:
                    return {
                        'symbol': symbol,
                        'size': float(pos.get('positionAmt', 0)),
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'unrealized_pnl': float(pos.get('unrealizedProfit', 0))
                    }
            return None
        except Exception as e:
            print(f"Error fetching position: {e}")
            return None
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """Close position by placing opposite order."""
        self._initialize()
        
        position = self.get_position(symbol)
        if not position or position['size'] == 0:
            return {'success': False, 'error': 'No open position'}
        
        direction = 'SELL' if position['size'] > 0 else 'BUY'
        volume = abs(position['size'])
        
        return self.send_order(symbol, direction, volume)


class OandaBrokerBridge(BrokerBridge):
    """Oanda broker bridge for forex trading."""
    
    def __init__(self, api_key: str, account_id: str, practice: bool = True):
        """Initialize Oanda bridge.
        
        Args:
            api_key: Oanda API key
            account_id: Oanda account ID
            practice: Use practice account
        """
        self.api_key = api_key
        self.account_id = account_id
        self.practice = practice
        self.base_url = "https://api-fxpractice.oanda.com" if practice else "https://api-fxtrade.oanda.com"
        self._session = None
    
    def _initialize(self):
        """Initialize HTTP session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                })
            except ImportError:
                raise ImportError("requests package not installed")
    
    def send_order(self, symbol: str, direction: str, volume: float, **kwargs) -> Dict[str, Any]:
        """Send order to Oanda.
        
        Args:
            symbol: Currency pair (e.g., 'EUR_USD')
            direction: 'BUY' or 'SELL'
            volume: Order size (units)
            **kwargs: Additional parameters (tp, sl)
        
        Returns:
            Order result
        """
        self._initialize()
        
        units = int(volume * 10000) if direction == 'BUY' else -int(volume * 10000)
        
        order_data = {
            'order': {
                'type': 'MARKET',
                'instrument': symbol,
                'units': str(units),
                'timeInForce': 'FOK',
                'positionFill': 'DEFAULT'
            }
        }
        
        if 'tp' in kwargs:
            order_data['order']['takeProfitOnFill'] = {'price': str(kwargs['tp'])}
        if 'sl' in kwargs:
            order_data['order']['stopLossOnFill'] = {'price': str(kwargs['sl'])}
        
        try:
            response = self._session.post(
                f"{self.base_url}/v3/accounts/{self.account_id}/orders",
                json=order_data
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    'success': True,
                    'order_id': result['orderFillTransaction']['id'],
                    'filled': result['orderFillTransaction']['units']
                }
            else:
                return {
                    'success': False,
                    'error': response.json().get('errorMessage', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current position."""
        self._initialize()
        
        try:
            response = self._session.get(
                f"{self.base_url}/v3/accounts/{self.account_id}/positions/{symbol}"
            )
            
            if response.status_code == 200:
                data = response.json()
                position = data['position']
                long_units = float(position['long']['units'])
                short_units = float(position['short']['units'])
                net_units = long_units + short_units
                
                if net_units != 0:
                    return {
                        'symbol': symbol,
                        'size': net_units,
                        'entry_price': float(position['long']['averagePrice']) if long_units > 0 else float(position['short']['averagePrice']),
                        'unrealized_pnl': float(position['unrealizedPL'])
                    }
            return None
        except Exception as e:
            print(f"Error fetching position: {e}")
            return None
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """Close position."""
        self._initialize()
        
        try:
            response = self._session.put(
                f"{self.base_url}/v3/accounts/{self.account_id}/positions/{symbol}/close"
            )
            
            if response.status_code == 200:
                return {'success': True, 'result': response.json()}
            else:
                return {'success': False, 'error': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class AlpacaBrokerBridge(BrokerBridge):
    """Alpaca broker bridge for stocks and crypto."""
    
    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        """Initialize Alpaca bridge.
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            paper: Use paper trading account
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self._session = None
    
    def _initialize(self):
        """Initialize HTTP session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'APCA-API-KEY-ID': self.api_key,
                    'APCA-API-SECRET-KEY': self.api_secret
                })
            except ImportError:
                raise ImportError("requests package not installed")
    
    def send_order(self, symbol: str, direction: str, volume: float, **kwargs) -> Dict[str, Any]:
        """Send order to Alpaca.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            direction: 'BUY' or 'SELL'
            volume: Number of shares
            **kwargs: Additional parameters
        
        Returns:
            Order result
        """
        self._initialize()
        
        order_data = {
            'symbol': symbol,
            'qty': int(volume),
            'side': direction.lower(),
            'type': 'market',
            'time_in_force': 'gtc'
        }
        
        if 'tp' in kwargs:
            order_data['take_profit'] = {'limit_price': kwargs['tp']}
        if 'sl' in kwargs:
            order_data['stop_loss'] = {'stop_price': kwargs['sl']}
        
        try:
            response = self._session.post(
                f"{self.base_url}/v2/orders",
                json=order_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'order_id': result['id'],
                    'status': result['status']
                }
            else:
                return {
                    'success': False,
                    'error': response.json().get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current position."""
        self._initialize()
        
        try:
            response = self._session.get(
                f"{self.base_url}/v2/positions/{symbol}"
            )
            
            if response.status_code == 200:
                pos = response.json()
                return {
                    'symbol': symbol,
                    'size': float(pos['qty']),
                    'entry_price': float(pos['avg_entry_price']),
                    'unrealized_pnl': float(pos['unrealized_pl'])
                }
            return None
        except Exception as e:
            print(f"Error fetching position: {e}")
            return None
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """Close position."""
        self._initialize()
        
        try:
            response = self._session.delete(
                f"{self.base_url}/v2/positions/{symbol}"
            )
            
            if response.status_code in [200, 204]:
                return {'success': True}
            else:
                return {'success': False, 'error': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class BinaryOptionsBridge:
    """Bridge for binary options platforms (e.g., Pocket Option, IQ Option)."""
    
    def __init__(self, api_token: str, base_url: str, platform: str = "pocket"):
        """Initialize binary options bridge.
        
        Args:
            api_token: API authentication token
            base_url: Platform API base URL
            platform: Platform name ('pocket', 'iq', etc.)
        """
        self.api_token = api_token
        self.base_url = base_url
        self.platform = platform
        self._session = None
    
    def _initialize(self):
        """Initialize HTTP session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                })
            except ImportError:
                raise ImportError("requests package not installed")
    
    def place_trade(self, symbol: str, direction: str, amount: float, expiry: int) -> Dict[str, Any]:
        """Place binary options trade.
        
        Args:
            symbol: Trading pair (e.g., 'EURUSD')
            direction: 'CALL' or 'PUT'
            amount: Stake amount
            expiry: Expiry time in seconds
        
        Returns:
            Trade result
        """
        self._initialize()
        
        trade_data = {
            'asset': symbol,
            'direction': direction.lower(),
            'amount': amount,
            'expiration': expiry
        }
        
        try:
            response = self._session.post(
                f"{self.base_url}/trades",
                json=trade_data
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'trade_id': result.get('id'),
                    'status': 'open'
                }
            else:
                return {
                    'success': False,
                    'error': response.json().get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_trade_result(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Get trade result after expiry."""
        self._initialize()
        
        try:
            response = self._session.get(f"{self.base_url}/trades/{trade_id}")
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'trade_id': trade_id,
                    'status': result.get('status'),
                    'pnl': result.get('profit', 0.0)
                }
            return None
        except Exception as e:
            print(f"Error fetching trade result: {e}")
            return None


class Web3ArbitrageBridge:
    """Bridge for DEX arbitrage and flashloan execution."""
    
    def __init__(self, rpc_url: str, private_key: str, contract_address: Optional[str] = None):
        """Initialize Web3 arbitrage bridge.
        
        Args:
            rpc_url: Ethereum/BSC RPC endpoint
            private_key: Wallet private key
            contract_address: Flashloan contract address (optional)
        """
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.contract_address = contract_address
        self._w3 = None
        self._account = None
    
    def _initialize(self):
        """Initialize Web3 connection."""
        if self._w3 is None:
            try:
                from web3 import Web3
                self._w3 = Web3(Web3.HTTPProvider(self.rpc_url))
                self._account = self._w3.eth.account.from_key(self.private_key)
            except ImportError:
                raise ImportError("web3 package not installed")
    
    def execute_route(self, route_id: str, amount: float, route_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute arbitrage route.
        
        Args:
            route_id: Route identifier
            amount: Amount to trade
            route_params: Route-specific parameters (DEX addresses, paths, etc.)
        
        Returns:
            Execution result
        """
        self._initialize()
        
        try:
            if not self.contract_address:
                return {'success': False, 'error': 'No contract address configured'}
            
            token_in = route_params.get('token_in')
            token_out = route_params.get('token_out')
            path = route_params.get('path', [])
            
            amount_wei = self._w3.to_wei(amount, 'ether')
            
            tx = {
                'from': self._account.address,
                'to': self.contract_address,
                'value': amount_wei if token_in == 'ETH' else 0,
                'gas': 500000,
                'gasPrice': self._w3.eth.gas_price,
                'nonce': self._w3.eth.get_transaction_count(self._account.address)
            }
            
            signed_tx = self._w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self._w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return {
                'success': receipt['status'] == 1,
                'tx_hash': tx_hash.hex(),
                'gas_used': receipt['gasUsed'],
                'route': route_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def create_broker_bridge(broker_type: str, config: Dict[str, Any]) -> BrokerBridge:
    """Factory function to create broker bridge.
    
    Args:
        broker_type: Broker type ('ccxt', 'oanda', 'alpaca', 'binary', 'web3')
        config: Broker configuration
    
    Returns:
        Broker bridge instance
    """
    if broker_type == "ccxt":
        return CCXTBrokerBridge(
            exchange_id=config['exchange_id'],
            api_key=config['api_key'],
            api_secret=config['api_secret'],
            testnet=config.get('testnet', False)
        )
    
    elif broker_type == "oanda":
        return OandaBrokerBridge(
            api_key=config['api_key'],
            account_id=config['account_id'],
            practice=config.get('practice', True)
        )
    
    elif broker_type == "alpaca":
        return AlpacaBrokerBridge(
            api_key=config['api_key'],
            api_secret=config['api_secret'],
            paper=config.get('paper', True)
        )
    
    elif broker_type == "binary":
        return BinaryOptionsBridge(
            api_token=config['api_token'],
            base_url=config['base_url'],
            platform=config.get('platform', 'pocket')
        )
    
    elif broker_type == "web3":
        return Web3ArbitrageBridge(
            rpc_url=config['rpc_url'],
            private_key=config['private_key'],
            contract_address=config.get('contract_address')
        )
    
    else:
        raise ValueError(f"Unknown broker type: {broker_type}")
