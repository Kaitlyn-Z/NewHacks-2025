import { StockAlert } from '@/types';

export const mockStockAlerts: StockAlert[] = [
  {
    id: '1',
    ticker: 'GME',
    mentionCount: 247,
    volumeRatio: 4.2,
    currentPrice: 23.45,
    priceChange: 12.5,
    detectedAt: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    priority: 'high',
    advice: 'GME is showing extremely high volume activity (4.2x average) with strong positive momentum. While the social sentiment is bullish, exercise caution as meme stocks are highly volatile. Consider taking profits or setting stop-losses to manage risk.'
  },
  {
    id: '2',
    ticker: 'AMC',
    mentionCount: 189,
    volumeRatio: 3.8,
    currentPrice: 8.92,
    priceChange: -2.3,
    detectedAt: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
    priority: 'high',
    advice: 'AMC displays high trading volume but negative price momentum. This divergence suggests potential profit-taking or uncertainty. Wait for price stabilization before entry, or consider short-term trading strategies with tight risk management.'
  },
  {
    id: '3',
    ticker: 'BB',
    mentionCount: 156,
    volumeRatio: 2.9,
    currentPrice: 4.67,
    priceChange: 8.7,
    detectedAt: new Date(Date.now() - 18 * 60 * 1000).toISOString(),
    priority: 'medium',
    advice: 'BB shows moderate volume increase with solid positive price action. The momentum is promising but not extreme. This could be a good entry point for swing trading, but maintain position sizing discipline given the meme stock nature.'
  },
  {
    id: '4',
    ticker: 'NOK',
    mentionCount: 98,
    volumeRatio: 2.1,
    currentPrice: 3.21,
    priceChange: 5.2,
    detectedAt: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
    priority: 'medium',
    advice: 'NOK exhibits steady volume growth with positive price momentum. The lower volatility compared to other meme stocks may offer a more conservative play. Monitor for continued social media traction before increasing position size.'
  },
  {
    id: '5',
    ticker: 'PLTR',
    mentionCount: 87,
    volumeRatio: 1.8,
    currentPrice: 15.34,
    priceChange: -1.4,
    detectedAt: new Date(Date.now() - 32 * 60 * 1000).toISOString(),
    priority: 'low',
    advice: 'PLTR shows modest volume activity with slight negative price movement. The current sentiment is mixed. This may be a consolidation phase; wait for clearer directional signals or consider this as a potential buying opportunity if you believe in fundamentals.'
  },
  {
    id: '6',
    ticker: 'TSLA',
    mentionCount: 234,
    volumeRatio: 1.5,
    currentPrice: 245.67,
    priceChange: 3.8,
    detectedAt: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
    priority: 'low',
    advice: 'TSLA maintains high social engagement with moderate volume and positive price action. As a more established stock with meme characteristics, it offers relatively lower risk. The current momentum suggests continued strength; suitable for both short and longer-term positions.'
  },
  {
    id: '7',
    ticker: 'NVDA',
    mentionCount: 145,
    volumeRatio: 2.3,
    currentPrice: 456.78,
    priceChange: 7.2,
    detectedAt: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    priority: 'medium',
    advice: 'NVDA demonstrates strong price appreciation with increased volume, backed by solid fundamentals in AI sector. This combination of technical momentum and fundamental strength makes it attractive. Consider gradual position building on pullbacks rather than chasing the current rally.'
  },
  {
    id: '8',
    ticker: 'AAPL',
    mentionCount: 67,
    volumeRatio: 1.2,
    currentPrice: 189.45,
    priceChange: 1.5,
    detectedAt: new Date(Date.now() - 28 * 60 * 1000).toISOString(),
    priority: 'low',
    advice: 'AAPL shows minimal unusual volume activity with steady positive movement. As a blue-chip stock with occasional meme characteristics, it represents a safer option. The current metrics suggest stable growth rather than speculative surge; suitable for conservative portfolios.'
  }
];

export const generateRandomAlert = (): StockAlert => {
  const tickers = ['GME', 'AMC', 'BB', 'NOK', 'PLTR', 'TSLA', 'NVDA', 'AAPL', 'MSFT', 'GOOGL', 'META', 'AMD'];
  const priorities: ('high' | 'medium' | 'low')[] = ['high', 'medium', 'low'];
  
  const randomTicker = tickers[Math.floor(Math.random() * tickers.length)];
  const randomPriority = priorities[Math.floor(Math.random() * priorities.length)];
  const volumeRatio = Math.random() * 5 + 1;
  const priceChange = (Math.random() - 0.5) * 20;
  
  return {
    id: Math.random().toString(36).substr(2, 9),
    ticker: randomTicker,
    mentionCount: Math.floor(Math.random() * 300) + 10,
    volumeRatio: volumeRatio,
    currentPrice: Math.random() * 500 + 10,
    priceChange: priceChange,
    detectedAt: new Date().toISOString(),
    priority: randomPriority,
    advice: `${randomTicker} is experiencing ${volumeRatio > 3 ? 'high' : volumeRatio > 2 ? 'moderate' : 'low'} volume activity with ${priceChange > 0 ? 'positive' : 'negative'} price momentum. Monitor closely and manage risk appropriately given the volatile nature of meme stocks.`
  };
};
